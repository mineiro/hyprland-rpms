#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/check-abi-rebuilds.sh [--base-ref <ref>] [--head-ref <ref>]

Checks that version bumps for in-repo packages shipping versioned shared
libraries or exact pkgconfig ABI locks also rebuild their in-repo consumers in
the same change.

Defaults:
  --base-ref  ABI_REBUILD_BASE or HEAD~1
  --head-ref  ABI_REBUILD_HEAD or HEAD

Use `--head-ref WORKTREE` to compare a commit against the current working tree,
including uncommitted tracked spec changes.
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

git config --global --add safe.directory "${repo_root}" >/dev/null 2>&1 || true

git rev-parse --verify "${base_ref}^{commit}" >/dev/null
if [[ "${head_ref}" != "WORKTREE" ]]; then
  git rev-parse --verify "${head_ref}^{commit}" >/dev/null
fi

spec_contents() {
  local ref="$1"
  local path="$2"

  if [[ "${ref}" == "WORKTREE" ]]; then
    cat "${path}" 2>/dev/null
  else
    git show "${ref}:${path}" 2>/dev/null
  fi
}

spec_field() {
  local ref="$1"
  local path="$2"
  local field="$3"

  spec_contents "${ref}" "${path}" \
    | awk -v key="${field}:" '$1 == key { sub(/^[^:]+:[[:space:]]*/, ""); print; exit }'
}

spec_exports_versioned_shared_library() {
  local ref="$1"
  local path="$2"

  spec_contents "${ref}" "${path}" \
    | grep -Ev '^[[:space:]]*#' \
    | grep -Eq '\.so\.\*'
}

spec_uses_pkgconfig() {
  local ref="$1"
  local path="$2"
  local provider="$3"

  spec_contents "${ref}" "${path}" \
    | grep -Ev '^[[:space:]]*#' \
    | grep -Eq "^(BuildRequires|Requires):[[:space:]].*pkgconfig\\(${provider}\\)([[:space:]]|$|[<>=])"
}

spec_buildrequires() {
  local ref="$1"
  local path="$2"
  local tmp=""

  if [[ "${ref}" == "WORKTREE" ]]; then
    rpmspec -q --buildrequires "${path}" 2>/dev/null || true
    return
  fi

  tmp="$(mktemp)"
  if spec_contents "${ref}" "${path}" > "${tmp}"; then
    rpmspec -q --buildrequires "${tmp}" 2>/dev/null || true
  fi
  rm -f "${tmp}"
}

spec_exact_pkgconfig_requirement_version() {
  local ref="$1"
  local path="$2"
  local provider="$3"

  spec_buildrequires "${ref}" "${path}" \
    | awk -v dep="pkgconfig(${provider})" '$1 == dep && $2 == "=" { print $3; exit }'
}

package_from_path() {
  local path="$1"
  path="${path#packages/}"
  printf '%s\n' "${path%%/*}"
}

if [[ "${head_ref}" == "WORKTREE" ]]; then
  mapfile -t changed_specs < <(
    {
      git diff --name-only "${base_ref}" -- 'packages/*/*.spec'
      git ls-files --others --exclude-standard -- 'packages/*/*.spec'
    } | sort -u
  )
else
  mapfile -t changed_specs < <(
    git diff --name-only "${base_ref}" "${head_ref}" -- 'packages/*/*.spec' | sort
  )
fi

if [[ ${#changed_specs[@]} -eq 0 ]]; then
  echo "No changed specs between ${base_ref} and ${head_ref}; ABI rebuild check skipped."
  exit 0
fi

declare -A changed_by_package=()
for spec in "${changed_specs[@]}"; do
  changed_by_package["$(package_from_path "${spec}")"]="${spec}"
done

if [[ "${head_ref}" == "WORKTREE" ]]; then
  mapfile -t head_specs < <(
    find packages -mindepth 2 -maxdepth 2 -type f -name '*.spec' | sort
  )
else
  mapfile -t head_specs < <(
    git ls-tree -r --name-only "${head_ref}" -- packages \
      | grep -E '^packages/[^/]+/[^/]+\.spec$' \
      | sort
  )
fi

failures=0

for provider_spec in "${changed_specs[@]}"; do
  provider="$(package_from_path "${provider_spec}")"
  old_version="$(spec_field "${base_ref}" "${provider_spec}" Version || true)"
  new_version="$(spec_field "${head_ref}" "${provider_spec}" Version || true)"

  [[ -n "${old_version}" && -n "${new_version}" ]] || continue
  [[ "${old_version}" != "${new_version}" ]] || continue

  if spec_exports_versioned_shared_library "${head_ref}" "${provider_spec}"; then
    declare -a consumers=()
    for spec in "${head_specs[@]}"; do
      consumer="$(package_from_path "${spec}")"
      [[ "${consumer}" != "${provider}" ]] || continue
      if spec_uses_pkgconfig "${head_ref}" "${spec}" "${provider}"; then
        consumers+=("${consumer}:${spec}")
      fi
    done

    if [[ ${#consumers[@]} -gt 0 ]]; then
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
    fi
  fi

  declare -a exact_consumers=()
  for spec in "${head_specs[@]}"; do
    consumer="$(package_from_path "${spec}")"
    [[ "${consumer}" != "${provider}" ]] || continue
    exact_version="$(spec_exact_pkgconfig_requirement_version "${head_ref}" "${spec}" "${provider}" || true)"
    if [[ -n "${exact_version}" ]]; then
      exact_consumers+=("${consumer}:${spec}:${exact_version}")
    fi
  done

  [[ ${#exact_consumers[@]} -gt 0 ]] || continue

  echo "Exact pkgconfig ABI provider changed: ${provider} ${old_version} -> ${new_version}"
  echo "  In-repo consumers with pkgconfig(${provider}) = <version> must track the new provider version and rebuild."

  for entry in "${exact_consumers[@]}"; do
    consumer="${entry%%:*}"
    rest="${entry#*:}"
    consumer_spec="${rest%%:*}"
    exact_version="${rest#*:}"

    if [[ "${exact_version}" != "${new_version}" ]]; then
      echo "  ERROR: ${consumer} requires pkgconfig(${provider}) = ${exact_version}, expected ${new_version}."
      failures=1
    fi

    if [[ -z "${changed_by_package[${consumer}]:-}" ]]; then
      echo "  ERROR: ${consumer} has an exact pkgconfig(${provider}) ABI lock but was not rebuilt in this change."
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
      echo "  OK: ${consumer} exact ABI lock covered (${old_consumer_version}-${old_consumer_release} -> ${new_consumer_version}-${new_consumer_release})"
    fi
  done
done

if [[ ${failures} -ne 0 ]]; then
  cat <<'EOF'

ABI rebuild coverage failed.
When a shared-library provider version or exact pkgconfig ABI lock changes,
rebuild its in-repo consumers in the same change. For same-upstream-version
consumers, bump the Release base so COPR publishes a newer RPM that links
against the new ABI target.

For local upgrade worktrees before commit/push, run:
  ./scripts/check-abi-rebuilds.sh --base-ref origin/main --head-ref WORKTREE
EOF
  exit 1
fi

echo "ABI rebuild coverage check passed."
