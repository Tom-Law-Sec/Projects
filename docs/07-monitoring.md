# 07 | Security monitoring, private logs and DNS filtering

## Why this is a security project

The original homelab used Uptime Kuma, Dozzle and AdGuard alongside its apps.
The security goals are to notice failures, preserve useful evidence and control
where DNS queries go without exposing an administration dashboard or sensitive
logs. Monitoring is not equivalent to intrusion detection, and a green HTTP
check does not prove that permissions, encryption or backups are correct. [P01]

This chapter uses the actual Uptime Kuma instance in the core stack. There is
no separate demonstration API or autonomous agent. DNS filtering and Dozzle
are scoped extensions to the existing-service work, not copied production
configurations.

## Step 1 - Protect monitoring access

Complete chapters 01-03. Open `https://status.lab.test:8443` through the SSH
tunnel, create a fresh administrator and keep this interface private. Record
the selected Kuma release. Do not put actual service names, failure messages
or infrastructure addresses on a publicly accessible status page. [S17]

The core Compose file gives Kuma persistent storage and a network shared with
Caddy. It deliberately does not mount the Docker socket. A read-only filesystem
mount of that socket does not make the Docker API read-only; access to a
rootful daemon remains highly privileged. [S02]

## Step 2 - Add a clearly scoped check

Append this lab-only internal endpoint to `labs/core/Caddyfile`:

```caddyfile
http://:2015 {
    respond /health-demo "classlab-ok" 200
}
```

Do not add port 2015 to the Compose host-port list. From `labs/core` on the
server, recreate Caddy after checking its configuration:

```bash
sudo ./lab.sh exec caddy caddy validate \
  --config /etc/caddy/Caddyfile --adapter caddyfile
sudo ./lab.sh up -d --force-recreate caddy
```

In Kuma, create an HTTP keyword monitor for `http://caddy:2015/health-demo`,
requiring `classlab-ok`. Use a 60-second interval for this exercise. The check
is on the container network; it does not verify the laptop's DNS, TLS trust,
SSH tunnel or application login. State that limitation in the evidence. [S17]

## Step 3 - Produce and recover from an actual failure

Change only the endpoint response text to `classlab-maintenance`, recreate
Caddy and observe the monitor after its next checks. A keyword failure should
appear even though the HTTP service responds. Restore `classlab-ok` and record
the recovery time. Do not invent a response time or uptime percentage.

An optional notification uses an account/channel you control. Keep webhook
URLs, tokens and recipient identifiers outside Git. Confirm delivery with this
small failure rather than testing against a real outage or posting a private
service address into a class channel.

## Step 4 - Inspect relevant logs without redistributing them

On the lab server, these commands read existing logs:

```bash
sudo journalctl -u ssh --since "30 minutes ago" --no-pager
cd ~/class-project-pack/labs/core
sudo ./lab.sh logs --since 30m --tail 100 caddy vaultwarden
```

Make one intentional failed login to a disposable account you own, then look
for the corresponding event. Do not brute-force passwords. Note timestamps and
whether the logged client identity represents the real client or a proxy.
Remove addresses, usernames, tokens and file names before sharing excerpts.
Do not switch an app to verbose request/body logging just to get a screenshot.

Dozzle can provide a convenient private view of container logs, but its socket
access is a separate trust decision. The baseline here uses CLI logs instead
of adding a new privileged integration. Retain a working private Dozzle setup
only after reviewing its own authentication and Docker API boundary. [S02, S30]

## Step 5 - Reproduce an AdGuard DNS-policy test

On a separate disposable host or VM, follow AdGuard Home's current installation
and first-run guide, S31. Configure an administrator and limit the DNS listener
to your intended LAN or private-overlay address. Permit TCP/UDP 53 only from
authorised clients. Keep the setup/admin UI private; remove temporary setup
exposure after enrolment. Never publish an unrestricted recursive resolver.

Do not change the whole household's DHCP or DNS while learning. Point a single
query at your new resolver first. On a Linux test client with `dnsutils`:

```bash
dig @YOUR_LAB_DNS_IP example.com A
dig @YOUR_LAB_DNS_IP example.com AAAA
```

In AdGuard's custom rules, temporarily add `||example.com^`. Repeat the explicit
query and inspect the query log. Record whether the selected blocking mode
returns a blocking address, an empty result or a DNS error. Remove the rule and
confirm normal resolution returns. The rule is a harmless policy test, not a
claim that the example domain is malicious. [S31]

## Understand DNS limits before changing clients

A configured resolver is not proof every app uses it. Browser DNS-over-HTTPS,
Android Private DNS and VPN-provided resolvers can use different paths. Verify
one controlled device before changing system-wide settings. Private names need
an appropriate resolver path, not just network reachability. The original work
included cases where private DNS/mobile resolution still needed verification.
Do not present that unfinished testing as a completed universal fix. [P01]

Blocking a domain is not a firewall rule for all traffic to its IP. DNS filtering
does not inspect encrypted file contents or prove a download safe. Retain only
the query history you need; DNS logs themselves reveal activity.

## Evidence and completion

Provide the monitor's defined scope, observed failure/recovery, one reviewed
log event and the DNS-rule test outcome. Add a denied attempt from an unauthorised
client to the monitoring/admin interface. A complete result explains what the
controls do **not** measure as well as what passed.

**References:** S02, S17, S30-S31; original context P01.
