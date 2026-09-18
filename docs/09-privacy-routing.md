# 09 | Build a custom Xray/REALITY privacy proxy

## Original project and security objective

The original custom proxy used Xray/REALITY with selective routing: ordinary
internet traffic used Mullvad egress while private service destinations retained
a NetBird path. NetBird management and the proxy had separate VPS roles. Later
app work was required to preserve the existing proxy rather than repurpose its
ports or route policy. [P01]

This is a new, smaller classroom implementation of that design. It supplies
client/server templates and failure tests, not the author's transport keys,
subscription link or production routing table. It begins with **explicit TCP
application proxying**, not a system-wide VPN. Only apps using the supplied
local SOCKS port participate. Other applications remain outside this test.

## Architecture and prerequisites

```text
Test app -> laptop SOCKS -> VLESS/REALITY -> separate proxy VPS
                                          |
                      allowed lab peer <--+--> Mullvad SOCKS
                        over NetBird             over WireGuard
                                                     |
                                                public internet
```

Use a fresh Debian proxy VM with console access, its own public IPv4, an owned
DNS hostname and permission to run the service. A self-hosted NetBird controller
is a separate role from chapter 02. You also need your own valid Mullvad account
and a disposable NetBird lab peer. These external resources can incur costs;
no account or infrastructure belonging to the author is supplied.

On the proxy VM, complete the Linux/Docker foundation and enrol it in your own
NetBird mesh. Preserve private administrator SSH. For the owned TLS target below,
TCP 80/443 are deliberately public; the authenticated proxy listens on TCP 8443.
Restrict 8443 to your test client's public source IP at the provider firewall
for this lab where practical. Do not open home database or administration ports.

The TLS target is a harmless certificate/handshake endpoint, not an application
or content site. Keep it separate from password vaults, files and admin pages.

## Step 1 - Write the outbound policy before deploying

| Request | Intended handling | Failure expectation |
| --- | --- | --- |
| One owned peer IPv4, TCP 8088 | Private NetBird path | No fallback onto the physical interface |
| Other private/reserved IP targets | Deny | No broad access to the mesh or VPS LAN |
| Ordinary public TCP target | Mullvad SOCKS through WireGuard | Request fails when that egress is absent |
| UDP or literal IPv6 target | Deny in this baseline | Not claimed as supported/tested |
| Private-name suffixes such as `lab.test` | Deny in this baseline | Do not leak those names to public egress |

Xray evaluates rules in order and defaults to the first outbound if none
matches. The template therefore makes the provider SOCKS path the first
outbound, places a single narrow private allow before the private-address
deny and has no public `freedom` fallback. Its only direct outbound is reachable
through the specific permitted peer/port rule. [S18]

The denied literal-IPv6 rule is not a system-wide IPv6 kill switch. Public
hostnames are forwarded for resolution by the provider proxy, which may choose
an IPv4 or IPv6 destination. That connection remains on the provider side of
the encrypted path. The laptop's unrelated IPv6 traffic is outside this lab.

## Step 2 - Prepare the files in a private workspace

On the proxy VM, copy the repository there through your own authorised SSH
connection. Then create an ignored workspace and copy the templates:

```bash
cd ~/class-project-pack/labs/proxy
mkdir -m 700 runtime
cp server.json.example runtime/server.json
cp wg-lab.conf.example runtime/wg-lab.conf
cp proxy-guard.nft.example runtime/proxy-guard.nft
cp Target.Caddyfile.example runtime/Target.Caddyfile
cp target.compose.yaml.example runtime/target.compose.yaml
chmod 600 runtime/*
```

If the workspace exists, inspect it instead of overwriting working profiles.
All `REPLACE_...` values must be filled privately. Keep client configuration in
a similarly private directory **on the laptop**. It must never contain the
server's private key or Mullvad's WireGuard private key.

## Step 3 - Establish an owned TLS target

