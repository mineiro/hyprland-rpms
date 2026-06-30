# COPR Setup

This repo is designed for COPR `SCM` package entries (one entry per package directory).

## Recommended COPR project layout

- COPR project name: `hyprwm` (or `hyprland`)
- Chroots:
  - `fedora-43-x86_64`
  - `fedora-44-x86_64`
  - `fedora-rawhide-x86_64`
  - `fedora-43-aarch64`
  - `fedora-44-aarch64`
  - `fedora-rawhide-aarch64`

If x86_64 builds are already stable and you are only rolling out aarch64,
trigger builds with explicit aarch64 chroots only:

```bash
copr-cli build-package <owner>/<project> --name <pkg> \
  -r fedora-43-aarch64 -r fedora-44-aarch64 -r fedora-rawhide-aarch64
```

If the package depends on another COPR package that is also being rolled out to
those chroots, build the dependency first and wait until it is published before
triggering the dependent package. This also applies to `BuildArch: noarch`
packages, because COPR still resolves `BuildRequires` inside each target
chroot.

## Add a package from this monorepo (SCM)

For each package directory:

- `Clone URL`: your Git repo URL
- `Committish`: `main`
- `Subdirectory`: `packages/<pkgname>`
- `Spec file`: `<pkgname>.spec`
- `Build source type`: `SCM`
- `Build SRPM with`: `make_srpm`

The shared `.copr/Makefile` handles SRPM generation inside COPR.

## Webhooks / auto rebuilds

Enable webhook rebuilds only after manual builds pass.

Recommended sequence:

1. Create package entry
2. Trigger one manual build
3. Verify dependency closure in COPR
4. Enable webhook + auto-rebuild on push/tag

For dependent package stacks, expand step 2 into a dependency-first sequence:

1. Trigger the leaf dependency build first
2. Wait for the target chroots to publish successfully
3. Trigger dependent packages afterward
4. Use explicit ordering rather than submitting the whole stack in parallel

## Maintenance batch ordering

For routine maintenance batches, do not submit the whole changed set as one
parallel group. Use COPR build ordering to preserve ABI and repository metadata
sequencing.

Recommended pattern:

1. Trigger independent leaf/support packages together:

   ```bash
   first="$(copr-cli build-package mineiro/hyprland --nowait --name app2unit | awk '/Created builds:/ { print $3 }')"
   copr-cli build-package mineiro/hyprland --nowait --with-build-id "$first" --name caelestia-cli
   copr-cli build-package mineiro/hyprland --nowait --with-build-id "$first" --name dart-sass
   copr-cli build-package mineiro/hyprland --nowait --with-build-id "$first" --name swayosd
   copr-cli build-package mineiro/hyprland --nowait --with-build-id "$first" --name uwsm
   ```

2. Trigger ABI/header providers together:

   ```bash
   provider="$(copr-cli build-package mineiro/hyprland --nowait --name aquamarine | awk '/Created builds:/ { print $3 }')"
   copr-cli build-package mineiro/hyprland --nowait --with-build-id "$provider" --name glaze
   ```

3. Queue consumers after providers:

   ```bash
   copr-cli build-package mineiro/hyprland --nowait --after-build-id "$provider" --name hyprtoolkit
   hyprland_build="$(copr-cli build-package mineiro/hyprland --nowait --after-build-id "$provider" --name hyprland | awk '/Created builds:/ { print $3 }')"
   copr-cli build-package mineiro/hyprland --nowait --after-build-id "$hyprland_build" --name hyprland-plugins
   ```

4. Watch all returned build IDs:

   ```bash
   copr-cli watch-build <build-id>...
   ```

Record the final build IDs in `AGENTS.md` so the next agent knows which COPR
publish completed and which validation gates remain.

## Notes on auto-updating versions

COPR can rebuild on webhook events, but it does not update spec versions on its own.

Use a separate automation layer (for example GitHub Actions or Packit) to:

1. Detect upstream releases/tags
2. Update `Version` / `Source` / patches in your spec
3. Commit or tag this packaging repo
4. Let COPR rebuild from webhook
