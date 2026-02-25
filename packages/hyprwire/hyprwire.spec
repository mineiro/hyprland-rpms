Name:           hyprwire
Version:        0.3.0
Release:        %autorelease
Summary:        Hyprland ecosystem Wayland protocol codegen and wire helpers

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwire
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils) >= 0.9.0
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(pugixml)

%description
Hyprwire provides protocol code generation tools and support libraries used by
Hyprland ecosystem components.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and build metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Upstream tests are optional and disabled for bootstrap builds.
:

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprwire-scanner
%{_libdir}/libhyprwire.so.*

%files devel
%{_includedir}/hyprwire/
%{_libdir}/libhyprwire.so
%{_libdir}/pkgconfig/hyprwire.pc
%{_libdir}/pkgconfig/hyprwire-scanner.pc
%{_libdir}/cmake/hyprwire-scanner/

%changelog
%autochangelog
