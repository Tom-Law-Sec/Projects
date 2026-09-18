# 08 | Harden the host and container boundary

## Original hardening and the classroom target

The original work reported SSH restricted to NetBird, closed Vaultwarden
registration, a disabled Vaultwarden server-admin panel, two-factor setup,
HTTPS access and careful separation of selected public apps from private
administration. Nextcloud work included reverse-proxy trust, Redis locking,
scheduled jobs and storage limits. [P01]

This chapter turns those goals into a checkable baseline. The exact SSH snippet
and narrow firewall guard supplied here are new examples, not exports of the
original host. Changing authentication or firewall rules can lock you out:
use your own disposable server, retain a provider/local console and keep a
known-good SSH session open until a **new** session passes.

## Step 1 - Inventory the current exposure

Run on the lab server and keep the full output private:

```bash
sudo ss -lntup
sudo systemctl --failed
sudo systemctl is-enabled ssh
sudo docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

For each listener, record its purpose, bound address, required source clients
and authentication. A listener on `127.0.0.1` is different from `0.0.0.0` or
`::`. A process being installed is different from it listening publicly.
Do not disable an unfamiliar service until you understand its dependencies.

The core web stack publishes only loopback TCP 8443. PostgreSQL and Redis have
no host-published ports. Docker network membership gives connected containers
reachability; it is not per-request authorisation. A compromised application
can still reach its own database. [S02, S24]

## Step 2 - Establish key-based SSH before removing passwords

On the laptop, create a dedicated key with a passphrase:

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/classlab_ed25519
```

If that path already exists, choose a new filename rather than overwriting a
key. Transfer only its `.pub` contents to the lab user's `~/.ssh/authorized_keys`
using the existing authorised connection or console. On Linux, `ssh-copy-id`
can perform this enrolment:

```bash
ssh-copy-id -i ~/.ssh/classlab_ed25519.pub \
  labuser@YOUR_LAB_NETBIRD_IP
ssh -o IdentitiesOnly=yes -i ~/.ssh/classlab_ed25519 \
  labuser@YOUR_LAB_NETBIRD_IP
```

Replace `labuser` with the ordinary account created for the lab. Verify the
server's host-key fingerprint against its trusted console, and confirm `sudo`
works in this new session. Windows OpenSSH has `ssh-keygen` and `ssh`, but not
normally `ssh-copy-id`; install the public key via the server console instead.
Never copy the private key to the server or class repository.

## Step 3 - Apply a small SSH baseline

Inspect the existing configuration and `/etc/ssh/sshd_config.d/` first. OpenSSH
usually uses the first obtained value for a setting, and `Match` rules can
alter effective settings. A new file alone does not prove the desired values
win. This is why the effective-configuration test below matters. [S25]

The supplied `labs/hardening/00-classlab.conf.example` contains:

```text
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding local
GatewayPorts no
PermitTunnel no
MaxAuthTries 3
LoginGraceTime 30
```

Local TCP forwarding is deliberately retained: the HTTPS exercise depends on
it. This is not a restricted-shell policy; an account with shell or Docker/sudo
privileges can still run other networking tools. Do not use this baseline on a
server that requires keyboard-interactive MFA without redesigning that login
flow first. [S25]

From the repository root, **only after key login works**:

```bash
sudo install -m 0644 labs/hardening/00-classlab.conf.example \
  /etc/ssh/sshd_config.d/00-classlab.conf
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T | grep -E \
  'permitrootlogin|passwordauthentication|kbdinteractiveauthentication|allowtcpforwarding|gatewayports'
```

When syntax or effective values are wrong, fix them before reloading. Review
applicable `Match` sections with `sshd -T -C` for the real lab user/source as
needed. On Debian's ordinary SSH service:

```bash
sudo systemctl reload ssh
```

Open another key-authenticated session and a fresh HTTPS forward. Then test a
password-only attempt with an owned account; it should not offer a successful
password login. Keep the original connection/console until both results are
known. Remove the new snippet and reload from that session if rollback is needed.

## Step 4 - Make administration NetBird-only

NetBird policy must allow only the intended administrator group to reach the
lab server's TCP 22. Remove an overlapping broad default grant after testing
the narrow rule. Application credentials still apply. Then independently deny
SSH arriving outside the overlay at the host boundary. [S05]

The example `labs/hardening/ssh-guard.nft.example` is a **narrow deny guard**,
not a complete host firewall. Replace `YOUR_NETBIRD_INTERFACE` with the verified
interface name from your own route/link inspection. It rejects TCP 22 on any
other interface, for both IPv4 and IPv6; it does not flush Docker/NetBird rules
or change every other service's policy. Existing restrictive rules can still
block SSH, so confirm the complete policy privately. [S24, S29]

After filling the template into a private file outside Git:

```bash
sudo nft -c -f /etc/classlab/ssh-guard.nft
sudo nft -f /etc/classlab/ssh-guard.nft
sudo nft list table inet classlab_ssh_guard
```

The first command checks syntax; it does not prove packet behaviour. Keep console
access while applying the second command. Do not enable or replace a generic
`nftables.service` that flushes a host's existing rules without reviewing it.
The supplied dedicated unit loads only this guard at boot. Follow its README,
verify a reboot with console access, and never assume an in-memory rule persists.

A host loopback SSH attempt is also denied by this example. This is intentional:
administration arrives through NetBird. This guard does not block the
**destination** of an established SSH local-forward channel at loopback 8443.

## Step 5 - Check container privileges and published ports

From `labs/core`, validate bindings without printing environment secrets:

```bash
sudo ./lab.sh config --format json | \
  python3 ../../scripts/check_bindings.py
```

The pipe carries expanded configuration locally; do not redirect it to a public
file or enable shell tracing. The helper prints only port bindings and rejects
unspecified/public addresses or host networking in the core stack.

Docker's published ports are not reliably controlled by a simple UFW rule in
the way a host-only listener is. Keep unnecessary ports unpublished, understand
the active Docker firewall backend and test from a second machine. Do not
replace Docker's generated rules with an unreviewed `flush ruleset`. [S24]

The core stack avoids host networking, privileged containers and socket mounts.
Its configuration files are read-only mounts where practical; its application
data remains writable. Adding `read_only`, dropping all capabilities or forcing
a random UID can break an image's initialisation. Test such changes separately
against that image rather than claiming a universal hardening flag. [S02]

## Step 6 - Harden accounts, recovery and maintenance

For Vaultwarden, close registration after the deliberate first-user exercise,
keep the separate server-admin endpoint disabled and enrol two-factor
verification. Store recovery material outside the vault. For Nextcloud, use
an ordinary daily account, narrow proxy trust and a tested quota. A quota is
not a physical reservation or a backup. Chapters 04-06 provide those tests.

Keep local `.env`, transport profiles and backup passwords out of Git; use
restrictive file permissions. `docker inspect` and resolved Compose output can
reveal environment secrets. A secret scanner is not a substitute for access
control or a manual review.

Before upgrades, record current versions/digests, read migrations, make a backup
and test recovery. Recheck exposure and access after upgrades and reboot.
Do not enable uncontrolled database-major updates on a working data directory.
The original hardening is not a guarantee that future configuration changes
remain safe. [S03, S12, S15]

## Completion evidence

Record: new key login succeeds; password-only login fails; an authorised overlay
peer reaches TCP 22; a LAN/unpermitted peer does not; no database is published;
the core binding check passes; the HTTPS tunnel still works; and the guard
survives a controlled reboot. Treat every unrun case as **not tested**.

**References:** S02-S03, S05, S12, S15, S24-S25, S29; original context P01.
