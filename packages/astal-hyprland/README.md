# astal-hyprland

Fedora RPM packaging for Astal's Hyprland IPC bindings.

Current packaging target:

- pinned `Aylur/astal` snapshot commit `41b5029` (`snapshot_date 20260319`)
- optional for AGS itself, but required for Hyprland-aware widgets
- runtime keeps `AstalHyprland-0.1.gir` alongside the typelib so AGS can
  type-generate against it
- local validation passes via SRPM generation plus Fedora 43/44/rawhide
  x86_64 `mock --chain`
