# astal-quarrel

Fedora RPM packaging for Astal's Quarrel command-line option helper library.

Current packaging target:

- pinned `Aylur/astal` snapshot commit `67ddc83` (`snapshot_date 20260430`)
- provides the `Quarrel-0.1` GIR/typelib and shared library
- introduced upstream after the previous Astal snapshot and kept split so
  Astal consumers only pull it when they need it