Create a DNS A record for an owned hostname such as the illustrative
`tls.example.com`, pointing to the proxy VM. Replace `REPLACE_TLS_HOSTNAME` in
the target Caddyfile. Do not create an AAAA record unless the intended IPv6
listener/firewall path has been configured and tested. The example name itself
cannot be used to obtain your certificate.

On the proxy VM, from the `runtime` directory:

```bash
cd ~/class-project-pack/labs/proxy/runtime
sudo docker compose -f target.compose.yaml config -q
sudo docker compose -f target.compose.yaml \
  config --lock-image-digests -o target.images.yaml
sudo docker compose -f target.compose.yaml \
  -f target.images.yaml up -d
```

This separate Compose file intentionally publishes 80/443. It must not be
merged into the private application stack. Caddy obtains a certificate for the
owned name when DNS and validation are correct. Its internal data directory
contains private CA/account material and stays out of Git. [S07]

Check the local TLS target using the real owned hostname in place of the
placeholder. Require a valid certificate, TLS 1.3 and negotiated `h2`:

```bash
openssl s_client -connect 127.0.0.1:443 \
  -servername YOUR_OWNED_TLS_HOSTNAME -tls1_3 -alpn h2 \
  -verify_hostname YOUR_OWNED_TLS_HOSTNAME -verify_return_error
```

Do not continue while validation fails. The Xray server uses local target
`127.0.0.1:443` and the matching hostname. REALITY can send unauthenticated
handshakes to its configured target, which is why this lab uses an owned,
harmless endpoint rather than forwarding strangers into a sensitive app. [S26]

## Step 4 - Create selective Mullvad egress

Return to the template directory on the proxy VM and install the required tools:

```bash
cd ~/class-project-pack/labs/proxy
sudo apt install wireguard-tools nftables curl openssl unzip
```

Commands from this point use that directory unless a different machine is named.
Generate a fresh WireGuard profile through your own Mullvad account.
From that profile, privately copy the assigned IPv4/CIDR, client private key,
provider peer public key and numeric endpoint/port into `runtime/wg-lab.conf`.
Do not copy the provider's full default-route profile over this selective lab.

Retain only `AllowedIPs = 10.64.0.1/32` from the template. Do not add global DNS,
`0.0.0.0/0`, `::/0` or full-tunnel firewall hooks. `wg-quick` will create the
specific route; it is not intended to replace the VPS's default route or its
SSH return path. The address `10.64.0.1:1080` is the documented Mullvad SOCKS
endpoint, not an address from the author's infrastructure. [S32-S33]

Install the filled profile and start its lab-specific service:

```bash
sudo install -m 0600 runtime/wg-lab.conf /etc/wireguard/wg-lab.conf
sudo systemctl enable --now wg-quick@wg-lab
ip route get 10.64.0.1
sudo wg show wg-lab
```

Confirm the route names `wg-lab`, generate a request below and inspect the
handshake/counters. Keep key, peer and endpoint output private. If the profile
cannot reach this SOCKS service, stop and compare it with current provider
instructions rather than enabling a broad default route as a shortcut.

## Step 5 - Add a narrow egress guard before client traffic

In `runtime/proxy-guard.nft`, replace the lab peer IPv4 and actual NetBird
interface. The first rule rejects provider-SOCKS traffic not leaving `wg-lab`;
the second rejects the allowed lab-peer traffic not leaving the overlay.
Neither rule replaces the host's complete firewall. [S29]

```bash
sudo install -d -m 0750 /etc/classlab
sudo install -m 0600 runtime/proxy-guard.nft /etc/classlab/proxy-guard.nft
sudo nft -c -f /etc/classlab/proxy-guard.nft
sudo install -m 0644 classlab-proxy-guard.service \
  /etc/systemd/system/classlab-proxy-guard.service
sudo systemctl daemon-reload
sudo systemctl enable --now classlab-proxy-guard
sudo nft list table inet classlab_proxy_guard
```

