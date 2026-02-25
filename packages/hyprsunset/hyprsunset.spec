Name:           hyprsunset
Version:        0.3.3
Release:        %autorelease
Summary:        Blue-light filter application for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsunset
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.7.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.5
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
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

%postun
%systemd_user_postun %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
%autochangelog
