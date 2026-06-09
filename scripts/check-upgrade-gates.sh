#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/check-upgrade-gates.sh [--base-ref <ref>]

Runs the fast local gates that should pass before committing/pushing a package
upgrade. The ABI gate compares <ref> against the current working tree so it
catches uncommitted consumer rebuild misses.

Defaults:
  --base-ref  UPGRADE_BASE_REF, ABI_REBUILD_BASE, or origin/main
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
base_ref="${UPGRADE_BASE_REF:-${ABI_REBUILD_BASE:-origin/main}}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-ref)
      base_ref="${2:-}"
      [[ -n "${base_ref}" ]] || { echo "--base-ref requires a value" >&2; exit 1; }
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

cd "${repo_root}"

if ! git rev-parse --verify "${base_ref}^{commit}" >/dev/null 2>&1; then
  echo "Base ref not found: ${base_ref}" >&2
  echo "Fetch it first or pass --base-ref <ref>." >&2
  exit 1
fi

./scripts/check-specs.sh
./scripts/check-abi-rebuilds.sh --base-ref "${base_ref}" --head-ref WORKTREE
