#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/new-package.sh <package-name> <upstream-git-url> [upstream-releases-url]

Example:
  scripts/new-package.sh hyprlock https://github.com/hyprwm/hyprlock.git https://github.com/hyprwm/hyprlock/releases
EOF
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage
  exit 1
fi

pkg="$1"
upstream_git="$2"
upstream_releases="${3:-}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template_dir="${repo_root}/templates/package"
pkg_dir="${repo_root}/packages/${pkg}"

if [[ -e "${pkg_dir}" ]]; then
  echo "Package directory already exists: ${pkg_dir}"
  exit 1
fi

cp -a "${template_dir}" "${pkg_dir}"
mv "${pkg_dir}/pkgname.spec" "${pkg_dir}/${pkg}.spec"

sed -i \
  -e "s/^PACKAGE_NAME=.*/PACKAGE_NAME=${pkg}/" \
  -e "s/^SPEC_FILE=.*/SPEC_FILE=${pkg}.spec/" \
  -e "s|^UPSTREAM_GIT=.*|UPSTREAM_GIT=${upstream_git}|" \
  -e "s|^UPSTREAM_RELEASES=.*|UPSTREAM_RELEASES=${upstream_releases}|" \
  -e "s/^COPR_PACKAGE=.*/COPR_PACKAGE=${pkg}/" \
  -e "s|^COPR_SUBDIR=.*|COPR_SUBDIR=packages/${pkg}|" \
  "${pkg_dir}/package.env"

sed -i \
  -e "s/^Name:.*/Name:           ${pkg}/" \
  "${pkg_dir}/${pkg}.spec"

cat > "${pkg_dir}/README.md" <<EOF
# ${pkg}

Starter packaging directory for \`${pkg}\`.

Update \`${pkg}.spec\` and \`package.env\` before first build.
EOF

echo "Created ${pkg_dir}"

