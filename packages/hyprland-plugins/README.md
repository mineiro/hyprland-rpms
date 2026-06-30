# hyprland-plugins

Fedora RPM packaging for `hyprland-plugins` (official Hyprland plugin bundle).

Current packaging target:

- upstream tag `v0.55.0` (compatible plugin family for the active Hyprland
  `0.55.x` stack)
- RPM release rebuilds track the exact packaged Hyprland patch release through
  `%{hyprland_target_version}`

Current repository policy:

- Hyprland is currently shipped at `0.55.4`.
- Do not move to a different plugin source tag unless upstream publishes a
  compatible tag for the target Hyprland family.
- For later Hyprland `0.55.x` patch releases, keep `Version: 0.55.0`, update
  `%{hyprland_target_version}`, bump `Release`, and rebuild after the Hyprland
  COPR build succeeds.
