# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. Re-verify dependency floors/patches against current Fedora and
# upstream before first COPR publish.
#
# Bundled sdbus-cpp policy (current): keep the bundled subproject tarball path
# for now because the validated upstream build flow expects subprojects/sdbus-cpp.
# Declare bundling explicitly and revisit unbundling once a reliable system
# sdbus-cpp build path is confirmed across the target Fedora/COPR matrix.

%global sdbus_version 2.1.0

Name:           hyprlock
Version:        0.9.2
Release:        %autorelease
Summary:        Hyprland's GPU-accelerated screen locking utility

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprlock
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/Kistler-Group/sdbus-cpp/archive/v%{sdbus_version}/sdbus-%{sdbus_version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.4.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(opengl)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

# Explicit bundled dependency declaration for Fedora packaging review and
# repackaging audits. Update/remove if this package is switched to system sdbus-cpp.
Provides:       bundled(sdbus-cpp) = %{sdbus_version}

%description
%{summary}.

%prep
%autosetup -p1
mkdir -p subprojects/sdbus-cpp
# Upstream expects the sdbus-cpp subproject tree at build time for this release.
tar -xf %{SOURCE1} -C subprojects/sdbus-cpp --strip=1

%build
pushd subprojects/sdbus-cpp
%cmake \
  -DCMAKE_INSTALL_PREFIX=%{_builddir}/sdbus \
  -DCMAKE_BUILD_TYPE=Release \
  -DSDBUSCPP_BUILD_DOCS=OFF \
  -DBUILD_SHARED_LIBS=OFF
%cmake_build
cmake --install %{_vpath_builddir}
popd

export PKG_CONFIG_PATH=%{_builddir}/sdbus/%{_lib}/pkgconfig

%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
# Keep the upstream example config in docs only; do not install the generated
# default config under /usr/share/hypr for the RPM payload.
rm -f %{buildroot}%{_datadir}/hypr/%{name}.conf

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%files
%license LICENSE
%doc README.md assets/example.conf
%{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/pam.d/%{name}

%changelog
%autochangelog
