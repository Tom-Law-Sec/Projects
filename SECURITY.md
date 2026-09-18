# Security and sharing boundaries

This is a new educational repository, not an export of a live server. Use
fresh accounts, a separate lab and disposable data. Do not publish personal
infrastructure addresses, transport profiles, passwords, private keys,
recovery material, CA private keys, database backups, raw screenshots, shell
history, request headers or private logs.

## Private homelab and deliberately public proxy are different roles

The core stack binds HTTPS only to `127.0.0.1`. Use the documented SSH local
forward; do not change the binding to all interfaces to fix a connection error.
Management access, database services and private application state are not
intended to be internet-facing. Never grant classmates access to a real password
vault or photo library.

The advanced proxy lab uses a **separate** VM. Its owned TLS target deliberately
publishes TCP 80/443, and its authenticated proxy listens on TCP 8443. Restrict
sources where practical, use fresh credentials, and complete the stated
allow/deny and connection-failure tests. Do not merge its public bindings into
the private core deployment or assume its narrow guard protects other traffic.

## Before publication or reporting

Keep completed proxy and WireGuard profiles outside Git. Files ending in
`.example` are templates only; never replace their placeholders with real
values and commit them. The ignore file and publication helper are safeguards,
not proof that the repository is free of sensitive material.

Review staged content, history, PDF text/links/metadata, images, releases and
attachments. The helper checks selected staged-file names and text patterns;
it does not fully scan PDF internals, every secret type or Git history.

Report suspected exposures privately to the repository owner without putting
working secrets in a public issue. Rotate/revoke exposed credentials first.
Removing a file from the current branch does not remove it from prior history.

This edition has local helper tests and structural checks, not end-to-end
deployment tests or a live security audit. Read `VALIDATION.md` before relying
on an expected result. Use only authorised systems and comply with applicable
network and service rules.
