#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Draft local libvirt/KVM headless smoke harness for COPR packages.

This script boots a Fedora cloud image with cloud-init, SSHes into it, installs
packages from the target COPR repo, runs headless smoke checks, and collects
logs/journal output for troubleshooting.

Usage:
  scripts/kvm-smoke-headless.sh [--owner <copr-owner>] [--project <copr-project>] \
    [--base-image /path/to/Fedora-Cloud-Base.qcow2] [options]

COPR target options:
  --owner OWNER            COPR owner (default: $COPR_OWNER or mineiro)
  --project PROJECT        COPR project (default: $COPR_PROJECT or hyprland)

Common options:
  --base-image PATH        Fedora cloud qcow2 image (optional; if omitted the
                           script downloads/caches a Fedora cloud image for
                           --release under .cache/kvm-smoke/images/)
  --release VERSION        Fedora release label for VM naming only (default: 44)
  --vm-name NAME           libvirt domain name (default derived from release)
  --ssh-user USER          Cloud image login user (default: fedora)
  --memory-mib MiB         VM RAM (default: 4096)
  --vcpus N                VM vCPU count (default: 4)
  --disk-size-gb N         Overlay disk size (default: 30)
  --network NAME           libvirt network name (default: default)
  --connect URI            libvirt URI (e.g. qemu:///system or qemu:///session)
  --graphics MODE          virt-install graphics mode (default: none)
  --osinfo VALUE           virt-install --osinfo value (default:
                           auto-select fedora<release> when available, else
                           detect=on,require=off)
  --timeout-sec N          Boot/SSH timeout in seconds (default: 600)
  --workdir PATH           Working directory (default depends on libvirt URI:
                           qemu:///system -> /var/tmp/hyprland-rpms-kvm-smoke
                           otherwise -> .cache/kvm-smoke)
  --keep-vm                Keep the VM running and skip destroy/undefine on exit
  --help                   Show this help

Environment variables:
  COPR_OWNER               Default COPR owner (overrides repo default)
  COPR_PROJECT             Default COPR project (overrides repo default)
  KVM_SMOKE_WORKDIR        Default working directory (overrides auto default)

Examples:
  ./scripts/kvm-smoke-headless.sh --release 43

  ./scripts/kvm-smoke-headless.sh \
    --owner mineiro --project hyprland \
    --release 44

  ./scripts/kvm-smoke-headless.sh \
    --owner mineiro --project hyprland \
    --base-image ~/.cache/fedora/Fedora-Cloud-Base-44.qcow2 \
    --release 44

  ./scripts/kvm-smoke-headless.sh \
    --owner mineiro --project hyprland \
    --base-image ~/.cache/fedora/Fedora-Cloud-Base-rawhide.qcow2 \
    --release rawhide --keep-vm

Notes:
  - This is a headless integration stage. It validates a full Fedora VM with
    systemd/logind and package installation/user-unit file presence, but it does
    not attempt to start a graphical Hyprland session.
  - A future graphical stage can reuse this harness with a different graphics
    mode and additional session startup assertions.
  - Auto-downloaded images are fetched from Fedora cloud image directories and
    verified against the published SHA256 CHECKSUM file before use.
  - By default, the script tries a release-matched virt-install `--osinfo`
    value (for example `fedora43`) and falls back to `detect=on,require=off`
    if the host libosinfo database does not provide it.
  - If --connect is not provided, the script prefers `qemu:///system` when it
    is accessible, otherwise it falls back to `qemu:///session`.
  - For `qemu:///system`, the script prefers `sudo` (if available) and keeps
    the sudo timestamp alive during the run so you are prompted only once.
  - For `qemu:///system`, the default workdir is moved to `/var/tmp` so the
    qemu user can access generated overlay/seed images without requiring
    execute permissions on your home directory.
EOF
}

log() {
  printf '[kvm-smoke] %s\n' "$*"
}

