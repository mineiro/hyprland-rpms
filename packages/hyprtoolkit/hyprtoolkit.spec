# Starter spec based on the solopasha/hyprlandRPM package, adapted to this
# monorepo style. The reference spec is older; validate dependency set and file
# lists carefully for current upstream releases before COPR publish.
#
# Current stack note: hyprtoolkit's in-memory image path requires the newer
# Hyprgraphics image constructor shipped in the validated `hyprgraphics 0.5.x`
# stack, so keep the dependency floor high enough to avoid mixed builds.

Name:           hyprtoolkit
Version:        0.5.4
Release:        %autorelease
Summary:        Modern C++ Wayland-native GUI toolkit used by Hypr ecosystem apps

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprtoolkit
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  cmake(hyprwayland-scanner) >= 0.4.5
BuildRequires:  gcc-c++
BuildRequires:  mesa-libEGL-devel
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(aquamarine) >= 0.11.0
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.5.1
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.13.0
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
Requires:       pkgconfig(aquamarine) >= 0.11.0
Requires:       pkgconfig(cairo)
Requires:       pkgconfig(hyprgraphics) >= 0.5.1

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
