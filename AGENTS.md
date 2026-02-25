# AGENTS.md

Session handoff notes for continuing work on this repo.

## Project intent

This repository is a Fedora RPM packaging monorepo for the Hypr ecosystem, intended for COPR SCM builds.

Goals:

- Build/maintain Hypr-related packages for Fedora 43, Fedora 44, and rawhide
- Keep a clean packaging repo (fresh start), not a fork of `solopasha/hyprlandRPM`
- Use COPR SCM package entries per package subdirectory
- Add automation later, after manual/local builds are stable

## Naming decisions (updated)

- Repo name: `hyprland-rpms` (chosen because it stays discoverable while still signaling an RPM packaging repo)
- Alternative considered: `hyprwm-rpms`
- COPR project name can still be shorter (`hyprland`) for discoverability

Why not just `hyprland` for the repo:

- This repo will include multiple packages (`hyprland`, `xdg-desktop-portal-hyprland`, `hyprlock`, `hypridle`, etc.), so a broader name is clearer.

## Reference used

Reference repo (for spec patterns only, not layout/process):

- `https://github.com/solopasha/hyprlandRPM`

What we intentionally avoided from the reference:

- Flat top-level directory sprawl for many unrelated packages
- Shared COPR SRPM logic with package-specific behavior
- Opaque update scripts/policies

## Scaffold created (2026-02-24)

Path:

- `~/Code/hyprland-rpms`

Key files/directories:

- `README.md` (repo overview and naming rationale)
- `.copr/Makefile` (generic `make_srpm` support for COPR SCM)
- `docs/`
  - `docs/copr-setup.md`
  - `docs/packaging-policy.md`
  - `docs/release-process.md`
- `scripts/`
  - `scripts/check-specs.sh`
  - `scripts/new-package.sh`
  - `scripts/bump-version.sh`
  - `scripts/copr-onboard-checklist.sh`
- `.github/workflows/`
  - `spec-lint.yml`
  - `repoclosure.yml`
- `templates/package/` (new-package template)
- `packages/hyprland/` (starter spec + metadata)
- `packages/xdg-desktop-portal-hyprland/` (starter spec + metadata)

## Current status

- Monorepo scaffold is complete and lintable.
- `make list` works.
- `make check-specs` passes (`rpmspec` parse + `rpmlint`).

Important:

