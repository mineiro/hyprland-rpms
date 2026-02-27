# hyprland-rpms

Monorepo for Fedora RPM packaging of the Hypr ecosystem (Hyprland and related components), designed for COPR SCM builds.

This repo is intentionally structured as a packaging monorepo, not a generic software repo:

- One package per directory under `packages/`
- Shared build helpers and CI at repo root
- COPR builds use `SCM` + `make_srpm`
- Local testing uses `rpmbuild` / `mock`

## Why this name?

`hyprland-rpms` is a better fit than `hyprland` when the repo contains multiple RPM package projects (for example `hyprland`, `xdg-desktop-portal-hyprland`, `hyprlock`, `hypridle`, `hyprpaper`).

If you want a broader ecosystem-focused name, a good alternative is `hyprwm-rpms`.

## Layout

```text
.
├── .copr/                  # COPR make_srpm integration
├── .github/workflows/      # CI checks (spec parse, repoclosure)
├── docs/                   # Packaging policy, COPR setup, release workflow
├── scripts/                # Helpers (new package, bump version, spec checks)
├── templates/package/      # Package directory template
└── packages/
    ├── hyprland/
    └── xdg-desktop-portal-hyprland/
```

## Repo goals

- Track stable upstream releases first
- Keep package build order and dependency floors explicit
- Support Fedora `43`, `44`, and `rawhide`
- Make COPR package definitions reproducible (documented and scriptable)
- Add automation incrementally after local/manual builds are stable

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

## COPR model (recommended)

- Create one COPR project (example: `yourname/hyprwm`)
- Add one COPR SCM package entry per subdirectory under `packages/`
- Use `Build Source Type: SCM`
- Use `Build SRPM with: make_srpm`
- Set package `Subdirectory` to `packages/<pkgname>`
- Enable auto-rebuild via webhook for pushes/tags after the package builds cleanly

See `docs/copr-setup.md`.
