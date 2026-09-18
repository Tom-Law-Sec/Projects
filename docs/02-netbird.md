# 02 | Private remote access with NetBird

## Original project and the principle

The original project connected personal devices and servers through a
self-hosted NetBird deployment. It allowed remote management without making
every administration page a public website. Reproduce the idea in a new network,
not by joining the original production account.

Separate three questions: can the device join the network, may it connect to
this server and port, and can its user authenticate to the application? A VPN
connection does not replace an SSH key or a vault login. [S04, S05]

## Step 1 - Prepare a separate controller

This advanced exercise needs a domain you control and a separate publicly
reachable Linux VM. At the documentation check for this edition, NetBird's
quickstart specifies at least 1 CPU, 2 GB RAM, TCP 80/443 and UDP 3478. Recheck
S04 before deployment because the server architecture and required ports can
change. Public controller requirements do not mean that home application ports
should also be public.

Use an illustrative name such as `netbird.example.com` in your notes, but replace
it privately with a real domain you own when installing. A reserved example
name cannot obtain a real public certificate. On the controller, install Docker
and Compose using the instructions for its own Linux distribution, plus `curl`
and `jq`. Establish provider-console access before changing firewall rules.

## Step 2 - Download, inspect and run the official installer

On the new controller, create a private working directory outside this
publication repository. Use the current bootstrap from S04. Download it to a
file instead of piping an unseen response directly into a shell:

```bash
mkdir -m 700 ~/netbird-bootstrap
cd ~/netbird-bootstrap
curl -fL \
  https://github.com/netbirdio/netbird/releases/latest/download/getting-started.sh \
  -o getting-started.sh
less getting-started.sh
sha256sum getting-started.sh
bash getting-started.sh
```

Record the installer checksum and resulting component versions privately. The
bootstrap URL is a moving release entrypoint; retaining this information matters
for reproducing what you actually installed. Do not commit its generated
configuration, databases or identity material to the class repository.

For a new isolated controller, follow the official included reverse-proxy path.
Decline optional features that publish private applications to the Internet:
this exercise only needs device connectivity. Create the first administrator
promptly, keep account recovery material private, and configure appropriate
account protection. Generated file names and screens are version-sensitive;
use S04 rather than an old screenshot when they differ.

## Step 3 - Enrol only your own lab devices

Install the NetBird client using its official platform instructions, S06. On a
Linux lab server, a readable installation-script workflow is:

```bash
curl -fL https://pkgs.netbird.io/install.sh -o /tmp/netbird-install.sh
less /tmp/netbird-install.sh
sudo bash /tmp/netbird-install.sh
sudo netbird up --management-url https://netbird.example.com
sudo netbird status
```

Replace the example management URL with your own before running `netbird up`.
Complete the authentication flow shown by the client. Do not publish the login
URL, setup key or full status output. Install and enrol the laptop separately,
using its official client. Each student should have an independent lab or an
explicitly authorised, instructor-managed environment.

## Step 4 - Define a small access policy

Create a group for your administration laptop and a different group for your
lab server. Add an explicit policy allowing the laptop group to initiate TCP
connections to the server group on port 22. For this pack, HTTPS is carried
inside an SSH local forward, so you do not need to permit a direct web port.

Check the new policy before removing any broad default policy. An existing
all-to-all grant can still allow access despite a second, narrower rule. Once
the intended route works, remove the broad grant and test again. Keep a console
or known-good session available while changing access control. [S05]

Create a fresh SSH key on the laptop, install only its public key into the lab
account, and verify a new key-authenticated session before disabling password
logins. Verify the server's host-key fingerprint through your own trusted
console rather than accepting an unexpected changed key blindly. The private
key must never leave the laptop's secret storage or appear in a repository.

## Step 5 - Prove both the allow and the deny

| Test | Expected result |
| --- | --- |
| Authorised laptop connects to lab server TCP 22 | Connection succeeds, then SSH authentication is required |
| A separate unenrolled or unpermitted test device attempts the same path | Connection is denied or unreachable |
| Laptop attempts an ungranted lab service port | No connection |
| NetBird is disconnected on the laptop | Private route is unavailable |

Use only your own devices and addresses for these tests. A failed `ping` is not
conclusive when ICMP was never allowed; test the exact permitted TCP service.
Likewise, a connected client does not prove that the intended access policy is
correct. Use application-level tests as well as the client status.

## Troubleshooting and limitations

When access fails, work in order: controller reachability, peer enrolment,
policy, target address, server listener and SSH authentication. Do not install
an additional VPN or broad route before understanding which layer failed.

This chapter explains the fresh bootstrap and access design; it does not ship
an immutable copy of the rapidly changing NetBird server stack. Preserve the
versions you install and consult its maintenance documentation for upgrades and
recovery. The chapter is not a claim that the author's live setup was rebuilt
or re-audited during preparation.

**References:** S04-S06; original context P01.
