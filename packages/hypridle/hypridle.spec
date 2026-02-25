# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. Re-verify dependency floors/patches against current Fedora and
# upstream before first COPR publish.
#
# Bundled sdbus-cpp policy (current): keep the bundled source tarball path for
# now because the validated upstream build flow for this release builds sdbus-cpp
# locally before compiling hypridle. Declare bundling explicitly and revisit
# unbundling once a reliable system sdbus-cpp build path is confirmed across the
# target Fedora/COPR matrix.

%global sdbus_version 2.1.0

Name:           hypridle
Version:        0.1.7
Release:        %autorelease
Summary:        Hyprland's idle daemon

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hypridle
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/Kistler-Group/sdbus-cpp/archive/v%{sdbus_version}/sdbus-%{sdbus_version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  cmake(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.7.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

# Explicit bundled dependency declaration for Fedora packaging review and
# repackaging audits. Update/remove if this package is switched to system sdbus-cpp.
Provides:       bundled(sdbus-cpp) = %{sdbus_version}

%description
%{summary}.

%prep
%autosetup -p1 -a1

%build
pushd sdbus-cpp-%{sdbus_version}
%cmake \
  -DCMAKE_INSTALL_PREFIX=%{_builddir}/sdbus \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=OFF
%cmake_build
cmake --install %{__cmake_builddir}
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

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun %{name}.service

%files
%license LICENSE
%doc README.md assets/example.conf
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
%autochangelog
