# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. Re-verify dependency floors/patches against current Fedora and
# upstream before first COPR publish.
#
# Track the latest upstream release when possible. `0.8.x` depends on
# `hyprtoolkit`, so keep `hyprtoolkit` packaged and version floors aligned with
# the validated Hypr stack to avoid mixed-ABI builddep resolution in COPR.

Name:           hyprpaper
Version:        0.8.3
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
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.5.3
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwire) >= 0.3.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
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
