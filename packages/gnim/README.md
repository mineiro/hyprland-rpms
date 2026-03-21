# gnim

Fedora RPM packaging for `gnim`.

Current packaging target:

- upstream release `1.9.0` from `Aylur/gnim`
- source payload comes from the published npm tarball for the same version
- installs under `%{_datadir}/ags/js/node_modules/gnim` because AGS `3.1.x`
  still expects the npm-style runtime tree
- local validation passes via SRPM generation plus Fedora 43/44/rawhide
  x86_64 `mock --chain` with the imported Astal/AGS stack
