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
- Container smoke-test automation is implemented and validated:
  - `scripts/copr-smoke-tests.sh` (Podman wrapper + in-container checks)
  - `.github/workflows/copr-smoke-tests.yml` (Fedora 43/44/rawhide matrix using `COPR_OWNER`/`COPR_PROJECT`) now runs successfully in GitHub Actions
- Local KVM smoke-test harness is implemented and locally validated on libvirt/KVM:
  - `scripts/kvm-smoke-headless.sh` (Fedora cloud image auto-download/cache + checksum verification, cloud-init + SSH checks, log collection)
  - headless mode passes on Fedora 43/44/rawhide
  - graphical mode passes locally via GDM auto-login into the default Hyprland session (`hyprland.desktop`), with screenshot/log capture and a tty fallback path available for debugging
  - graphical runs now support best-effort virgl/SPICE GL acceleration with automatic fallback to non-accelerated graphics when host EGL/virgl is unavailable
- `packages/hyprlock/` has been added as the next ecosystem package starter (`0.9.2`), adapted from the `solopasha/hyprlandRPM` baseline; local SRPM and clean `mock --rebuild` pass on Fedora 43/44/rawhide using the `mineiro/hyprland` COPR repo for dependencies.
- `packages/hypridle/` has been added as the next ecosystem package starter (`0.1.7`), adapted from the `solopasha/hyprlandRPM` baseline; local SRPM and clean `mock --rebuild` pass on Fedora 43/44/rawhide using the `mineiro/hyprland` COPR repo for dependencies.
- `hypridle` has been onboarded to COPR (`mineiro/hyprland`) and COPR builds are passing on Fedora 43/44/rawhide.
- `packages/hyprtoolkit/` has been added at the latest upstream release (`0.5.3`), locally validated on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. It currently carries a small compatibility patch set for the validated `hyprgraphics 0.4.0` stack (in-memory image constructor fallback) plus portability fixes (`NAME_MAX` / `<limits.h>`).
- `packages/hyprpaper/` has been updated back to the latest upstream release (`0.8.3`) and successfully built in COPR (`mineiro/hyprland`) after publishing `hyprtoolkit`; local validation currently includes Fedora 43/44/rawhide `mock --chain` (`hyprtoolkit` -> `hyprpaper`) with clean standalone `mock --rebuild` queued for a later validation pass.
- `packages/hyprpicker/` has been added at the latest upstream release (`0.4.6`), locally validated on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. It currently carries a small upstream header-fix patch (`#include <mutex>`) needed on newer Fedora toolchains (Fedora 44/rawhide / GCC 15).
- `packages/hyprsunset/` has been added at the latest upstream release (`0.3.3`), locally validated on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds.
- `packages/hyprpolkitagent/` has been added at the latest upstream release (`0.1.3`), locally validated on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. It has a runtime dependency on `hyprland-qt-support`, so the Qt support trio is now the next packaging focus.
- `packages/hyprland-qt-support/` has been added (`0.1.0`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds; it carries a small upstream CMake patch to fix project version initialization order.
- `packages/hyprqt6engine/` has been added (`0.1.0`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds; it carries a small upstream Qt private-module detection patch for newer Qt6.
- `packages/hyprland-guiutils/` has been added at the latest upstream release (`0.2.1`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. This is the upstream successor to `hyprland-qtutils`, so `hyprland-qtutils` packaging is being deferred in favor of `hyprland-guiutils`.
- `packages/hyprsysteminfo/` has been added at the latest upstream release (`0.1.3`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds; it carries a small Qt6 Wayland private-module detection patch for newer Qt6.
- `packages/hyprlauncher/` has been added at the latest upstream release (`0.1.5`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds; it carries a small portability patch adding missing POSIX includes (`NAME_MAX`, `read`) required on newer Fedora toolchains.
- `packages/hyprshot/` has been added at the latest upstream release (`1.3.0`, `Gustash/Hyprshot`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds; this is a noarch shell-script package.
- `packages/hyprpwcenter/` has been added at the latest upstream release (`0.1.2`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds.
- `packages/hyprdim/` has been added at the latest upstream release (`3.0.1`, `donovanglover/hyprdim`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. It uses vendored Rust crates (`Source1`) generated during SRPM creation so builds work offline in mock/COPR.
- `.copr/Makefile` now conditionally supports Rust vendored-source generation for packages that declare `%cargo_prep` + `Source1`, including robust `%{_sourcedir}` / `spectool -R` handling for COPR SCM `make_srpm`, so offline-capable Rust SRPMs (for example `hyprdim`) build reliably in COPR.
- `packages/hyprshutdown/` has been added at the latest upstream release (`0.1.0`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds.
- `packages/hyprland-plugins/` has been added as a split-plugin bundle package targeting the latest compatible upstream tag for the current stack (`v0.53.0` for `hyprland 0.53.x`), locally validated via SRPM + clean `mock --rebuild` on Fedora 43/44/rawhide, and onboarded to COPR (`mineiro/hyprland`) with successful Fedora 43/44/rawhide builds. It intentionally version-locks plugin subpackages to `hyprland 0.53.3` because plugin binaries are ABI-coupled to Hyprland.
- `packages/waybar/` has been added at the latest upstream release (`0.15.0`, `Alexays/Waybar`) as a stable `waybar` package (not `waybar-git`) to provide a newer build than Fedora's default repo version when needed; local SRPM and clean `mock --rebuild` pass on Fedora 43/44/rawhide, and COPR builds are now passing in `mineiro/hyprland`.

- TODOs remain for:
  - continue tightening graphical VM assertions/log diagnostics (PipeWire/portal/user-service readiness, etc.) without making the harness flaky
  - re-validate/tune newly added dependency floors and any Fedora version-specific conditionals as packages evolve
  - final packaging polish/review for bundled components (currently `xdg-desktop-portal-hyprland`, `hyprlock`, and `hypridle` carry bundled `sdbus-cpp` declarations)
  - revisit bundling declarations if upstream release contents or build paths change

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
| `hyprlock` | ecosystem app | 13 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | starter spec added (`0.9.2`), includes documented temporary bundled `sdbus-cpp`; local SRPM and clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing in `mineiro/hyprland` |
| `hypridle` | ecosystem app | 14 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | starter spec added (`0.1.7`), includes documented temporary bundled `sdbus-cpp`; local SRPM and clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing in `mineiro/hyprland` |
| `hyprtoolkit` | ecosystem library/toolkit | 15 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.5.3`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary compatibility patch for current `hyprgraphics 0.4.0` stack and portability fixes (`NAME_MAX`, missing includes) |
| `hyprpaper` | ecosystem app | 16 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.8.3`; local SRPM + `mock --chain` (local `hyprtoolkit` + `hyprpaper`) pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing after `hyprtoolkit` publish |
| `hyprpicker` | ecosystem app | 17 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.4.6`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary upstream header-fix patch (`#include <mutex>`) for Fedora 44/rawhide/GCC 15 builds |
| `hyprsunset` | ecosystem app | 18 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.3.3`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing |
| `hyprpolkitagent` | ecosystem app | 19 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.1.3`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; runtime `Requires: hyprland-qt-support` |
| `hyprland-qt-support` | Qt support stack | 20 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | version `0.1.0`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary CMake patch for project/version initialization order |
| `hyprqt6engine` | Qt support stack | 21 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | version `0.1.0`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary Qt private-module detection patch for newer Qt6 |
| `hyprland-guiutils` | ecosystem app (GUI utils) | 22 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.2.1`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; upstream successor to `hyprland-qtutils` |
| `hyprsysteminfo` | ecosystem app | 23 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.1.3`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary Qt private-module detection patch for newer Qt6 |
| `hyprlauncher` | ecosystem app | 24 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.1.5`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; carries temporary portability patch for missing POSIX includes (`NAME_MAX`, `read`) on newer Fedora toolchains |
| `hyprshot` | ecosystem app | 25 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `1.3.0` from `Gustash/Hyprshot`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; noarch shell-script package |
| `hyprpwcenter` | ecosystem app | 26 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.1.2`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing |
| `hyprdim` | ecosystem app (Rust) | 27 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `3.0.1` from `donovanglover/hyprdim`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide; COPR builds passing; uses vendored Rust `Source1` tarball generated during SRPM creation for offline mock/COPR builds |
| `hyprshutdown` | ecosystem app | 28 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream `0.1.0`; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide via `mineiro/hyprland` COPR repo deps; COPR builds passing; depends on `hyprtoolkit`, `hyprutils`, `glaze`, `pixman`, and `libdrm` |
| `hyprland-plugins` | ecosystem plugins | 29 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | official Hyprland plugins bundle; latest compatible upstream tag for current stack is `v0.53.0` (repo tags are version-family aligned); packaged as split plugin subpackages with strict runtime `Requires: hyprland = 0.53.3` to match the current COPR Hyprland ABI target; COPR builds passing |
| `waybar` | desktop bar (Wayland/Hyprland) | 30 | `COPR` | `ok` | `ok` | `ok` | `yes` | `ok` | latest upstream stable `0.15.0` from `Alexays/Waybar`; packaged as stable `waybar` (not `waybar-git`) to provide a newer build than Fedora default repos; local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide; COPR builds passing |

Recommended usage:

1. Update `Spec status` whenever a package moves stages (`NS` -> `SC` -> `WIP` -> `SRPM` ...)
2. Record `F43/F44/Rawhide mock` results immediately after each `mock --rebuild`
3. Flip `COPR pkg entry` to `yes` only after the SCM package entry is created
4. Mark `COPR builds` as `ok/fail` per latest build result and keep failure reasons in `Notes`

## Validation strategy (updated)

Use a staged validation approach instead of a single "smoke test":

1. `CI container smoke` (fast, blocking)
   - Validate COPR repo metadata, dependency resolution, package installability, file placement, and basic CLI presence in clean Fedora 43/44/rawhide containers.
   - Primary tooling: `scripts/copr-smoke-tests.sh` and `.github/workflows/copr-smoke-tests.yml`.
2. `Local KVM headless` (slower, realistic system integration)
   - Validate a full Fedora VM with `systemd`/`logind`, package installation, user-unit file presence, and log collection (`journalctl`) for failures.
   - Primary tooling: `scripts/kvm-smoke-headless.sh` (implemented harness with Fedora cloud image auto-download/cache support).
3. `Local KVM graphical` (manual first, later automated)
   - Validate actual Hyprland session startup/runtime behavior (preferably libvirt/KVM first, then optionally real hardware/self-hosted systems for deeper confidence).
   - Current default path uses `gdm` auto-login into the default Hyprland session (`hyprland.desktop`) to exercise a distro-like user experience; tty-based graphical smoke remains available as a fallback/debug path.
   - Treat this as a separate stage from packaging/install smoke tests.

## Suggested next steps (carry-over)

1. Keep the CI container smoke workflow green and tune assertions conservatively when package outputs evolve.
2. Continue hardening the local KVM graphical smoke stage (service diagnostics, optional acceleration controls, clearer failure artifacts) while keeping it reliable on non-virgl hosts.
3. Re-run `repoclosure` after the recent ecosystem additions (`hyprdim`, `hyprshutdown`, `hyprland-plugins`) and verify the repo still closes cleanly across Fedora 43/44/rawhide.
4. Review bundling/unbundling options for `xdg-desktop-portal-hyprland`, `hyprlock`, and `hypridle` (`sdbus-cpp`) and document any policy changes in spec comments/docs.
5. Re-run `repoclosure` and clean standalone `mock --rebuild` for the latest `hyprpaper` (`0.8.3`) after batching a few more ecosystem packages (if desired).
6. Decide when to enable COPR webhooks/auto-rebuilds, then add upstream version bump automation only after the manual workflow (including smoke tests) is stable.

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

Run container smoke tests against COPR (Fedora 43/44/rawhide):

```bash
./scripts/copr-smoke-tests.sh mineiro hyprland
```

Run local KVM smoke test (Fedora cloud image auto-download/cache supported):

```bash
./scripts/kvm-smoke-headless.sh --release 44
```

Run local KVM graphical smoke test (GDM + default Hyprland session):

```bash
./scripts/kvm-smoke-headless.sh --smoke-mode graphical --release 43 --keep-vm
```

Skip the virgl/SPICE GL acceleration probe on hosts where it is known to fail:

```bash
./scripts/kvm-smoke-headless.sh --smoke-mode graphical --graphics-accel off --release 43
```

## Notes for continuation

When resuming, start by reading:

1. `README.md`
2. `docs/packaging-policy.md`
3. `packages/hyprland/hyprland.spec`
4. This `AGENTS.md`

Primary near-term task:

- Keep the container smoke-test path (`scripts/copr-smoke-tests.sh` + CI workflow) as the fast baseline, continue hardening the local libvirt/KVM graphical smoke stage (GDM/default-session path), and then shift focus to packaging-policy cleanup plus the next ecosystem packages.
