%global astal_commit 67ddc83e0bdbda6de7f6f15e4fbc5d6b9d2d1b18
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260430

Name:           astal-mpris
Version:        0.1.0
Release:        %autorelease
Summary:        MPRIS library and CLI bindings for Astal

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
BuildRequires:  pkgconfig(json-glib-1.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
MPRIS library and CLI bindings for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/mpris
%meson
%meson_build
popd

%install
pushd lib/mpris
%meson_install
popd

%check
:

%files
%license LICENSE
%{_bindir}/astal-mpris
%{_datadir}/gir-1.0/AstalMpris-0.1.gir
%{_libdir}/girepository-1.0/AstalMpris-0.1.typelib
%{_libdir}/libastal-mpris.so.0{,.*}

%files devel
%{_includedir}/astal-mpris.h
%{_libdir}/libastal-mpris.so
%{_libdir}/pkgconfig/astal-mpris-0.1.pc
%{_datadir}/vala/vapi/astal-mpris-0.1.vapi

%changelog
%autochangelog
