%global upstream_commit e200b726577240a7a5e0a83428d69291c110676a
%global upstream_shortcommit %(c=%{upstream_commit}; echo ${c:0:7})

Name:           appmenu-glib-translator
Version:        25.04
Release:        %autorelease
Summary:        Translator from DBusMenu to GMenuModel

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu
Source0:        %{url}/archive/%{upstream_commit}/vala-panel-appmenu-%{upstream_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  vala
BuildRequires:  gobject-introspection-devel
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Library that translates DBusMenu data into GLib menu models.

%description devel
Development files for %{name}.

%prep
%autosetup -n vala-panel-appmenu-%{upstream_commit} -p1

%build
pushd subprojects/appmenu-glib-translator
%meson
%meson_build
popd

%install
pushd subprojects/appmenu-glib-translator
%meson_install
popd

%check
:

%files
%license LICENSE
%{_libdir}/girepository-1.0/AppmenuGLibTranslator-24.02.typelib
%{_libdir}/libappmenu-glib-translator.so.*

%files devel
%{_datadir}/gir-1.0/AppmenuGLibTranslator-24.02.gir
%{_datadir}/vala/vapi/appmenu-glib-translator.vapi
%{_datadir}/vala/vapi/appmenu-glib-translator.deps
%{_includedir}/appmenu-glib-translator/
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
%autochangelog