- `packages/hyprland/hyprland.spec` is buildable in local `mock --chain` for Fedora 43/44/rawhide (`0.53.3`) with the packaged local dependency stack (`hyprwayland-scanner`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`, `aquamarine`, `hyprwire`, `hyprland-protocols`, `glaze`).
- TODOs remain for:
  - clean standalone `mock --rebuild` validation (without local chain) when dependent versions land in repos/COPR
  - final dependency floors and version-specific conditionals
  - final packaging polish/review for bundled components (for example, current `xdg-desktop-portal-hyprland` spec carries bundled `sdbus-cpp`)
  - bundling declarations if required by upstream release contents

- `packages/xdg-desktop-portal-hyprland/xdg-desktop-portal-hyprland.spec` has been re-verified via local full-stack `mock --chain` on Fedora 43/44/rawhide against the Hyprland `0.53.3` stack, but still needs final Fedora packaging-policy review before publishing.

## COPR strategy (agreed)

Use one COPR project with multiple SCM package entries.

Per package entry:

- Build source type: `SCM`
- Clone URL: this monorepo URL
- Committish: `main`
- Subdirectory: `packages/<pkgname>`
- Spec file: `<pkgname>.spec`
- Build SRPM with: `make_srpm`

Auto-rebuild/webhooks:

- Enable only after first manual builds succeed
- COPR can auto-rebuild from webhook events, but it does NOT auto-bump spec versions
- Upstream version bump automation should be handled later via GitHub Actions or Packit

## Suggested build/update order for Hypr stack

Start with foundational libraries before `hyprland`:

1. `hyprwayland-scanner`
2. `hyprutils`
3. `hyprlang`
4. `hyprcursor`
5. `hyprgraphics`
6. `aquamarine`
7. `hyprwire`
8. `hyprland-protocols`
9. `glaze` (pin to compatible `6.x` for Hyprland `0.53.x`)
10. `hyprland`
11. `xdg-desktop-portal-hyprland`

This order is documented in `docs/packaging-policy.md`.

## Package matrix (tracking)

Use this table as the single place to track packaging/build progress across Fedora releases.

Status legend:

- `NS` = not started
- `SC` = scaffolded (directory/spec starter exists)
- `WIP` = actively being fixed
- `SRPM` = SRPM builds locally
- `M43` / `M44` / `MRH` = mock rebuild passes for Fedora 43 / 44 / rawhide
- `COPR` = COPR build passing
- `DONE` = published/stable in COPR for target chroots

Build result legend (per Fedora columns):

- `-` = not attempted
- `ok` = passing
- `fail` = failing
- `n/a` = not targeted

| Package | Role | Priority | Spec status | F43 mock | F44 mock | Rawhide mock | COPR pkg entry | COPR builds | Notes |
|---|---|---:|---|---|---|---|---|---|---|
| `hyprwayland-scanner` | core toolchain | 1 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.4.5`) and mock rebuilds pass on Fedora 43/44/rawhide |
| `hyprutils` | core library | 2 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.11.0`); Fedora 43/44/rawhide builds revalidated via mock chain while testing `hyprland`/`hyprwire` |
| `hyprlang` | core library | 3 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.6.8`) and mock rebuilds pass on Fedora 43/44/rawhide |
| `hyprcursor` | core library | 4 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.1.13`) and mock rebuilds pass on Fedora 43/44/rawhide |
| `hyprgraphics` | core library | 5 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | Fedora 43/44/rawhide mock chain (`hyprutils -> hyprlang -> hyprgraphics`) passes; clean F43 mock against distro `hyprutils` failed due older dependency version |
| `aquamarine` | core library | 6 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | Fedora 43/44/rawhide mock chain (`hyprwayland-scanner -> hyprutils -> aquamarine`) passes; clean F43 mock failed on unavailable BuildRequires in distro repos |
| `hyprwire` | core library/tooling | 7 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.3.0`) and Fedora 43/44/rawhide mock chain rebuilds pass; required by `hyprctl` in Hyprland `0.53.x` |
| `hyprland-protocols` | protocol definitions | 8 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.7.0`) and Fedora 43/44/rawhide mock chain rebuilds pass |
| `glaze` | compatibility dependency | 9 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`6.1.0`); pinned to `6.x` for Hyprland `0.53.x` compatibility and Fedora 43/44/rawhide mock chain rebuilds pass |
| `hyprland` | compositor | 10 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`0.53.3`); Fedora 43/44/rawhide pass via full mock chain including `hyprland-protocols` and `glaze`; `hyprpm` and `start-hyprland` enabled in package output |
| `xdg-desktop-portal-hyprland` | portal backend | 11 | `MRH` | `ok` | `ok` | `ok` | `no` | `-` | local SRPM builds (`1.3.11`); Fedora 43/44/rawhide pass via full mock chain against Hyprland `0.53.3` stack; includes `pkgconfig(libspa-0.2)` and bundled `sdbus-cpp` declaration |
| `hyprlock` | ecosystem app | 12 | `NS` | `-` | `-` | `-` | `no` | `-` | add after core chain stabilizes |
| `hypridle` | ecosystem app | 13 | `NS` | `-` | `-` | `-` | `no` | `-` | add after core chain stabilizes |
| `hyprpaper` | ecosystem app | 14 | `NS` | `-` | `-` | `-` | `no` | `-` | optional early package, lower risk than Hyprland |

Recommended usage:

1. Update `Spec status` whenever a package moves stages (`NS` -> `SC` -> `WIP` -> `SRPM` ...)
2. Record `F43/F44/Rawhide mock` results immediately after each `mock --rebuild`
3. Flip `COPR pkg entry` to `yes` only after the SCM package entry is created
4. Mark `COPR builds` as `ok/fail` per latest build result and keep failure reasons in `Notes`

## Suggested next steps (carry-over)

1. Create COPR project and add SCM package entries for the validated chain (`hyprwayland-scanner`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`, `aquamarine`, `hyprwire`, `hyprland-protocols`, `glaze`, `hyprland`, `xdg-desktop-portal-hyprland`).
2. Run COPR builds in dependency order, then run repoclosure against the COPR repos after the first successful batch.
3. Re-test `hyprland` and `xdg-desktop-portal-hyprland` with clean standalone `mock --rebuild` once the dependent versions are available through COPR-enabled repos (not only local chains).
4. Review bundling/unbundling options for `xdg-desktop-portal-hyprland` (`sdbus-cpp`) and document the policy decision in the spec/comments.
5. Add upstream version bump automation only after manual workflow is stable.

## Working conventions for future edits

- Keep one package per `packages/<name>/`
- Prefer stable specs first; add `-git` variants later if needed
- Keep package-specific patches in `patches/`
- Use `%autorelease` + `%autochangelog` unless there is a strong reason not to
- Validate with `make check-specs` before pushing
- Test SRPM + `mock` builds before enabling COPR webhooks

## Commands used in this repo

List packages:

```bash
make list
```

Check specs:

```bash
make check-specs
```

Build SRPM for one package:

```bash
make srpm PACKAGE=xdg-desktop-portal-hyprland
```

Scaffold a new package:

```bash
./scripts/new-package.sh hyprlock https://github.com/hyprwm/hyprlock.git https://github.com/hyprwm/hyprlock/releases
```

## Notes for continuation

When resuming, start by reading:

1. `README.md`
2. `docs/packaging-policy.md`
3. `packages/hyprland/hyprland.spec`
4. This `AGENTS.md`

Primary near-term task:

- The local dependency chain now builds through `xdg-desktop-portal-hyprland` in `mock --chain` for Fedora 43/44/rawhide; next focus is COPR onboarding/build-order validation and clean non-chain rebuilds where practical.
