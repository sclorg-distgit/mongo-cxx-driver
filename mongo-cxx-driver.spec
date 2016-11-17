%{?scl:%scl_package mongo-cxx-driver}
# for better compatibility with SCL spec file
%global pkg_name mongo-cxx-driver

#%global scl_python2 python27
#%global buildscls %{scl} %{?scl_python2}
%global buildscls %{scl}

Name:           %{?scl_prefix}mongo-cxx-driver
Version:        1.1.2
Release:        4%{?dist}
Summary:        A legacy C++ Driver for MongoDB
Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/mongodb/mongo-cxx-driver/wiki
Source0:        https://github.com/mongodb/%{pkg_name}/archive/legacy-%{version}.tar.gz

BuildRequires:  %{?scl_prefix}boost-devel >= 1.49
BuildRequires:  openssl-devel
BuildRequires:  %{?scl_prefix}scons
BuildRequires:  cyrus-sasl-devel
# Tests requirements
#BuildRequires:  %{?scl_python2}-python-virtualenv
#BuildRequires:  %{?scl_prefix}mongodb-server
#BuildRequires:  git

#%{?scl_python2:
#BuildRequires:  %{scl_python2}-python-virtualenv
#}

# Mongodb must run on a little-endian CPU (see bug #630898)
ExcludeArch:    ppc ppc64 %{sparc} s390 s390x

Provides: %{?scl_prefix}libmongodb = 2.6.0-%{release}
Provides: %{?scl_prefix}libmongodb%{?_isa} = 2.6.0-%{release}
Obsoletes: %{?scl_prefix}libmongodb <= 2.4.9-8

%description
This package provides the shared library for the MongoDB legacy C++ Driver.


%package devel
Summary:        MongoDB header files
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}

Provides: %{?scl_prefix}libmongodb-devel = 2.6.0-%{release}
Provides: %{?scl_prefix}libmongodb-devel%{?_isa} = 2.6.0-%{release}
Obsoletes: %{?scl_prefix}libmongodb-devel <= 2.4.9-8

Provides:       %{?scl_prefix}mongodb-devel = 2.6.0-%{release}
Obsoletes:      %{?scl_prefix}mongodb-devel < 2.4

%description devel
This package provides the header files for MongoDB legacy C++ driver.


%prep
# -n the name of the directory to cd after unpacking
%setup -q -n %{pkg_name}-legacy-%{version}

# CRLF -> LF
sed -i 's/\r//' README.md

# use _lib
sed -i -e "s@\$INSTALL_DIR/lib@\$INSTALL_DIR/%{_lib}@g" src/SConscript.client

# versioned client library
(pre='EnsureSConsVersion(2, 3, 0)'
post='sharedLibEnv.AppendUnique(SHLIBVERSION="%{?scl_prefix}%{version}")'
sed -i -r \
  -e "s|([[:space:]]*)(sharedLibEnv *= *libEnv.Clone.*)|\1$pre\n\1\2\n\1$post|" \
  -e "s|(sharedLibEnv.)Install *\(|\1InstallVersionedLib(|" \
  src/SConscript.client)

# use optflags
(opt=$(echo "%{optflags}" | sed -r -e 's| |","|g' )
sed -i -r -e "s|(if nix:)|\1\n\n    env.Append( CCFLAGS=[\"$opt\"] )\n\n|" SConstruct)

# fix one unit test which uses gnu++11 code (c++11 is used)
sed -i 's|ASSERT_PARSES(double, "0xabcab.defdefP-10", 0xabcab.defdefP-10);||' src/mongo/base/parse_number_test.cpp

# Fix boost:ref usage in examples
sed -i -r -e "s|boost::ref|std::ref|g" src/mongo/client/examples/connect.cpp


%build
%{?scl:scl enable %{buildscls} - << "EOF"}
# see 'scons -h' for options
scons \
        %{?_smp_mflags} \
        --sharedclient \
        --ssl \
        --use-sasl-client \
        --disable-warnings-as-errors \
        --propagate-shell-environment

%{?scl:EOF}

%install
%{?scl:scl enable %{buildscls} - << "EOF"}
# NOTE: If install flags are not the same as in %%build,
#   it will be built twice!
scons install \
        %{?_smp_mflags} \
        --sharedclient \
        --ssl \
        --use-sasl-client \
        --disable-warnings-as-errors \
        --propagate-shell-environment \
        --prefix=%{buildroot}%{_prefix}

