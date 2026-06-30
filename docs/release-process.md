# Release Process

## Manual update flow (recommended first)

1. Check upstream versions:
   - `./scripts/check-upstream-versions.sh --changed-only`
   - `./scripts/check-upstream-versions.sh --package <name>`
2. Update the package spec (`Version`, `Source`, dependency floors, patches)
   - Before committing, run the worktree preflight gate:
     `make check-upgrade UPGRADE_BASE_REF=origin/main`
   - This parses/lints specs and checks that shared-library package bumps and
     exact `pkgconfig(<package>) = <version>` ABI locks rebuild in-repo
     consumers by changing their `Version` or `Release`.
3. Build SRPM locally:
   - `make srpm PACKAGE=<name>`
4. Build in `mock` for Fedora 43/44/rawhide (x86_64 baseline):
   - `mock -r fedora-43-x86_64 --rebuild dist/srpm/<file>.src.rpm`
   - `mock -r fedora-44-x86_64 --rebuild dist/srpm/<file>.src.rpm`
   - `mock -r fedora-rawhide-x86_64 --rebuild dist/srpm/<file>.src.rpm`
   - Add aarch64 mock rebuilds when needed/available:
     - `mock -r fedora-43-aarch64 --rebuild dist/srpm/<file>.src.rpm`
     - `mock -r fedora-44-aarch64 --rebuild dist/srpm/<file>.src.rpm`
     - `mock -r fedora-rawhide-aarch64 --rebuild dist/srpm/<file>.src.rpm`
5. Commit changes
6. Push to your packaging repo
7. Trigger COPR build (manual or webhook)
   - For aarch64-only rollouts on already-stable x86_64 stacks:
     - `copr-cli build-package <owner>/<project> --name <pkg> -r fedora-43-aarch64 -r fedora-44-aarch64 -r fedora-rawhide-aarch64`
   - For packages with `BuildRequires` / runtime `Requires` on other COPR-packaged
     dependencies, publish the dependency on the target chroots first, wait for
     it to land in the repo metadata, and only then trigger the dependent build.
   - If multiple dependent builds need to be queued together, prefer explicit
     ordering (`--after-build-id` where applicable) instead of submitting the
     whole stack simultaneously.
8. Run repoclosure checks on the COPR project
9. Run smoke tests (container CI baseline; local KVM for deeper runtime checks when relevant)

## Maintenance batch playbook

Use this when the routine upstream check finds several independent package
bumps plus a small ABI-coupled Hypr stack rebuild.

1. Check for drift and update specs:
   - `./scripts/check-upstream-versions.sh --changed-only`
   - Bump `Version`, reset stale same-version rebuild bases on true upstream
     bumps, and update dependency floors when a provider ABI moves.
2. Generate SRPMs for every changed package:
   - `make srpm PACKAGE=<pkg>`
   - Include same-version rebuild consumers in this set, not only packages
     whose upstream version changed.
3. Run the pre-push gate:
   - `make check-upgrade UPGRADE_BASE_REF=origin/main`
   - If it reports an ABI provider miss, bump the consumer `Release` base
     (`%autorelease -b N`) and regenerate that consumer SRPM.
4. Run a focused mock matrix in dependency order:
   - `./scripts/mock-matrix-build.sh --skip-srpm --mode chain --release 43 --release 44 --release rawhide --arch x86_64 --addrepo 'https://download.copr.fedorainfracloud.org/results/mineiro/hyprland/fedora-$releasever-$basearch/' <ordered packages...>`
   - Put ABI providers before consumers. For example:
     `aquamarine glaze hyprtoolkit hyprland hyprland-plugins`.
   - Put leaf packages anywhere in the same chain after their SRPMs exist.
5. Commit and push only after the local gates are green.
6. Trigger COPR with explicit batch ordering:
   - Start independent leaf/support builds together with `--with-build-id`.
   - Start provider builds together, for example `aquamarine` and `glaze`.
   - Queue consumers with `--after-build-id <provider-build-id>`.
   - Queue `hyprland-plugins` with `--after-build-id <hyprland-build-id>`.
7. Watch the batch:
   - `copr-cli watch-build <build-id>...`
   - If `watch-build` is quiet, spot-check long builds with
     `copr-cli status <build-id>`.
8. Update `AGENTS.md` with the commit, build IDs, validation results, and next
   open task before ending the session.

Recent example from the 2026-06-30 maintenance pass:

- Commit: `27db241` (`Update Hyprland maintenance package set`)
- Leaf/support builds: `app2unit` `10662392`, `swayosd` `10662393`,
  `caelestia-cli` `10662394`, `dart-sass` `10662395`, `uwsm` `10662396`
- Provider builds: `aquamarine` `10662397`, `glaze` `10662398`
- Rebuilds after providers: `hyprtoolkit` `10662399`, `hyprland` `10662400`
- Exact Hyprland ABI rebuild: `hyprland-plugins` `10662401`
- All listed COPR builds succeeded.

