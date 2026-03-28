# satty

Fedora RPM packaging for `satty`.

Current packaging target:

- upstream release `0.20.1` from `Satty-org/Satty`
- GTK4/libadwaita screenshot annotation tool for Wayland workflows

Notes:

- Rust dependencies are vendored into `Source1` during SRPM creation so
  mock/COPR builds can run offline.
