# 05 | File sync with Nextcloud, PostgreSQL and Redis

## Original project and the architecture

The original Nextcloud project provided remote file access with a defined
storage budget. Mobile and desktop use was reported in the project history.
This teaching version uses PostgreSQL, Redis and a separate, disposable data
tree to make the application relationships reproducible.

The image used here is the community-maintained Nextcloud Docker microservice
image, not the vendor's All-in-One deployment. We use it to make the application,
database, cache and job runner visible as separate components. [S11]

```text
Caddy -> Nextcloud web application -> PostgreSQL metadata
                      |-----------> Redis coordination/cache
                      |-----------> Managed file directory
Cron -> same configuration and managed files -> scheduled jobs
```

A database record and an uploaded file solve different storage problems. An
empty database with an old data folder is not automatically a complete restore.
Likewise, Redis is not your recovery copy of uploaded documents.

## Step 1 - Understand the supplied variables

Read `x-nc-env` in `compose.yaml`. The database host is the Compose service name
`db`, not `localhost`: inside a container, localhost refers to that container.
The database name and account are dedicated to this application. The generated
database password is shared only with the components that need it.

The public-facing classroom name is `cloud.lab.test:8443`. The external protocol
and URL overrides tell Nextcloud how clients reached it through Caddy. Only the
specific proxy address is trusted. `REDIS_HOST=redis` selects the separate Redis
service. The application and cron job runner use the same persistent directory.
These environment options are defined in the image documentation. [S10, S11]

## Step 2 - Start the database and application

Run on the lab server, in `labs/core`:

```bash
sudo ./lab.sh up -d db redis nextcloud
sudo ./lab.sh ps
sudo ./lab.sh exec --user www-data nextcloud php occ status
```

On first start the image needs to initialise the installation. Until that
finishes, `occ status` can fail or show an incomplete state. Inspect local logs
privately and retry the status check; do not delete the database to make an
initialisation warning disappear.

Once installed, the status command should show the application installed and
not requiring a database upgrade. Then start the job runner and select cron:

```bash
sudo ./lab.sh up -d cron
sudo ./lab.sh exec --user www-data nextcloud php occ background:cron
```

This edition keeps the database/cache network private and provides the cron
container a separate outbound network for jobs that require Internet access.
No database or Redis port is published on the host.

## Step 3 - Sign in and create a normal user

Open `https://cloud.lab.test:8443` in the trusted lab browser. The initial admin
name is `labadmin`; its generated password is in the server's private `.env`.
Read it privately without streaming the terminal to the class. These values
are used during initial installation, not as a universal password reset method.

Create a normal account such as `student-demo` and give it a small quota, for
example 1 GB. Use the normal account for the file exercise. Keep administration
separate from routine use so that you can explain which tasks require elevated
application privileges.

Upload three harmless files with distinct content. Rename one through Nextcloud,
download another and compare its hash with the original. Check that a file
uploaded under one user is not visible to another user without an intentional
share. A successful admin login alone does not test user isolation.

## Step 4 - Test the client workflow

A desktop sync client can connect to the same classroom URL while the SSH
tunnel is open and its certificate is trusted. Use a new local sync folder,
not a directory containing the only copy of your coursework. Create one small
text file locally, allow it to sync, then modify it through the web interface
and observe the client's behaviour.

Distinguish **synchronisation** from **backup**. A synchronised deletion or bad
change can propagate. The existence of a second client does not prove that you
can recover an earlier server state after a hardware failure.

A phone is an advanced extension because the basic SSH-forwarded lab is tied to
the laptop. Do not point a phone at a public login page and assume its native
API has passed all tests. Use a separately planned private HTTPS path and verify
its authentication, certificate trust and upload behaviour.

## Step 5 - Check the operational details

Review the administration overview. Explain each remaining warning rather than
claiming a warning-free deployment without checking. Confirm that background
jobs run. Test the DAV discovery redirect from the laptop:

```bash
curl --cacert classlab-root.crt \
  --resolve cloud.lab.test:8443:127.0.0.1 \
  -I https://cloud.lab.test:8443/.well-known/caldav
```

The Caddy configuration should return a redirect to the application's DAV path
using the same external HTTPS hostname and port. That verifies a specific
integration detail; it does not establish that every calendar client works.

The application's quota is not a hard quota for the entire physical disk.
Database growth, previews, versions, trash, logs and backups also need capacity.
Keep Immich's media directory separate from Nextcloud's managed data directory.
Do not manipulate files underneath Nextcloud as if its metadata will always
update automatically.

## Troubleshooting, backup and completion

An untrusted-domain message points to hostname configuration. An HTTP redirect
or mixed-content problem points to the proxy/external URL. A database connection
failure points to credentials, service discovery or database readiness. A stuck
sync client may involve permissions, quota, conflict handling or an interrupted
tunnel. Reinstalling a desktop client is not a substitute for understanding the
server-side error.

A recovery set includes configuration, managed files and the matching database.
Use chapter 11's stopped-stack recovery exercise, or follow Nextcloud's documented
maintenance-mode/database backup procedure for a production design. [S12]

**Finish with:** normal-user login, a verified file round-trip, an isolation test,
working scheduled jobs, documented quota/headroom and a successful separate
restore drill before placing valuable files on the service.

**References:** S10-S12; original context P01.