die() {
  printf '[kvm-smoke] ERROR: %s\n' "$*" >&2
  exit 1
}

fedora_pkg_hint_for_cmd() {
  case "$1" in
    cloud-localds) printf 'cloud-utils\n' ;;
    virt-install) printf 'virt-install\n' ;;
    virsh) printf 'libvirt-client\n' ;;
    qemu-img) printf 'qemu-img\n' ;;
    ssh|ssh-keygen) printf 'openssh-clients\n' ;;
    curl) printf 'curl\n' ;;
    sha256sum) printf 'coreutils\n' ;;
    awk) printf 'gawk\n' ;;
    grep) printf 'grep\n' ;;
    sed) printf 'sed\n' ;;
    sort|head|tail) printf 'coreutils\n' ;;
    date) printf 'coreutils\n' ;;
    *)
      return 1
      ;;
  esac
}

require_cmd() {
  local cmd="$1"
  local pkg_hint

  if command -v "${cmd}" >/dev/null 2>&1; then
    return 0
  fi

  if pkg_hint="$(fedora_pkg_hint_for_cmd "${cmd}")"; then
    die "Missing required command: ${cmd} (Fedora package: ${pkg_hint})"
  fi

  die "Missing required command: ${cmd}"
}

sudo_prefix=()
sudo_keepalive_pid=""

run_virsh() {
  "${sudo_prefix[@]}" virsh "$@"
}

run_virt_install() {
  "${sudo_prefix[@]}" virt-install "$@"
}

sanitize() {
  tr -cs '[:alnum:]' '-' <<<"$1" | sed 's/^-//; s/-$//'
}

default_vm_name() {
  local rel="$1"
  printf 'hyprland-smoke-%s' "$(sanitize "${rel}")"
}

ssh_opts() {
  local key_path="$1"
  printf '%s\n' \
    "-i" "$key_path" \
    "-o" "BatchMode=yes" \
    "-o" "StrictHostKeyChecking=no" \
    "-o" "UserKnownHostsFile=/dev/null" \
    "-o" "ConnectTimeout=5"
}

normalize_release_label() {
  local rel="${1,,}"
  case "${rel}" in
    rawhide|rh)
      printf 'rawhide\n'
      ;;
    f[0-9]*)
      printf '%s\n' "${rel#f}"
      ;;
    [0-9]*)
      printf '%s\n' "${rel}"
      ;;
    *)
      printf '%s\n' "${rel}"
      ;;
  esac
}

fedora_cloud_image_dirs() {
  local rel
  rel="$(normalize_release_label "${1}")"

  if [[ "${rel}" == "rawhide" ]]; then
    printf '%s\n' \
      "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Cloud/x86_64/images/" \
      "https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Cloud/x86_64/images/"
  else
    printf '%s\n' \
      "https://dl.fedoraproject.org/pub/fedora/linux/releases/${rel}/Cloud/x86_64/images/" \
      "https://download.fedoraproject.org/pub/fedora/linux/releases/${rel}/Cloud/x86_64/images/" \
      "https://dl.fedoraproject.org/pub/fedora/linux/development/${rel}/Cloud/x86_64/images/" \
      "https://download.fedoraproject.org/pub/fedora/linux/development/${rel}/Cloud/x86_64/images/"
  fi
}

extract_listing_entries() {
  sed -n 's/.*href="\([^"]*\)".*/\1/p'
}

select_latest_cloud_qcow2_from_listing() {
  grep -E '^Fedora-Cloud-Base-Generic.*x86_64.*\.qcow2$' \
    | sort -V \
    | tail -n 1
}

select_checksum_candidates_from_listing() {
  grep -E 'CHECKSUM$' \
    | sort -V -r
}

fetch_cloud_listing() {
  local dir_url="$1"
  curl -fsSL "${dir_url}" 2>/dev/null
}

