# Starter spec for stable Hyprland packaging in this monorepo.
# Use Fedora dist-git/SRPM as the primary baseline and compare with solopasha's
# hyprland-git spec for newer dependency floors and patches.
#
# This file is intentionally a clean starting point, not a drop-in final spec.

Name:           hyprland
Version:        0.54.0
Release:        %autorelease
Summary:        Dynamic tiling Wayland compositor

# TODO: Re-verify all bundled component licenses for the target version.
License:        BSD-3-Clause AND BSD-2-Clause AND HPND-sell-variant AND LGPL-2.1-or-later
URL:            https://github.com/hyprwm/Hyprland
Source0:        %{url}/releases/download/v%{version}/source-v%{version}.tar.gz

BuildRequires:  cmake
# Encode the validated Hypr stack floors so COPR/builddep does not mix older
# Fedora packages with newer COPR packages (for example hyprutils ABI drift).
BuildRequires:  cmake(glaze) >= 7.0.0
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(aquamarine) >= 0.10.0
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(hyprcursor) >= 0.1.13
BuildRequires:  pkgconfig(hyprgraphics) >= 0.4.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwire) >= 0.3.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libliftoff)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(muparser)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(re2)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(uuid)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-errors)
BuildRequires:  pkgconfig(xcb-ewmh)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-renderutil)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-shm)
BuildRequires:  pkgconfig(xcb-util)
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-xinput)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xwayland)

Requires:       xorg-x11-server-Xwayland%{?_isa}
Recommends:     kitty
Recommends:     wofi
Recommends:     playerctl
Recommends:     brightnessctl
Recommends:     mesa-dri-drivers
Recommends:     polkit

%description
Hyprland is a dynamic tiling Wayland compositor that focuses on both
performance and visuals.

%package        uwsm
Summary:        Session files for a uwsm-managed Hyprland session
Requires:       uwsm

%description    uwsm
Session files for a uwsm-managed Hyprland session.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and protocol files for %{name}.

%prep
%autosetup -n hyprland-source -N
# TODO: Verify source directory name from the release tarball and adjust %%autosetup.
# TODO: If upstream bundles modified subprojects (for example udis86), document/declare bundling.

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
# Add upstream tests when they can run reliably in mock/COPR.
:

%post
# TODO: Add scriptlets only if the final package installs systemd units or caches.

%files
%license LICENSE
%doc README.md
%{_bindir}/Hyprland
%{_bindir}/hyprland
%{_bindir}/hyprctl
%{_bindir}/hyprpm
%{_bindir}/start-hyprland
%{_datadir}/bash-completion/completions/hyprctl
%{_datadir}/bash-completion/completions/hyprpm
%{_datadir}/fish/vendor_completions.d/hyprctl.fish
%{_datadir}/fish/vendor_completions.d/hyprpm.fish
%{_datadir}/zsh/site-functions/_hyprctl
%{_datadir}/zsh/site-functions/_hyprpm
%{_datadir}/wayland-sessions/hyprland.desktop
%{_datadir}/hypr/
%{_datadir}/xdg-desktop-portal/hyprland-portals.conf
%{_mandir}/man1/*.1*

%files uwsm
%{_datadir}/wayland-sessions/hyprland-uwsm.desktop

%files devel
%{_includedir}/hyprland/
%{_datadir}/pkgconfig/hyprland.pc

%changelog
%autochangelog
