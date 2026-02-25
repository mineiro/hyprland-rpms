#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/bump-version.sh <package-name-or-dir> <new-version>

Examples:
  scripts/bump-version.sh hyprland 0.52.0
  scripts/bump-version.sh packages/hyprlock 0.8.1
EOF
}

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

target="$1"
new_version="$2"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "${target}" ]]; then
  pkg_dir="$(cd "${target}" && pwd)"
elif [[ -d "${repo_root}/packages/${target}" ]]; then
  pkg_dir="${repo_root}/packages/${target}"
else
  echo "Package directory not found: ${target}"
  exit 1
fi

spec="$(find "${pkg_dir}" -maxdepth 1 -type f -name '*.spec' | head -n1)"
if [[ -z "${spec}" ]]; then
  echo "No .spec file found in ${pkg_dir}"
  exit 1
fi

old_version="$(awk '/^Version:[[:space:]]+/ {print $2; exit}' "${spec}")"
if [[ -z "${old_version}" ]]; then
  echo "Could not read Version from ${spec}"
  exit 1
fi

sed -i -E "0,/^Version:[[:space:]]+/{s//Version:        ${new_version}/}" "${spec}"

echo "Updated ${spec#${repo_root}/}: ${old_version} -> ${new_version}"
echo "Reminder: verify Source URLs, patches, and dependency floors before build."