download_file() {
  local url="$1"
  local dst="$2"
  log "Downloading ${url}"
  curl -fL --retry 3 --retry-delay 2 -o "${dst}" "${url}"
  make_qemu_system_readable "${dst}"
}

checksum_hash_for_image() {
  local checksum_file="$1"
  local image_name="$2"

  awk -v img="${image_name}" '
    $1 == "SHA256" && $2 == "(" img ")" && $3 == "=" && length($4) == 64 {
      print $4
      exit
    }
  ' "${checksum_file}"
}

verify_image_checksum() {
  local image_path="$1"
  local checksum_file="$2"
  local image_name hash

  image_name="$(basename "${image_path}")"
  hash="$(checksum_hash_for_image "${checksum_file}" "${image_name}")"
  [[ -n "${hash}" ]] || die "No SHA256 entry for ${image_name} in $(basename "${checksum_file}")"

  log "Verifying checksum for ${image_name}"
  printf '%s  %s\n' "${hash}" "${image_path}" | sha256sum -c - >/dev/null
}

resolve_auto_base_image() {
  local rel cache_dir listing dir_url image_name checksum_name
  local image_path checksum_path
  local -a checksum_candidates=()

  rel="$(normalize_release_label "${release_label}")"
  cache_dir="${workdir}/images/${rel}"
  mkdir -p "${cache_dir}"
  ensure_qemu_system_dir_traversable "${workdir}" "${workdir}/images" "${cache_dir}"

  listing=""
  dir_url=""
  image_name=""
  checksum_name=""

  while IFS= read -r candidate_dir; do
    [[ -n "${candidate_dir}" ]] || continue
    if listing="$(fetch_cloud_listing "${candidate_dir}")"; then
      image_name="$(
        printf '%s\n' "${listing}" \
          | extract_listing_entries \
          | select_latest_cloud_qcow2_from_listing \
          || true
      )"
      if [[ -n "${image_name}" ]]; then
        mapfile -t checksum_candidates < <(
          printf '%s\n' "${listing}" \
            | extract_listing_entries \
            | select_checksum_candidates_from_listing \
            || true
        )
        [[ ${#checksum_candidates[@]} -gt 0 ]] || die "Could not find CHECKSUM file in ${candidate_dir}"
        dir_url="${candidate_dir}"
        break
      fi
    fi
  done < <(fedora_cloud_image_dirs "${rel}")

  [[ -n "${dir_url}" ]] || die "Could not resolve Fedora cloud image listing for release ${rel}"
  [[ -n "${image_name}" ]] || die "Could not find Fedora cloud qcow2 image for release ${rel}"

  for checksum_name in "${checksum_candidates[@]}"; do
    checksum_path="${cache_dir}/${checksum_name}"
    if [[ ! -f "${checksum_path}" ]]; then
      download_file "${dir_url}${checksum_name}" "${checksum_path}"
    fi
    if [[ -n "$(checksum_hash_for_image "${checksum_path}" "${image_name}")" ]]; then
      break
    fi
    checksum_name=""
  done

  [[ -n "${checksum_name}" ]] || die "No CHECKSUM file in ${dir_url} contains ${image_name}"

  image_path="${cache_dir}/${image_name}"
  checksum_path="${cache_dir}/${checksum_name}"

  if [[ ! -f "${image_path}" ]]; then
    download_file "${dir_url}${image_name}" "${image_path}"
  fi

  if ! verify_image_checksum "${image_path}" "${checksum_path}"; then
    log "Checksum verification failed for cached image; re-downloading"
    rm -f "${image_path}" "${checksum_path}"
    download_file "${dir_url}${checksum_name}" "${checksum_path}"
    download_file "${dir_url}${image_name}" "${image_path}"
    verify_image_checksum "${image_path}" "${checksum_path}"
  fi
  make_qemu_system_readable "${checksum_path}" "${image_path}"

  base_image="${image_path}"
}

resolve_base_image() {
  if [[ -n "${base_image}" ]]; then
    [[ -f "${base_image}" ]] || die "Base image not found: ${base_image}"
    return 0
  fi

  resolve_auto_base_image
}

default_libvirt_uri() {
  if [[ -S /run/libvirt/libvirt-sock || -S /var/run/libvirt/libvirt-sock ]]; then
    printf 'qemu:///system\n'
  else
    printf 'qemu:///session\n'
  fi
}

init_libvirt_arg_arrays() {
  virsh_args=()
  virt_install_args=()
  if [[ -n "${libvirt_uri}" ]]; then
    virsh_args+=(--connect "${libvirt_uri}")
    virt_install_args+=(--connect "${libvirt_uri}")
  fi
}

enable_sudo_for_system_libvirt_if_available() {
  if [[ "${libvirt_uri}" != "qemu:///system" || "${EUID}" -eq 0 ]]; then
    return 0
  fi

  if ! command -v sudo >/dev/null 2>&1; then
    log "sudo not found; proceeding without sudo helper (you may see repeated authentication prompts)"
    return 0
  fi

  log "Acquiring sudo credentials for system libvirt access (single prompt)"
  sudo -v || die "Failed to acquire sudo credentials for qemu:///system access"
  sudo_prefix=(sudo)

  (
    while true; do
      sudo -n true >/dev/null 2>&1 || exit 0
      sleep 60
    done
  ) &
  sudo_keepalive_pid="$!"
}

maybe_auto_select_osinfo_value() {
  local rel list
  local -a candidates=()

  if [[ "${osinfo_explicit}" -eq 1 ]]; then
    return 0
  fi

  rel="$(normalize_release_label "${release_label}")"
  case "${rel}" in
    rawhide)
      candidates=(fedorarawhide fedora-rawhide)
      ;;
    [0-9]*)
      candidates=("fedora${rel}" "fedora-${rel}")
      ;;
    *)
      candidates=()
      ;;
  esac

  [[ ${#candidates[@]} -gt 0 ]] || return 0

  list="$(virt-install --osinfo list 2>/dev/null || true)"
  [[ -n "${list}" ]] || return 0

  local candidate
  for candidate in "${candidates[@]}"; do
    if awk '{print $1}' <<<"${list}" | grep -Fxq "${candidate}"; then
      osinfo_value="${candidate}"
      log "Auto-selected virt-install --osinfo ${osinfo_value}"
      return 0
    fi
  done
}

apply_default_workdir_for_libvirt() {
  if [[ "${workdir_explicit}" -eq 1 || -n "${KVM_SMOKE_WORKDIR:-}" ]]; then
    return 0
  fi

  if [[ "${libvirt_uri}" == "qemu:///system" ]]; then
    workdir="${system_default_workdir}"
  else
    workdir="${repo_default_workdir}"
  fi
}

ensure_qemu_system_dir_traversable() {
  [[ "${libvirt_uri}" == "qemu:///system" ]] || return 0

  local path
  for path in "$@"; do
    [[ -n "${path}" && -d "${path}" ]] || continue
    chmod 0711 "${path}" 2>/dev/null || true
  done
}

make_qemu_system_readable() {
  [[ "${libvirt_uri}" == "qemu:///system" ]] || return 0

  local path
  for path in "$@"; do
    [[ -n "${path}" && -e "${path}" ]] || continue
    chmod 0644 "${path}" 2>/dev/null || true
  done
}

init_run_layout() {
  mkdir -p "${workdir}/runs"
  run_id="$(date +%Y%m%d-%H%M%S)"
  run_dir="${workdir}/runs/${vm_name}-${run_id}"
  mkdir -p "${run_dir}"
  ensure_qemu_system_dir_traversable "${workdir}" "${workdir}/runs" "${run_dir}"

  overlay_img="${run_dir}/${vm_name}.qcow2"
  seed_img="${run_dir}/${vm_name}-seed.iso"
  user_data="${run_dir}/user-data"
  meta_data="${run_dir}/meta-data"
  ssh_key="${run_dir}/id_ed25519"
  ssh_pub="${ssh_key}.pub"
  remote_log="${run_dir}/remote-smoke.log"
  host_log="${run_dir}/host-summary.log"

  exec > >(tee -a "${host_log}") 2>&1
  trap cleanup EXIT
}

# Defaults
default_copr_owner="mineiro"
default_copr_project="hyprland"
repo_default_workdir="${repo_root}/.cache/kvm-smoke"
system_default_workdir="/var/tmp/hyprland-rpms-kvm-smoke"

copr_owner="${COPR_OWNER:-${default_copr_owner}}"
copr_project="${COPR_PROJECT:-${default_copr_project}}"
base_image=""
release_label="44"
vm_name=""
ssh_user="fedora"
memory_mib="4096"
vcpus="4"
disk_size_gb="30"
libvirt_network="default"
libvirt_uri=""
graphics_mode="none"
osinfo_value="detect=on,require=off"
osinfo_explicit=0
timeout_sec="600"
workdir="${KVM_SMOKE_WORKDIR:-${repo_default_workdir}}"
workdir_explicit=0
keep_vm=0
run_id=""
run_dir=""
overlay_img=""
seed_img=""
user_data=""
meta_data=""
ssh_key=""
ssh_pub=""
remote_log=""
host_log=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner)
      copr_owner="${2:-}"
      shift 2
      ;;
    --project)
      copr_project="${2:-}"
      shift 2
      ;;
    --base-image)
      base_image="${2:-}"
      shift 2
      ;;
    --release)
      release_label="${2:-}"
      shift 2
      ;;
    --vm-name)
      vm_name="${2:-}"
      shift 2
      ;;
    --ssh-user)
      ssh_user="${2:-}"
      shift 2
      ;;
    --memory-mib)
      memory_mib="${2:-}"
      shift 2
      ;;
    --vcpus)
      vcpus="${2:-}"
      shift 2
      ;;
    --disk-size-gb)
      disk_size_gb="${2:-}"
      shift 2
      ;;
    --network)
      libvirt_network="${2:-}"
      shift 2
      ;;
    --connect)
      libvirt_uri="${2:-}"
      shift 2
      ;;
    --graphics)
      graphics_mode="${2:-}"
      shift 2
      ;;
    --osinfo)
      osinfo_value="${2:-}"
      osinfo_explicit=1
      shift 2
      ;;
    --timeout-sec)
      timeout_sec="${2:-}"
      shift 2
      ;;
    --workdir)
      workdir="${2:-}"
      workdir_explicit=1
      shift 2
      ;;
    --keep-vm)
      keep_vm=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

