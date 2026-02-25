# Starter spec based on the solopasha/hyprlandRPM package, kept intentionally minimal.
# Verify Epoch/Version/BuildRequires against current upstream and Fedora before release.
#
# Bundled sdbus-cpp policy (current): keep the bundled subproject tarball path for
# now because the validated Fedora/COPR build path for this upstream release uses
# upstream's subprojects/sdbus-cpp layout. Declare bundling explicitly and revisit
# unbundling once a reliable system sdbus-cpp build path is confirmed across the
# target Fedora/COPR matrix.

%global sdbus_version 2.1.0

Name:           xdg-desktop-portal-hyprland
Epoch:          1
Version:        1.3.11
Release:        %autorelease
Summary:        xdg-desktop-portal backend for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/xdg-desktop-portal-hyprland
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/Kistler-Group/sdbus-cpp/archive/v%{sdbus_version}/sdbus-%{sdbus_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.7.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(Qt6Widgets)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)

Requires:       dbus
Requires:       xdg-desktop-portal
Requires:       grim
Requires:       slurp
Requires:       qt6-qtwayland
Recommends:     hyprpicker

Enhances:       hyprland
Supplements:    hyprland

# Explicit bundled dependency declaration for Fedora packaging review and
# repackaging audits. Update/remove if this package is switched to system sdbus-cpp.
Provides:       bundled(sdbus-cpp) = %{sdbus_version}

%description
%{summary}.

%prep
%autosetup -p1
# Upstream expects the sdbus-cpp subproject tree at build time for this release.
tar -xf %{SOURCE1} -C subprojects/sdbus-cpp --strip=1

%build
%cmake -DBUILD_SHARED_LIBS:BOOL=OFF -DCMAKE_BUILD_TYPE=Release
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

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprland-share-picker
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.hyprland.service
%{_datadir}/xdg-desktop-portal/portals/hyprland.portal
%{_libexecdir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
%autochangelog