## Dependency-first rollout rule

- Do not treat "noarch" as exempt from dependency sequencing.
- A noarch package still runs `builddep` inside each target chroot, so a new
  aarch64 rollout can fail if one of its `BuildRequires` is only published on
  x86_64 at the time the build starts.
- Recent example: `caelestia-cli` aarch64 rollout required
  `python3-materialyoucolor`; triggering both at once caused `caelestia-cli`
  to fail in COPR until `python-materialyoucolor` finished publishing on the
  aarch64 chroots.

## Same-version ABI rebuild rule

- If a dependency ABI changes and downstream packages are rebuilt without an
  upstream version bump, the rebuilt consumers must get a higher RPM release.
- Do not rely on a plain COPR rebuild of the same `Version-Release`; DNF will
  keep the already-installed headers and can continue treating them as the old
  ABI consumers.
- For this repo's specs, bump the release base explicitly (for example
  `Release: %autorelease -b 2`) on every same-version consumer rebuild, then
  reset it on the next upstream version bump.
- Recent example: the `hyprutils 0.12.0` soname move (`libhyprutils.so.10` ->
  `.11`) required `-2` rebuilds of the unchanged-version Hypr stack so users
  could upgrade cleanly.
- The `Spec Lint` workflow runs `scripts/check-abi-rebuilds.sh` to catch common
  cases before COPR publish: if an in-repo package that ships `*.so.*` changes
  `Version`, any in-repo `pkgconfig(<package>)` consumers must also change
  `Version` or `Release` in the same commit/PR. The same gate also checks exact
  `pkgconfig(<package>) = <version>` locks, such as `hyprland-plugins` against
  `pkgconfig(hyprland)`.
- The same check can be run before commit/push against uncommitted worktree
  changes with `make check-upgrade UPGRADE_BASE_REF=origin/main`.

## Rawhide Python ABI rebuild rule

- Rawhide may move to the next Python minor before Fedora 43/44 do.
- Native Python extension packages in this COPR can then become uninstallable
  on rawhide until they are rebuilt against the new `python(abi)`.
- If repoclosure reports a stale `python(abi)` dependency, bump the package's
  `Release` base and rebuild it in COPR even when the upstream version is
  unchanged.
- Recent example: `python-materialyoucolor 3.0.2-1.fc45` required
  `python(abi) = 3.14` after rawhide moved to Python 3.15, so it needed a
  same-version release rebuild.

## Hyprland plugins compatibility gate

- `hyprland-plugins` must follow upstream ABI-compatible release families.
- Do not bump `hyprland-plugins` for a new Hyprland family unless upstream
  publishes a compatible release/tag for that family.
- Current status: Hyprland `0.55.4` is published with the compatible
  `hyprland-plugins` `v0.55.0` family.
- It is valid for the plugin source tag to remain at `v0.55.0` while the RPM
  release and `%{hyprland_target_version}` track later compatible Hyprland
  `0.55.x` patch releases.
- Keep transitional `Obsoletes` in `hyprland` for legacy `0.53.x` plugin RPMs
  until the upgrade path has been exercised across supported Fedora releases.
- Repoclosure and smoke gates should include `hyprland-plugins` whenever the
  plugin package is pinned to the active Hyprland ABI family.
- If old retired plugin RPMs remain in COPR metadata, repoclosure may exclude
  only those retired subpackage names until the stale build is removed.

## Validation gates (current)

Use staged validation instead of relying on a single build result:

1. `repoclosure` (repo-level dependency sanity)
2. `CI container smoke` (fast installability/package layout checks)
3. `Local KVM headless smoke` (real Fedora VM with `systemd`/`logind`)
4. `Local KVM graphical smoke` (Hyprland session startup/runtime sanity)

Recommended commands:

- Container smoke (local wrapper):
  - `./scripts/copr-smoke-tests.sh mineiro hyprland`
- KVM headless smoke:
  - `./scripts/kvm-smoke-headless.sh --release 44`
- KVM graphical smoke (GDM + default Hyprland session):
  - `./scripts/kvm-smoke-headless.sh --smoke-mode graphical --release 43 --keep-vm`
- KVM graphical smoke without the virgl/SPICE GL acceleration probe (useful on hosts that always fail EGL init):
  - `./scripts/kvm-smoke-headless.sh --smoke-mode graphical --graphics-accel off --release 43`

Notes:

- The KVM harness auto-downloads/caches Fedora cloud images and verifies checksums.
- In graphical mode, the harness tries virgl/SPICE GL acceleration by default and automatically falls back to non-accelerated graphics when the host lacks working EGL/virgl.
- `gdm` is the default graphical session path because it exercises the distro/default Hyprland session flow; tty graphical mode remains available for debugging (`--graphical-session-mode tty`).

## Automation later

After the package is stable, add automation for version bumps:

- Option A: GitHub Actions + release polling
- Option B: Packit `copr_build` on upstream release events

Keep automation package-specific. Avoid one script that mutates many specs without validation.
