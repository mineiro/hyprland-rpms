Name:           swayosd
Version:        0.3.1
Release:        %autorelease
Summary:        On-screen display service for volume, brightness, lock keys, and media keys

License:        GPL-3.0-only AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 OR BSL-1.0) AND BSD-2-Clause AND BSD-3-Clause AND ISC AND LGPL-2.1-or-later AND Unicode-3.0 AND Zlib
URL:            https://github.com/ErikReider/SwayOSD
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  gcc
BuildRequires:  meson >= 0.62.0
BuildRequires:  rust
BuildRequires:  sassc
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  pkgconfig(libevdev)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(systemd)

Requires:       dbus
Recommends:     brightnessctl
%{?systemd_requires}

%global _description %{expand:
SwayOSD provides on-screen display notifications for common desktop actions on
Wayland compositors, including volume, brightness, lock-key states, and media
key feedback.}

%description
%{_description}

%prep
%autosetup -p1 -n SwayOSD-%{version}
tar -xJf %{SOURCE1}
%cargo_prep -v vendor

%build
%meson
%meson_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
%meson_install

%check
# No stable non-interactive upstream test target suitable for mock.
:

%post
%systemd_post swayosd-libinput-backend.service

%preun
%systemd_preun swayosd-libinput-backend.service

%postun
%systemd_postun_with_restart swayosd-libinput-backend.service

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc README.md
%{_bindir}/swayosd-client
%{_bindir}/swayosd-server
%{_bindir}/swayosd-libinput-backend
%config(noreplace) %{_sysconfdir}/xdg/swayosd/backend.toml
%config(noreplace) %{_sysconfdir}/xdg/swayosd/config.toml
%config(noreplace) %{_sysconfdir}/xdg/swayosd/style.css
%{_unitdir}/swayosd-libinput-backend.service
%{_libdir}/udev/rules.d/99-swayosd.rules
%{_datadir}/dbus-1/system-services/org.erikreider.swayosd.service
%{_datadir}/dbus-1/system.d/org.erikreider.swayosd.conf
%{_datadir}/polkit-1/actions/org.erikreider.swayosd.policy
%{_datadir}/polkit-1/rules.d/org.erikreider.swayosd.rules

%changelog
%autochangelog
