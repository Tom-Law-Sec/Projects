# Reproducibility record - fill after YOUR build

The teaching pack is edition 1.1, prepared 2026-09-17. This blank record is not a
claim that the container stack was deployed or benchmarked during authoring.
Starting image tags in .env.example are lab channels. Lock digests before use.

| Component | Exact version / digest you used | Checked on | Result |
| --- | --- | --- | --- |
| Debian | Not recorded | | |
| Docker Engine | Not recorded | | |
| Docker Compose | Not recorded | | |
| Caddy | Not recorded | | |
| Vaultwarden | Not recorded | | |
| Nextcloud (web and cron must match) | Not recorded | | |
| PostgreSQL | Not recorded | | |
| Redis | Not recorded | | |
| Uptime Kuma | Not recorded | | |
| NetBird bootstrap checksum and versions | Keep private until reviewed | | |
| Immich release, Compose checksum and images | Not recorded | | |
| restic | Not recorded | | |
| OpenSSH / effective policy | Keep sensitive values private | | |
| nftables / guard and reboot test | Not recorded | | |
| Xray server core / archive SHA-256 | Not recorded | | |
| Xray client core / schema compatibility | Not recorded | | |
| WireGuard tools / egress test | No keys or endpoint IDs | | |
| AdGuard / Dozzle when used | Not recorded | | |

A reviewed image-only digest override can be shared to reproduce your tested
build. A full `docker compose config` dump can contain secrets and should not be
committed. Keep private hostnames and account information out of this record.
Do not replace a production database major image tag without a supported migration.
