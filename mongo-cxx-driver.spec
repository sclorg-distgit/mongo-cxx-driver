%{?scl:%scl_package mongo-cxx-driver}
%{!?scl:%global pkg_name %{name}}

# Do we want to run tests during build
%bcond_without run_tests

%global buildscls %{?scl} devtoolset-6

Name:           %{?scl_prefix}mongo-cxx-driver
Version:        3.1.2
Release:        1%{?dist}
Summary:        The MongoDB C++11 Driver Library
Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/mongodb/%{pkg_name}
Source0:        https://github.com/mongodb/%{pkg_name}/archive/r%{version}.tar.gz

# Allow building with system cmake which is older than 3.2 required by upstream
Patch0:         allow-older-cmake.patch

Requires:       %{?scl_prefix}%{pkg_name}-bsoncxx%{?_isa} = %{version}-%{release}

%{?scl:Requires: %{scl}-runtime}
BuildRequires:  %{?scl_prefix}boost-devel
BuildRequires:  devtoolset-6-gcc-c++
BuildRequires:  cmake
BuildRequires:  %{?scl_prefix}mongo-c-driver-devel >= 1.5.0
BuildRequires:  %{?scl_prefix}libbson-devel >= 1.5.0
BuildRequires:  openssl-devel
BuildRequires:  cyrus-sasl-devel
%if %{with run_tests}
BuildRequires:  %{?scl_prefix}mongodb-server
%endif


%description
This package provides the shared library for the MongoDB C++ Driver.



%package devel
Summary:        The MongoDB C++11 Driver Library header files
Group:          Development/Libraries
Requires:       %{?scl_prefix}%{pkg_name}%{?_isa} = %{version}-%{release}


%description devel
This package provides the header files for MongoDB C++ driver.


%package bsoncxx
Summary:        C++ library for working with BSON
Group:          Development/Libraries
Requires:       %{?scl_prefix}%{pkg_name}%{?_isa} = %{version}-%{release}


%description bsoncxx
This package provides the shared library for working with BSON.


%package bsoncxx-devel
Summary:        C++ header files for library for working with BSON
Group:          Development/Libraries
Requires:       %{?scl_prefix}%{pkg_name}-bsoncxx%{?_isa} = %{version}-%{release}


%description bsoncxx-devel
This package provides the C++ header files for library for working with BSON.




%prep
%{?scl:scl enable %{buildscls} - << \EOF}
set -ex
# -n the name of the directory to cd after unpacking
%setup -q -n %{pkg_name}-r%{version}
%patch0 -p1

# Install to lib64/ instead of lib/ directories
sed -i -e 's|lib\([ /)]\)|lib${LIB_SUFFIX}\1|g' \
        src/*/CMakeLists.txt \
        src/*/config/CMakeLists.txt

sed -i -e "s|lib$|$(basename %{_libdir})|g" \
        src/*/config/*.pc.in
%{?scl:EOF}


%build
%{?scl:scl enable %{buildscls} - << \EOF}
set -ex
%cmake -DBSONCXX_POLY_USE_BOOST=1 -DCMAKE_SKIP_RPATH=1 .
make %{?_smp_mflags}
%{?scl:EOF}


%install
%{?scl:scl enable %{buildscls} - << \EOF}
set -e
%make_install

# There is no option to build without static library
rm -f %{buildroot}%{_libdir}/libmongocxx.a \
      %{buildroot}%{_libdir}/libbsoncxx.a

%{?scl:EOF}


%check
%{?scl:scl enable %{buildscls} - << \EOF}
set -ex
%if %{with run_tests}
: Run a server
mkdir dbtest
mongod \
  --logpath     $PWD/server.log \
  --dbpath      $PWD/dbtest \
  --fork

: Run the test suite
ret=0
make test || ret=1

: Cleanup
mongod --dbpath $PWD/dbtest --shutdown

exit $ret
%endif
%{?scl:EOF}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%{!?_licensedir:%global license %%doc}
%files
%doc README.md
%license LICENSE
%{_libdir}/libmongocxx.so.*


%files devel
%{_includedir}/mongocxx/
%{_libdir}/libmongocxx.so
%{_libdir}/pkgconfig/libmongocxx.pc
%{_libdir}/cmake/libmongocxx*


%files bsoncxx
%doc README.md
%license LICENSE
%{_libdir}/libbsoncxx.so.*


%files bsoncxx-devel
%{_includedir}/bsoncxx
%{_libdir}/libbsoncxx.so
%{_libdir}/pkgconfig/libbsoncxx.pc
%{_libdir}/cmake/libbsoncxx*


%changelog
* Tue Jul 18 2017 Marek Skalický <mskalick@redhat.com> - 3.1.2-1
- Update to 3.1.2
  Resolves: RHBZ#1474255

* Mon Jun 26 2017 Marek Skalický <mskalick@redhat.com> - 3.1.1-5
- Add explicit package version requirement

* Fri Jun 23 2017 Marek Skalický <mskalick@redhat.com> - 3.1.1-4
- Fix bsoncxx dependency

* Fri Jun 23 2017 Marek Skalický <mskalick@redhat.com> - 3.1.1-3
- Run tests during build

* Thu Jun 22 2017 Marek Skalický <mskalick@redhat.com> - 3.1.1-2
- Convert to SCL
- Add patch to allow using of older cmake from RHEL

* Wed Jun 14 2017 Marek Skalický <mskalick@redhat.com> - 3.1.1-1
- Update to stable C++ release line r3.1.x (uncompatible with legacy version)

* Tue Feb 28 2017 Marek Skalický <mskalick@redhat.com> - 1.1.2-5
- Temporary disable optimizations (some tests are failing with it)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Nov 19 2016 Peter Robinson <pbrobinson@fedoraproject.org> 1.1.2-3
- Remove ExclusiveArch. While a MongoDB instance is little endian only, this is a client
- Build with openssl 1.0

* Tue Aug 02 2016 Marek Skalický <mskalick@redhat.com> - 1.1.2-2
- Enabled sasl support
- Unit tests added in check section

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
