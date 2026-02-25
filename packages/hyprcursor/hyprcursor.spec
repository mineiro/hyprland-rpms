Name:           hyprcursor
Version:        0.1.13
Release:        %autorelease
Summary:        Hyprland cursor format library and utilities

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprlang) >= 0.4.2
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(tomlplusplus)

%description
Hyprcursor provides the Hyprland cursor format library and utilities,
including `hyprcursor-util` for creating cursor themes.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DINSTALL_TESTS=OFF
%cmake_build

%install
%cmake_install

%check
# Upstream tests are built during %build; test execution is skipped in bootstrap packaging.
:

%files
%license LICENSE
%doc README.md docs/
%{_bindir}/hyprcursor-util
%{_libdir}/libhyprcursor.so.*

%files devel
%{_includedir}/hyprcursor.hpp
%{_includedir}/hyprcursor/
%{_libdir}/libhyprcursor.so
%{_libdir}/pkgconfig/hyprcursor.pc

%changelog
%autochangelog
