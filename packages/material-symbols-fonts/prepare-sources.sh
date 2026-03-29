#!/usr/bin/bash
set -euo pipefail

SPEC=${1:-material-symbols-fonts.spec}
SOURCEDIR=${2:-"${PWD}/sources"}

commit=$(awk '/^%global[[:space:]]+commit0[[:space:]]+/ { print $3; exit }' "${SPEC}")
snapshot_date=$(awk '/^%global[[:space:]]+snapshot_date[[:space:]]+/ { print $3; exit }' "${SPEC}")
name=$(rpmspec -P "${SPEC}" | awk '/^Name:[[:space:]]*/ { print $2; exit }')
source_name=$(rpmspec -P "${SPEC}" | awk '/^Source0:[[:space:]]*/ { print $2; exit }' | xargs basename)

if [ -z "${commit}" ] || [ -z "${snapshot_date}" ] || [ -z "${name}" ] || [ -z "${source_name}" ]; then
	echo "Failed to resolve source metadata from ${SPEC}" >&2
	exit 1
fi

mkdir -p "${SOURCEDIR}"

if [ -f "${SOURCEDIR}/${source_name}" ]; then
	exit 0
fi

tmpdir=$(mktemp -d)
trap 'rm -rf "${tmpdir}"' EXIT

archive_root="${name}-${snapshot_date}"
raw_root="https://raw.githubusercontent.com/google/material-design-icons/${commit}"

fetch_raw() {
	local remote_path=$1
	local output_path=$2

	curl -L -g --fail --retry 3 "${raw_root}/${remote_path}" -o "${output_path}"
}

mkdir -p "${tmpdir}/${archive_root}/variablefont"
fetch_raw "LICENSE" "${tmpdir}/${archive_root}/LICENSE"
fetch_raw "README.md" "${tmpdir}/${archive_root}/README.md"
fetch_raw "variablefont/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf"
fetch_raw "variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].ttf" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].ttf"
fetch_raw "variablefont/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].ttf" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].ttf"
fetch_raw "variablefont/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].codepoints" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].codepoints"
fetch_raw "variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints"
fetch_raw "variablefont/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].codepoints" \
	"${tmpdir}/${archive_root}/variablefont/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].codepoints"

ttf_count=$(find "${tmpdir}/${archive_root}/variablefont" -maxdepth 1 -type f -name '*.ttf' | wc -l)
codepoint_count=$(find "${tmpdir}/${archive_root}/variablefont" -maxdepth 1 -type f -name '*.codepoints' | wc -l)

[ "${ttf_count}" -eq 3 ] || { echo "Expected 3 Material Symbols TTF files, found ${ttf_count}" >&2; exit 1; }
[ "${codepoint_count}" -eq 3 ] || { echo "Expected 3 Material Symbols codepoint files, found ${codepoint_count}" >&2; exit 1; }

tar -cJf "${SOURCEDIR}/${source_name}" -C "${tmpdir}" "${archive_root}"
