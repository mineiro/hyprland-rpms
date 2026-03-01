#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
Run mock builds across a Fedora/architecture matrix.

Usage:
  scripts/mock-matrix-build.sh [options] <package> [<package> ...]
  scripts/mock-matrix-build.sh [options] --all-packages

Options:
  --all-packages              Build every package under packages/
  --release <43|44|rawhide>  Target Fedora release (repeatable)
  --arch <x86_64|aarch64>    Target architecture (repeatable)
  --mode <chain|rebuild>     Build mode (default: chain)
  --addrepo <url>            Extra repository for mock buildroot (repeatable)
  --result-root <path>       Base output directory (default: repo/mock-results)
  --srpm-out <path>          SRPM output directory (default: repo/dist/srpm)
  --skip-srpm                Reuse existing SRPMs in --srpm-out
  --continue-on-failure      Continue remaining chroots if one fails
  --mock-arg <arg>           Extra argument passed to mock (repeatable)
  --help                     Show this help

Examples:
  ./scripts/mock-matrix-build.sh --all-packages
  ./scripts/mock-matrix-build.sh --mode rebuild --all-packages
  ./scripts/mock-matrix-build.sh \
    --release 44 --release rawhide \
    --arch x86_64 --arch aarch64 \
    hyprwayland-scanner hyprutils hyprlang
USAGE
}

log() {
  printf '[matrix] %s\n' "$*"
}

die() {
  printf '[matrix] ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

is_valid_release() {
  case "$1" in
    43|44|rawhide)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_valid_arch() {
  case "$1" in
    x86_64|aarch64)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

require_value() {
  local opt="$1"
  local val="${2:-}"
  [[ -n "${val}" ]] || die "${opt} requires a value"
}

release_set=0
arch_set=0
all_packages=0
skip_srpm=0
continue_on_failure=0
mode="chain"
result_root="${repo_root}/mock-results"
srpm_out="${repo_root}/dist/srpm"

declare -a releases=()
declare -a arches=()
declare -a package_args=()
declare -a extra_repos=()
declare -a mock_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-packages)
      all_packages=1
      shift
      ;;
    --release)
      require_value "$1" "${2:-}"
      is_valid_release "$2" || die "Unsupported release: $2"
      releases+=("$2")
      release_set=1
      shift 2
      ;;
    --arch)
      require_value "$1" "${2:-}"
      is_valid_arch "$2" || die "Unsupported arch: $2"
      arches+=("$2")
      arch_set=1
      shift 2
      ;;
    --mode)
      require_value "$1" "${2:-}"
      case "$2" in
        chain|rebuild)
          mode="$2"
          ;;
        *)
          die "Unsupported mode: $2"
          ;;
      esac
      shift 2
      ;;
    --addrepo)
      require_value "$1" "${2:-}"
      extra_repos+=("$2")
      shift 2
      ;;
    --result-root)
      require_value "$1" "${2:-}"
      result_root="$2"
      shift 2
      ;;
    --srpm-out)
      require_value "$1" "${2:-}"
      srpm_out="$2"
      shift 2
      ;;
    --skip-srpm)
      skip_srpm=1
      shift
      ;;
    --continue-on-failure)
      continue_on_failure=1
      shift
      ;;
    --mock-arg)
      require_value "$1" "${2:-}"
      mock_args+=("$2")
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        package_args+=("$1")
        shift
      done
      ;;
    -*)
      die "Unknown option: $1"
      ;;
    *)
      package_args+=("$1")
      shift
      ;;
  esac
done

if [[ ${release_set} -eq 0 ]]; then
  releases=(43 44 rawhide)
fi

if [[ ${arch_set} -eq 0 ]]; then
  arches=(x86_64 aarch64)
fi

require_cmd make
require_cmd mock

