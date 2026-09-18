# 01 | Build the Linux and Docker foundation

## Original project and learning goal

The original small-form-factor Debian server hosts multiple independent Docker
services. The important skill is not the make of computer: it is separating the
operating system, application configuration, writable data and recovery copies.
This exercise creates a fresh version of that foundation.

For planning, allow roughly 2 CPU cores and 4 GB RAM for a small subset of the
examples, or 8 GB for the core exercises with more headroom. These are classroom
planning estimates, not measured requirements or a promise of performance.
Immich has its own heavier requirements; do not assume it will fit comfortably
beside every other service. Start with one project at a time.

## Step 1 - Install a separate lab machine

Install a supported Debian release on a disposable VM or spare computer. The
reference target is Debian 13. Select an ordinary user account and SSH if remote
administration is needed. Use a non-identifying hostname such as `lab-host`.
Read every disk-selection screen: installing an operating system can erase the
selected disk. Do not practise partitioning on a disk containing the only copy
of your files.

After installation, run the following **on the lab server**, not on a Windows
PowerShell prompt:

```bash
sudo apt update
sudo apt upgrade
sudo apt install ca-certificates curl git openssl python3 jq
cat /etc/os-release
free -h
df -h
```

`apt update` refreshes package information; `apt upgrade` applies available
updates. `free` shows memory and `df` shows mounted filesystem capacity. Keep
full outputs private: device names, usernames and mount paths can identify the
real setup. Your public report can record a general capacity and the release.

## Step 2 - Install Docker from its supported repository

Use Docker's current Debian instructions, reference S01. On a fresh Debian
machine, its repository setup can be performed as follows. Do not use this as
an automatic migration script for an already-running container host.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf '%s\n' 'Types: deb' \
  'URIs: https://download.docker.com/linux/debian' \
  "Suites: $VERSION_CODENAME" 'Components: stable' \
  "Architectures: $(dpkg --print-architecture)" \
  'Signed-By: /etc/apt/keyrings/docker.asc' | \
  sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo docker run --rm hello-world
sudo docker compose version
```

The test container should print its success message and exit. The Compose
command must exist. These instructions retain `sudo` rather than granting an
ordinary account Docker-group access: control of a rootful Docker daemon is
highly privileged. Do not treat a Docker-group account as unprivileged. [S01, S02]

## Step 3 - Place the teaching repository on the server

Extract `class-project-pack` into your lab user's home folder. When working on a
separate laptop, transfer this sanitised folder through your authorised SSH
connection. Do not substitute a copy of your original server configuration.
The directory containing README.md is the repository root.

```bash
cd ~/class-project-pack
python3 scripts/init_env.py
cd labs/core
```

The helper reads `.env.example`, generates two independent passwords and writes
an untracked `.env` with restrictive file permissions. It refuses to overwrite
an existing one. An environment file keeps secrets out of committed examples;
it is not an encrypted secret store. Root and the Docker administrator can still
access service configuration. Do not post `docker inspect` or fully expanded
Compose output to a public issue.

## Step 4 - Check networking and freeze the images

The illustrative Nextcloud proxy network uses `172.28.250.0/24`. Inspect your
existing routes and Docker networks privately before first deployment. When
there is an overlap, change `NC_FRONT_SUBNET`, `CADDY_NC_IP` and
`NEXTCLOUD_NC_IP` together to an unused private subnet. This is not the author's
real network and must not be blindly copied into an existing environment.

```bash
ip route
sudo docker network ls
sudo docker compose config -q
sudo docker compose config --lock-image-digests -o compose.images.yaml
```

`config -q` checks the model without printing interpolated secrets. The lock
command creates an image-digest override. The supplied `lab.sh` automatically
uses that override for subsequent commands. Initial image tags are convenient
channels, not immutable versions: record the resolved digests in your version
record. Do not replace a database major version on an existing data directory
without the database's supported migration procedure. [S03]

## Step 5 - Start the small core

```bash
sudo ./lab.sh up -d caddy vaultwarden uptime-kuma
sudo ./lab.sh ps
sudo ./lab.sh logs --tail 30 caddy
```

Logs stay private until reviewed. Vaultwarden starts with registrations disabled.
Nextcloud is deliberately started later, after access and HTTPS are understood.
All application data lives under the ignored `labs/core/data/` directory. A
container can be recreated without losing bind-mounted data, but deleting that
directory will remove the actual application state.

The only published web port is `127.0.0.1:8443`. Docker-published ports can
interact unexpectedly with host firewall tools, so this lab does not rely only
on a reassuring firewall status message. Verify the actual binding and perform
a negative reachability test. [S01]

## Checkpoint

Docker's test succeeded, the Compose model validates, the selected image digests
were recorded, and the three services are running. A browser on another machine
cannot open the web apps yet; this is expected until chapters 02-03 establish
the authorised path.

**Common failures:** a missing Compose plugin; lack of disk space; a subnet
collision; a port already in use; or using the wrong operating system's package
instructions. Diagnose the stated error rather than disabling the firewall or
using `chmod -R 777`.

**References:** S01-S03; original project context P01.
