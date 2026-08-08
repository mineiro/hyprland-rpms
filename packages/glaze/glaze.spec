%global debug_package %{nil}

# Keep this package on the 7.x series. Hyprland resolves glaze with
# `find_package(glaze 7...<8)`, so an 8.x update here would stop satisfying it
# and silently fall back to an offline-unavailable FetchContent download.
# 7.9.1 is the newest 7.x tag; do not take the upstream 8.x tags that the
# upstream version audit reports until Hyprland raises that bound.

Name:           glaze
Version:        7.9.1
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
