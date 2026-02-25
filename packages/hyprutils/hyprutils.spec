Name:           hyprutils
Version:        0.11.0
Release:        %autorelease
Summary:        Utility library used across the Hyprland ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprutils
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(pixman-1)

%description
Hyprutils is a small C++ utility library used across the Hyprland ecosystem.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Upstream ships optional tests that require GTest; disabled for bootstrap builds.
:

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprutils.so.*

%files devel
%{_includedir}/hyprutils/
%{_libdir}/libhyprutils.so
%{_libdir}/pkgconfig/hyprutils.pc

%changelog
%autochangelog
