Name:           caelestia-cli
Version:        1.0.8
Release:        %autorelease
Summary:        Command-line companion for the Caelestia shell and dotfiles

License:        GPL-3.0-only
URL:            https://github.com/caelestia-dots/cli
Source0:        %{url}/releases/download/v%{version}/caelestia-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-build
BuildRequires:  python3-hatch-vcs
BuildRequires:  python3-hatchling
BuildRequires:  python3-installer
BuildRequires:  python3-materialyoucolor
BuildRequires:  python3-pillow

Requires:       python3-materialyoucolor
Requires:       python3-pillow

Recommends:     app2unit
Recommends:     cliphist
Recommends:     fuzzel
Recommends:     git-core
Recommends:     gpu-screen-recorder
Recommends:     grim
Recommends:     libnotify
Recommends:     slurp
Recommends:     swappy
Recommends:     wl-clipboard

%description
Caelestia CLI provides the `caelestia` command used to control the Caelestia
shell and related dotfiles. It includes helpers for scheme management,
wallpaper-driven dynamic colours, screenshots, recording, clipboard history,
and shell IPC.

%prep
%autosetup -n caelestia-%{version}

%build
%{__python3} -m build --wheel --no-isolation

%install
%{__python3} -m installer \
    --destdir %{buildroot} \
    --prefix %{_prefix} \
    dist/*.whl

install -Dpm0644 completions/caelestia.fish \
    %{buildroot}%{_datadir}/fish/vendor_completions.d/caelestia.fish

%check
cd /tmp
export XDG_CONFIG_HOME="$PWD/xdg/config"
export XDG_DATA_HOME="$PWD/xdg/data"
export XDG_STATE_HOME="$PWD/xdg/state"
export XDG_CACHE_HOME="$PWD/xdg/cache"
mkdir -p \
    "$XDG_CONFIG_HOME" \
    "$XDG_DATA_HOME" \
    "$XDG_STATE_HOME" \
    "$XDG_CACHE_HOME"
sitepkgs="$(find %{buildroot}%{_prefix}/lib -path '*/site-packages' -type d | head -n1)"
test -n "$sitepkgs"
PYTHONPATH="$sitepkgs" %{buildroot}%{_bindir}/caelestia --help >/dev/null
names="$(PYTHONPATH="$sitepkgs" %{buildroot}%{_bindir}/caelestia scheme list --names)"
printf '%s\n' "$names" | grep -qx 'catppuccin'

%files
%license LICENSE
%doc README.md
%{_bindir}/caelestia
%{_datadir}/fish/vendor_completions.d/caelestia.fish
%{_prefix}/lib/python3*/site-packages/caelestia/
%{_prefix}/lib/python3*/site-packages/caelestia-*.dist-info/

%changelog
%autochangelog
