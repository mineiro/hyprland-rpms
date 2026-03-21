%global astal_commit 41b50290c6a1cdce7b482897c22fe49286912b9a
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260319

Name:           astal-greet
Version:        0.1.0
Release:        %autorelease
Summary:        Greetd client library and CLI bindings for Astal

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{astal_commit}/astal-%{astal_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(json-glib-1.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Greetd client library and CLI bindings for Astal-based applications.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/greet
%meson
%meson_build
popd

%install
pushd lib/greet
%meson_install
popd

%check
:

%files
%license LICENSE
%{_bindir}/astal-greet
%{_datadir}/gir-1.0/AstalGreet-0.1.gir
%{_libdir}/girepository-1.0/AstalGreet-0.1.typelib
%{_libdir}/libastal-greet.so.0{,.*}

%files devel
%{_includedir}/astal-greet.h
%{_libdir}/libastal-greet.so
%{_libdir}/pkgconfig/astal-greet-0.1.pc
%{_datadir}/vala/vapi/astal-greet-0.1.vapi

%changelog
%autochangelog
