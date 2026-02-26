# Adapted from the historical Fedora/AUR swww packaging model, updated for the
# Codeberg "awww" rename and this monorepo's Rust vendoring workflow.
%bcond_with check
%global commit 2c86d41d07471f518e24f5cd1f586e4d2a32d12c
%global shortcommit 2c86d41d
%global commitdate 20260212
# Prevent brp-mangle-shebangs from treating Rust inner attributes ("#![...]")
# in vendored debugsource files as invalid script shebangs.
%global __brp_mangle_shebangs_exclude_from ^/usr/src/debug/.*/vendor/.*\\.rs$

Name:           awww
Version:        0.11.2^git%{commitdate}
Release:        %autorelease
Summary:        Efficient animated wallpaper daemon for Wayland, controlled at runtime

# Baseline license set derived from the prior swww package. Re-verify if upstream
# dependency graph changes materially across major releases.
License:        GPL-3.0-only AND (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND BSD-2-Clause AND BSD-3-Clause AND MIT AND (MIT OR Apache-2.0) AND (MIT OR Apache-2.0 OR NCSA) AND (CC0-1.0 OR Apache-2.0) AND (MIT OR Apache-2.0 OR Zlib) AND (Unlicense OR MIT) AND Zlib
URL:            https://codeberg.org/LGFae/awww
# Upstream has renamed the project to "awww" on main, but the latest tagged
# release (v0.11.2) still builds the legacy swww binaries. Package a pinned
# snapshot until the first post-rename awww release is tagged.
Source0:        %{url}/archive/main.tar.gz#/%{name}-%{shortcommit}.tar.gz
Source1:        %{name}-%{shortcommit}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  pkgconfig(dav1d)
BuildRequires:  pkgconfig(liblz4)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  scdoc

%global _description %{expand:
awww is an efficient animated wallpaper daemon and CLI for wlroots/layer-shell
Wayland compositors, controlled at runtime.}

%description %{_description}

This package is currently built from a pinned upstream snapshot because the
rename to `awww` has not yet landed in a tagged release (latest tag `v0.11.2`
still builds the legacy `swww` binaries).

%prep
%autosetup -p1 -n awww
tar -xJf %{SOURCE1}
%cargo_prep -v vendor

%build
%cargo_build -f all-formats
./doc/gen.sh
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
install -Dpm0755 target/release/awww %{buildroot}%{_bindir}/awww
install -Dpm0755 target/release/awww-daemon %{buildroot}%{_bindir}/awww-daemon
install -Dpm0644 completions/_awww %{buildroot}%{zsh_completions_dir}/_awww
install -Dpm0644 completions/awww.bash %{buildroot}%{bash_completions_dir}/awww
install -Dpm0644 completions/awww.fish %{buildroot}%{fish_completions_dir}/awww.fish
install -Dpm0644 ./doc/generated/*.1 -t %{buildroot}%{_mandir}/man1

%if %{with check}
%check
%cargo_test
%endif

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc CHANGELOG.md
%doc README.md
%{_bindir}/awww
%{_bindir}/awww-daemon
%{_mandir}/man1/awww*.1.*
%{bash_completions_dir}/awww
%{fish_completions_dir}/awww.fish
%{zsh_completions_dir}/_awww

%changelog
%autochangelog
