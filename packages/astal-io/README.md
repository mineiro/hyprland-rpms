# astal-io

Fedora RPM packaging for `astal-io` from the `Aylur/astal` monorepo.

Current packaging target:

- pinned upstream snapshot commit `41b5029` (`snapshot_date 20260319`)
- runtime keeps `AstalIO-0.1.gir` alongside the typelib so `ags init` can
  generate types
- local validation passes via SRPM generation plus Fedora 43/44/rawhide
  x86_64 `mock --chain` with `gnim`, `astal3`, `astal4`, `astal-hyprland`,
  and `aylurs-gtk-shell`
