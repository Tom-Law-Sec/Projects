# TomSec | Cybersecurity Homelab Projects

**Classroom edition 1.1 - 17 September 2026**

A sanitised, GitHub-ready learning pack centred on a hardened homelab,
self-hosted services and a custom privacy proxy. It documents the security
purpose of each component, provides separate lab examples and shows how to
test access controls, failure behaviour and recovery.

**Start with [the handbook](pdf/TomSec_Cybersecurity_Handbook.pdf) or
[the project overview](pdf/TomSec_Cybersecurity_Project_Overview.pdf).**

These are teaching configurations, not an export of the author's servers.
Use a fresh VM, your own accounts and disposable data. Real endpoints,
private keys, proxy profiles and production configuration are not included.

## Projects and security objectives

| Project | Security objective | Guide |
| --- | --- | --- |
| Linux and Docker homelab | Understand privilege, persistence and attack surface | [01](docs/01-foundation.md) |
| Self-hosted NetBird | Separate device enrolment, network access and app login | [02](docs/02-netbird.md) |
| Private HTTPS with Caddy | Encrypt access and verify the correct server | [03](docs/03-https.md) |
| Vaultwarden | Close registration, disable server admin and practise MFA/recovery | [04](docs/04-vaultwarden.md) |
| Nextcloud with PostgreSQL and Redis | Isolate data services and verify trust, quotas and permissions | [05](docs/05-nextcloud.md) |
| Immich | Control photo-library access and understand its recovery set | [06](docs/06-immich.md) |
| Security monitoring and DNS filtering | Detect outages, review logs privately and test DNS policy | [07](docs/07-monitoring.md) |
| Host and container hardening | Key-based SSH, private administration and exposure reduction | [08](docs/08-hardening.md) |
| Custom Xray/REALITY proxy | Separate Mullvad internet egress from authorised NetBird destinations | [09](docs/09-privacy-routing.md) |
| Ingress and access-control verification | Distinguish public app access from private management | [10](docs/10-access-verification.md) |
| Backup and restore | Recover a usable service, not just produce an archive | [11](docs/11-backup.md) |
| Safe sharing | Publish examples and evidence without operational secrets | [12](docs/12-sharing.md) |

[Scope and provenance](docs/00-scope.md) distinguish reported original work from
new classroom hardening measures. The proxy chapter includes server/client
configuration templates, selective WireGuard egress, a narrow egress guard,
and a connection-failure test matrix. It is not a copy of a live proxy profile.

## Begin with the private homelab

Follow chapters 01-03 in order on a fresh Debian lab. The core stack binds
HTTPS only to server loopback; reach it using the documented SSH local forward.
No paid VPS is needed for this first local exercise. Self-hosted NetBird and the
advanced proxy exercise require additional machines/accounts and may incur costs.

From the extracted repository root on the lab server:

```bash
python3 scripts/init_env.py
cd labs/core
sudo docker compose config -q
sudo docker compose config --lock-image-digests -o compose.images.yaml
sudo ./lab.sh up -d caddy vaultwarden uptime-kuma
```

The browser names, CA verification and SSH tunnel in chapter 03 are required.
An HTTPS error before those steps is expected. Do not change a binding to
`0.0.0.0` merely to make an error disappear.

## Security checks without deployment

With Python 3.11 or newer, from the root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_proxy.py labs/proxy/server.json.example
```

These check examples and helper behaviour, not the live security of a server.
Run `scripts/check_bindings.py` against **normalised Compose JSON** as described
in the handbook, not against the YAML file itself. See [VALIDATION.md](VALIDATION.md)
for the exact authoring checks and untested deployment steps.

## Repository layout

```text
README.md                  Start here
pdf/                       Revised handbook and overview
docs/                      Editable Markdown chapters
diagrams/                  Mermaid source diagrams
labs/core/                 Private self-hosted application stack
labs/proxy/                Xray, WireGuard, TLS-target and guard templates
labs/hardening/            SSH baseline and narrow management guard
labs/immich/               Matching-release installation notes
scripts/                   Secret generation, checks and encrypted core backup
tests/                     Deterministic safety/configuration tests
SOURCES.md                 Primary technical references and provenance
VALIDATION.md              Checks actually performed
VERSION-RECORD.md          Record YOUR installed versions and results
```

## Privacy, licensing and publication

No production domains, server addresses, account handles, passwords, tokens,
private keys, original screenshots or personal media are supplied. Reference
URLs belong to upstream projects; illustrative addresses are not the author's.
No unauthorised-access exercises, copyrighted media bundles or licensing
bypasses are included. Proxy use must comply with the network owner's permission.

Use your own measured results and follow course attribution/assistance rules.
New teaching material is MIT-licensed; upstream applications keep their own
licenses. No remote repository or live server was changed for this edition.

## Rebuild the PDFs

The finished PDFs are included. The optional builder uses Python 3.13,
WeasyPrint 68.0 and markdown-it-py 4.2.0, with WeasyPrint's native dependencies
and DejaVu system fonts. No font files are bundled.

```bash
python3 tools/render_pdfs.py
```

Review the new PDFs and repeat publication checks after editing.
