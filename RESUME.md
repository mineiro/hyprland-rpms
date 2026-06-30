# RESUME.md

Use this file to quickly restart work in a new Codex session.

## Start here

From a terminal:

```bash
cd ~/Code/hyprland-rpms
```

Then start Codex from this directory and paste one of the prompts below.

## Default resume prompt (recommended)

```text
Read `AGENTS.md`, `README.md`, `docs/release-process.md`, and `docs/packaging-policy.md`, then continue from the latest handoff / next step in `AGENTS.md`. Update `AGENTS.md` as you make progress.
```

## Resume routine maintenance

```text
Read `AGENTS.md` and `docs/release-process.md`. Run `./scripts/check-upstream-versions.sh --changed-only`, apply the maintenance batch playbook, validate with `make check-upgrade UPGRADE_BASE_REF=origin/main` plus a focused mock matrix, then commit/push and trigger COPR in dependency order if all gates pass.
```

## Resume and scaffold next foundational packages

```text
Read `AGENTS.md` and continue the Hypr stack bootstrap. Scaffold the next foundational package directories from the package matrix using `scripts/new-package.sh`, and update the matrix statuses in `AGENTS.md`.
```

## Resume and make a specific package buildable

Replace `<pkg>` with the package name.

```text
Read `AGENTS.md` and focus on `packages/<pkg>`. Make the spec buildable as an SRPM locally, run `make check-specs`, and update the package matrix in `AGENTS.md` with the new status and notes.
```

## Resume and debug a mock build failure

```text
Read `AGENTS.md`, inspect the current package matrix notes, then debug the latest mock build failure for `<pkg>` on Fedora `<43|44|rawhide>`. Patch the spec, rerun validation, and update `AGENTS.md`.
```

## Resume and onboard packages to COPR

```text
Read `AGENTS.md` and `docs/copr-setup.md`. Prepare the next package(s) for COPR SCM onboarding (subdirectory/spec settings), generate the onboarding checklist output, and update the matrix columns for COPR package entry/build status.
```

## Resume and add automation later

```text
Read `AGENTS.md` and `docs/release-process.md`. Propose and implement a minimal automation workflow for upstream version bump detection for one package only, then document it and update `AGENTS.md`.
```

## Session hygiene (important)

- Always read `AGENTS.md` first.
- For update batches, follow `docs/release-process.md` before triggering COPR.
- Update `AGENTS.md` after meaningful progress (status changes, blockers, next steps).
- Keep package changes isolated to `packages/<name>/`.
- Run:

```bash
make check-specs
```

before finishing a session.
