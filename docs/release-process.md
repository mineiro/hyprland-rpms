# Release Process

## Manual update flow (recommended first)

1. Check upstream versions:
   - `./scripts/check-upstream-versions.sh --changed-only`
   - `./scripts/check-upstream-versions.sh --package <name>`
2. Update the package spec (`Version`, `Source`, dependency floors, patches)
3. Build SRPM locally:
   - `make srpm PACKAGE=<name>`
4. Build in `mock` for Fedora 43/44:
   - `mock -r fedora-43-x86_64 --rebuild dist/srpm/<file>.src.rpm`
   - `mock -r fedora-44-x86_64 --rebuild dist/srpm/<file>.src.rpm`
5. Commit changes
6. Push to your packaging repo
7. Trigger COPR build (manual or webhook)
8. Run repoclosure checks on the COPR project
9. Run smoke tests (container CI baseline; local KVM for deeper runtime checks when relevant)

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