if [[ -z "${vm_name}" ]]; then
  vm_name="$(default_vm_name "${release_label}")"
fi

require_cmd virt-install
require_cmd virsh
require_cmd qemu-img
require_cmd cloud-localds
require_cmd ssh
require_cmd curl
require_cmd sha256sum
require_cmd awk
require_cmd grep
require_cmd sed
require_cmd sort
require_cmd head
require_cmd tail
require_cmd date
require_cmd ssh-keygen

virsh_args=()
virt_install_args=()

vm_created=0
vm_ip=""
logs_collected=0

cleanup() {
  local rc=$?

  if [[ -n "${sudo_keepalive_pid}" ]]; then
    kill "${sudo_keepalive_pid}" >/dev/null 2>&1 || true
  fi

  if [[ -n "${vm_ip}" && "${logs_collected}" -eq 0 ]]; then
    collect_remote_logs "${vm_ip}" || true
  fi

  if [[ "${keep_vm}" -eq 0 && "${vm_created}" -eq 1 ]]; then
    log "Destroying and undefining VM ${vm_name}"
    run_virsh "${virsh_args[@]}" destroy "${vm_name}" >/dev/null 2>&1 || true
    run_virsh "${virsh_args[@]}" undefine "${vm_name}" --nvram >/dev/null 2>&1 || \
      run_virsh "${virsh_args[@]}" undefine "${vm_name}" >/dev/null 2>&1 || true
  elif [[ "${vm_created}" -eq 1 ]]; then
    log "Keeping VM ${vm_name} (--keep-vm)"
  fi

  if [[ $rc -ne 0 ]]; then
    log "Smoke test failed. Collected artifacts: ${run_dir}"
  else
    log "Smoke test complete. Collected artifacts: ${run_dir}"
  fi

  exit $rc
}

