# Immich: use the matching official release files

Read ../../docs/06-immich.md before downloading or running anything. This folder
intentionally does not ship a hand-written replacement database stack. Immich's
release Compose file and environment template must come from the SAME selected
release. The setup recipe keeps port 2283 on loopback and uses an SSH tunnel.

Put downloaded files in `upstream/` (ignored). Review and retain their release
number and checksums privately. Never point Immich at Nextcloud's managed data
directory or reuse its database. This classroom exercise uses synthetic photos.
