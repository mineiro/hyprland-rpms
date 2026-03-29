Name:           hellwal
Version:        1.0.7
Release:        2%{?dist}
Summary:        Wallpaper-driven color palette generator with templated output

# Upstream is MIT; bundled stb_image.h is dual MIT/Public Domain and packaged
# here under its MIT alternative.
License:        MIT
URL:            https://github.com/danihek/hellwal
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Use packaged templates/themes when the default per-user directories are empty
# so the Fedora build works out of the box without manual copying.
Patch0:         patches/0001-use-packaged-system-data-dirs-as-default-fallbacks.patch
# Terminal recoloring should never block palette generation on a bad PTY.
Patch1:         patches/0002-terminal-color-writes-must-be-best-effort.patch

BuildRequires:  gcc
BuildRequires:  make

%description
Hellwal generates 16-color palettes from wallpapers or static theme files and
renders them into user templates. This package ships the upstream example
templates, preset themes, bash completion, and example integration script.

%prep
%autosetup -p1 -n %{name}-%{version}
awk 'BEGIN { flag = 0 } \
    /ALTERNATIVE A - MIT License/ { flag = 1 } \
    /ALTERNATIVE B - Public Domain/ { flag = 0 } \
    flag { print }' stb_image.h > LICENSE.stb_image

%build
%make_build \
    CC="%{__cc}" \
    CFLAGS="%{optflags}" \
    LDFLAGS="%{?__global_ldflags} -lm"

%install
install -Dpm0755 hellwal %{buildroot}%{_bindir}/hellwal
install -Dpm0644 assets/hellwal-completion.bash \
    %{buildroot}%{bash_completions_dir}/hellwal
install -d %{buildroot}%{_datadir}/hellwal/templates
cp -a templates/. %{buildroot}%{_datadir}/hellwal/templates/
install -d %{buildroot}%{_datadir}/hellwal/themes
cp -a themes/. %{buildroot}%{_datadir}/hellwal/themes/

%check
./hellwal --version | grep -qx '%{version}'
./hellwal --help | grep -Fq '%{_datadir}/hellwal/templates'
rm -rf test-output
mkdir -p test-output
./hellwal \
    --theme gruvbox.hellwal \
    --theme-folder themes \
    --template-folder templates \
    --output "$PWD/test-output/" \
    --quiet
test -f test-output/variables.sh
test -f test-output/hyprland-colors.conf

%files
%license LICENSE
%license LICENSE.stb_image
%doc README.md
%doc assets/script.sh
%{_bindir}/hellwal
%{bash_completions_dir}/hellwal
%dir %{_datadir}/hellwal
%dir %{_datadir}/hellwal/templates
%{_datadir}/hellwal/templates/*
%dir %{_datadir}/hellwal/themes
%{_datadir}/hellwal/themes/*

%changelog
%autochangelog
