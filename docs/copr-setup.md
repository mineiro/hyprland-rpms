# COPR Setup

This repo is designed for COPR `SCM` package entries (one entry per package directory).

## Recommended COPR project layout

- COPR project name: `hyprwm` (or `hyprland`)
- Chroots:
  - `fedora-43-x86_64`
  - `fedora-44-x86_64`
  - `fedora-rawhide-x86_64`
- Add `aarch64` later after x86_64 is stable

## Add a package from this monorepo (SCM)

For each package directory:

- `Clone URL`: your Git repo URL
- `Committish`: `main`
- `Subdirectory`: `packages/<pkgname>`
- `Spec file`: `<pkgname>.spec`
- `Build source type`: `SCM`
- `Build SRPM with`: `make_srpm`

The shared `.copr/Makefile` handles SRPM generation inside COPR.

## Webhooks / auto rebuilds

Enable webhook rebuilds only after manual builds pass.

Recommended sequence:

1. Create package entry
2. Trigger one manual build
3. Verify dependency closure in COPR
4. Enable webhook + auto-rebuild on push/tag

## Notes on auto-updating versions

COPR can rebuild on webhook events, but it does not update spec versions on its own.

Use a separate automation layer (for example GitHub Actions or Packit) to:

1. Detect upstream releases/tags
2. Update `Version` / `Source` / patches in your spec
3. Commit or tag this packaging repo
4. Let COPR rebuild from webhook

