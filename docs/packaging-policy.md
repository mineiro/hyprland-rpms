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
- Treat `hyprland-plugins` as ABI-family-coupled with Hyprland. If upstream
  has not published a plugin release for the target Hyprland family, keep
  plugins paused instead of forcing speculative compatibility.
- Current decision: pair Hyprland `0.56.1` with the compatible
  `hyprland-plugins` `v0.56.0` source family, rebuilt with the exact
  `%{hyprland_target_version}` runtime lock. Later Hyprland `0.56.x` patch
  releases may use the same policy unless upstream publishes a newer compatible
  plugin tag. Retired plugin subpackages from the `0.53.x` family are obsoleted
  by `hyprland-plugins`.
- Current rollout policy: include `hyprland-plugins` in validation gates only
  when the plugin package is pinned to the active Hyprland ABI family.
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
3. `hyprtoolkit`
4. `hyprpaper` (latest `0.8.x` path depends on `hyprtoolkit`)
5. `swayosd` (Rust + Meson package; keep vendored `Source1` workflow for offline mock/COPR builds)

## AGS / Astal specifics

- Keep `aylurs-gtk-shell` as the RPM name; Fedora already ships an unrelated
  `ags` package.
- Keep the imported Astal libraries on one pinned monorepo snapshot so API/ABI
  expectations stay aligned across `astal-io`, `astal3`, `astal4`,
  `astal-hyprland`, `astal-apps`, `astal-auth`, `astal-battery`,
  `astal-bluetooth`, `astal-greet`, `astal-mpris`, `astal-network`,
  `astal-notifd`, `astal-power-profiles`, `astal-wireplumber`,
  `astal-wl`, `astal-tray`, `astal-river`, `astal-cava`, and
  `astal-quarrel`.
- Keep optional Astal integrations split into separate RPMs instead of
  bundling them into one `astal-libs` package, so AGS users only install the
  dependency stacks they actually need.
- Package external prerequisites separately as `appmenu-glib-translator`,
  `wl-vapi-gen`, and `libcava` so `astal-tray`, `astal-river`, and
  `astal-cava` stay unbundled.
- Keep `gnim` installed under `%{_datadir}/ags/js/node_modules/gnim` until
  upstream AGS stops expecting the npm-style runtime tree.
- Current `aylurs-gtk-shell` downstream patch set covers packaged `gnim`,
  safer GIR selection defaults, Fedora's packaged `npx`, and the correct
  `gtk4-layer-shell` soname.
- `ags init` / `ags types` still fetch `@ts-for-gir/cli` via `npx`; packaging
  that dependency is the next step for a fully offline AGS bootstrap flow.

Suggested AGS / Astal package order:

1. `gnim`
2. `astal-io`
3. `astal3`
4. `astal4`
5. `astal-hyprland`
6. `aylurs-gtk-shell`
7. `astal-apps`
8. `astal-auth`
9. `astal-battery`
10. `astal-bluetooth`
11. `astal-greet`
12. `astal-mpris`
13. `astal-network`
14. `astal-quarrel`
15. `astal-notifd`
16. `astal-power-profiles`
17. `astal-wireplumber`
18. `appmenu-glib-translator`
19. `wl-vapi-gen`
20. `libcava`
21. `astal-wl`
22. `astal-tray`
23. `astal-river`
24. `astal-cava`

## Font packaging specifics

- Use the Fedora font macros (`%fontpkg`, `%fontbuild`, `%fontinstall`,
  `%fontcheck`, `%fontfiles`) rather than staging font files by hand. Let the
  macros generate `Name:`, the per-family subpackages and the appstream
  metainfo.
- One subpackage per upstream *font family*. Two builds that share a family name
  (a variable and a static cut of the same font, or TTF and OTF encodings) are
  alternate encodings of one family, not two packages — pick one, otherwise
  fontconfig ends up with duplicate families.
- Do not reference `%{name}` above `%fontpkg`. The macros only emit `Name:` at
  that point, so `%{name}` is unset earlier in the file. A standalone
  `rpmspec -P` hides this because rpm expands source lines late, but
  `scripts/check-specs.sh` passes every spec to one `rpmlint` invocation sharing
  a single rpm macro context, where an earlier spec's `Name:` leaks in.
- Check the generated package names before trusting them. `%fontpkgname<N>`
  derives from the family name using the "WPF font selection model"
  simplifications, which strip trailing weight, width, slant and `normal`
  tokens; families that differ only by such a token collapse onto the same RPM
  name and need an explicit `%global fontpkgname<N>` override. `Maple Mono
  Normal` versus `Maple Mono` is the worked example in the repo.
- Split source packages along whichever axis drives download size, not along
  every axis upstream offers. The Maple Mono set keeps its four feature cuts as
  subpackages of one spec but splits the glyph-set axis across four source
  packages, so rebuilding the 4 MB cuts does not drag the 140 MB CJK assets
  along.
- Prefer release assets over repacked tarballs when upstream publishes usable
  ones. If the asset filename has no version in it, append a `#/` fragment to
  the `Source` URL so the locally cached copy is versioned; `spectool` skips
  files that already exist, so an unversioned name silently survives a bump.

## What to avoid (fresh-start guardrails)

- Large top-level flat directories for dozens of unrelated packages
- Package-specific CI logic hardcoded in a shared COPR Makefile
- Hidden update scripts with no documented trigger or version policy
- Mixing stable and snapshot semantics in one spec without clear macros
