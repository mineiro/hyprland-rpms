# hyprpaper

Starter packaging directory for `hyprpaper` in this monorepo.

Current status:
- starter spec added (adapted from the `solopasha/hyprlandRPM` baseline)
- version pinned to `0.7.6` for compatibility with the current Hyprland `0.53.x`
  packaging stack in this repo (`0.8.x` requires `hyprtoolkit` and newer
  Hyprgraphics APIs)
- local SRPM + clean `mock --rebuild` pass on Fedora 43/44/rawhide against the
  `mineiro/hyprland` COPR dependency stack
