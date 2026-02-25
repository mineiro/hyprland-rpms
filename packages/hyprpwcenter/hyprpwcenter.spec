Name:           hyprpwcenter
Version:        0.1.2
Release:        %autorelease
Summary:        GUI PipeWire control center for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpwcenter
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.5.3
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(pixman-1)

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake \
  -GNinja \
  -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/hyprpwcenter.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprpwcenter
%{_datadir}/applications/hyprpwcenter.desktop

%changelog
%autochangelog
