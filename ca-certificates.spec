### Note that mkcabundle.pl is used to generate ca-bundle.crt
### before generating a source RPM, and is not used during the
### build.

%define pkidir %{_sysconfdir}/pki

Summary: The Mozilla CA root certificate bundle
Name: ca-certificates
Version: 2010
Release: 3%{?dist}
License: Public Domain
Group: System Environment/Base
URL: http://www.mozilla.org/
Source0: certdata.txt
Source1: blacklist.txt
Source2: generate-cacerts.pl
Source3: certdata2pem.py
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: perl, java-openjdk, python, rcs
BuildArch: noarch

%description
This package contains the set of CA certificates chosen by the
Mozilla Foundation for use with the Internet PKI.

%prep
rm -rf %{name}
mkdir %{name} %{name}/certs %{name}/java

%build
pushd %{name}/certs
 cp %{SOURCE0} %{SOURCE1} .
 python %{SOURCE3} 
popd
pushd %{name}
 (
   cat <<EOF
# This is a bundle of X.509 certificates of public Certificate
# Authorities.  It was generated from the Mozilla root CA list.
#
# Source: mozilla/security/nss/lib/ckfw/builtins/certdata.txt
#
# Generated from:
EOF
   ident -q %{SOURCE0} | sed '1d;s/^/#/';
   echo '#';
 ) > ca-bundle.crt
 (
   cat <<EOF
# This is a bundle of X.509 certificates of public Certificate
# Authorities.  It was generated from the Mozilla root CA list.
# These certificates are in the OpenSSL "TRUSTED CERTIFICATE"
# format and have trust bits set accordingly.
#
# Source: mozilla/security/nss/lib/ckfw/builtins/certdata.txt
#
# Generated from:
EOF
   ident -q %{SOURCE0} | sed '1d;s/^/#/';
   echo '#';
 ) > ca-bundle.trust.crt
 for f in certs/*.crt; do 
   tbits=`sed -n '/^# openssl-trust/{s/^.*=//;p;}' $f`
   case $tbits in
   *serverAuth*) openssl x509 -text -in "$f" >> ca-bundle.crt ;;
   esac
   if [ -n "$tbits" ]; then
      targs=""
      for t in $tbits; do
         targs="${targs} -addtrust $t"
      done
      openssl x509 -text -in "$f" -trustout $targs >> ca-bundle.trust.crt
   fi
 done
popd
pushd %{name}/java
 test -s ../ca-bundle.crt || exit 1
 %{__perl} %{SOURCE2} %{_bindir}/keytool ../ca-bundle.crt
 touch -r %{SOURCE0} cacerts
popd

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT{%{pkidir}/tls/certs,%{pkidir}/java}

install -p -m 644 %{name}/ca-bundle.crt $RPM_BUILD_ROOT%{pkidir}/tls/certs/ca-bundle.crt
install -p -m 644 %{name}/ca-bundle.trust.crt $RPM_BUILD_ROOT%{pkidir}/tls/certs/ca-bundle.crt
ln -s certs/ca-bundle.crt $RPM_BUILD_ROOT%{pkidir}/tls/cert.pem
touch -r %{SOURCE0} $RPM_BUILD_ROOT%{pkidir}/tls/certs/ca-bundle.crt
touch -r %{SOURCE0} $RPM_BUILD_ROOT%{pkidir}/tls/certs/ca-bundle.trust.crt

# Install Java cacerts file.
mkdir -p -m 700 $RPM_BUILD_ROOT%{pkidir}/java
install -p -m 644 %{name}/java/cacerts $RPM_BUILD_ROOT%{pkidir}/java/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{pkidir}/java
%config(noreplace) %{pkidir}/java/cacerts
%dir %{pkidir}/tls
%dir %{pkidir}/tls/certs
%config(noreplace) %{pkidir}/tls/certs/ca-bundle.*crt
%{pkidir}/tls/cert.pem

%changelog
* Thu Mar 18 2010 Joe Orton <jorton@redhat.com> - 2010-3
- update to certdata.txt r1.58
- add /etc/pki/tls/certs/ca-bundle.trust.crt using 'TRUSTED CERTICATE' format
- exclude ECC certs from the Java cacerts database
- catch keytool failures
- fail parsing certdata.txt on finding untrusted but not blacklisted cert

* Fri Jan 15 2010 Joe Orton <jorton@redhat.com> - 2010-2
- fix Java cacert database generation: use Subject rather than Issuer
  for alias name; add diagnostics; fix some alias names.

* Mon Jan 11 2010 Joe Orton <jorton@redhat.com> - 2010-1
- adopt Python certdata.txt parsing script from Debian

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2009-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Joe Orton <jorton@redhat.com> 2009-1
- update to certdata.txt r1.53

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2008-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Oct 14 2008 Joe Orton <jorton@redhat.com> 2008-7
- update to certdata.txt r1.49

* Wed Jun 25 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 2008-6
- Change generate-cacerts.pl to produce pretty aliases.

* Mon Jun  2 2008 Joe Orton <jorton@redhat.com> 2008-5
- include /etc/pki/tls/cert.pem symlink to ca-bundle.crt

* Tue May 27 2008 Joe Orton <jorton@redhat.com> 2008-4
- use package name for temp dir, recreate it in prep

* Tue May 27 2008 Joe Orton <jorton@redhat.com> 2008-3
- fix source script perms
- mark packaged files as config(noreplace)

* Tue May 27 2008 Joe Orton <jorton@redhat.com> 2008-2
- add (but don't use) mkcabundle.pl
- tweak description
- use /usr/bin/keytool directly; BR java-openjdk

* Tue May 27 2008 Joe Orton <jorton@redhat.com> 2008-1
- Initial build (#448497)
