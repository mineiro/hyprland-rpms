# Packaging Policy

This repo is packaging infrastructure, not an upstream source mirror.

## Rules

1. One RPM package per directory under `packages/<name>/`.
2. Keep package-specific patches under `packages/<name>/patches/`.
3. Do not mix unrelated package content in the same directory.
4. Prefer stable release packages first; add `-git` variants only when needed.
5. Avoid vendoring bundled dependencies unless Fedora packaging requires it.
   - If bundling is temporarily required, document the rationale in the spec,
     declare `Provides: bundled(<name>)`, and record the intended unbundling
     exit criteria (what has to become true before switching to a system copy).
6. Use `Release: %autorelease` and `%autochangelog` for new specs unless there is a strong reason not to.
7. Use Fedora conditionals only when necessary (`%if 0%{?fedora} >= 44`), and document why.
8. Test locally with `rpmbuild` and `mock` before enabling COPR auto-rebuilds.

## Hypr ecosystem specifics

- Version compatibility matters across `hypr*` libraries and Hyprland.
- Update build/runtime dependency floors deliberately.
- Build in dependency order when introducing a stack upgrade.
- When a validated COPR stack exists, encode minimum compatible dependency
  floors in specs to avoid mixed-ABI `builddep` resolution (for example older
  Fedora `hyprutils` vs newer COPR `hyprutils`).
- Current temporary bundled dependency exceptions (to be reviewed regularly):
  - `xdg-desktop-portal-hyprland`: bundled `sdbus-cpp`
  - `hyprlock`: bundled `sdbus-cpp`
  - `hypridle`: bundled `sdbus-cpp`

Suggested initial package order:

1. `hyprwayland-scanner`
2. `hyprutils`
3. `hyprlang`
4. `hyprcursor`
5. `hyprgraphics`
6. `aquamarine`
7. `hyprwire`
8. `hyprland-protocols`
9. `glaze`
10. `hyprland`
11. `xdg-desktop-portal-hyprland`

Suggested next ecosystem packages after the core chain stabilizes:

1. `hyprlock`
2. `hypridle`
3. `hyprpaper`

## What to avoid (fresh-start guardrails)

- Large top-level flat directories for dozens of unrelated packages
- Package-specific CI logic hardcoded in a shared COPR Makefile
- Hidden update scripts with no documented trigger or version policy
- Mixing stable and snapshot semantics in one spec without clear macros
