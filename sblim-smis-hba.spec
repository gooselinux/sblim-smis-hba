%define provider_dir %{_libdir}/cmpi/

Name:           sblim-smis-hba
Version:        1.0.0
Release:        1%{?dist}
Summary:        SBLIM SMIS HBA HDR Providers

Group:          Systems Management/Base
License:        EPL and SNIA
URL:            http://sblim.wiki.sourceforge.net/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Patch4: upstream tarball doesn't contain testsuite but default Makefile is going to build it
Patch0:         sblim-smis-hba-1.0.0-no-testsuite.patch
Patch1:         sblim-smis-hba-1.0.0-include.patch

BuildRequires:  sblim-cmpi-devel, sblim-tools-libra-devel, sblim-cmpi-base-devel
BuildRequires:  libhbaapi-devel
BuildRequires:  autoconf, automake, libtool
BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}, curl-devel, perl, libsysfs-devel
BuildRequires:  binutils-devel, autoconf, automake, libtool, flex, bison

Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires:       tog-pegasus
Requires:       libhbaapi
Requires:       sblim-cmpi-base

%description
SMI-S standards based HBA CMPI Providers.

%package devel
Summary:       SBLIM SMIS HBA HDR Instrumentation Header Development Files
Requires:      %{name} = %{version}-%{release}

%description devel
SBLIM SMIS HBA HDR Provider Development Package contains header files and
link libraries for dependent provider packages.

%package test
Summary:       SBLIM SMIS HBA HDR Instrumentation Testcase Files
Requires:      %{name} = %{version}-%{release}
Requires:      sblim-testsuite

%description -n        sblim-smis-hba-test
SBLIM SMIS HBA HDR Testcase Files for the SBLIM Testsuite


%prep
%setup -q
%patch0 -p1 -b .no-testsuite
%patch1 -p2 -b .include
autoreconf
# ltmain.sh is old, create new one
rm -f ltmain.sh
libtoolize --force


%build
%configure \
   TESTSUITEDIR=%{_datadir}/sblim-testsuite \
   CIMSERVER=pegasus \
   PROVIDERDIR=%{provider_dir} \
   LDFLAGS="-L${RPM_BUILD_ROOT}%{_libdir}/cmpi";
# workaround libtool issue
sed -i -e '/not ending/ s/.*/true/' libtool
# do not use smp_flags!
make


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{_libdir}/cmpi/*a


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%docdir %{_datadir}/doc/%{name}-%{version}
%{_datadir}/%{name}
%{_datadir}/doc/%{name}-%{version}
/%{_libdir}/cmpi/libcmpiLinux_Common.so*
/%{_libdir}/cmpi/libcmpiLinux_ECTP_Provider.so*
/%{_libdir}/cmpi/libcmpiSMIS_HBA_HDR_Provider.so*

#%files devel
#%defattr(-,root,root,-)
#%{_includedir}/*
#%{_libdir}/*.so


%define HBA_SCHEMA %{_datadir}/%{name}/Linux_SMIS_HBA_HDR.mof %{_datadir}/%{name}/Linux_SMIS_ECTP.mof
%define HBA_REGISTRATION %{_datadir}/%{name}/Linux_SMIS_HBA_HDR.reg %{_datadir}/%{name}/Linux_SMIS_ECTP.reg

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]
then
  %{_datadir}/%{name}/provider-register.sh -d \
        -r %{HBA_REGISTRATION} -m %{HBA_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
# Register Schema and Provider - this is higly provider specific
%{_datadir}/%{name}/provider-register.sh \
        -r %{HBA_REGISTRATION} -m %{HBA_SCHEMA} > /dev/null 2>&1 || :;
/sbin/ldconfig

%preun
# Deregister only if not upgrading 
if [ $1 -eq 0 ]
then
  %{_datadir}/%{name}/provider-register.sh -d \
        -r %{HBA_REGISTRATION} -m %{HBA_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun
if [ $1 -eq 0 ]
then
  /sbin/ldconfig
fi


%changelog
* Thu Jul 15 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.0.0-1
- Initial support

