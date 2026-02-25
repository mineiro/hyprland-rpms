#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/copr-onboard-checklist.sh <copr-owner> <copr-project> <git-clone-url> <package-name>

This prints the recommended COPR SCM settings for a package in this monorepo.
Verify exact copr-cli flags with:
  copr-cli add-package-scm --help
EOF
}

if [[ $# -ne 4 ]]; then
  usage
  exit 1
fi

owner="$1"
project="$2"
clone_url="$3"
pkg="$4"

cat <<EOF
COPR package onboarding checklist
================================
COPR project: ${owner}/${project}
Package name: ${pkg}
Clone URL:    ${clone_url}
Committish:   main
Subdirectory: packages/${pkg}
Spec file:    ${pkg}.spec
Source type:  SCM
SRPM method:  make_srpm

Web UI fields:
- Clone URL      = ${clone_url}
- Committish     = main
- Subdirectory   = packages/${pkg}
- Spec File      = ${pkg}.spec
- Build Source   = SCM
- Build SRPM with= make_srpm

Suggested first step:
- Add package entry with auto-rebuild disabled
- Run one manual build for Fedora 43/44
- Enable webhook after success
EOF

