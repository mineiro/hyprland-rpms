Name:           hyprshutdown
Version:        0.1.0
Release:        %autorelease
Summary:        Graceful shutdown/logout utility for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprshutdown
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  cmake(glaze) >= 6.1.0
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.5.3
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)

%description
hyprshutdown is a graceful shutdown/logout utility for Hyprland that closes
applications cleanly before exiting the compositor.

%prep
%autosetup -p1

%build
%cmake \
  -GNinja \
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
%{_bindir}/%{name}

%changelog
%autochangelog