# There is no option to build without static library
rm -f %{buildroot}%{_libdir}/libmongoclient.a

ln -s libmongoclient.so.%{?scl_prefix}%{version}    %{buildroot}%{_libdir}/libmongoclient.so.%{?scl_prefix}1
ln -s libmongoclient.so.%{?scl_prefix}%{version}    %{buildroot}%{_libdir}/libmongoclient.so

%{?scl:EOF}

%check
%{?scl:scl enable %{buildscls} - << "EOF"}
### Koji and Brew do not allow internet connection during build,
### so skipping integration tests and building examples

## Install mongo-orchestration into virtualenvironment
#virtualenv ./orchestration
#source ./orchestration/bin/activate
#pip install git+git://github.com/mongodb/mongo-orchestration@master

## Tests need running mongo-orchestration
#mongo-orchestration start --no-fork &

# Run tests
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH \
scons unit \
        %{?_smp_mflags} \
        --sharedclient \
        --ssl \
        --disable-warnings-as-errors \
        --use-sasl-client \
        --gtest-filter=-SASL* \
        --propagate-shell-environment

#mongo-orchestration stop

%{?scl:EOF}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc README.md APACHE-2.0.txt
%{_libdir}/libmongoclient.so.*

%files devel
%{_includedir}/*
%{_libdir}/libmongoclient.so

%changelog
* Thu Oct 20 2016 Marek Skalický <mskalick@redhat.com> - 1.1.2-4
- Disable c++11, do not use devtoolset-4 for building
   Resolves: RHBZ#1387220

* Tue Aug 02 2016 Marek Skalický <mskalick@redhat.com> - 1.1.2-3
- Unit tests added in check section

* Mon Jul 25 2016 Marek Skalický <mskalick@redhat.com> - 1.1.2-2
- Converted to SCL

* Wed Jun 22 2016 Marek Skalicky <mskalick@redhat.com> - 1.1.2-1
- Upgrade to version 1.1.2

* Tue May 17 2016 Jonathan Wakely <jwakely@redhat.com> - 1.1.0-4
- Rebuilt for linker errors in boost (#1331983)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 18 2016 Jonathan Wakely <jwakely@redhat.com> - 1.1.0-2
- Rebuilt for Boost 1.60

* Thu Dec 10 2015 Marek Skalicky <mskalick@redhat.com> - 1.1.0-1
- Upgrade to version 1.1.0

* Fri Nov 20 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.7-1
- Upgrade to version 1.0.7

* Thu Oct 22 2015 Tim Niemueller <tim@niemueller.de> - 1.0.6-1
- Upgrade to version 1.0.6
- Add --c++11 flag

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1.0.5-2
- Rebuilt for Boost 1.59

* Wed Aug 19 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.5-1
- Upgrade to version 1.0.5

* Mon Aug 17 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.4-1
- Upgrade to version 1.0.4

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1.0.2-3
- rebuild for Boost 1.58

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 26 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.2-1
- Upgrade to version 1.0.2

* Tue Apr 14 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.1-1
- Upgrade to version 1.0.1

* Tue Feb 10 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.0-3
- Disabled -Werror (dont't build with gcc 5.0)

* Wed Feb 04 2015 Petr Machata <pmachata@redhat.com> - 1.0.0-2
- Bump for rebuild.

* Thu Jan 29 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.0-1
- Upgrade to stable version 1.0.0

* Tue Jan 27 2015 Petr Machata <pmachata@redhat.com> - 1.0.0-0.8.rc3
- Rebuild for boost 1.57.0

* Fri Jan 02 2015 Marek Skalicky <mskalick@redhat.com> - 1.0.0-0.7.rc3
- Upgrade to rc3

* Tue Nov 18 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.6.rc2
- Upgrade to rc2
- Changed scons target to build only driver

* Mon Oct 27 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.5.rc1
- Upgrade to rc1
- Added mongo-cxx-driver-devel requires (openssl-devel, boost-devel)

* Sat Oct 25 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.0-0.4.rc1
- Don't reset the Release until 1.0.0 GA

* Fri Oct 24 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.1.rc1
- Upgrade to rc1

* Thu Oct 9 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.3.rc0
- Added Provides: mongodb-devel = 2.6.0-1 provided by libmongo-devel

* Thu Oct 9 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.2.rc0
- Added Provides: libmongodb%{?_isa} packages

* Tue Sep 30 2014 Marek Skalický <mskalick@redhat.com> - 1.0.0-0.1.rc0
- initial port