domain_exists() {
  run_virsh "${virsh_args[@]}" dominfo "${vm_name}" >/dev/null 2>&1
}

network_exists() {
  run_virsh "${virsh_args[@]}" net-info "${libvirt_network}" >/dev/null 2>&1
}

network_is_active() {
  run_virsh "${virsh_args[@]}" net-info "${libvirt_network}" 2>/dev/null \
    | awk -F: '/^Active:/ {gsub(/^[[:space:]]+/, "", $2); gsub(/[[:space:]]+$/, "", $2); print $2; exit}' \
    | grep -qi '^yes$'
}

ensure_libvirt_network() {
  local net_start_err

  if ! network_exists; then
    if [[ "${libvirt_uri}" == "qemu:///session" ]]; then
      die "Libvirt network '${libvirt_network}' not found on ${libvirt_uri}. Try --connect qemu:///system (recommended) and ensure the network exists, or pass a different --network."
    fi
    die "Libvirt network '${libvirt_network}' not found on ${libvirt_uri}. Create/start it (for example: sudo virsh net-start ${libvirt_network})."
  fi

  if network_is_active; then
    return 0
  fi

  log "Starting libvirt network ${libvirt_network}"
  if ! net_start_err="$(run_virsh "${virsh_args[@]}" net-start "${libvirt_network}" 2>&1)"; then
    if grep -qi 'already active' <<<"${net_start_err}"; then
      log "Libvirt network ${libvirt_network} is already active"
      return 0
    fi
    if [[ -n "${net_start_err}" ]]; then
      while IFS= read -r line; do
        [[ -n "${line}" ]] || continue
        printf '[kvm-smoke] virsh net-start: %s\n' "${line}" >&2
      done <<<"${net_start_err}"
    fi
    die "Libvirt network '${libvirt_network}' exists but could not be started on ${libvirt_uri}. Check the error lines above (common causes: missing dnsmasq/libvirt network packages, stale virbr0 bridge, or disabled libvirt network daemon)."
  fi
  run_virsh "${virsh_args[@]}" net-autostart "${libvirt_network}" >/dev/null 2>&1 || true
}

