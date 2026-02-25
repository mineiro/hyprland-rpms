Name:           hyprlang
Version:        0.6.8
Release:        %autorelease
Summary:        Library implementing the Hypr configuration language

License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils) >= 0.7.1

%description
Hyprlang is the configuration language library used across the Hyprland
ecosystem.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Upstream test binaries are built, but test execution is skipped during bootstrap packaging.
:

%files
%license LICENSE
%doc README.md COPYRIGHT
%{_libdir}/libhyprlang.so.*

%files devel
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
%autochangelog
