# 06 | A separate Immich photo library

## Original project and why it stays separate

The original photo service was reported working through HTTPS, with the initial
administrator created and phone media uploads running. Its storage was kept
separate from Nextcloud. This class lab preserves that separation and uses only
harmless sample photos you own.

Do not treat a photo uploader as proof that the server has a recoverable backup.
Immich's database and photo/video files are distinct parts of the recovery set.
A database backup alone does not contain the media. [S15]

## Step 1 - Check capacity before installing

Read the current installation and requirements pages, S13-S14. At the check for
this edition, the quickstart calls for at least 6 GB RAM and two CPU cores. Leave
additional headroom for the operating system and any other services. These are
not performance benchmarks for the original hardware. On a small machine,
stop other labs or use a separate VM rather than launching everything together.

Prepare an empty, sufficiently large local storage location. Do not reuse the
Nextcloud data directory or its PostgreSQL database. Do not place the live
Immich database on a network share. Record the actual release chosen before
starting; application and database dependencies must remain compatible.

## Step 2 - Download a matching official release pair

Immich's supporting services and database extensions change over time. This
pack intentionally does not invent a replacement Compose stack. Open the
project's official release page and select a supported, non-prerelease tag.
Use that **same tag** for both required files.

Run on the lab server from the repository root:

```bash
mkdir -p labs/immich/upstream
cd labs/immich/upstream
read -r -p 'Official release tag, for example vX.Y.Z: ' IMMICH_RELEASE
curl -fL \
  "https://github.com/immich-app/immich/releases/download/$IMMICH_RELEASE/docker-compose.yml" \
  -o docker-compose.yml
curl -fL \
  "https://github.com/immich-app/immich/releases/download/$IMMICH_RELEASE/example.env" \
  -o .env
chmod 600 .env
```

Do this only in a new empty directory. Downloading to `.env` over an existing
installation would overwrite its settings. The example `vX.Y.Z` is descriptive,
not a real release tag to enter. Confirm both downloads succeeded before going
further. Retain their checksums and the chosen release in your private build
record. The ignored `upstream/` folder is not part of the public repository.

## Step 3 - Configure private data and pin the version

Read the downloaded files. In `.env`, set `UPLOAD_LOCATION` to an empty photo
library location and `DB_DATA_LOCATION` to a separate local database location.
The relative defaults can be used for a disposable exercise with enough disk
space. Set `IMMICH_VERSION` to the exact release tag selected above rather than
a moving major-release alias.

Generate an independent database password with `openssl rand -hex 24` and place
it privately in `DB_PASSWORD`. Do not record it in screenshots or reuse the
Nextcloud password. Keep other database identifiers consistent with the official
file. Do not change a password in `.env` later and assume an existing database's
account password has automatically changed.

## Step 4 - Replace the public port binding before first start

Create `compose.private.yaml` beside the downloaded files with:

```yaml
services:
  immich-server:
    ports: !override
      - "127.0.0.1:2283:2283"
```

This requires a Compose version supporting `!override` (2.24.4 or newer). It
replaces the upstream port list; an ordinary merged list can accidentally retain
the public binding. Verify the model before starting. A changed upstream service
name or target port must be reconciled with the selected official release.

```bash
sudo docker compose -f docker-compose.yml -f compose.private.yaml config -q
sudo docker compose -f docker-compose.yml -f compose.private.yaml \
  config --format json | python3 ../../../scripts/check_bindings.py
sudo docker compose -f docker-compose.yml -f compose.private.yaml \
  config --lock-image-digests -o compose.images.yaml
sudo docker compose -f docker-compose.yml -f compose.private.yaml \
  -f compose.images.yaml up -d
```

The helper prints port bindings, not environment secrets. It fails when a
published port is not explicitly loopback-bound. Keep using all three `-f`
arguments for later commands so the privacy override and image lock remain in
force. Do not run a bare `docker compose up` here and drop the overrides.

## Step 5 - Open a local test connection

On the laptop, open an independent tunnel:

```bash
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:2283:127.0.0.1:2283 \
  labuser@YOUR_LAB_SERVER_ADDRESS
```

Open `http://127.0.0.1:2283` on that laptop. This HTTP connection is local to the
laptop and then carried through the SSH connection; it is not an instruction
to expose unencrypted HTTP on a public server. The first-user flow creates an
administrator, so complete it while only you can reach the service. [S13]

Upload a few owned sample images and a short sample video. Check that processing
finishes, thumbnails appear and the originals can be downloaded. Restart the
containers without deleting storage and confirm the sample library remains.

## Step 6 - Learn the mobile and recovery boundaries

The laptop tunnel is not a phone endpoint. For a mobile extension, design a
private HTTPS address reachable by the enrolled phone, with a certificate the
actual app trusts. Test foreground upload, background operation, permissions
and reconnection separately. A browser login does not prove all of those work.

Do **not** enable automatic local deletion in this exercise. Keep the originals
until a verified restore from an independent backup has succeeded. “Uploaded”,
“synchronised”, “in the recycle bin” and “recoverable after losing the server”
are different states.

Use the selected release's backup and restore instructions for its database,
and back up the corresponding media tree. Test recovery on a separate instance
with compatible versions. A storage quota or a second directory on the same
physical disk does not protect against loss of that disk. [S15]

**Finish with:** matching release files, recorded digests, loopback-only binding,
an initial admin, verified sample upload/download, persistence and a documented
restore plan. The mobile extension is not complete until tested on the phone.

**References:** S13-S15, S22; original context P01.
