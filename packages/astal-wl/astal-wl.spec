%global astal_commit 6e49ec972f5d85437ce80e8b511d22b35a91b0df
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260421

Name:           astal-wl
Version:        0.1.0
Release:        %autorelease
Summary:        Generic Wayland helper library for Astal

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  wl-vapi-gen
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Generic Wayland helper library for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/wl
%meson
%meson_build
popd

%install
pushd lib/wl
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/AstalWl-0.1.gir
%{_libdir}/girepository-1.0/AstalWl-0.1.typelib
%{_libdir}/libastal-wl.so.0{,.*}

%files devel
%{_includedir}/astal-wl.h
%{_libdir}/libastal-wl.so
%{_libdir}/pkgconfig/astal-wl-0.1.pc
%{_datadir}/vala/vapi/astal-wl-0.1.vapi

%changelog
%autochangelog
