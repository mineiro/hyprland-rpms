Name:           hyprwayland-scanner
Version:        0.4.5
Release:        %autorelease
Summary:        Wayland protocol scanner for the Hyprland ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwayland-scanner
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(pugixml)

%description
A C++23 Wayland protocol scanner used by the Hyprland ecosystem to generate
modern C++ bindings for Wayland protocols.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Upstream does not ship an automated test suite in the release tarball.
:

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprwayland-scanner
%{_libdir}/pkgconfig/hyprwayland-scanner.pc
%{_libdir}/cmake/hyprwayland-scanner/hyprwayland-scanner-config.cmake
%{_libdir}/cmake/hyprwayland-scanner/hyprwayland-scanner-config-version.cmake

%changelog
%autochangelog
