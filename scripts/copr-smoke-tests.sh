#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  scripts/copr-smoke-tests.sh <copr-owner> <copr-project> [fedora-version...]

Examples:
  ./scripts/copr-smoke-tests.sh mineiro hyprland
  ./scripts/copr-smoke-tests.sh mineiro hyprland 43 44 rawhide

Environment variables:
  COPR_OWNER            COPR owner (alternative to positional arg)
  COPR_PROJECT          COPR project (alternative to positional arg)
  FEDORA_VERSIONS       Comma-separated versions for podman wrapper mode
                        (default: 43,44,rawhide)
  SMOKE_DNF_OPTS        Extra dnf options for install commands

Internal use (CI/container mode):
  ./scripts/copr-smoke-tests.sh --inside-container
EOF
}

log() {
  printf '[smoke] %s\n' "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

write_copr_repo_file() {
  local owner="$1"
  local project="$2"

  cat > /etc/yum.repos.d/copr-hyprland.repo <<EOF
[copr:${owner}:${project}]
name=COPR ${owner}/${project}
baseurl=https://download.copr.fedorainfracloud.org/results/${owner}/${project}/fedora-\$releasever-\$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://download.copr.fedorainfracloud.org/results/${owner}/${project}/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1
EOF
}

run_inside_container() {
  local owner="${COPR_OWNER:-}"
  local project="${COPR_PROJECT:-}"
  local dnf_opts
  local libdir plugin_dir
  local -a repo_packages plugin_packages all_packages expected_bins plugin_sos

  if [[ -z "${owner}" || -z "${project}" ]]; then
    echo "Set COPR_OWNER and COPR_PROJECT for --inside-container mode" >&2
    exit 1
  fi

  dnf_opts=("--setopt=install_weak_deps=0" "--nodocs")
  if [[ -n "${SMOKE_DNF_OPTS:-}" ]]; then
    # shellcheck disable=SC2206
    dnf_opts+=(${SMOKE_DNF_OPTS})
  fi

  log "Configuring COPR repo ${owner}/${project}"
  write_copr_repo_file "${owner}" "${project}"

  # Install the full set of packages currently published from this repo,
  # including explicit hyprland plugin subpackages (the meta package only
  # recommends them, and weak deps are disabled for deterministic installs).
  repo_packages=(
    hyprwayland-scanner
    hyprutils
    hyprlang
    hyprcursor
    hyprgraphics
    aquamarine
    hyprwire
    hyprland-protocols
    glaze
    hyprland
    hyprland-uwsm
    xdg-desktop-portal-hyprland
    uwsm
    hyprlock
    hypridle
    hyprpaper
    hyprpicker
    hyprsunset
    hyprpolkitagent
    hyprland-qt-support
    hyprqt6engine
    hyprland-guiutils
    hyprsysteminfo
    hyprlauncher
    hyprshot
    hyprpwcenter
    hyprdim
    hyprshutdown
    hyprtoolkit
  )
  all_packages=("${repo_packages[@]}")

  log "Installing smoke-test target packages"
  dnf -y --refresh install "${dnf_opts[@]}" "${all_packages[@]}"

  log "Verifying RPMs are installed"
  rpm -q "${all_packages[@]}"

  log "Verifying binaries are present"
  expected_bins=(
    Hyprland
    hyprctl
    hyprpm
    hyprland-share-picker
    hyprwayland-scanner
    hyprlock
    hypridle
    hyprpaper
    hyprpicker
    hyprsunset
    hyprsysteminfo
    hyprlauncher
    hyprshot
    hyprpwcenter
    hyprdim
    hyprshutdown
    uwsm
    uwsm-app
    uuctl
    fumon
  )
  for bin in "${expected_bins[@]}"; do
    command -v "${bin}" >/dev/null || {
      echo "Missing expected command: ${bin}" >&2
      exit 1
    }
  done

  log "Verifying key files are present"
  test -f /usr/share/wayland-sessions/hyprland.desktop
  test -f /usr/share/wayland-sessions/hyprland-uwsm.desktop
  test -f /usr/share/dbus-1/services/org.freedesktop.impl.portal.desktop.hyprland.service
  test -f /usr/share/xdg-desktop-portal/portals/hyprland.portal
  test -f /usr/lib/systemd/user/fumon.service
  test -x /usr/libexec/hyprpolkitagent
  test -x /usr/bin/hyprland-dialog
  compgen -G '/usr/lib/systemd/user/wayland-*.target' >/dev/null
  compgen -G '/usr/lib/systemd/user/wayland-*.service' >/dev/null

  log "Running basic CLI smoke checks"
  local hyprctl_rc=0
  hyprctl --help >/dev/null || hyprctl_rc=$?
  if [[ "${hyprctl_rc}" -ne 0 && "${hyprctl_rc}" -ne 1 ]]; then
    echo "hyprctl --help failed with unexpected rc=${hyprctl_rc}" >&2
    exit "${hyprctl_rc}"
  fi
  hyprpm --help >/dev/null
  # This can abort without a graphical session; package/file presence is the primary check.
  hyprland-share-picker --help >/dev/null || true
  uwsm --help >/dev/null
  uuctl --help >/dev/null
  if command -v systemctl >/dev/null 2>&1; then
    fumon --help >/dev/null
  else
    log "Skipping fumon --help (systemctl not present in minimal container)"
  fi

  log "Smoke test passed"
}

run_with_podman() {
  local owner="$1"
  local project="$2"
  shift 2

  require_cmd podman

  local -a versions=()
  local image
  local version

  if [[ "$#" -gt 0 ]]; then
    versions=("$@")
  elif [[ -n "${FEDORA_VERSIONS:-}" ]]; then
    IFS=',' read -r -a versions <<<"${FEDORA_VERSIONS}"
  else
    versions=(43 44 rawhide)
  fi

  for version in "${versions[@]}"; do
    image="registry.fedoraproject.org/fedora:${version}"
    log "Running smoke test in ${image}"
    podman run --rm --pull=missing \
      -e COPR_OWNER="${owner}" \
      -e COPR_PROJECT="${project}" \
      -v "${repo_root}:/work:ro,z" \
      -w /work \
      "${image}" \
      bash ./scripts/copr-smoke-tests.sh --inside-container
  done

  log "All container smoke tests passed"
}

main() {
  if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
  fi

  if [[ "${1:-}" == "--inside-container" ]]; then
    shift
    run_inside_container "$@"
    exit 0
  fi

  local owner="${COPR_OWNER:-${1:-}}"
  local project="${COPR_PROJECT:-${2:-}}"

  if [[ -z "${owner}" || -z "${project}" ]]; then
    usage >&2
    exit 1
  fi

  if [[ $# -ge 2 ]]; then
    shift 2
  else
    set --
  fi

  run_with_podman "${owner}" "${project}" "$@"
}

main "$@"
