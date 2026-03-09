# cliphist

Fedora RPM packaging for `cliphist`.

Current packaging target:

- upstream release `0.7.0` from `sentriz/cliphist`
- Go-based Wayland clipboard history manager with text and image support
- uses vendored Go modules (`Source1`) for offline mock/COPR-style builds

Build note:

- Regenerate `sources/cliphist-0.7.0-vendor.tar.gz` from upstream source with
  `go mod vendor` before SRPM/mock builds when dependencies change.