wait_for_ip() {
  local deadline now candidate
  deadline=$((SECONDS + timeout_sec))

  while (( SECONDS < deadline )); do
    candidate="$(
      run_virsh "${virsh_args[@]}" domifaddr "${vm_name}" --source lease 2>/dev/null \
        | awk '/ipv4/ {sub(/\/.*/, "", $4); print $4; exit}'
    )"
    if [[ -z "${candidate}" ]]; then
      candidate="$(
        run_virsh "${virsh_args[@]}" domifaddr "${vm_name}" --source agent 2>/dev/null \
          | awk '/ipv4/ {sub(/\/.*/, "", $4); print $4; exit}'
      )"
    fi
    if [[ -n "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
    sleep 5
  done

  return 1
}

wait_for_ssh() {
  local ip="$1"
  local -a opts
  local deadline
  mapfile -t opts < <(ssh_opts "${ssh_key}")
  deadline=$((SECONDS + timeout_sec))

  while (( SECONDS < deadline )); do
    if ssh "${opts[@]}" "${ssh_user}@${ip}" 'true' >/dev/null 2>&1; then
      return 0
    fi
    sleep 5
  done
  return 1
}

collect_remote_logs() {
  local -a opts
  local ip="$1"
  logs_collected=1
  mapfile -t opts < <(ssh_opts "${ssh_key}")

  log "Collecting VM logs from ${ip}"
  run_virsh "${virsh_args[@]}" dumpxml "${vm_name}" > "${run_dir}/${vm_name}.xml" 2>/dev/null || true

  ssh "${opts[@]}" "${ssh_user}@${ip}" \
    'sudo journalctl -b --no-pager' > "${run_dir}/journalctl-boot.log" 2>&1 || true

  ssh "${opts[@]}" "${ssh_user}@${ip}" \
    "sudo bash -lc 'journalctl --user -b --no-pager || true'" \
    > "${run_dir}/journalctl-user.log" 2>&1 || true

  ssh "${opts[@]}" "${ssh_user}@${ip}" \
    'sudo dnf repolist --all' > "${run_dir}/dnf-repolist.log" 2>&1 || true

  ssh "${opts[@]}" "${ssh_user}@${ip}" \
    'rpm -q hyprland hyprland-uwsm xdg-desktop-portal-hyprland uwsm' \
    > "${run_dir}/rpm-q.log" 2>&1 || true
}

write_cloud_init() {
  local pubkey
  pubkey="$(cat "${ssh_pub}")"

  cat > "${user_data}" <<EOF
#cloud-config
users:
  - name: ${ssh_user}
    gecos: ${ssh_user}
    groups: [wheel]
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    shell: /bin/bash
    lock_passwd: true
    ssh_authorized_keys:
      - ${pubkey}
ssh_pwauth: false
package_update: false
runcmd:
  - [ sh, -c, 'echo kvm-smoke cloud-init ready > /var/tmp/kvm-smoke-ready' ]
EOF

  cat > "${meta_data}" <<EOF
instance-id: ${vm_name}-${run_id}
local-hostname: ${vm_name}
EOF
}

create_overlay_disk() {
  local base_abs
  base_abs="$(cd "$(dirname "${base_image}")" && pwd)/$(basename "${base_image}")"
  log "Creating overlay disk from ${base_abs}"
  qemu-img create -f qcow2 -F qcow2 -b "${base_abs}" "${overlay_img}" >/dev/null
  qemu-img resize "${overlay_img}" "${disk_size_gb}G" >/dev/null
  make_qemu_system_readable "${overlay_img}"
}

ensure_ssh_key() {
  log "Generating ephemeral SSH key"
  ssh-keygen -q -t ed25519 -N '' -f "${ssh_key}" >/dev/null
}

create_seed_iso() {
  log "Creating cloud-init seed image"
  cloud-localds "${seed_img}" "${user_data}" "${meta_data}" >/dev/null
  make_qemu_system_readable "${seed_img}"
}

create_vm() {
  local -a args
  args=(
    "${virt_install_args[@]}"
    --name "${vm_name}"
    --memory "${memory_mib}"
    --vcpus "${vcpus}"
    --import
    --noautoconsole
    --graphics "${graphics_mode}"
    --osinfo "${osinfo_value}"
    --network "network=${libvirt_network},model=virtio"
    --disk "path=${overlay_img},format=qcow2,bus=virtio"
    --disk "path=${seed_img},device=cdrom"
  )

  if [[ "${graphics_mode}" == "none" ]]; then
    args+=(--serial pty --console pty,target_type=serial)
  fi

  log "Creating VM ${vm_name}"
  run_virt_install "${args[@]}"
  vm_created=1
}

wait_for_boot() {
  log "Waiting for VM IP address"
  vm_ip="$(wait_for_ip)" || die "Timed out waiting for VM IP address"
  log "VM IP address: ${vm_ip}"

  log "Waiting for SSH on ${ssh_user}@${vm_ip}"
  wait_for_ssh "${vm_ip}" || die "Timed out waiting for SSH"

  local -a opts
  mapfile -t opts < <(ssh_opts "${ssh_key}")

  log "Waiting for cloud-init (best effort)"
  ssh "${opts[@]}" "${ssh_user}@${vm_ip}" \
    'cloud-init status --wait || true' >/dev/null 2>&1 || true
}

run_remote_smoke() {
  local -a opts
  mapfile -t opts < <(ssh_opts "${ssh_key}")

  log "Running remote headless smoke checks"
  ssh "${opts[@]}" "${ssh_user}@${vm_ip}" \
    "sudo bash -s -- '${copr_owner}' '${copr_project}' '${ssh_user}'" \
    >"${remote_log}" 2>&1 <<'EOF'
set -euo pipefail

owner="$1"
project="$2"
login_user="$3"

cat > /etc/yum.repos.d/copr-hyprland.repo <<REPO
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
REPO

dnf -y --refresh install --setopt=install_weak_deps=0 --nodocs \
  hyprland hyprland-uwsm xdg-desktop-portal-hyprland uwsm

rpm -q hyprland hyprland-uwsm xdg-desktop-portal-hyprland uwsm

command -v Hyprland >/dev/null
command -v hyprctl >/dev/null
command -v hyprpm >/dev/null
command -v hyprland-share-picker >/dev/null
command -v uwsm >/dev/null
command -v uwsm-app >/dev/null
command -v uuctl >/dev/null
command -v fumon >/dev/null

test -f /usr/share/wayland-sessions/hyprland.desktop
test -f /usr/share/wayland-sessions/hyprland-uwsm.desktop
test -f /usr/share/dbus-1/services/org.freedesktop.impl.portal.desktop.hyprland.service
test -f /usr/share/xdg-desktop-portal/portals/hyprland.portal
test -f /usr/lib/systemd/user/fumon.service
ls /usr/lib/systemd/user/wayland-*.service >/dev/null
ls /usr/lib/systemd/user/wayland-*.target >/dev/null

systemctl --version >/dev/null
loginctl --version >/dev/null

# Best-effort user manager probe in a real VM; this may still fail if no user
# manager is active for the SSH session. Keep this non-fatal for headless stage.
if command -v loginctl >/dev/null 2>&1; then
  loginctl enable-linger "${login_user}" || true
fi

if runuser -u "${login_user}" -- bash -lc \
  'systemctl --user --no-pager list-unit-files "fumon.service" "wayland-*.service" "wayland-*.target"' \
  >/dev/null 2>&1; then
  echo "systemctl --user probe: OK"
else
  echo "systemctl --user probe: skipped/failed (non-fatal in headless stage)" >&2
fi

hyprpm --help >/dev/null
uwsm --help >/dev/null
uuctl --help >/dev/null
EOF

  log "Remote smoke checks passed (see ${remote_log})"
}

main() {
  if [[ -z "${libvirt_uri}" ]]; then
    libvirt_uri="$(default_libvirt_uri)"
  fi
  apply_default_workdir_for_libvirt
  enable_sudo_for_system_libvirt_if_available
  init_libvirt_arg_arrays
  init_run_layout
  maybe_auto_select_osinfo_value

  log "Run directory: ${run_dir}"
  log "Workdir: ${workdir}"
  log "Target COPR: ${copr_owner}/${copr_project}"
  log "VM name: ${vm_name}"
  log "Libvirt URI: ${libvirt_uri}"
  log "virt-install --osinfo: ${osinfo_value}"

  resolve_base_image
  log "Base image: ${base_image}"

  if domain_exists; then
    die "A libvirt domain named ${vm_name} already exists (use --vm-name or remove it first)"
  fi

  ensure_libvirt_network

  ensure_ssh_key
  write_cloud_init
  create_overlay_disk
  create_seed_iso
  create_vm
  wait_for_boot
  run_remote_smoke
  collect_remote_logs "${vm_ip}"

  log "Headless KVM smoke test passed"
}

main "$@"
