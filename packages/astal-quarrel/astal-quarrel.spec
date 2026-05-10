%global astal_commit 67ddc83e0bdbda6de7f6f15e4fbc5d6b9d2d1b18
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global snapshot_date 20260430

Name:           astal-quarrel
Version:        0.1.0
Release:        %autorelease
Summary:        Quarrel helper library from the Astal project

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
Quarrel is a command-line option helper library from the Astal project.

%description devel
Development files for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
pushd lib/quarrel
%meson
%meson_build
popd

%install
pushd lib/quarrel
%meson_install
popd

%check
:

%files
%license LICENSE
%{_datadir}/gir-1.0/Quarrel-0.1.gir
%{_libdir}/girepository-1.0/Quarrel-0.1.typelib
%{_libdir}/libquarrel.so.0{,.*}

%files devel
%{_includedir}/quarrel.h
%{_libdir}/libquarrel.so
%{_libdir}/pkgconfig/quarrel-0.1.pc
%{_datadir}/vala/vapi/quarrel-0.1.vapi

%changelog
%autochangelog
