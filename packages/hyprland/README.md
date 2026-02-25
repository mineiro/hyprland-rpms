# hyprland (starter package)

This directory contains the Fedora RPM packaging for stable `hyprland`.

Notes:

- Start from the Fedora dist-git spec or SRPM when available, then compare against `solopasha/hyprlandRPM` for recent dependency updates/macros.
- Keep `hyprland` and `hyprland-git` separate specs if you decide to ship both.
- Expect synchronized updates with `hypr*` libraries and `aquamarine`.

Before first COPR build, verify:

1. `Version` and `Source0`
2. `BuildRequires` match current upstream build system
3. `%files` reflects actual installed paths
4. Package builds in Fedora 43/44 mock chroots

