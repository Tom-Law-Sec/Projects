# Custom privacy proxy - separate lab, separate secrets

Read `docs/09-privacy-routing.md` before installing anything. This directory
contains templates, not a ready-to-use profile and not the original deployment.
Do not commit filled configurations. Use a **separate proxy VPS**, not the
NetBird controller and not the existing homelab host.

The baseline carries explicit TCP proxy requests. Public destinations use a
Mullvad SOCKS endpoint reached through a selective WireGuard route. One owned
NetBird peer and TCP port 8088 are permitted for a private-path test. Other
private destinations, literal IPv6 destinations and UDP requests are denied.
It does not alter the laptop's system-wide route, DNS or kill switch.

## File roles

| File | Role |
| --- | --- |
| `server.json.example` | Authenticated VLESS/REALITY listener and ordered outbound policy |
| `client.json.example` | Loopback SOCKS entrance and a single encrypted server outbound |
| `wg-lab.conf.example` | Only the provider SOCKS /32 goes through WireGuard |
| `proxy-guard.nft.example` | Deny fallback paths to provider/private-peer addresses |
| `classlab-proxy-guard.service` | Load the narrow guard once at boot |
| `xray-lab.service` | Unprivileged service with guard prerequisite |
| `target.compose.yaml.example` | Deliberately public, harmless TLS handshake target |
| `Target.Caddyfile.example` | Owned hostname, no private service or filesystem content |

## Template substitutions

Replace every `REPLACE_...` value privately. Use an ordinary text editor;
never run `envsubst` over unknown configuration or paste keys into a public
prompt. Replace the same peer IPv4 in both the Xray rule and nftables guard.

The server's REALITY private key stays on the server. The corresponding
client `password` value is sensitive profile material even though it is an
X25519 public-key-derived field. The UUID and short ID must agree on both ends.
The WireGuard private key is completely separate from those values.

The JSON shape follows the current upstream docs checked for this edition:
`users`, flattened VLESS/SOCKS outbound settings, `method: raw`, and the
REALITY client `password` field. Some older clients use `clients`, `vnext`,
`servers`, `network` or `publicKey`. Do not mix schemas: use a compatible core
on both ends and require `xray run -test` to pass. No Xray core binary is bundled,
version-pinned or claimed as executed during authoring.

## Guard installation, persistence and rollback

Load each guard table **once**. Run `nft -c -f` first. If the table already exists
from a manual load, do not immediately start the loader unit again. Enable it
for the next boot, or use a trusted console to stop the proxy, remove only the
lab guard table and start the unit once. Never flush unrelated rules.

The proxy unit requires the guard loader to succeed. It does not detect an
administrator subsequently deleting rules from the kernel. Keep the rule
loaded while simulating WireGuard/NetBird failures. Test after reboot too.

For removal, stop/disable `xray-lab` first. Then stop/disable the lab guard unit
and remove only `inet classlab_proxy_guard` if retiring the lab. Remove the
WireGuard profile and TLS-target containers only after confirming they are
lab-only. Do not copy destructive removal commands onto an existing server.
