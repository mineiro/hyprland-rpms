# aquamarine

Fedora RPM packaging for `aquamarine`.

Current packaging target:

- upstream release `0.12.1` from `hyprwm/aquamarine`
- core Hyprland rendering backend library
- exports a versioned shared library, so in-repo pkgconfig consumers must be
  rebuilt when its version changes