Load the table once. Read `labs/proxy/README.md` before reloading or applying a
file already loaded manually. Never use `nft flush ruleset`. If a route vanishes,
the guard is intended to stop the same destination escaping through another
interface. The interruption test still has to prove the actual behaviour.

From the proxy VM, verify the provider path without changing the system proxy:

```bash
curl --noproxy '' --max-time 15 \
  --socks5-hostname 10.64.0.1:1080 \
  https://am.i.mullvad.net/connected
```

The response should identify Mullvad egress. Keep the reported address private.
`--socks5-hostname` delegates hostname resolution for this request instead of
resolving the requested website locally. SOCKS itself is not encryption; this
provider hop is protected by WireGuard. [S28, S32]

## Step 6 - Install a compatible Xray core and generate identities

Use the official Xray-core release page, S23. On an x86-64 Debian lab, download
the selected release's `Xray-linux-64.zip` and matching `.dgst` checksum file.
For other CPU architectures choose the corresponding official asset instead.
Do not execute an unreviewed third-party install script.

```bash
uname -m
# Replace with the selected official release tag, including its leading v.
XRAY_VERSION='REPLACE_WITH_COMPATIBLE_RELEASE_TAG'
curl -fL "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip" \
  -o runtime/Xray-linux-64.zip
curl -fL "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip.dgst" \
  -o runtime/Xray-linux-64.zip.dgst
sha256sum runtime/Xray-linux-64.zip
cat runtime/Xray-linux-64.zip.dgst
```

Compare the SHA-256 value with the release checksum before extraction. Record
the exact version and hash. This identifies the artifact; a checksum from the
same source is not independent proof of the publisher's trustworthiness.
Extract only after the values agree, then install the binary under a lab name:

```bash
unzip runtime/Xray-linux-64.zip -d runtime/xray-release
sudo install -m 0755 runtime/xray-release/xray /usr/local/bin/xray-lab
xray-lab version
xray-lab uuid
xray-lab x25519
openssl rand -hex 8
```

Generate a fresh UUID, REALITY key pair and short ID. Copy them directly into
private files; do not post the output. The server gets the REALITY private key.
The client gets the corresponding `Password`/public-key-derived value, which
must also be kept private as profile material. Both get the same UUID and short
ID. The WireGuard key pair remains separate. [S26-S27]

The templates use the current documented JSON layout (`users`, flattened
outbounds, `method: raw`, client `password`). An older bundled GUI core may use
older field names. Select compatible client/server cores and require their
own configuration tests to pass; structural JSON parsing alone is insufficient.

## Step 7 - Install and test the server profile

Fill the server JSON with the generated identity fields, owned TLS hostname
and one lab-peer IPv4. The direct allow is restricted to that peer's TCP 8088.
Check the policy with the supplied helper, then use Xray's own parser:

```bash
python3 ../../scripts/check_proxy.py runtime/server.json --ready
xray-lab run -test -config runtime/server.json
```

The helper prints only a verdict, never the credential values. It checks a
small intended policy, not every possible Xray option or security property.
Do not start the listener until both checks succeed.

Create the dedicated service account only if it does not already exist:

```bash
id xraylab || sudo useradd --system --no-create-home \
  --shell /usr/sbin/nologin xraylab
sudo chown root:xraylab /etc/classlab
sudo chmod 0750 /etc/classlab
sudo install -o root -g xraylab -m 0640 runtime/server.json \
  /etc/classlab/xray-server.json
sudo install -m 0644 xray-lab.service /etc/systemd/system/xray-lab.service
sudo systemctl daemon-reload
sudo systemctl enable --now xray-lab
sudo systemctl status xray-lab --no-pager
```

The service runs without root, depends on the guard loader and has no writable
host filesystem requirement. Guard loading failure should prevent startup.
These are proposed classroom controls, not an executed authoring result.
Read errors privately and fix the failed requirement rather than running the
whole proxy permanently as root. [S35]

