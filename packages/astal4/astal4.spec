%global astal_commit 6e49ec972f5d85437ce80e8b511d22b35a91b0df
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260421

Name:           astal4
Version:        4.0.0
Release:        %autorelease
Summary:        Astal GTK4 widget library

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)

Requires:       astal-io%{?_isa}

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       astal-io-devel%{?_isa}

%description
Astal GTK4 widget library for desktop shell and panel projects.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/astal/gtk4
%meson
%meson_build
popd

%install
pushd lib/astal/gtk4
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/Astal-4.0.gir
%{_libdir}/girepository-1.0/Astal-4.0.typelib
%{_libdir}/libastal-4.so.4{,.*}

%files devel
%{_includedir}/astal-4.h
%{_libdir}/libastal-4.so
%{_libdir}/pkgconfig/astal-4-4.0.pc
%{_datadir}/vala/vapi/astal-4-4.0.vapi

%changelog
%autochangelog
