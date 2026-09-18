# 11 | Encrypted backups and a real restore drill

## Original lesson: storage budgets are not recovery

The original file/photo work used separate allocations and planned backup
space. That is useful capacity management, but a second directory on the same
physical disk is not protection against losing that disk. A quota, mirror,
recycle bin, synchronised client and recoverable backup solve different problems.

This classroom exercise stops the small core stack and uses restic to make an
encrypted backup. It is a deliberately simple cold-backup method, accepting
brief downtime instead of pretending that a live file copy guarantees database
consistency. It covers `labs/core`, **not the separate Immich or NetBird stacks**.
Use their own matching-version recovery instructions for those services.

## Step 1 - Identify the complete recovery set

The core directory contains the application files, PostgreSQL data, Vaultwarden
state, Kuma state, Caddy's private CA material, configuration, image lock, site
files and `.env`. All of those can be sensitive. The backup is not suitable for
upload to GitHub just because the archive is compressed.

Redis is configured as a non-persistent cache for this exercise. The authoritative
file and database state belongs to the applications. The cold backup preserves
PostgreSQL's physical data, so restore with the recorded compatible image and
major version before attempting upgrades. [S12]

## Step 2 - Prepare a genuinely separate destination

Use a mounted external drive or another appropriately protected repository.
For the example commands, `/mnt/backup` is an already-mounted destination.
This guide does not partition or format it. Check that the intended backup
filesystem is actually mounted; a missing mount can cause writes to land on the
same system disk you thought you were protecting.

Install restic on the lab server and create a private password file:

```bash
sudo apt install restic
mountpoint /mnt/backup
sudo install -d -m 700 /root/.config/classlab
sudo sh -c 'set -C; umask 077; openssl rand -hex 32 > /root/.config/classlab/restic-pass'
```

Stop if the mount check does not identify the intended mounted destination.
`set -C` prevents overwriting an existing password file: changing it blindly can
make old backups inaccessible. Keep an additional secure recovery copy of the
password somewhere separate from the server and backup disk. Never publish it.

Initialise a new restic repository once:

```bash
sudo restic -r /mnt/backup/classlab \
  -p /root/.config/classlab/restic-pass init
```

The repository is encrypted using restic's supported design. Encryption does
not remove the need for access control, a recoverable password and a destination
that survives the relevant failure. [S19]

## Step 3 - Run the stopped-stack backup

From the repository root on the lab server:

```bash
sudo scripts/backup_core.sh \
  /mnt/backup/classlab /root/.config/classlab/restic-pass
```

The helper verifies the repository can be opened before stopping services. It
records which core services were running, stops the stack, backs up the core
folder, and attempts to restart only the previously running services even when
the backup fails. A failure remains a failure: the script does not label a
partial or interrupted backup successful.

Read its output privately. The backup tool can show hostnames and paths. Verify
that the applications restarted and that the command exit status was successful.
A script saying it “started a backup” would not prove one was completed.

## Step 4 - Verify and restore into a new location

List snapshots and check the repository:

```bash
sudo restic -r /mnt/backup/classlab \
  -p /root/.config/classlab/restic-pass snapshots
sudo restic -r /mnt/backup/classlab \
  -p /root/.config/classlab/restic-pass check
```

Choose an actual snapshot ID from your own output. On an isolated recovery VM
or a new empty test location, restore it using the recorded ID:

```bash
SNAPSHOT_ID='REPLACE_WITH_YOUR_SNAPSHOT_ID'
sudo restic -r /mnt/backup/classlab \
  -p /root/.config/classlab/restic-pass \
  restore "$SNAPSHOT_ID" --target /srv/classlab-restore-test
```

Do not restore over the working source to “test” your only backup. The restored
files appear below the target with their recorded directory structure. Locate
the restored core folder, inspect it and retain its matching `.env` and image
lock. On a separate VM, start only the services you need to verify recovery.
Use a new SSH tunnel to that VM; do not run two stacks on the same conflicting
loopback port or connect the restored service to production clients.

## Step 5 - Prove application-level recovery

A successful archive extraction is not the final test. Log into the restored
fake vault and read the demo item. Log into Nextcloud and download the test
files. Compare their hashes with the known originals. Confirm the normal user
still cannot see another user's private files. Check that the monitoring
configuration and HTTPS health endpoint also work.

Record the snapshot, matching images, restore steps and actual verification.
Do not record the passwords. Only after a successful drill should you describe
the backup process as tested for that particular scenario.

## Retention and other services

This edition does not schedule destructive retention or pruning commands.
Plan retention after measuring how much data changes, how much recovery history
is needed and how much space is available. Monitor failed backups and perform
periodic restores; a growing directory of untested archives is weak evidence.

For Nextcloud live backups, follow its documented maintenance/database method.
For Immich, back up the database plus media using the selected release's
instructions. For NetBird, preserve its identity/configuration state through
its documented maintenance procedure. Never call the core-only script a backup
of the entire homelab. [S04, S12, S15]

**References:** S12, S15, S19-S20.
