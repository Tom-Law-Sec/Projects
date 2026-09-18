# 00 | Scope, original work and classroom evidence

## What these projects demonstrate

The focus is the security engineering behind a self-hosted homelab: reducing
unnecessary exposure, separating private administration from app access,
protecting credentials, choosing explicit network paths and proving recovery.
Installing a container is the start of a project, not its security conclusion.

The original environment used a small Debian host, Docker services and private
NetBird connectivity. Some applications were deliberately available remotely
through HTTPS. The custom Xray/REALITY setup separated private NetBird traffic
from internet traffic using Mullvad egress. Classroom examples recreate those
principles without reproducing the original addresses or secrets. [P01]

## Original implementation versus teaching controls

**Reported original work** means the project history describes the setting or
outcome. It is not a fresh audit. **Classroom adaptation** means a new example
or a safer, smaller reproduction. **Verification task** means the student must
run the test and record the actual result; the expected result is not evidence.

| Project or control | Basis in original work | Treatment in this edition |
| --- | --- | --- |
| Debian/Docker homelab | Multiple self-hosted services reported working | Fresh host with separate app networks and data paths |
| Private management | Self-hosted NetBird and NetBird-only SSH reported | Own mesh, explicit policies and independent SSH tests |
| Vaultwarden | Registration/admin disabled; Aegis two-factor setup reported | Fake vault, controlled enrolment, MFA and recovery exercise |
| Nextcloud | PostgreSQL, Redis, cron, proxy settings and DAV redirects reported | Separate lab with permission and persistence checks |
| Immich | HTTPS access and phone uploads reported | Independent photo lab; no original photos or library export |
| Application ingress | Cloudflare Tunnel for selected apps; separate VPS photo edge reported | Private baseline; public-ingress design and deny tests |
| Monitoring and DNS | Uptime Kuma, Dozzle and AdGuard used in the homelab | Actual service check, private log review and DNS-policy exercise |
| Custom proxy | Xray/REALITY, Mullvad egress and private NetBird routing reported | Fresh profiles and explicit, limited destination policy |
| Storage and recovery | Capacity allocations and local backups discussed/used | Encrypted off-source backup and isolated restore drill |

The supplied nftables guards, exact SSH snippet, restricted demo proxy policy
and automated checks are **new teaching examples**. Do not describe those exact
files, their thresholds or their test results as historical production settings.
The reference history does not establish a completed end-to-end leak audit,
universal kill switch or successful disaster-recovery drill.

## Deliberate differences from the original network

The core classroom apps are private by default, reached through an SSH tunnel.
This is intentionally narrower than a production system with selected public
apps. NetBird control and the custom proxy use separate VPS roles; neither is
installed over the other. The proxy begins with an explicit TCP application
proxy rather than immediately altering the learner's entire machine with TUN.

A single allowed lab peer and test port replace a broad real overlay route.
A dedicated, owned TLS target replaces any identifying transport destination.
Public egress has no configured direct-internet fallback. These choices make
failures and boundaries easier to test; they are not an anonymity guarantee.

## Information excluded from the public pack

Production service domains, host/overlay addresses, account identifiers,
credentials, client subscription links, private keys, recovery codes, exact
private paths, logs, screenshots, photos and media catalogues are not included.
`lab.test` and `example.com` names are placeholders. Generate transport keys,
application passwords and provider configuration in your own private workspace.

A proxy, VPN or self-hosted application is not inherently unlawful. The pack
teaches authorised deployment and testing only; unsuitable third-party data,
unlicensed assets and unauthorised-access material are excluded rather than
concealed. No live system is being opened to the class.

## Required evidence for each project

Record the aim and permission, component versions, the trust boundary, a working
positive test, an attempted denied action, one controlled failure and one
limitation. For data services, include a persistence or recovery check. Label
unperformed checks **not tested**. Keep full diagnostic output private and
share only a reviewed summary or a reconstruction using fictional values.

Start from a fresh VM or spare machine and keep console access before firewall
or authentication changes. The following chapters explain where each command
runs and how to recover from a failed change. [P01; VALIDATION.md]
