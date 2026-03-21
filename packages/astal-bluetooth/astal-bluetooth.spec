%global astal_commit 41b50290c6a1cdce7b482897c22fe49286912b9a
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260319

Name:           astal-bluetooth
Version:        0.1.0
Release:        %autorelease
Summary:        Bluetooth library for Astal

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Bluetooth integration library for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/bluetooth
%meson
%meson_build
popd

%install
pushd lib/bluetooth
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/AstalBluetooth-0.1.gir
%{_libdir}/girepository-1.0/AstalBluetooth-0.1.typelib
%{_libdir}/libastal-bluetooth.so.0{,.*}

%files devel
%{_includedir}/astal-bluetooth.h
%{_libdir}/libastal-bluetooth.so
%{_libdir}/pkgconfig/astal-bluetooth-0.1.pc
%{_datadir}/vala/vapi/astal-bluetooth-0.1.vapi

%changelog
%autochangelog
