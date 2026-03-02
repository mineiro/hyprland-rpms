Name:           hyprls
Version:        0.13.0
Release:        %autorelease
Summary:        Language server for Hyprland configuration files

License:        MIT
URL:            https://github.com/hyprland-community/hyprls
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.gz

BuildRequires:  gcc
BuildRequires:  golang

%description
hyprls is a language server implementation for Hyprland configuration files.
It provides completion, hover documentation, symbol extraction, and related IDE
features over the Language Server Protocol.

%prep
%autosetup -p1
# Fedora 43 currently provides Go 1.25.x; upstream's code builds fine with 1.25.
sed -i 's/^go 1\.26\.0$/go 1.25.0/' go.mod
tar -xzf %{SOURCE1}

%build
export GOTOOLCHAIN=local
export GOFLAGS="${GOFLAGS:-} -mod=vendor"
go build \
    -buildmode=pie \
    -compiler gc \
    -buildvcs=false \
    -ldflags "-linkmode external -extldflags '%{__global_ldflags}' -X github.com/hyprland-community/hyprls.Version=%{version}" \
    -o %{name} ./cmd/hyprls

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%check
# Upstream has no stable, non-networked test target suitable for RPM builds.
:

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
%autochangelog