if [[ ${all_packages} -eq 1 && ${#package_args[@]} -gt 0 ]]; then
  die "Use either explicit packages or --all-packages, not both"
fi

declare -a packages=()
if [[ ${all_packages} -eq 1 ]]; then
  mapfile -t packages < <(find "${repo_root}/packages" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
else
  packages=("${package_args[@]}")
fi

[[ ${#packages[@]} -gt 0 ]] || die "No packages selected"

for pkg in "${packages[@]}"; do
  [[ -d "${repo_root}/packages/${pkg}" ]] || die "Unknown package directory: packages/${pkg}"
  [[ -f "${repo_root}/packages/${pkg}/${pkg}.spec" ]] || die "Missing spec file: packages/${pkg}/${pkg}.spec"
done

mkdir -p "${srpm_out}" "${result_root}"

if [[ ${skip_srpm} -eq 0 ]]; then
  for pkg in "${packages[@]}"; do
    log "Building SRPM: ${pkg}"
    make -C "${repo_root}" srpm PACKAGE="${pkg}" OUTDIR="${srpm_out}"
  done
else
  log "Skipping SRPM build phase"
fi

declare -a srpms=()
for pkg in "${packages[@]}"; do
  latest_srpm="$(ls -1t "${srpm_out}/${pkg}-"*.src.rpm 2>/dev/null | head -n 1 || true)"
  [[ -n "${latest_srpm}" ]] || die "No SRPM found for ${pkg} under ${srpm_out}"
  srpms+=("${latest_srpm}")
done

declare -a chroots=()
for rel in "${releases[@]}"; do
  for arch in "${arches[@]}"; do
    cfg="fedora-${rel}-${arch}"
    [[ -f "/etc/mock/${cfg}.cfg" ]] || die "Mock config not found: /etc/mock/${cfg}.cfg"
    chroots+=("${cfg}")
  done
done

declare -A chroot_status=()
run_stamp="$(date +%Y%m%d-%H%M%S)"
had_failure=0

for cfg in "${chroots[@]}"; do
  run_dir="${result_root}/${cfg}/matrix-${run_stamp}"
  mkdir -p "${run_dir}"

  log "Running ${mode} build in ${cfg}"

  extra_repo_args=()
  for repo in "${extra_repos[@]}"; do
    extra_repo_args+=(--addrepo "$repo")
  done

  if [[ "${mode}" == "chain" ]]; then
    mkdir -p "${run_dir}/localrepo"
    if mock --chain \
      -r "${cfg}" \
      --localrepo "${run_dir}/localrepo" \
      "${extra_repo_args[@]}" \
      "${mock_args[@]}" \
      "${srpms[@]}"; then
      chroot_status["${cfg}"]="ok"
    else
      chroot_status["${cfg}"]="fail"
      had_failure=1
      if [[ ${continue_on_failure} -eq 0 ]]; then
        break
      fi
    fi
  else
    rebuild_failed=0
    for i in "${!packages[@]}"; do
      pkg="${packages[$i]}"
      srpm="${srpms[$i]}"
      pkg_result_dir="${run_dir}/${pkg}"
      mkdir -p "${pkg_result_dir}"

      log "Rebuilding ${pkg} in ${cfg}"
      if ! mock \
        -r "${cfg}" \
        --resultdir "${pkg_result_dir}" \
        "${extra_repo_args[@]}" \
        "${mock_args[@]}" \
        --rebuild "${srpm}"; then
        rebuild_failed=1
        had_failure=1
        if [[ ${continue_on_failure} -eq 0 ]]; then
          break
        fi
      fi
    done

    if [[ ${rebuild_failed} -eq 0 ]]; then
      chroot_status["${cfg}"]="ok"
    else
      chroot_status["${cfg}"]="fail"
      if [[ ${continue_on_failure} -eq 0 ]]; then
        break
      fi
    fi
  fi
done

printf '\n[matrix] Summary (%s mode):\n' "${mode}"
for cfg in "${chroots[@]}"; do
  status="${chroot_status[$cfg]:-not-run}"
  printf '[matrix]   %-24s %s\n' "${cfg}" "${status}"
done

if [[ ${had_failure} -ne 0 ]]; then
  exit 1
fi

log "All requested matrix builds completed successfully"
