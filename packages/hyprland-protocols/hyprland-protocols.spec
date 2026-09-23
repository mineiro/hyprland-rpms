Name:           hyprland-protocols
Version:        0.7.1
Release:        %autorelease
Summary:        Wayland protocols used by Hyprland ecosystem components

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  ninja-build

%description
XML protocol definitions and pkg-config metadata for Hyprland-specific Wayland
protocol extensions.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%cmake -GNinja
%cmake_build

%install
%cmake_install

%check
# No upstream test suite.
:

%files
%license LICENSE
%doc README.md
%{_datadir}/hyprland-protocols
%{_datadir}/pkgconfig/hyprland-protocols.pc

%changelog
%autochangelog
