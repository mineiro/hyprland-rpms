# Official plugin bundle for Hyprland. Plugin binaries are ABI-coupled to the
# exact Hyprland release family they are built against.
#
# This repo currently ships Hyprland 0.53.3, while upstream plugin tags are
# published on 0.53.0 / 0.52.0 / ... boundaries. We pin the latest compatible
# plugin tag (`v0.53.0`) and lock runtime Requires to Hyprland 0.53.3.

%global hyprland_target_version 0.53.3
%global __provides_exclude_from ^(%{_libdir}/hyprland/.*\\.so)$

%global plugins %{shrink:
  borders-plus-plus
  csgo-vulkan-fix
  hyprbars
  hyprexpo
  hyprfocus
  hyprscrolling
  hyprtrails
  hyprwinwrap
  xtra-dispatchers
}

Name:           hyprland-plugins
Version:        0.53.0
Release:        %autorelease
Summary:        Official plugins for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-plugins
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprland) = %{hyprland_target_version}
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       hyprland%{?_isa} = %{hyprland_target_version}
# Print Recommends for each split plugin package.
%{lua:for w in rpm.expand('%plugins'):gmatch('%S+') do print('Recommends: hyprland-plugin-'..w..'\n') end}

%description
Official Hyprland plugins packaged as split subpackages. Plugin binaries are
version-locked to the current Hyprland packaging target to avoid ABI/runtime
mismatches.

%define _plugin_pkg() \%package -n hyprland-plugin-%1\
Summary:        %1 plugin for Hyprland\
Requires:       hyprland%{?_isa} = %{hyprland_target_version}\
\%description -n hyprland-plugin-%1\
\%1 plugin for Hyprland.\
\%files -n hyprland-plugin-%1\
\%%license LICENSE\
\%%doc README.md\
\%%dir %{_libdir}/hyprland\
\%{_libdir}/hyprland/lib%1.so\
%{nil}

# Expand split subpackages for each plugin.
%{lua:for w in rpm.expand('%plugins'):gmatch('%S+') do print(rpm.expand('%_plugin_pkg '..w)..'\n') end}

%prep
%autosetup -n %{name}-%{version} -p1

%build
for plugin in %{plugins}; do
  pushd "$plugin"
  %meson --libdir=%{_libdir}/hyprland
  %meson_build
  popd
done

%install
for plugin in %{plugins}; do
  pushd "$plugin"
  %meson_install
  popd
done

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%files

%changelog
%autochangelog
