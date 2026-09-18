#!/usr/bin/env bash
# Cold encrypted backup. Supply an ALREADY INITIALISED external restic repository.
# Usage: sudo scripts/backup_core.sh /mnt/backup/classlab /root/.config/classlab/restic-pass
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo so all application files can be read.' >&2; exit 2; }
[[ $# -eq 2 ]] || { echo 'Usage: backup_core.sh REPOSITORY PASSWORD_FILE' >&2; exit 2; }
command -v restic >/dev/null
repo=$(realpath -e -- "$1")
pass=$(realpath -e -- "$2")
[[ -d "$repo" && -f "$pass" ]] || { echo 'Invalid repository/password file.' >&2; exit 2; }
core=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../labs/core" && pwd -P)
case "$repo/" in "$core/"*) echo 'Repository must be outside the source tree.' >&2; exit 2;; esac
case "$pass" in "$core/"*) echo 'Keep the restic password outside the backup source.' >&2; exit 2;; esac
export RESTIC_REPOSITORY="$repo" RESTIC_PASSWORD_FILE="$pass"
# Fail before stopping applications if the repository cannot be opened.
restic snapshots --latest 1 >/dev/null
cd -- "$core"
running=()
# Capture the command first so a Compose error aborts before any service stops.
running_output=$(./lab.sh ps --services --status running)
if [[ -n "$running_output" ]]; then
  mapfile -t running <<< "$running_output"
fi
resume() {
  local rc=$?
  trap - EXIT
  if (( ${#running[@]} )); then
    ./lab.sh start "${running[@]}" || { echo 'IMPORTANT: failed to restart a service.' >&2; exit 3; }
  fi
  exit "$rc"
}
trap resume EXIT
./lab.sh stop
restic backup "$core" --tag classlab-cold
printf '
Backup finished. Check snapshots and perform a separate restore drill.
'
