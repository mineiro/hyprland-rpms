Name:           hyprsysteminfo
Version:        0.1.3
Release:        %autorelease
Summary:        Application to display information about the running system

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsysteminfo
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:         patches/0001-fix-qt-private-module-detection.patch

ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  qt6-rpm-macros
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickControls2)
BuildRequires:  cmake(Qt6WaylandClient)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0

Requires:       /usr/bin/free
Requires:       /usr/bin/lscpu
Requires:       /usr/bin/lspci
Requires:       hyprland-qt-support%{?_isa}

%description
A small Qt6/QML application to display system information and diagnostics
without using the terminal.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop

%changelog
%autochangelog
