# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. Re-verify dependency floors/patches against current Fedora and
# upstream before first COPR publish.
#
# Version pin note (current stack): `0.8.x` moved to a `hyprtoolkit`-based
# dependency path that expects newer Hyprgraphics APIs than the current Hyprland
# `0.53.x` validation stack in this repo. Keep `hyprpaper` on the latest known
# compatible line for now and revisit when the core stack is upgraded.

Name:           hyprpaper
Version:        0.7.6
Release:        %autorelease
Summary:        Blazing fast Wayland wallpaper utility with IPC controls

# LICENSE: BSD-3-Clause
# protocols/wlr-layer-shell-unstable-v1.xml: HPND-sell-variant
License:        BSD-3-Clause AND HPND-sell-variant
URL:            https://github.com/hyprwm/hyprpaper
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.4.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
Hyprpaper is a blazing fast wallpaper utility for Hyprland with the ability
to dynamically change wallpapers through sockets. It also works on other
wlroots-based compositors.

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
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
%autochangelog
