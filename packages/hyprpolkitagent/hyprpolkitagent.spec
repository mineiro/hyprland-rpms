Name:           hyprpolkitagent
Version:        0.2.0
Release:        %autorelease
Summary:        Simple polkit authentication agent for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpolkitagent
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(hyprutils) >= 0.14.2

BuildRequires:  pkgconfig(hyprtoolkit) >= 0.6.0
BuildRequires:  pkgconfig(hyprgraphics) >= 0.5.1
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(sdbus-c++) >= 2

Requires:       polkit

%description
A simple polkit authentication agent for Hyprland, written in C++ with Hyprtoolkit.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun %{name}.service

%files
%license LICENSE
%doc README.md
%{_datadir}/dbus-1/services/org.hyprland.%{name}.service
%{_libexecdir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
%autochangelog
