# libcava

Fedora RPM packaging for the CAVA shared library.

Current packaging target:

- upstream tag `0.10.7`
- builds the shared library only, with optional input/output backends disabled
- stages upstream embedded config/shader asset paths into the Meson build dir
- used as the system dependency for `astal-cava`
