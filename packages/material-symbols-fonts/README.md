# material-symbols-fonts

Fedora RPM packaging for `material-symbols-fonts`.

Current packaging target:

- upstream snapshot `20260327` from `google/material-design-icons` `master`
- Google Material Symbols variable TTF fonts (`Outlined`, `Rounded`, `Sharp`)

Notes:

- upstream's classic `Material Icons` fonts remain frozen on the old `4.0.0`
  line; this package tracks the newer actively updated `Material Symbols` set
- the RPM intentionally ships the desktop-relevant TTF variable fonts, not the
  upstream webfont `woff2` payload
- `Source0` is repacked locally from the upstream `master` snapshot so the SRPM
  only carries the installable fonts plus license and documentation files,
  without downloading the full upstream asset tree during SRPM creation
- the three families stay in one package because upstream publishes them as
  one closely coupled icon set, similar to Fedora's existing
  `material-icons-fonts` style bundle
