# hyprls

Fedora RPM packaging for `hyprls`.

Current packaging target:

- upstream release `0.13.0` from `hyprland-community/hyprls`
- Go-based Hyprland configuration language server
- uses vendored Go modules (`Source1`) for offline mock/COPR-style builds

Build note:

- Regenerate `sources/hyprls-0.13.0-vendor.tar.gz` from upstream source with
  `go mod vendor` before SRPM/mock builds when dependencies change.
