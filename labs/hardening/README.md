# Apply only to an owned disposable lab

Read handbook chapter 08 first. These files are new classroom examples, not
original server configuration. Keep console access and an existing good SSH
session. Verify the actual NetBird interface and SSH account before editing.

Copy templates to a private directory outside this repository. Install nftables
using the lab distribution's packages (`sudo apt install nftables` on Debian).
Do **not** overwrite or blindly enable the distribution-wide firewall ruleset.
Create `/etc/classlab` with `sudo install -d -m 0700 /etc/classlab`; the guard
file is root-readable and must be edited with `sudo`.

For persistence, install the dedicated unit after checking the filled rule:

```bash
sudo nft -c -f /etc/classlab/ssh-guard.nft
sudo install -m 0644 labs/hardening/classlab-ssh-guard.service \
  /etc/systemd/system/classlab-ssh-guard.service
sudo systemctl daemon-reload
sudo systemctl enable classlab-ssh-guard.service
```

If the guard was already loaded manually, **do not start it a second time**.
Enablement arranges the first load after reboot. If it is not yet loaded,
`sudo systemctl start classlab-ssh-guard` loads it once now. Confirm intended
allow/deny results, then reboot with console access and verify again. Rules are
not continuously enforced against other privileged processes that replace them.

This unit ordering is not an atomic SSH-startup guarantee; network/cloud firewall
policy must independently keep public SSH closed. Different SSH socket-activation
setups require their own review. Never rely only on boot ordering.

Rollback from a trusted console: first stop/disable this guard unit if enabled,
then remove **only its table** with
`sudo nft delete table inet classlab_ssh_guard`. This reopens the previous
network policy for SSH; do so only while recovering and restore the intended
restriction afterwards. Never use `nft flush ruleset` here.

For rule changes, keep the console, stop the unit, remove only its table, then
start the updated unit once. If unrelated rules are managed by NetBird, Docker
or another firewall, retain them and test the combined result. Disabling a
unit does not itself delete rules already loaded into the kernel.
