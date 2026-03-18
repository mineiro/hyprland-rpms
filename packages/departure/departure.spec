%bcond_with check
%global crate departure

Name:           departure
Version:        0.1.0
Release:        %autorelease
Summary:        Flexible logout application for Wayland with Material You theming

# LICENSE.dependencies contains a full license breakdown generated at build time.
License:        MIT AND (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND CC0-1.0 AND ISC AND MPL-2.0 AND (MIT OR Zlib OR Apache-2.0) AND (Unlicense OR MIT) AND Unicode-3.0
URL:            https://github.com/mpalatsi/departure
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)

%global _description %{expand:
Departure is a GTK4-based logout application for Wayland compositors with
configurable actions and theme integration for workflows such as pywal and
matugen.}

%description
%{_description}

%prep
%autosetup -p1
tar -xJf %{SOURCE1}
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

%if %{with check}
%check
%cargo_test
%endif

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc README.md
%{_bindir}/%{name}

%changelog
%autochangelog
