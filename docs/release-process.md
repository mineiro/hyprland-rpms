# Release Process

## Manual update flow (recommended first)

1. Update the package spec (`Version`, `Source`, dependency floors, patches)
2. Build SRPM locally:
   - `make srpm PACKAGE=<name>`
3. Build in `mock` for Fedora 43/44:
   - `mock -r fedora-43-x86_64 --rebuild dist/srpm/<file>.src.rpm`
   - `mock -r fedora-44-x86_64 --rebuild dist/srpm/<file>.src.rpm`
4. Commit changes
5. Push to your packaging repo
6. Trigger COPR build (manual or webhook)
7. Run repoclosure checks on the COPR project

## Automation later

After the package is stable, add automation for version bumps:

- Option A: GitHub Actions + release polling
- Option B: Packit `copr_build` on upstream release events

Keep automation package-specific. Avoid one script that mutates many specs without validation.

