%global astal_commit 6e49ec972f5d85437ce80e8b511d22b35a91b0df
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260421

Name:           astal-wireplumber
Version:        0.1.0
Release:        %autorelease
Summary:        WirePlumber library for Astal

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  vala
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(wireplumber-0.5)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
WirePlumber integration library for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/wireplumber
%meson
%meson_build
popd

%install
pushd lib/wireplumber
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/AstalWp-0.1.gir
%{_libdir}/girepository-1.0/AstalWp-0.1.typelib
%{_libdir}/libastal-wireplumber.so.0{,.*}

%files devel
%{_includedir}/astal-wp.h
%{_includedir}/astal/wireplumber/
%{_libdir}/libastal-wireplumber.so
%{_libdir}/pkgconfig/astal-wireplumber-0.1.pc
%{_datadir}/vala/vapi/astal-wireplumber-0.1.vapi
%{_datadir}/vala/vapi/astal-wireplumber-0.1.deps

%changelog
%autochangelog
