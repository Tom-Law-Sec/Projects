# 03 | Private HTTPS and the reverse proxy

## The data path

The original work used reverse proxies and different access paths for public
and private services. This class version deliberately chooses a smaller access
surface: one loopback listener, an authenticated SSH tunnel and local HTTPS.

```text
Browser on student laptop
  -> https://check.lab.test:8443/healthz
  -> laptop loopback / SSH local forward
  -> authorised SSH connection to lab server
  -> server 127.0.0.1:8443
  -> Caddy HTTPS listener
  -> selected application or static files

Database and Redis: no host ports published
Other LAN/Internet clients: no direct web listener provided
```

The hostname selects the application, the certificate authenticates that name,
the tunnel supplies the authorised network path, and the application still
controls its own users. These are different jobs, not interchangeable features.

## Step 1 - Start the SSH forward on the laptop

Keep this terminal open. Replace the account and address with your own values.
The literal placeholder below is not a working destination.

```bash
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:8443:127.0.0.1:8443 \
  labuser@YOUR_LAB_SERVER_ADDRESS
```

The left-hand listener is on the laptop; the right-hand destination is evaluated
from the SSH server. A local port forward does not require a router port-forward
for 8443. When the SSH process stops, the browser path stops too. Do not change
`127.0.0.1` to `0.0.0.0` to share the tunnel with other machines.

When everything runs on one Linux computer, no SSH tunnel is needed. Keep the
same localhost names and certificate steps.

## Step 2 - Add fictional local names on the laptop

Add the following single line to the laptop's hosts file using an administrator
editor. On Linux the file is `/etc/hosts`; on Windows it is
`C:\Windows\System32\drivers\etc\hosts`.

```text
127.0.0.1 vault.lab.test cloud.lab.test status.lab.test check.lab.test
```

This must be on the computer running the browser, not only on the server.
It maps names to the local tunnel entrance. Keep the file's other entries and
remove this line after the lab. These names are not public DNS records.

## Step 3 - Export only the lab's public CA certificate

Caddy's `tls internal` uses a local certificate authority. Containers cannot
automatically make your separate laptop trust that authority. Export its public
root certificate from the running server container, not its private key. [S07]

Run **on the server**, from `labs/core`:

```bash
sudo ./lab.sh cp \
  caddy:/data/caddy/pki/authorities/local/root.crt \
  ./classlab-root.crt
sudo chown "$(id -u):$(id -g)" classlab-root.crt
openssl x509 -in classlab-root.crt -noout -fingerprint -sha256
```

Transfer `classlab-root.crt` to the laptop using your already verified SSH
connection. Compare its SHA-256 certificate fingerprint with the value observed
through the trusted server session. A certificate downloaded from an unknown
page is not a trustworthy basis for adding a new root authority.

For the browser exercise, import it as a trusted website authority in a
**dedicated lab browser profile**. In Firefox, this is in certificate management
under Privacy & Security, Authorities. Do not override managed college security
settings. Only import your own verified lab CA, understand that a trusted root
has broad signing power, and remove it when the exercise ends. Some native
applications do not trust user-added authorities; do not disable their TLS
verification as a workaround.

## Step 4 - Test without bypassing certificate verification

From the laptop directory containing the copied certificate:

```bash
curl --cacert classlab-root.crt \
  --resolve check.lab.test:8443:127.0.0.1 \
  -I https://check.lab.test:8443/healthz
```

The expected result is an HTTPS response for the lab health endpoint, ordinarily
`200 OK`. This command explicitly supplies the trusted CA and destination;
it does not use `-k` or otherwise disable certificate checks. In Windows
PowerShell, use `curl.exe` when `curl` is an alias to another command.

Open `https://check.lab.test:8443/healthz` in the lab browser. Then try
`https://status.lab.test:8443`. Keep the port suffix: the container's internal
443 is intentionally mapped to host 8443, and no HTTP redirect port is published.

## Step 5 - Inspect the proxy behaviour

Open `labs/core/Caddyfile`. Each site has one responsibility. The vault route
forwards to Vaultwarden; the cloud route forwards to Nextcloud; the status route
forwards to Uptime Kuma; the check route returns a fixed health marker.
There is no website, content-management system or site-asset directory.
The proxy does not expose database ports or mount the Docker socket.

Nextcloud receives an explicit external HTTPS URL and trusts only the designated
Caddy address on its dedicated frontend network. Do not replace this with
`trusted_proxies = all addresses`. Correct proxy trust matters for client-IP
handling and security features. [S10]

## Failure tests and troubleshooting

Close the SSH tunnel: the laptop page should stop responding. Test the lab
server's LAN address from another machine: port 8443 should not provide this
site. Inspect the Compose binding: it should say `127.0.0.1`, not an unspecified
host address. These tests are stronger evidence than assuming a VPN or firewall
makes every service private.

A certificate warning normally means the wrong name, missing trust or a different
CA. A connection refusal normally means no tunnel or no listener. A `502` points
toward the proxy's upstream application. A correct HTML login page is not the
same as a functioning mobile API.

The original RSS work exposed this last distinction: an interactive access
login can return HTML where an app expects an API response. Service-token support
depends on the client being able to send the required headers. Prefer an
appropriate private access path over removing authentication from every API
route. The RSS/mobile fix is not claimed as completed here. [S16]

**References:** S07, S10, S16; original context P01.
