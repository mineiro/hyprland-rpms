%global astal_commit 6e49ec972f5d85437ce80e8b511d22b35a91b0df
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260421

Name:           astal-io
Version:        0.1.0
Release:        %autorelease
Summary:        Astal core library and CLI

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

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Astal core library and CLI used by higher-level Astal libraries and AGS.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/astal/io
%meson
%meson_build
popd

%install
pushd lib/astal/io
%meson_install
popd

%check
:

%files
%license LICENSE
%{_bindir}/astal
%{_datadir}/gir-1.0/AstalIO-0.1.gir
%{_libdir}/girepository-1.0/AstalIO-0.1.typelib
%{_libdir}/libastal-io.so.0{,.*}

%files devel
%{_includedir}/astal-io.h
%{_libdir}/libastal-io.so
%{_libdir}/pkgconfig/astal-io-0.1.pc
%{_datadir}/vala/vapi/astal-io-0.1.vapi

%changelog
%autochangelog
