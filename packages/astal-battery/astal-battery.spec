%global astal_commit f58cae8f268dedffb6d1448b5b32f39b71953958
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260519

Name:           astal-battery
Version:        0.1.0
Release:        %autorelease -b 2
Summary:        Battery library and CLI bindings for Astal

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
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(json-glib-1.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Battery library and CLI bindings for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/battery
%meson
%meson_build
popd

%install
pushd lib/battery
%meson_install
popd

%check
:

%files
%license LICENSE
%{_bindir}/astal-battery
%{_datadir}/gir-1.0/AstalBattery-0.1.gir
%{_libdir}/girepository-1.0/AstalBattery-0.1.typelib
%{_libdir}/libastal-battery.so.0{,.*}

%files devel
%{_includedir}/astal-battery.h
%{_libdir}/libastal-battery.so
%{_libdir}/pkgconfig/astal-battery-0.1.pc
%{_datadir}/vala/vapi/astal-battery-0.1.vapi

%changelog
%autochangelog
