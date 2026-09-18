# Validation record for classroom edition 1.1

Prepared 17 September 2026. This record describes checks performed on the
teaching pack. It is not a security certification, penetration test or claim
that the original homelab or the supplied deployments were audited here.

## Checks completed

| Check | Result and scope |
| --- | --- |
| Python unit suite | 28 tests passed: 8 binding checks, 4 hardening-template checks, 11 proxy-template checks, 4 staged-publication checks and 1 secret-initialiser check |
| Python and Bash syntax | All supplied Python files parsed; `lab.sh` and `backup_core.sh` passed `bash -n` |
| Core configuration | YAML parsed; the only published core port is `127.0.0.1:8443:443`; no privileged mode, host networking or Docker socket mounts |
| Proxy examples | Both JSON examples parsed; the server example passed the limited policy helper; the separate TLS-target Compose example parsed as YAML |
| Secret initialiser | In a temporary copy, generated distinct passwords, used mode 0600, did not print values and refused overwrite |
| Publication helper | Disposable Git tests rejected a staged `.env`, filled client profile and synthetic token without echoing the token; a harmless README passed |
| Final package review | The staged package passed its limited publication helper; obsolete project files and references were removed; Markdown links and source identifiers were reviewed |
| PDF review | Both PDFs were rebuilt, their extracted text, links and metadata checked, and rendered pages reviewed for layout and residual identifying content |

Checks used Python 3.13 on Linux. The helper scripts target Python 3.11 or
newer; other platforms and Python releases have not been exhaustively tested.
Template assertions test selected properties only. They cannot establish that
a daemon accepts a configuration or that packets follow its intended policy.

## Not tested during preparation

Docker Engine/Compose deployments, image pulls, Caddy runtime validation and
application start-up were not run. YAML parsing is **not** equivalent to
`docker compose config` or a successful service deployment. Image digests and
installed application versions have not been fabricated.

The Xray binary was not available for its own configuration test. REALITY
handshakes, NetBird enrolment and policy enforcement, Mullvad/WireGuard egress,
firewall rule loading and persistence, systemd start-up, SSH effective settings,
and deliberate tunnel-failure tests were not executed here. These are explicit
lab verification tasks. The template helper is not a complete Xray schema,
credential, cryptographic or network-security validator.

Certificate installation, Vaultwarden/Nextcloud/Immich account workflows,
AdGuard filtering, real monitoring alerts, phone uploads and encrypted
backup/restore were not exercised against live services. Whole-device TUN,
DNS, UDP and IPv6 behaviour have not been certified. No live infrastructure or
remote repository was modified for this revision.

The original project's hardening is described as reported project history.
Additional SSH, firewall and proxy examples are separate teaching adaptations,
not evidence that those exact configurations were deployed on the author's
systems. See chapter 00 for the distinction.

## Repeat and extend the checks

From the repository root:

```bash
python3 -m unittest discover -s tests -v
bash -n labs/core/lab.sh scripts/backup_core.sh
python3 scripts/check_proxy.py labs/proxy/server.json.example
```

On a fresh lab, perform the real program-specific checks before starting a
service: quiet Compose validation, Caddy validation, `sshd -t` and effective
configuration checks, `nft -c -f`, and the selected Xray core's `run -test`.
Keep expanded configuration and output containing credentials private.

Then record both allow and deny tests, interruption and recovery results, and
a separate-target restore. Use `VERSION-RECORD.md` and the chapter 12 worksheet.
An expected result is not an observed result; mark unperformed checks as such.
