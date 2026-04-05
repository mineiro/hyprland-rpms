#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/check-upstream-versions.sh [--changed-only] [--package <name>]

Options:
  --changed-only       show only rows where local != upstream or source check != ok
  --package <name>     check only one package directory under packages/
  -h, --help           show this help

Status values:
  same                 local version equals upstream version
  different            local version differs from upstream version
  snapshot             local version is a VCS snapshot or pinned commit ahead of the latest stable tag
  manual               upstream version check is intentionally skipped for this package
  unknown              upstream version could not be determined
EOF
}

changed_only=0
package_filter=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --changed-only)
      changed_only=1
      shift
      ;;
    --package)
      package_filter="${2:-}"
      if [[ -z "${package_filter}" ]]; then
        echo "--package requires a value"
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git not found"
  exit 1
fi

if ! command -v rpmspec >/dev/null 2>&1; then
  echo "rpmspec not found"
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

declare -A git_versions_cache

if [[ -n "${package_filter}" ]]; then
  env_files=("${repo_root}/packages/${package_filter}/package.env")
else
  mapfile -t env_files < <(find "${repo_root}/packages" -mindepth 2 -maxdepth 2 -type f -name package.env | sort)
fi

if [[ ${#env_files[@]} -eq 0 ]]; then
  echo "No package.env files found under packages/"
  exit 1
fi

if [[ -n "${package_filter}" && ! -f "${env_files[0]}" ]]; then
  echo "Package not found: ${package_filter}"
  exit 1
fi

curl_ok() {
  local url="$1"

  if curl -fsSLI --connect-timeout 5 --max-time 15 "${url}" >/dev/null 2>&1; then
    return 0
  fi

  curl -fsSL --connect-timeout 5 --max-time 15 --range 0-0 "${url}" -o /dev/null >/dev/null 2>&1
}

check_source_url() {
  local source_url="$1"

  if [[ -z "${source_url}" || ! "${source_url}" =~ ^https?:// ]]; then
    printf '%s\n' "n/a"
    return 0
  fi

  if curl_ok "${source_url}"; then
    printf '%s\n' "ok"
    return 0
  fi

  printf '%s\n' "missing"
}

fetch_git_versions() {
  local upstream_git="$1"
  local cached versions

  cached="${git_versions_cache["${upstream_git}"]+set}"
  if [[ "${cached}" == "set" ]]; then
    printf '%s\n' "${git_versions_cache["${upstream_git}"]}"
    return 0
  fi

  versions="$(
    git ls-remote --tags --refs "${upstream_git}" 2>/dev/null \
      | awk -F/ '{print $NF}' \
      | grep -E '^[vV]?[0-9]+(\.[0-9]+){1,3}([._-][0-9A-Za-z.-]+)?$' \
      | sed -E 's/^[vV]//' \
      | sort -uV
  )"

  git_versions_cache["${upstream_git}"]="${versions}"
  printf '%s\n' "${versions}"
}

is_prerelease_version() {
  local version="$1"

  [[ "${version}" =~ (^|[._-])(alpha|beta|pre|preview|rc)([._-]?[0-9A-Za-z.-]*)?$ ]]
}

fetch_latest_tag_from_git() {
  local upstream_git="$1"
  local versions stable latest

  versions="$(fetch_git_versions "${upstream_git}")"
  if [[ -z "${versions}" ]]; then
    return 0
  fi

  stable="$(printf '%s\n' "${versions}" | while IFS= read -r version; do
    [[ -z "${version}" ]] && continue
    if ! is_prerelease_version "${version}"; then
      printf '%s\n' "${version}"
    fi
  done | tail -n1)"
  if [[ -n "${stable}" ]]; then
    printf '%s\n' "${stable}"
    return 0
  fi

  latest="$(printf '%s\n' "${versions}" | tail -n1)"
  printf '%s\n' "${latest}"
}

fetch_pypi_latest_version() {
  local dist="$1"
  local json

  json="$(curl -fsSL "https://pypi.org/pypi/${dist}/json" 2>/dev/null || true)"
  jq -r '.info.version // empty' <<<"${json}" 2>/dev/null || true
}

fetch_npm_latest_version() {
  local pkg="$1"
  local json

  json="$(curl -fsSL "https://registry.npmjs.org/${pkg}/latest" 2>/dev/null || true)"
  jq -r '.version // empty' <<<"${json}" 2>/dev/null || true
}

get_source_url() {
  local spec_path="$1"
  local source_url

  source_url="$(
    rpmspec --define '_tmppath /tmp' -P "${spec_path}" 2>/dev/null \
      | awk '/^Source([0-9]*)?:[[:space:]]*/ {print $2; exit}'
  )"

  if [[ -z "${source_url}" ]]; then
    source_url="$(awk '/^Source([0-9]*)?:[[:space:]]*/ {print $2; exit}' "${spec_path}")"
  fi

  printf '%s\n' "${source_url%%#*}"
}

get_local_version() {
  local spec_path="$1"
  local local_version

  local_version="$(
    rpmspec --define '_tmppath /tmp' -P "${spec_path}" 2>/dev/null \
      | awk '/^Version:[[:space:]]*/ {print $2; exit}'
  )"

  if [[ -z "${local_version}" ]]; then
    local_version="$(awk '/^Version:[[:space:]]+/{print $2; exit}' "${spec_path}")"
  fi

  printf '%s\n' "${local_version}"
}

detect_source_kind() {
  local source_url="$1"

  if [[ -z "${source_url}" || ! "${source_url}" =~ ^https?:// ]]; then
    printf '%s\n' "n/a"
  elif [[ "${source_url}" =~ ^https://files\.pythonhosted\.org/packages/source/[^/]+/[^/]+/ ]]; then
    printf '%s\n' "pypi"
  elif [[ "${source_url}" =~ ^https://registry\.npmjs\.org/ ]]; then
    printf '%s\n' "npm"
  elif [[ "${source_url}" =~ ^https://github\.com/[^/]+/[^/]+/releases/download/ ]]; then
    printf '%s\n' "github-release"
  elif [[ "${source_url}" =~ ^https://github\.com/[^/]+/[^/]+/archive/ ]]; then
    printf '%s\n' "github-archive"
  elif [[ "${source_url}" =~ ^https://codeberg\.org/[^/]+/[^/]+/(archive|releases)/ ]]; then
    printf '%s\n' "codeberg"
  else
    printf '%s\n' "url"
  fi
}

fetch_source_latest_version() {
  local source_url="$1"

  if [[ "${source_url}" =~ ^https://files\.pythonhosted\.org/packages/source/[^/]+/([^/]+)/ ]]; then
    fetch_pypi_latest_version "${BASH_REMATCH[1]}"
    return 0
  fi

  if [[ "${source_url}" =~ ^https://registry\.npmjs\.org/(@[^/]+/[^/]+)/-/ ]]; then
    fetch_npm_latest_version "${BASH_REMATCH[1]}"
    return 0
  fi

  if [[ "${source_url}" =~ ^https://registry\.npmjs\.org/([^@/][^/]+)/-/ ]]; then
    fetch_npm_latest_version "${BASH_REMATCH[1]}"
    return 0
  fi

  printf '%s\n' ""
}

is_commit_archive_source() {
  local source_url="$1"

  [[ "${source_url}" =~ /archive/[0-9a-f]{7,40}([./-]|$) ]]
}

version_gt() {
  local left="$1"
  local right="$2"
  local highest

  highest="$(printf '%s\n%s\n' "${left}" "${right}" | sort -V | tail -n1)"
  [[ "${left}" != "${right}" && "${highest}" == "${left}" ]]
}

fetch_latest_matching_source_version() {
  local upstream_git="$1"
  local source_url="$2"
  local local_version="$3"
  local versions candidate candidate_url
  local -a stable_candidates=()
  local -a prerelease_candidates=()

  if [[ -z "${upstream_git}" || "${source_url}" != *"${local_version}"* ]]; then
    return 0
  fi

  versions="$(fetch_git_versions "${upstream_git}")"
  if [[ -z "${versions}" ]]; then
    return 0
  fi

  while IFS= read -r candidate; do
    [[ -z "${candidate}" ]] && continue
    if is_prerelease_version "${candidate}"; then
      prerelease_candidates+=("${candidate}")
    else
      stable_candidates+=("${candidate}")
    fi
  done <<<"${versions}"

  for ((idx=${#stable_candidates[@]} - 1; idx >= 0; idx--)); do
    candidate="${stable_candidates[idx]}"
    candidate_url="${source_url//${local_version}/${candidate}}"
    if curl_ok "${candidate_url}"; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  for ((idx=${#prerelease_candidates[@]} - 1; idx >= 0; idx--)); do
    candidate="${prerelease_candidates[idx]}"
    candidate_url="${source_url//${local_version}/${candidate}}"
    if curl_ok "${candidate_url}"; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
}

printf '%-28s %-24s %-18s %-10s %-16s %s\n' "PACKAGE" "LOCAL" "UPSTREAM" "STATUS" "SOURCE" "UPSTREAM_GIT"

for envf in "${env_files[@]}"; do
  pkg_dir="$(dirname "${envf}")"
  pkg_name="$(basename "${pkg_dir}")"

  spec_file="$(awk -F= '/^SPEC_FILE=/{print $2}' "${envf}")"
  upstream_git="$(awk -F= '/^UPSTREAM_GIT=/{print $2}' "${envf}")"
  upstream_releases="$(awk -F= '/^UPSTREAM_RELEASES=/{print $2}' "${envf}")"
  upstream_check="$(awk -F= '/^UPSTREAM_CHECK=/{print $2}' "${envf}")"

  if [[ -z "${spec_file}" || -z "${upstream_git}" ]]; then
    local_version="(invalid package.env)"
    upstream_version="(unknown)"
    status="unknown"
    if [[ ${changed_only} -eq 0 ]]; then
      printf '%-28s %-24s %-18s %-10s %s\n' "${pkg_name}" "${local_version}" "${upstream_version}" "${status}" "${upstream_git:-N/A}"
    fi
    continue
  fi

  spec_path="${pkg_dir}/${spec_file}"
  if [[ ! -f "${spec_path}" ]]; then
    local_version="(missing spec)"
    upstream_version="(unknown)"
    status="unknown"
    if [[ ${changed_only} -eq 0 ]]; then
      printf '%-28s %-24s %-18s %-10s %s\n' "${pkg_name}" "${local_version}" "${upstream_version}" "${status}" "${upstream_git}"
    fi
    continue
  fi

  local_version="$(get_local_version "${spec_path}")"
  source_url="$(get_source_url "${spec_path}")"
  source_kind="$(detect_source_kind "${source_url}")"
  source_check="$(check_source_url "${source_url}")"
  source_version="$(fetch_source_latest_version "${source_url}")"
  upstream_version=""
  manual_check=0

  if [[ "${upstream_check}" == "manual" ]]; then
    manual_check=1
  elif [[ -n "${source_version}" ]]; then
    upstream_version="${source_version}"
  elif [[ -z "${upstream_releases}" ]] && is_commit_archive_source "${source_url}"; then
    manual_check=1
  else
    upstream_version="$(fetch_latest_matching_source_version "${upstream_git}" "${source_url}" "${local_version}")"
    if [[ -z "${upstream_version}" ]]; then
      upstream_version="$(fetch_latest_tag_from_git "${upstream_git}" || true)"
    fi
  fi

  local_base="${local_version%%^git*}"
  source_label="${source_check}:${source_kind}"

  if [[ ${manual_check} -eq 1 ]]; then
    upstream_version="(manual)"
    status="manual"
  elif [[ -z "${upstream_version}" ]]; then
    upstream_version="(unknown)"
    status="unknown"
  elif [[ "${local_version}" == "${upstream_version}" ]]; then
    status="same"
  elif [[ "${local_base}" == "${upstream_version}" ]]; then
    status="snapshot"
  elif is_commit_archive_source "${source_url}" && version_gt "${local_version}" "${upstream_version}"; then
    status="snapshot"
  else
    status="different"
  fi

  if [[ ${changed_only} -eq 1 && "${status}" == "manual" ]]; then
    continue
  fi

  if [[ ${changed_only} -eq 1 && "${status}" == "same" && "${source_check}" == "ok" ]]; then
    continue
  fi

  printf '%-28s %-24s %-18s %-10s %-16s %s\n' \
    "${pkg_name}" \
    "${local_version}" \
    "${upstream_version}" \
    "${status}" \
    "${source_label}" \
    "${upstream_git}"
done
