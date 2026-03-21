%global upstream_name ags

Name:           aylurs-gtk-shell
Version:        3.1.1
Release:        %autorelease
Summary:        Scaffolding CLI for Astal and Gnim projects

# Verify upstream licensing before shipping:
# - package.json says LGPL-2.1
# - LICENSE in the tarball is GPLv3
License:        GPL-3.0-or-later
URL:            https://github.com/Aylur/%{upstream_name}
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{upstream_name}-%{version}.tar.gz
Source1:        %{name}-%{version}-cli-vendor.tar.xz
Patch0:         patches/0001-meson-stop-installing-vendored-gnim.patch
Patch1:         patches/0002-types-skip-empty-extra-gir-dirs.patch
Patch2:         patches/0003-types-prefer-fedora-npx.patch
Patch3:         patches/0004-types-limit-default-modules.patch
Patch4:         patches/0005-use-layer-shell-soname-for-preload.patch

# Upstream issues to resolve before the first successful build:
# - Source0 v3.1.1 still reports version 3.1.0 in package.json
# - upstream meson.build assumes vendored gnim; Fedora carries Patch0

BuildRequires:  gcc
BuildRequires:  gjs
BuildRequires:  go-rpm-macros
BuildRequires:  golang >= 1.24
BuildRequires:  meson
BuildRequires:  pkgconfig(gtk4-layer-shell-0)

Requires:       bash
Requires:       /usr/bin/sass
Requires:       gjs
Requires:       astal3
Requires:       astal4
Requires:       gnim >= 1.9.0
Requires:       nodejs-npm
Conflicts:      ags

%description
AGS is a scaffolding CLI for Astal and Gnim projects.

%prep
%autosetup -p1 -n %{upstream_name}-%{version}
tar -xJf %{SOURCE1} -C cli

%build
export GOFLAGS='-mod=vendor'
%meson
%meson_build

%install
%meson_install

%check
:

%files
%license LICENSE
%{_bindir}/ags
%{_datadir}/ags

%changelog
%autochangelog
