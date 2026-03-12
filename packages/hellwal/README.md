# hellwal

Fedora RPM packaging for `hellwal`.

Current packaging target:

- upstream release `1.0.7` from `danihek/hellwal`
- lightweight C-based wallpaper color palette generator
- ships upstream templates/themes under `/usr/share/hellwal`
- carries a small downstream fallback patch so packaged templates/themes work
  without first copying them into `~/.config/hellwal`
