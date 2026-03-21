%global upstream_commit d0f7714eba4f8d263b99117c0921e7c810ef69a2
%global upstream_shortcommit %(c=%{upstream_commit}; echo ${c:0:7})

Name:           wl-vapi-gen
Version:        1.0.0
Release:        %autorelease
Summary:        Wayland protocol to Vala VAPI generator

License:        GPL-3.0-only
URL:            https://github.com/kotontrion/wl-vapi-gen
Source0:        %{url}/archive/%{upstream_commit}/%{name}-%{upstream_shortcommit}.tar.gz

BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  python3

Requires:       python3

%description
Helper tool that generates Vala VAPI files from Wayland protocol XML
descriptions.

%prep
%autosetup -n %{name}-%{upstream_commit} -p1

%build
%meson
%meson_build

%install
%meson_install

%check
:

%files
%license LICENSE
%{_bindir}/wl-vapi-gen
%{_datadir}/pkgconfig/wl-vapi-gen.pc

%changelog
%autochangelog
