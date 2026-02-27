#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/check-upstream-versions.sh [--changed-only] [--package <name>]

Options:
  --changed-only       show only rows where local != upstream
  --package <name>     check only one package directory under packages/
  -h, --help           show this help

Status values:
  same                 local version equals upstream version
  different            local version differs from upstream version
  snapshot             local version is a VCS snapshot of upstream base version
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

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

fetch_github_latest_tag() {
  local owner="$1"
  local repo="$2"
  local json tag

  json="$(curl -fsSL "https://api.github.com/repos/${owner}/${repo}/releases/latest" 2>/dev/null || true)"
  tag="$(jq -r '.tag_name // empty' <<<"${json}" 2>/dev/null || true)"
  if [[ -n "${tag}" ]]; then
    printf '%s\n' "${tag}"
    return 0
  fi

  json="$(curl -fsSL "https://api.github.com/repos/${owner}/${repo}/tags?per_page=1" 2>/dev/null || true)"
  tag="$(jq -r '.[0].name // empty' <<<"${json}" 2>/dev/null || true)"
  printf '%s\n' "${tag}"
}

fetch_codeberg_latest_tag() {
  local owner="$1"
  local repo="$2"
  local json tag

  json="$(curl -fsSL "https://codeberg.org/api/v1/repos/${owner}/${repo}/releases?limit=1" 2>/dev/null || true)"
  tag="$(jq -r '.[0].tag_name // empty' <<<"${json}" 2>/dev/null || true)"
  if [[ -n "${tag}" ]]; then
    printf '%s\n' "${tag}"
    return 0
  fi

  json="$(curl -fsSL "https://codeberg.org/api/v1/repos/${owner}/${repo}/tags?page=1&limit=1" 2>/dev/null || true)"
  tag="$(jq -r '.[0].name // empty' <<<"${json}" 2>/dev/null || true)"
  printf '%s\n' "${tag}"
}

fetch_latest_tag_from_git() {
  local upstream_git="$1"

  git ls-remote --tags --refs "${upstream_git}" 2>/dev/null \
    | awk -F/ '{print $NF}' \
    | grep -E '^[vV]?[0-9]+(\.[0-9]+){1,3}([._-][0-9A-Za-z.-]+)?$' \
    | sort -V \
    | tail -n1
}

printf '%-28s %-24s %-18s %-10s %s\n' "PACKAGE" "LOCAL" "UPSTREAM" "STATUS" "UPSTREAM_GIT"

for envf in "${env_files[@]}"; do
  pkg_dir="$(dirname "${envf}")"
  pkg_name="$(basename "${pkg_dir}")"

  spec_file="$(awk -F= '/^SPEC_FILE=/{print $2}' "${envf}")"
  upstream_git="$(awk -F= '/^UPSTREAM_GIT=/{print $2}' "${envf}")"

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

  local_version="$(awk '/^Version:[[:space:]]+/{print $2; exit}' "${spec_path}")"
  upstream_tag=""

  if [[ "${upstream_git}" =~ ^https://github.com/([^/]+)/([^/.]+)(\.git)?$ ]]; then
    upstream_tag="$(fetch_github_latest_tag "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")"
  elif [[ "${upstream_git}" =~ ^https://codeberg.org/([^/]+)/([^/.]+)(\.git)?$ ]]; then
    upstream_tag="$(fetch_codeberg_latest_tag "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")"
  fi

  if [[ -z "${upstream_tag}" ]]; then
    upstream_tag="$(fetch_latest_tag_from_git "${upstream_git}" || true)"
  fi

  upstream_version="${upstream_tag#v}"
  local_base="${local_version%%^git*}"

  if [[ -z "${upstream_tag}" ]]; then
    upstream_version="(unknown)"
    status="unknown"
  elif [[ "${local_version}" == "${upstream_version}" ]]; then
    status="same"
  elif [[ "${local_base}" == "${upstream_version}" ]]; then
    status="snapshot"
  else
    status="different"
  fi

  if [[ ${changed_only} -eq 1 && "${status}" == "same" ]]; then
    continue
  fi

  printf '%-28s %-24s %-18s %-10s %s\n' "${pkg_name}" "${local_version}" "${upstream_version}" "${status}" "${upstream_git}"
done
