# 10 | Separate public applications from private management

## What was done in the original environment

The original deployment deliberately made selected apps reachable remotely
without requiring every client to join the management network. Vaultwarden and
Nextcloud used Cloudflare Tunnel. The photo service used a separate, scoped
VPS HTTPS edge with a private path to its origin. Administration remained
private, and later ingress work was required to preserve the existing custom
proxy. These are reported outcomes, not a new live audit. [P01]

The central lesson is **expose only the application path you intend**, while
retaining application authentication and independently restricting the origin.
A working public login page does not imply public SSH should also work. A
private management network does not automatically make every Docker listener
private.

## Step 1 - Define the intended reachability

Use a separate policy table for your lab. The default classroom stack is
narrower than the original selected-public-app design:

| Surface | Classroom default | Evidence required |
| --- | --- | --- |
| SSH | Approved administrator peer over NetBird | New authorised login works; other sources denied |
| Vault/file/photo apps | Private tunnel or independent private photo lab | Intended login works; unauthorised data access fails |
| PostgreSQL / Redis | Container backend network only | No host-published database port |
| Kuma / log viewer / DNS administration | Private only | No external administrative access |
| Custom proxy on separate VM | Authenticated TCP 8443, limited test sources | Valid profile works; wrong credentials fail |
| Owned proxy TLS target | Public, harmless response on 80/443 | Contains no private app or admin route |

Do not apply the core loopback-only port checker to the deliberately public
TLS-target stack and call its expected failure a vulnerability. Each stack
has a different documented exposure policy. Test the appropriate policy.

## Step 2 - Verify the private HTTPS baseline

From the laptop with the chapter 03 tunnel and verified CA certificate:

```bash
curl --cacert classlab-root.crt \
  --resolve check.lab.test:8443:127.0.0.1 \
  https://check.lab.test:8443/healthz
```

Expect the fixed `classlab-https-ok` marker. Close the SSH tunnel and repeat:
the request should no longer reach the remote lab. From another owned LAN
client, test the server's LAN address on TCP 8443; it should not expose this
site. Confirm the test client really has a path to the server before attributing
all failures to your security controls. [S07, S24]

Test authentication separately. Use an incognito/new lab profile with no login
cookie and confirm private files/vault contents are not available. A `200` login
page is not a failed security test; an unauthenticated response containing
private data would be. Test only owned demo accounts and harmless files.

## Step 3 - Understand Tunnel, Access and origin authentication

Cloudflare Tunnel provides a connector path from an origin to Cloudflare;
Cloudflare Access is a separate access-policy layer. A published Tunnel
hostname is not made user-private merely by having a tunnel. The app may still
be intentionally reachable by anyone who can attempt its own login. The original
Vaultwarden/Nextcloud work should not be relabelled as Access-protected without
evidence of such a policy. [S16, S34; P01]

An interactive browser Access login can interfere with a native app expecting
an API response. Machine access may require a service token and compatible
headers; not every client supports that. The original RSS/mobile work exposed
this distinction. Do not solve a failed mobile API test by broadly removing
authentication or bypassing all API paths. Choose a deliberately private path
or a documented, client-compatible authentication design. [S16]

Even a correctly authenticated edge should not allow direct public access to
an origin that bypasses the edge. Identify every listener, router forward,
Docker published port, DNS record and alternate hostname before concluding
that the application is reachable through only the intended path.

## Step 4 - Design a controlled public-ingress extension

This is an advanced design/verification extension, not an automatic publication
of the core apps. First prove the private stack works. Start public tests with
only the harmless health endpoint and an owned domain; keep real accounts and
files out of the experiment.

For an independent Cloudflare Tunnel, use S34's current connector and ingress
instructions in a private workspace. Match explicit hostnames, end with a
non-routing/catch-all rejection, and keep generated credentials out of Git.
If the connector uses HTTPS to your origin, verify its certificate and name;
do not disable origin certificate verification as a permanent fix.

Before placing a real self-hosted app behind a different external hostname,
update its documented external URL and trusted-domain/proxy settings. For
Nextcloud, retain a narrow trusted-proxy list and verify DAV behaviour. A
successful health route does not prove the application's login, uploads,
WebSocket connections or mobile API will work. [S10-S11, S34]

For a VPS reverse-proxy edge, restrict the origin route to the exact peer and
app port. The proxy's network identity should not gain blanket homelab access.
Keep the custom Xray listener and configuration untouched; list occupied ports
and confirm a rollback plan before adding an edge listener. Re-run both public
egress and private-routing tests afterwards. [S05; P01]

## Step 5 - Collect positive and negative evidence

On your own Linux test machines, a basic single-port test can use Python:

```bash
python3 -c "import socket; s=socket.create_connection(('YOUR_LAB_IP',8443),3); s.close(); print('TCP connected')"
```

Replace the placeholder with one owned endpoint. Run it from the approved
source and a separate unapproved source. A connection exception is an observed
connection failure, not proof which firewall caused it. Combine it with your
listener and rule inspection; do not scan unrelated networks.

For the selected app, record logged-out behaviour, correct login, a wrong
password attempt, another normal user's denied data access, and the expected
HTTP/API result. Check the real external hostname and the direct-origin path
independently. Testing one browser over Wi-Fi does not cover mobile data,
IPv6, a different DNS resolver or a second ingress route.

## Step 6 - Preserve privacy when sharing the results

Share a table of expected versus observed outcomes using role labels such as
`admin laptop`, `unapproved peer` and `file service`. Reconstruct topology with
fictional addresses. Do not publish live DNS inventories, NetBird peer IDs,
account email addresses, authentication headers or complete reverse-proxy logs.

Removing a name from a report protects the report's privacy; it does not enforce
access control on the service. Keep access restrictions effective even when an
attacker knows the hostname. Add a limitation whenever a test did not establish
which layer caused an outcome.

## Completion evidence

Finish with a reviewed exposure table, at least one permitted and one denied
network test, one authentication/authorisation test and a no-regression check
for the custom proxy. Mark external-ingress or native-client steps **not tested**
when they were only designed. Do not claim the class pack audited the original
production network.

**References:** S05, S07, S10-S11, S16, S24, S34; original context P01.
