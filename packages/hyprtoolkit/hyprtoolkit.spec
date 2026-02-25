# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. The reference spec is older; validate dependency set and file
# lists carefully for current upstream releases before COPR publish.
#
# Current compatibility patch: latest hyprtoolkit (`0.5.3`) can call a newer
# Hyprgraphics in-memory image constructor that is not present in the current
# validated stack (`hyprgraphics 0.4.0`). Keep a small fallback patch until the
# core stack is upgraded and the patch can be dropped.

Name:           hyprtoolkit
Version:        0.5.3
Release:        %autorelease
Summary:        Modern C++ Wayland-native GUI toolkit used by Hypr ecosystem apps

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprtoolkit
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:         patches/0001-image-compat-fallback-for-older-hyprgraphics.patch

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  cmake(hyprwayland-scanner) >= 0.4.5
BuildRequires:  gcc-c++
BuildRequires:  mesa-libEGL-devel
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(aquamarine) >= 0.10.0
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.4.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(iniparser)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(aquamarine)
Requires:       pkgconfig(cairo)
Requires:       pkgconfig(hyprgraphics)

%description    devel
Development files for %{name}.

%prep
%autosetup -p1

%build
%cmake -GNinja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%files
%license LICENSE
%doc README.md
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
%autochangelog
