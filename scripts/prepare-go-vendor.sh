#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/prepare-go-vendor.sh <spec-file> <source-dir> <go-subdir>
USAGE
}

if [[ $# -ne 3 ]]; then
  usage
  exit 1
fi

spec_file="$1"
source_dir="$2"
go_subdir="$3"

[[ -n "${go_subdir}" ]] || exit 0
command -v go >/dev/null 2>&1 || { echo "go not found"; exit 1; }
command -v rpmspec >/dev/null 2>&1 || { echo "rpmspec not found"; exit 1; }

spec_rendered="$(rpmspec -P "${spec_file}")"

source1_name="$(awk '/^Source1:[[:space:]]*/ { print $2 }' <<<"${spec_rendered}")"
source1_name="${source1_name##*/}"
if [[ -z "${source1_name}" ]]; then
  exit 0
fi

if [[ -f "${source_dir}/${source1_name}" ]]; then
  exit 0
fi

src0_name="$(awk '/^Source0:[[:space:]]*/ { print $2 }' <<<"${spec_rendered}")"
src0_name="${src0_name##*/}"
[[ -n "${src0_name}" ]] || { echo "Could not determine Source0 from ${spec_file}"; exit 1; }

src0_path="${source_dir}/${src0_name}"
[[ -f "${src0_path}" ]] || { echo "Missing Source0 tarball: ${src0_path}"; exit 1; }

tmpdir="$(mktemp -d)"
gocache="$(mktemp -d)"
gomodcache="$(mktemp -d)"
cleanup() {
  chmod -R u+w "${tmpdir}" "${gocache}" "${gomodcache}" 2>/dev/null || true
  rm -rf "${tmpdir}" "${gocache}" "${gomodcache}" 2>/dev/null || true
}
trap cleanup EXIT

tar -xf "${src0_path}" -C "${tmpdir}"
srcdir="$(find "${tmpdir}" -mindepth 1 -maxdepth 1 -type d -print -quit)"
[[ -n "${srcdir}" ]] || { echo "Failed to locate extracted source dir"; exit 1; }

gosrc="${srcdir}/${go_subdir}"
[[ -f "${gosrc}/go.mod" ]] || { echo "go.mod not found in ${gosrc}"; exit 1; }

(
  cd "${gosrc}"
  GOCACHE="${gocache}" GOMODCACHE="${gomodcache}" GO111MODULE=on go mod vendor
)

tar -cJf "${source_dir}/${source1_name}" -C "${gosrc}" vendor
