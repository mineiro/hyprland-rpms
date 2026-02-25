Name:           aquamarine
Version:        0.10.0
Release:        %autorelease
Summary:        Lightweight Linux rendering backend library for the Hypr ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/aquamarine
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  hyprwayland-scanner >= 0.4.0
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(hyprutils) >= 0.8.0
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput) >= 1.26.0
BuildRequires:  pkgconfig(libseat) >= 0.8.0
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)

%description
Aquamarine is a lightweight Linux rendering backend library used across the
Hyprland ecosystem.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build --target aquamarine

%install
%cmake_install

%check
# Test binaries are not built/run during bootstrap packaging.
:

%files
%license LICENSE
%doc README.md docs/
%{_libdir}/libaquamarine.so.*

%files devel
%{_includedir}/aquamarine/
%{_libdir}/libaquamarine.so
%{_libdir}/pkgconfig/aquamarine.pc

%changelog
%autochangelog
