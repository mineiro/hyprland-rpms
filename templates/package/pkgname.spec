# Starter spec template.
# Fill in all TODOs before building.

Name:           pkgname
Version:        0.0.0
Release:        %autorelease
Summary:        TODO

License:        TODO
URL:            https://example.invalid
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make

%description
TODO.

%prep
%autosetup -p1

%build
%configure
make %{?_smp_mflags}

%install
%make_install

%files
# TODO: list packaged files

%changelog
%autochangelog

