# hyprtoolkit

Fedora RPM packaging for `hyprtoolkit`.

Current packaging target:

- upstream release `0.6.0` from `hyprwm/hyprtoolkit`
- Wayland GUI toolkit used by Hyprland utilities and Hyprpolkitagent
- builds against Hyprutils `>= 0.14.2` and the Aquamarine `0.15.0` stack
- exports `libhyprtoolkit.so.6`; in-repo consumers need a release rebuild
  when moving from the `0.5.x` ABI
- local SRPM/mock/COPR validation tracked in `AGENTS.md`
