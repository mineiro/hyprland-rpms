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
- `packages/uwsm/` has been added (ported from `solopasha/hyprlandRPM` spec baseline, adapted to this monorepo style).

Important:

- `packages/hyprland/hyprland.spec` is buildable in local `mock --chain` for Fedora 43/44/rawhide (`0.53.3`) with the packaged local dependency stack (`hyprwayland-scanner`, `hyprutils`, `hyprlang`, `hyprcursor`, `hyprgraphics`, `aquamarine`, `hyprwire`, `hyprland-protocols`, `glaze`).
- `packages/xdg-desktop-portal-hyprland/xdg-desktop-portal-hyprland.spec` has been re-verified via local full-stack `mock --chain` on Fedora 43/44/rawhide against the Hyprland `0.53.3` stack.
- COPR onboarding is complete in `mineiro/hyprland` (after correcting an initial typoed project name `hyperland`):
  - SCM package entries created for the validated stack plus `uwsm`
  - all target builds succeeded on Fedora 43/44/rawhide
- `repoclosure` now passes for Fedora 43/44/rawhide after adding `uwsm` (required by `hyprland-uwsm` subpackage runtime dependency).
- Clean standalone `mock --rebuild` (non-chain) has been re-validated for `hyprland` and `xdg-desktop-portal-hyprland` on Fedora 43/44/rawhide using the `mineiro/hyprland` COPR repos (`mock --addrepo ...`).

- TODOs remain for:
  - containerized install/smoke-test automation for Fedora 43/44/rawhide against COPR
  - optional graphical runtime validation (VM-based Hyprland startup/session checks)
  - final dependency floors and version-specific conditionals
  - final packaging polish/review for bundled components (for example, current `xdg-desktop-portal-hyprland` spec carries bundled `sdbus-cpp`)
  - bundling declarations if required by upstream release contents

## COPR strategy (agreed)

Use one COPR project with multiple SCM package entries.

Per package entry:

- Build source type: `SCM`
- Clone URL: this monorepo URL
- Committish: `main`
- Subdirectory: `packages/<pkgname>`
- Spec file: `<pkgname>.spec`
- Build SRPM with: `make_srpm`

Active project:

- `mineiro/hyprland` (current canonical COPR project; an earlier typoed project `mineiro/hyperland` was used during initial onboarding/testing)

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

Additional runtime/support package now included in COPR:

12. `uwsm` (required so `hyprland-uwsm` is repo-installable and repoclosure passes)

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
| `hyprwayland-scanner` | core toolchain | 1 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.4.5`) and mock rebuilds pass on Fedora 43/44/rawhide; COPR SCM entry/builds passing in `mineiro/hyprland` |
| `hyprutils` | core library | 2 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.11.0`); Fedora 43/44/rawhide builds revalidated via mock chain while testing `hyprland`/`hyprwire`; COPR builds passing |
| `hyprlang` | core library | 3 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.6.8`) and mock rebuilds pass on Fedora 43/44/rawhide; rebuilt in COPR against `hyprutils` `0.11.0` ABI |
| `hyprcursor` | core library | 4 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.1.13`) and mock rebuilds pass on Fedora 43/44/rawhide; COPR builds passing |
| `hyprgraphics` | core library | 5 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | Fedora 43/44/rawhide mock chain (`hyprutils -> hyprlang -> hyprgraphics`) passes; clean F43 mock against distro `hyprutils` had previously failed due older dependency version |
| `aquamarine` | core library | 6 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | Fedora 43/44/rawhide mock chain (`hyprwayland-scanner -> hyprutils -> aquamarine`) passes; clean F43 mock had previously failed on unavailable BuildRequires in distro repos |
| `hyprwire` | core library/tooling | 7 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.3.0`) and Fedora 43/44/rawhide mock chain rebuilds pass; COPR build verified requiring `libhyprutils.so.10` |
| `hyprland-protocols` | protocol definitions | 8 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.7.0`) and Fedora 43/44/rawhide mock chain rebuilds pass; COPR builds passing |
| `glaze` | compatibility dependency | 9 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`6.1.0`); pinned to `6.x` for Hyprland `0.53.x` compatibility and Fedora 43/44/rawhide mock chain rebuilds pass; COPR builds passing |
| `hyprland` | compositor | 10 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`0.53.3`); full mock chain pass on Fedora 43/44/rawhide; clean standalone `mock --rebuild` also revalidated on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo; `hyprpm`/`start-hyprland`/`hyprland-uwsm` in package output |
| `xdg-desktop-portal-hyprland` | portal backend | 11 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | local SRPM builds (`1.3.11`); full mock chain pass on Fedora 43/44/rawhide; clean standalone `mock --rebuild` also revalidated on Fedora 43/44/rawhide via `mineiro/hyprland`; includes `pkgconfig(libspa-0.2)` and bundled `sdbus-cpp` declaration |
| `uwsm` | session manager/runtime dependency | 12 | `COPR` | `-` | `-` | `-` | `yes` | `ok` | added to satisfy `hyprland-uwsm` runtime dependency; COPR builds pass on Fedora 43/44/rawhide; repoclosure passes after publishing |
| `hyprlock` | ecosystem app | 13 | `NS` | `-` | `-` | `-` | `no` | `-` | add after core chain stabilizes |
| `hypridle` | ecosystem app | 14 | `NS` | `-` | `-` | `-` | `no` | `-` | add after core chain stabilizes |
| `hyprpaper` | ecosystem app | 15 | `NS` | `-` | `-` | `-` | `no` | `-` | optional early package, lower risk than Hyprland |

Recommended usage:

1. Update `Spec status` whenever a package moves stages (`NS` -> `SC` -> `WIP` -> `SRPM` ...)
2. Record `F43/F44/Rawhide mock` results immediately after each `mock --rebuild`
3. Flip `COPR pkg entry` to `yes` only after the SCM package entry is created
4. Mark `COPR builds` as `ok/fail` per latest build result and keep failure reasons in `Notes`

## Suggested next steps (carry-over)

1. Automate containerized install/smoke tests (Fedora 43/44/rawhide) against `mineiro/hyprland` for at least `hyprland`, `xdg-desktop-portal-hyprland`, and `uwsm`.
2. Optionally add VM-based graphical validation (local/libvirt-first) to verify a Hyprland session can start with `uwsm`; treat this as a separate, slower validation stage.
3. Update docs/tracking (`AGENTS.md` package matrix, COPR notes, and any other docs) to reflect the completed COPR onboarding, `uwsm` addition, repoclosure pass, and clean standalone mock rebuild validation.
4. Review bundling/unbundling options for `xdg-desktop-portal-hyprland` (`sdbus-cpp`) and document the policy decision in the spec/comments.
5. Decide when to enable COPR webhooks/auto-rebuilds, then add upstream version bump automation only after the manual workflow (including smoke tests) is stable.

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

- Automate post-build smoke tests in clean Fedora 43/44/rawhide containers against `mineiro/hyprland`, and optionally prototype VM-based graphical validation for Hyprland/`uwsm` sessions.
