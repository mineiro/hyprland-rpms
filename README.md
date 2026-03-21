# hyprland-rpms

Monorepo for Fedora RPM packaging of the Hypr ecosystem and related desktop
utilities, designed for COPR SCM builds.

This repo is intentionally structured as a packaging monorepo, not a generic software repo:

- One package per directory under `packages/`
- Shared build helpers and CI at repo root
- COPR builds use `SCM` + `make_srpm`
- Local testing uses `rpmbuild` / `mock`

## Layout

```text
.
├── .copr/                  # COPR make_srpm integration
├── .github/workflows/      # CI checks (spec parse, repoclosure)
├── docs/                   # Packaging policy, COPR setup, release workflow
├── scripts/                # Helpers (new package, bump version, spec checks)
├── templates/package/      # Package directory template
└── packages/
    ├── caelestia-cli/
    ├── dart-sass/
    ├── hyprland/
    ├── python-materialyoucolor/
    └── xdg-desktop-portal-hyprland/
```

## Repo goals

- Track stable upstream releases first
- Keep package build order and dependency floors explicit
- Support Fedora `43`, `44`, and `rawhide`
- Make COPR package definitions reproducible (documented and scriptable)
- Add automation incrementally after local/manual builds are stable

Recent package additions include Caelestia support components
(`python-materialyoucolor`, `caelestia-cli`), utility packages such as
`dart-sass`, and newer Wayland desktop tools including `swayosd` and
`departure`. The repo now also carries the AGS/Astal userspace stack
(`gnim`, `astal-io`, `astal3`, `astal4`, `astal-hyprland`,
`aylurs-gtk-shell`) so Hyprland users do not need a separate COPR just to
install AGS-related packages.

## Plugin policy (current)

- `hyprland-plugins` is ABI-coupled to Hyprland and is currently paused for the
  `0.54.x` stack until upstream publishes a compatible plugins release.
- Legacy `0.53.x` plugin RPMs are transition-cleaned by `hyprland` package
  obsoletes so users can upgrade to `hyprland 0.54.x` without dependency
  deadlocks.
- Existing plugin users can stay on their installed `0.53.x` set; plugin RPMs
  are treated as legacy until a compatible upstream release lands.

## Quick start

Install baseline packaging tools:

```bash
sudo dnf install -y rpm-build rpmdevtools mock rpmlint copr-cli git
```

Build a source RPM locally (package subdir):

```bash
cd packages/xdg-desktop-portal-hyprland
make srpm
```

List packages:

```bash
make list
```

Parse/lint specs:

```bash
make check-specs
```

Check upstream versions before bumping:

```bash
./scripts/check-upstream-versions.sh --changed-only
```

Check one package:

```bash
./scripts/check-upstream-versions.sh --package hyprland
```

Run a full mock matrix across Fedora 43/44/rawhide and x86_64/aarch64:

```bash
./scripts/mock-matrix-build.sh --all-packages
```

Run only the core dependency chain across the full matrix:

```bash
./scripts/mock-matrix-build.sh hyprwayland-scanner hyprutils hyprlang hyprcursor hyprgraphics aquamarine hyprwire hyprland-protocols glaze hyprland xdg-desktop-portal-hyprland uwsm
```

## COPR model (recommended)

- Create one COPR project (example: `yourname/hyprwm`)
- Add one COPR SCM package entry per subdirectory under `packages/`
- Use `Build Source Type: SCM`
- Use `Build SRPM with: make_srpm`
- Set package `Subdirectory` to `packages/<pkgname>`
- Enable auto-rebuild via webhook for pushes/tags after the package builds cleanly

See `docs/copr-setup.md`.
