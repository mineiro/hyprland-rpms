# hyprpaper

Starter packaging directory for `hyprpaper` in this monorepo.

Current status:
- starter spec added (adapted from the `solopasha/hyprlandRPM` baseline)
- tracked at the latest upstream release (`0.8.3`)
- depends on `hyprtoolkit` (`0.8.x` dependency path)
- validate via `mock --chain` (local `hyprtoolkit` + `hyprpaper`) until
  `hyprtoolkit` is published in COPR, then re-run clean `mock --rebuild`
