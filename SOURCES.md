# Technical sources and provenance

Prepared 17 September 2026. These are primary project documentation references,
not an assertion that every upstream version remains unchanged after this date.
The examples and educational explanations are newly authored. Check release-specific
notes before deployment, upgrades and restoration.

## S01 | Docker Engine installation on Debian

Installation, supported Debian versions and Docker/firewall caveat.

<https://docs.docker.com/engine/install/debian/>

## S02 | Docker Engine security

Docker daemon privileges and attack surface.

<https://docs.docker.com/engine/security/>

## S03 | Docker Compose config reference

Quiet validation, interpolation and image-digest override.

<https://docs.docker.com/reference/cli/docker/compose/config/>

## S04 | NetBird self-hosting quickstart

Current controller bootstrap and infrastructure requirements.

<https://docs.netbird.io/selfhosted/selfhosted-quickstart>

## S05 | NetBird groups and access policies

Explicit access grants and the broad default policy.

<https://docs.netbird.io/manage/access-control>

## S06 | NetBird Linux installation

Official client installation and management URL.

<https://docs.netbird.io/get-started/install/linux>

## S07 | Caddy automatic HTTPS

Local certificate authority and client trust requirements.

<https://caddyserver.com/docs/automatic-https>

## S08 | Vaultwarden HTTPS guidance

Secure web-vault context and proxy use.

<https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS>

## S09 | Vaultwarden registration controls

Registration and invitation configuration.

<https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users>

## S10 | Nextcloud reverse-proxy configuration

Trusted proxies and external URL/protocol handling.

<https://docs.nextcloud.com/server/latest/admin_manual/configuration_server/reverse_proxy_configuration.html>

## S11 | Nextcloud Docker image documentation

Community-maintained image, PostgreSQL/Redis, persistence and environment variables.

<https://github.com/nextcloud/docker>

## S12 | Nextcloud backup documentation

Application files, configuration and database recovery set.

<https://docs.nextcloud.com/server/latest/admin_manual/maintenance/backup.html>

## S13 | Immich Docker Compose installation

Official release files and installation flow.

<https://docs.immich.app/install/docker-compose/>

## S14 | Immich requirements and quickstart

Memory, CPU and database storage requirements; also see https://docs.immich.app/ .

<https://docs.immich.app/install/requirements/>

## S15 | Immich backup and restore

Database and media must both be backed up; release compatibility matters.

<https://docs.immich.app/administration/backup-and-restore/>

## S16 | Cloudflare Access service tokens

Machine authentication requires compatible client/header handling.

<https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/>

## S17 | Uptime Kuma project documentation

Monitoring types, Docker image and local-data requirement.

<https://github.com/louislam/uptime-kuma>

## S18 | Project X routing configuration

Ordered routing rules and outbound selection.

<https://xtls.github.io/en/config/routing.html>

## S19 | restic repository preparation

Encrypted repository initialisation and password handling.

<https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html>

## S20 | restic restore documentation

Restoring to a separate target and verifying recovery.

<https://restic.readthedocs.io/en/stable/050_restore.html>

## S21 | GitHub removing sensitive repository data

Rotate exposed credentials; deletion does not erase old copies/history.

<https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>

## S22 | Docker Compose merge and override rules

Replacing, rather than accumulating, a service port list.

<https://docs.docker.com/reference/compose-file/merge/>


## S23 | Xray-core official releases

Choose a compatible core and verify the selected artifact; no binary is bundled.

<https://github.com/XTLS/Xray-core/releases>

## S24 | Docker firewall and port-publishing behaviour

<https://docs.docker.com/engine/network/packet-filtering-firewalls/>

<https://docs.docker.com/engine/network/port-publishing/>

## S25 | OpenSSH daemon configuration reference

Authentication, forwarding and effective settings; consult the installed manual too.

<https://man.openbsd.org/sshd_config>

## S26 | Xray transport and REALITY configuration

<https://xtls.github.io/en/config/transport.html>

<https://xtls.github.io/en/config/transports/reality.html>

## S27 | Xray VLESS configuration

<https://xtls.github.io/en/config/inbounds/vless.html>

<https://xtls.github.io/en/config/outbounds/vless.html>

## S28 | Xray SOCKS outbound

<https://xtls.github.io/en/config/outbounds/socks.html>

## S29 | nftables packet/interface matching

<https://wiki.nftables.org/wiki-nftables/index.php/Matching_packet_metainformation>

## S30 | Dozzle authentication and security considerations

<https://dozzle.dev/guide/authentication>

## S31 | AdGuard Home installation and configuration

<https://adguard-dns.io/kb/adguard-home/getting-started/>

## S32 | Mullvad WireGuard and provider SOCKS

<https://mullvad.net/en/help/easy-wireguard-mullvad-setup-linux>

<https://mullvad.net/en/help/socks5-proxy>

## S33 | WireGuard wg-quick reference

<https://man7.org/linux/man-pages/man8/wg-quick.8.html>

## S34 | Cloudflare Tunnel configuration and ingress

<https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/>

## S35 | systemd execution and privilege controls

<https://manpages.debian.org/trixie/systemd/systemd.exec.5.en.html>

## S36 | Xray SOCKS inbound

<https://xtls.github.io/en/config/inbounds/socks.html>

## P01 | Author-supplied project history

Sanitised summaries of the author's reported projects and outcomes. These
establish project context, not an independent live-server audit. Actual domains,
addresses, secrets and private media were not reproduced.

## Third-party rights

Applications referenced here retain their upstream licenses. The included MIT
license covers only newly authored teaching material and example code. It does
not grant rights to redistribute media, commercial assets, credentials or an
upstream product's proprietary components.
