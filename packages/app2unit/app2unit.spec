Name:           app2unit
Version:        1.4.1
Release:        %autorelease
Summary:        Launch desktop entries and commands as user services or scopes

License:        GPL-3.0-only
URL:            https://github.com/Vladimir-csp/app2unit
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  gzip
BuildRequires:  make
BuildRequires:  scdoc

Requires:       systemd
Requires:       xdg-utils
Recommends:     libnotify
Recommends:     xdg-terminal-exec >= 0.13.0

%description
app2unit launches desktop entries, files, URLs, or arbitrary commands as user
services or scopes. It also ships helper aliases for opener and terminal launch
modes.

%prep
%autosetup -n %{name}-%{version}

%build
%make_build

%install
%make_install prefix=%{_prefix}

%check
sh -n app2unit

%files
%license LICENSE
%doc README.md
%{_bindir}/app2unit
%{_bindir}/app2unit-open
%{_bindir}/app2unit-open-scope
%{_bindir}/app2unit-open-service
%{_bindir}/app2unit-term
%{_bindir}/app2unit-term-scope
%{_bindir}/app2unit-term-service
%{_mandir}/man1/app2unit.1.*

%changelog
%autochangelog
