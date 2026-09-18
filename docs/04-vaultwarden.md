# 04 | A self-hosted password-vault lab

## Original project and the classroom boundary

The original Vaultwarden deployment was reported working. This classroom
version makes closed registration, a disabled server administration interface
and account-level two-factor authentication explicit goals. It teaches
controlled access and persistence, not hosting real classmates' passwords.

Vaultwarden is a community implementation compatible with Bitwarden clients;
it is not the same product as Bitwarden's official server. Its web vault needs
a suitable secure browser context, so complete the HTTPS chapter first. [S08]

## What the configuration does

In `labs/core/compose.yaml`, the service has a persistent `/data` mount but no
published host port. Only Caddy can reach it through its application network.
`DOMAIN` points to the actual classroom URL, including `:8443`.
`SIGNUPS_ALLOWED` starts false; `INVITATIONS_ALLOWED` is false. No `ADMIN_TOKEN`
is configured, so the separate server administration panel is not enabled.
These are explicit choices, not evidence that an installation can never be
compromised. [S09]

The vault's user account and the server administration panel are separate
concepts. A person who can sign in to their vault does not automatically need
the server-wide administration interface.

## Step 1 - Start and verify the empty service

Run on the lab server from `labs/core`:

```bash
sudo ./lab.sh up -d vaultwarden caddy
sudo ./lab.sh ps
```

Open `https://vault.lab.test:8443` through the verified laptop tunnel. There
should not yet be an account you can use. A real deployment must not be left
with open first-user enrolment while other people can reach it.

## Step 2 - Create one disposable account deliberately

Use only a fictional lab identity and a new passphrase you do not use anywhere
else. While access is restricted to your own machine, privately edit `.env` and
set `VW_SIGNUPS_ALLOWED=true`. Recreate the service:

```bash
sudo ./lab.sh up -d --force-recreate vaultwarden
```

Create your one demonstration account in the web vault. Immediately set
`VW_SIGNUPS_ALLOWED=false` again and repeat the same recreate command.
A restart alone may not apply changed container environment values; the explicit
recreation makes that transition clear.

Use a separate browser session to attempt a second registration. It should be
rejected. Merely hiding a registration button would not establish that the
registration API itself is disabled. Preserve a sanitised description of the
negative test, not a screenshot containing the real password or email.

## Step 3 - Create and synchronise a fake vault item

Add an item named `Classroom Demo` using a fictional service such as
`https://example.com`. Enter only generated demonstration credentials. Lock and
unlock the vault. Then log out and sign in again. Verify that the item persists
and that a different, incorrect passphrase does not unlock the account.

A test browser extension is optional and should use a separate lab profile.
Point it at the classroom server URL only after checking certificate trust.
Do not move your everyday password manager account to this exercise server.

## Step 4 - Demonstrate two-factor authentication

Using the application's security settings, enable a supported second factor
for the disposable account. Keep the resulting setup QR code, seed and recovery
code private. Do not include them in evidence even for a demo: teaching everyone
to publish recovery material is a bad habit. Log out and verify that the next
login requires the expected second factor.

Account two-factor authentication does not rescue a leaked master password in
every possible attack, and it does not replace server maintenance or backups.
Document it as one layer of protection, not as a complete security claim.

## Step 5 - Verify persistence and recovery requirements

Recreate the container without deleting `data/vaultwarden`:

```bash
sudo ./lab.sh up -d --force-recreate vaultwarden
```

Log in again and verify the fake item. The exercise demonstrates separation of
container lifecycle from persistent state. It is not a backup test until the
data is restored into a separate environment, covered in chapter 11.

A safe recovery set includes the application's database and associated persistent
files, not just the visible Compose file. The supplied cold-backup approach
stops writers before taking an encrypted copy, avoiding a casual live-copy of
a changing SQLite database. Keep any encrypted backup's recovery material away
from the same disk that it is meant to protect.

## Troubleshooting and evidence

For a page that will not load, test the tunnel, name and CA trust before changing
Vaultwarden. For a failure to create an account, check the deliberate signup
window rather than permanently opening registrations. For a new configuration
that appears ignored, check container recreation and whether an existing
application configuration overrides an environment option.

**Finish with:** a trusted HTTPS page, one disposable account, rejected second
registration, demonstrated second-factor login, and persistence after recreation.
No real secrets should appear in screenshots, terminal recordings or the report.

**References:** S08-S09; original context P01.
