Name:           hyprpicker
Version:        0.4.6
Release:        %autorelease
Summary:        wlroots-compatible Wayland color picker

# LICENSE: BSD-3-Clause
# protocols/wlr-layer-shell-unstable-v1.xml: HPND-sell-variant
License:        BSD-3-Clause AND HPND-sell-variant
URL:            https://github.com/hyprwm/hyprpicker
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# GCC 15 / newer Fedora toolchains expose a missing direct include upstream.
Patch0:         patches/0001-include-mutex-for-gcc-15-build.patch

ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

Recommends:     wl-clipboard

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_MANDIR=%{_mandir}
%cmake_build

%install
%cmake_install

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.*

%changelog
%autochangelog
