%global astal_commit 6e49ec972f5d85437ce80e8b511d22b35a91b0df
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260421

Name:           astal3
Version:        3.0.0
Release:        %autorelease
Summary:        Astal GTK3 widget library

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  gobject-introspection-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(gtk-layer-shell-0)
BuildRequires:  pkgconfig(wayland-client)

Requires:       astal-io%{?_isa}

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       astal-io-devel%{?_isa}

%description
Astal GTK3 widget library for desktop shell and panel projects.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/astal/gtk3
%meson
%meson_build
popd

%install
pushd lib/astal/gtk3
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/Astal-3.0.gir
%{_libdir}/girepository-1.0/Astal-3.0.typelib
%{_libdir}/libastal.so.3{,.*}

%files devel
%{_includedir}/astal.h
%{_libdir}/libastal.so
%{_libdir}/pkgconfig/astal-3.0.pc
%{_datadir}/vala/vapi/astal-3.0.vapi

%changelog
%autochangelog
