# aylurs-gtk-shell

Fedora RPM packaging for `ags`.

Naming note:

- upstream project name remains `ags`
- installed command remains `ags`
- RPM package name is `aylurs-gtk-shell` to avoid collision with Fedora's unrelated `ags` package

Current packaging target:

- upstream release `v3.1.2`
- `meson.build` installs `node_modules/gnim`, but the release tarball does not contain that path
- `LICENSE` is GPLv3 while `package.json` says `LGPL-2.1`
- local validation passes via SRPM generation plus Fedora 43/44/rawhide
  x86_64 `mock --chain` with `gnim`, `astal-io`, `astal3`, `astal4`,
  and `astal-hyprland`

Packaging notes:

- package `gnim` separately
- package the required Astal runtime stack separately (`astal-io`, `astal3`, `astal4`)
- install it in the AGS runtime path `%{_datadir}/ags/js/node_modules/gnim`
- pull in a provider for `/usr/bin/sass`, because AGS compiles `.scss` by shelling out to `sass`
- carry a small meson patch so AGS stops trying to install vendored `gnim`
- carry a small types patch so `ags init` and `ags types` stop scanning every GIR installed on the system
- keep using Fedora's `nodejs-npm` for `/usr/bin/npx`

Current patches:

- `patches/0001-meson-stop-installing-vendored-gnim.patch`
- `patches/0002-types-skip-empty-extra-gir-dirs.patch`
- `patches/0003-types-prefer-fedora-npx.patch`
- `patches/0004-types-limit-default-modules.patch`

Remaining known issue:

- `ags init` still fetches `@ts-for-gir/cli` at runtime through `npx`
- the package build itself is offline-capable now, but a fully offline
  `ags init` / `ags types` experience still needs `@ts-for-gir/cli` packaged
  or vendored

Next packaging step:

- package `@ts-for-gir/cli` as its own RPM instead of fetching it at runtime
- then decide whether AGS should `Require`, `Recommend`, or split out a scaffold/devel helper for type generation