## Step 8 - Start an explicit client, then verify egress

On the laptop, install the same compatible official core for its platform.
Copy `client.json.example` to a private `client.json`, restrict file access,
and fill the server's public IPv4, UUID, owned TLS hostname, client REALITY
password and short ID. No server-side private key belongs on the laptop.

The laptop SOCKS listener binds to `127.0.0.1:10808`, with UDP disabled. It has
only one outbound and no configured direct fallback. Run the core in the
foreground so it can be stopped with Ctrl+C:

```bash
xray run -test -config client.json
xray run -config client.json
```

Use `xray-lab` on Linux if that is the binary name you installed, or `xray.exe`
on Windows. In another laptop terminal:

```bash
curl --noproxy '' --max-time 15 \
  --socks5-hostname 127.0.0.1:10808 \
  https://am.i.mullvad.net/connected
```

On PowerShell use `curl.exe`, and write the command on one line instead of
copying Bash backslash continuations. The reported egress should be Mullvad,
not the laptop's ordinary connection or the proxy VM's public address.
This establishes only this request's path, not a whole-device privacy audit.

## Step 9 - Prove the private NetBird branch

On the disposable homelab peer, create one harmless marker outside real data
and bind a temporary server only to its overlay IPv4:

```bash
mkdir -m 700 ~/classlab-proxy-check
printf 'netbird-path-ok\n' > ~/classlab-proxy-check/health.txt
python3 -m http.server 8088 --bind YOUR_LAB_PEER_IPV4 \
  --directory ~/classlab-proxy-check
```

Allow only the proxy VM's peer group to reach this peer on TCP 8088 in NetBird.
No router port forward is needed. The Python server is a temporary diagnostic
endpoint, not a production service; stop it after the test. From the laptop:

```bash
curl --noproxy '' --max-time 10 \
  --socks5-hostname 127.0.0.1:10808 \
  http://YOUR_LAB_PEER_IPV4:8088/health.txt
```

Expect the marker. An owned negative test to the same peer's TCP 22 through
this proxy should fail because the Xray policy permits only 8088. A separate
NetBird administrator session may still use SSH; that is a different path.
The server sees the proxy peer as the network source, so every authorised
proxy client shares that network identity. Do not treat this as per-user
NetBird authorisation or open broad mesh access to untrusted clients.

## Step 10 - Test interruption, recovery and limits

Keep the guard loaded and console/private management available. With only the
harmless requests running, test these one at a time:

| Test | Expected result |
| --- | --- |
| Stop `wg-quick@wg-lab` on the proxy VM | New public proxy requests fail; no ordinary-internet fallback |
| Restart WireGuard | Public requests recover through Mullvad |
| Disconnect the **test service peer** from NetBird | Private-marker request fails; public proxy requests still work |
| Restore that peer | Private request recovers |
| Stop laptop Xray | Explicit SOCKS requests fail rather than use a system route |
| Use a wrong client UUID in a separate private test profile | Cannot obtain proxy access |
| Reboot proxy VM with console access | Guard, profiles and intended routes recover before approval |

Do not disconnect the only remote-management path to perform a test. Inspect
fresh requests, not just a GUI status label. Record the actual results and
untested cases. A failure is a useful finding, not something to hide. Provider
rate limits, source-IP firewall restrictions and TLS-target errors can also
cause a connection to fail; distinguish those causes.

The original Windows/Android deployment used client routing/TUN features too.
They are an advanced extension here: verify bootstrap exclusions, DNS, UDP,
IPv6, private-name resolution, suspend/resume and reconnect behaviour separately
before sending all device traffic through it. Do not replace a working desktop
routing setup with this lab profile. This pack does not claim a validated
full-device kill switch or invisible/untraceable traffic.

**References:** S18, S23, S26-S29, S32-S36; original context P01.
