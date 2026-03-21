#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/prepare-go-vendor.sh <spec-file> <source-dir> <go-subdir>
USAGE
}

normalize_vendor_modules() {
  local go_mod="$1"
  local modules_txt="$2"
  local explicit_tmp normalized_tmp

  [[ -f "${modules_txt}" ]] || return 0

  explicit_tmp="$(mktemp)"
  normalized_tmp="$(mktemp)"

  awk '
    function emit_requirement(module, version) {
      if (module == "" || version == "") {
        return
      }

      sub(/[[:space:]]+\/\/.*/, "", version)
      print module "\t" version
    }

    /^[[:space:]]*require[[:space:]]*\(/ {
      in_require_block = 1
      next
    }

    in_require_block && /^[[:space:]]*\)/ {
      in_require_block = 0
      next
    }

    in_require_block {
      emit_requirement($1, $2)
      next
    }

    /^[[:space:]]*require[[:space:]]+/ {
      emit_requirement($2, $3)
    }
  ' "${go_mod}" > "${explicit_tmp}"

  if [[ ! -s "${explicit_tmp}" ]]; then
    rm -f "${explicit_tmp}" "${normalized_tmp}"
    return 0
  fi

  awk -v explicit_file="${explicit_tmp}" '
    BEGIN {
      while ((getline line < explicit_file) > 0) {
        split(line, fields, "\t")
        if (fields[1] != "" && fields[2] != "") {
          explicit[fields[1] SUBSEP fields[2]] = 1
        }
      }
      close(explicit_file)
    }

    function flush_pending() {
      if (pending_header && should_mark_explicit) {
        print "## explicit"
      }

      pending_header = 0
      should_mark_explicit = 0
    }

    /^# / {
      flush_pending()
      print

      pending_header = 1
      should_mark_explicit = explicit[$2 SUBSEP $3]
      next
    }

    {
      if (pending_header) {
        if ($0 ~ /^## explicit([;[:space:]]|$)/) {
          should_mark_explicit = 0
        } else if (should_mark_explicit) {
          print "## explicit"
          should_mark_explicit = 0
        }

        pending_header = 0
      }

      print
    }

    END {
      flush_pending()
    }
  ' "${modules_txt}" > "${normalized_tmp}"

  mv "${normalized_tmp}" "${modules_txt}"
  rm -f "${explicit_tmp}"
}

if [[ $# -ne 3 ]]; then
  usage
  exit 1
fi

spec_file="$1"
source_dir="$2"
go_subdir="$3"
spec_dir="$(dirname "${spec_file}")"

[[ -n "${go_subdir}" ]] || exit 0
command -v go >/dev/null 2>&1 || { echo "go not found"; exit 1; }
command -v rpmspec >/dev/null 2>&1 || { echo "rpmspec not found"; exit 1; }

spec_rendered="$(rpmspec -P "${spec_file}")"

source1_name="$(awk '/^Source1:[[:space:]]*/ { print $2 }' <<<"${spec_rendered}")"
source1_name="${source1_name##*/}"
if [[ -z "${source1_name}" ]]; then
  exit 0
fi

src0_name="$(awk '/^Source0:[[:space:]]*/ { print $2 }' <<<"${spec_rendered}")"
src0_name="${src0_name##*/}"
[[ -n "${src0_name}" ]] || { echo "Could not determine Source0 from ${spec_file}"; exit 1; }

src0_path="${source_dir}/${src0_name}"
if [[ ! -f "${src0_path}" && -f "${spec_dir}/${src0_name}" ]]; then
  src0_path="${spec_dir}/${src0_name}"
fi
if [[ ! -f "${src0_path}" && -f "${spec_dir}/sources/${src0_name}" ]]; then
  src0_path="${spec_dir}/sources/${src0_name}"
fi
if [[ ! -f "${src0_path}" && -f "${spec_dir}/SOURCES/${src0_name}" ]]; then
  src0_path="${spec_dir}/SOURCES/${src0_name}"
fi

rpm_sourcedir="$(rpm --eval '%{_sourcedir}' 2>/dev/null || true)"
if [[ ! -f "${src0_path}" && -n "${rpm_sourcedir}" && -f "${rpm_sourcedir}/${src0_name}" ]]; then
  src0_path="${rpm_sourcedir}/${src0_name}"
fi
if [[ ! -f "${src0_path}" && -f "${HOME}/rpmbuild/SOURCES/${src0_name}" ]]; then
  src0_path="${HOME}/rpmbuild/SOURCES/${src0_name}"
fi

[[ -f "${src0_path}" ]] || { echo "Missing Source0 tarball: ${source_dir}/${src0_name}"; exit 1; }

if [[ "${src0_path}" != "${source_dir}/${src0_name}" ]]; then
  cp -f "${src0_path}" "${source_dir}/${src0_name}"
  src0_path="${source_dir}/${src0_name}"
fi

rm -f "${source_dir}/${source1_name}"

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
  normalize_vendor_modules "${gosrc}/go.mod" "${gosrc}/vendor/modules.txt"
)

tar -cJf "${source_dir}/${source1_name}" -C "${gosrc}" vendor
