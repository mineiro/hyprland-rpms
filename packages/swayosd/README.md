# swayosd

Fedora RPM packaging for `swayosd` (https://github.com/ErikReider/SwayOSD).

Current packaging target:

- upstream release `0.3.2`
- Rust/Meson OSD service with vendored `Source1` Rust dependencies

Local validation status:

- `make srpm PACKAGE=swayosd`: pass
- `./scripts/mock-matrix-build.sh --arch x86_64 swayosd`: pass on Fedora 43/44/rawhide

Notes:

- Rust dependencies are vendored into `Source1` during SRPM creation so mock/COPR
  builds can run offline.
