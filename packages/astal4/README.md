# astal4

Fedora RPM packaging for the Astal GTK4 widget library.

Current packaging target:

- pinned `Aylur/astal` snapshot commit `41b5029` (`snapshot_date 20260319`)
- runtime keeps `Astal-4.0.gir` alongside the typelib so AGS can type-generate
  against it
- build/runtime stack depends on `astal-io`
- local validation passes via SRPM generation plus Fedora 43/44/rawhide
  x86_64 `mock --chain`
