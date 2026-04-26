#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/check-abi-rebuilds.sh [--base-ref <ref>] [--head-ref <ref>]

Checks that version bumps for in-repo packages shipping versioned shared
libraries also rebuild their in-repo pkgconfig consumers in the same change.

Defaults:
  --base-ref  ABI_REBUILD_BASE or HEAD~1
  --head-ref  ABI_REBUILD_HEAD or HEAD
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
base_ref="${ABI_REBUILD_BASE:-}"
head_ref="${ABI_REBUILD_HEAD:-HEAD}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-ref)
      base_ref="${2:-}"
      [[ -n "${base_ref}" ]] || { echo "--base-ref requires a value" >&2; exit 1; }
      shift 2
      ;;
    --head-ref)
      head_ref="${2:-}"
      [[ -n "${head_ref}" ]] || { echo "--head-ref requires a value" >&2; exit 1; }
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

if [[ -z "${base_ref}" ]]; then
  base_ref="HEAD~1"
fi

cd "${repo_root}"

git rev-parse --verify "${base_ref}^{commit}" >/dev/null
git rev-parse --verify "${head_ref}^{commit}" >/dev/null

spec_field() {
  local ref="$1"
  local path="$2"
  local field="$3"

  git show "${ref}:${path}" 2>/dev/null \
    | awk -v key="${field}:" '$1 == key { sub(/^[^:]+:[[:space:]]*/, ""); print; exit }'
}

spec_exports_versioned_shared_library() {
  local ref="$1"
  local path="$2"

  git show "${ref}:${path}" 2>/dev/null \
    | grep -Ev '^[[:space:]]*#' \
    | grep -Eq '\.so\.\*'
}

spec_uses_pkgconfig() {
  local ref="$1"
  local path="$2"
  local provider="$3"

  git show "${ref}:${path}" 2>/dev/null \
    | grep -Ev '^[[:space:]]*#' \
    | grep -Eq "^(BuildRequires|Requires):[[:space:]].*pkgconfig\\(${provider}\\)([[:space:]]|$|[<>=])"
}

package_from_path() {
  local path="$1"
  path="${path#packages/}"
  printf '%s\n' "${path%%/*}"
}

mapfile -t changed_specs < <(
  git diff --name-only "${base_ref}" "${head_ref}" -- 'packages/*/*.spec' | sort
)

if [[ ${#changed_specs[@]} -eq 0 ]]; then
  echo "No changed specs between ${base_ref} and ${head_ref}; ABI rebuild check skipped."
  exit 0
fi

declare -A changed_by_package=()
for spec in "${changed_specs[@]}"; do
  changed_by_package["$(package_from_path "${spec}")"]="${spec}"
done

mapfile -t head_specs < <(
  git ls-tree -r --name-only "${head_ref}" -- packages \
    | grep -E '^packages/[^/]+/[^/]+\.spec$' \
    | sort
)

failures=0

for provider_spec in "${changed_specs[@]}"; do
  provider="$(package_from_path "${provider_spec}")"
  old_version="$(spec_field "${base_ref}" "${provider_spec}" Version || true)"
  new_version="$(spec_field "${head_ref}" "${provider_spec}" Version || true)"

  [[ -n "${old_version}" && -n "${new_version}" ]] || continue
  [[ "${old_version}" != "${new_version}" ]] || continue
  spec_exports_versioned_shared_library "${head_ref}" "${provider_spec}" || continue

  declare -a consumers=()
  for spec in "${head_specs[@]}"; do
    consumer="$(package_from_path "${spec}")"
    [[ "${consumer}" != "${provider}" ]] || continue
    if spec_uses_pkgconfig "${head_ref}" "${spec}" "${provider}"; then
      consumers+=("${consumer}:${spec}")
    fi
  done

  [[ ${#consumers[@]} -gt 0 ]] || continue

  echo "ABI provider changed: ${provider} ${old_version} -> ${new_version}"
  echo "  ${provider_spec} ships versioned shared libraries and has in-repo pkgconfig consumers."

  for entry in "${consumers[@]}"; do
    consumer="${entry%%:*}"
    consumer_spec="${entry#*:}"

    if [[ -z "${changed_by_package[${consumer}]:-}" ]]; then
      echo "  ERROR: ${consumer} consumes pkgconfig(${provider}) but was not rebuilt in this change."
      failures=1
      continue
    fi

    old_consumer_version="$(spec_field "${base_ref}" "${consumer_spec}" Version || true)"
    new_consumer_version="$(spec_field "${head_ref}" "${consumer_spec}" Version || true)"
    old_consumer_release="$(spec_field "${base_ref}" "${consumer_spec}" Release || true)"
    new_consumer_release="$(spec_field "${head_ref}" "${consumer_spec}" Release || true)"

    if [[ "${old_consumer_version}" == "${new_consumer_version}" \
      && "${old_consumer_release}" == "${new_consumer_release}" ]]; then
      echo "  ERROR: ${consumer} changed but kept the same Version/Release; bump Release for the rebuild."
      failures=1
    else
      echo "  OK: ${consumer} rebuild covered (${old_consumer_version}-${old_consumer_release} -> ${new_consumer_version}-${new_consumer_release})"
    fi
  done
done

if [[ ${failures} -ne 0 ]]; then
  cat <<'EOF'

ABI rebuild coverage failed.
When a shared-library provider version changes, rebuild its in-repo consumers
in the same change. For same-upstream-version consumers, bump the Release base
so COPR publishes a newer RPM that links against the new soname.
EOF
  exit 1
fi

echo "ABI rebuild coverage check passed."
