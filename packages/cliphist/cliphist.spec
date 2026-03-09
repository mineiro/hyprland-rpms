Name:           cliphist
Version:        0.7.0
Release:        %autorelease
Summary:        Wayland clipboard manager with support for multimedia

License:        BSD-3-Clause AND GPL-3.0-only AND MIT
URL:            https://github.com/sentriz/cliphist
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.gz

BuildRequires:  gcc
BuildRequires:  golang

Requires:       wl-clipboard
Requires:       xdg-utils

%description
cliphist is a Wayland clipboard history manager with support for both text and
images. It stores clipboard contents losslessly and exposes a small CLI for
listing, decoding, deleting, and wiping history entries.

%prep
%autosetup -p1 -n %{name}-%{version}
tar -xzf %{SOURCE1}

%build
export GOTOOLCHAIN=local
export GOFLAGS="${GOFLAGS:-} -mod=vendor"
go build \
    -buildmode=pie \
    -compiler gc \
    -buildvcs=false \
    -ldflags "-linkmode external -extldflags '%{__global_ldflags}'" \
    -o %{name} .

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%check
export GOTOOLCHAIN=local
export GOFLAGS="${GOFLAGS:-} -mod=vendor"
go test ./...

%files
%license LICENSE
%doc CHANGELOG.md readme.md version.txt
%{_bindir}/%{name}

%changelog
%autochangelog
