%global ags_jsdir %{_datadir}/ags/js
%global gnimdir %{ags_jsdir}/node_modules/%{name}

Name:           gnim
Version:        1.9.1
Release:        %autorelease
Summary:        JSX and reactivity library for GNOME JavaScript

License:        MIT
URL:            https://github.com/Aylur/gnim
Source0:        https://registry.npmjs.org/%{name}/-/%{name}-%{version}.tgz#/%{name}-%{version}-npm.tgz
BuildArch:      noarch

# AGS 3.1.x currently expects this npm-style runtime path:
#   /usr/share/ags/js/node_modules/gnim/dist

%description
Gnim is a JSX and reactivity library for GNOME JavaScript.

This package installs the published runtime payload in the location AGS expects
today, so AGS can consume a packaged copy instead of a vendored tree.

%prep
%setup -q -c -T -n %{name}-%{version}
tar -xzf %{SOURCE0} --strip-components=1

%build
:

%install
mkdir -p %{buildroot}%{gnimdir}
cp -a %{_builddir}/%{name}-%{version}/dist %{_builddir}/%{name}-%{version}/package.json %{buildroot}%{gnimdir}/

%check
:

%files
%license LICENSE
%doc README.md
%dir %{_datadir}/ags
%dir %{ags_jsdir}
%dir %{ags_jsdir}/node_modules
%{gnimdir}

%changelog
%autochangelog
