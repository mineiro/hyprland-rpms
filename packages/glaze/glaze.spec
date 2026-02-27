%global debug_package %{nil}

Name:           glaze
Version:        7.0.2
Release:        %autorelease
Summary:        Header-only C++ JSON serialization and reflection library

License:        MIT
URL:            https://github.com/stephenberry/glaze
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build

%description
Glaze is a header-only C++ library for JSON serialization, reflection, and
related utilities. This package installs headers and CMake package metadata.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%cmake \
  -Dglaze_INSTALL_CMAKEDIR=%{_libdir}/cmake/glaze \
  -Dglaze_DEVELOPER_MODE=OFF \
  -Dglaze_ENABLE_FUZZING=OFF \
  -DBUILD_TESTING=OFF \
  -DGLAZE_BUILD_TESTS=OFF \
  -Dglaze_BUILD_TESTS=OFF \
  -DGLAZE_BUILD_EXAMPLES=OFF \
  -Dglaze_BUILD_EXAMPLES=OFF
%cmake_build

%install
%cmake_install

%check
# Tests are disabled for bootstrap packaging.
:

%files
%license LICENSE
%doc README.md
%{_includedir}/glaze
%{_libdir}/cmake/glaze

%changelog
%autochangelog
