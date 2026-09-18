#!/usr/bin/env python3
"""A limited staged-file helper, NOT a full secret scanner or publication approval.

Requires a Git repo. Reads only staged blobs, not working-tree replacements.
Never prints matched secret values. Images/PDFs need separate visual/metadata review.
"""
from pathlib import PurePosixPath
import re
import subprocess

PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(rb"AKIA[A-Z0-9]{16}"),
    re.compile(rb"Authorization[=: ]+Bearer[ ]+[A-Za-z0-9._-]{20,}", re.I),
]
BANNED_NAMES = {"server.json", "client.json", "wg-lab.conf", "proxy-guard.nft", "ssh-guard.nft"}
BANNED_PARTS = {"data", "private", "secrets", "backups", "runtime", "upstream"}
BANNED_SUFFIXES = {".key", ".pem", ".pfx", ".p12", ".sqlite", ".db", ".pcap", ".pcapng", ".har", ".log", ".sql"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def main() -> int:
    try:
        files = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Run inside a Git repository after staging the intended public files.")
        return 2
    failures = 0
    for name_b in filter(None, files):
        name = name_b.decode("utf-8", errors="surrogateescape")
        p = PurePosixPath(name)
        bad_env = p.name.startswith(".env") and p.name != ".env.example"
        if bad_env or p.name in BANNED_NAMES or BANNED_PARTS.intersection(p.parts) or p.suffix.lower() in BANNED_SUFFIXES:
            print(f"REVIEW forbidden/private-looking path: {name}"); failures += 1
        try:
            size = int(git("cat-file", "-s", f":{name}"))
            if size > 5_000_000:
                print(f"REVIEW large staged file manually: {name}"); failures += 1
                continue
            body = git("show", f":{name}")
        except (subprocess.CalledProcessError, ValueError):
            print(f"REVIEW unreadable staged blob: {name}"); failures += 1
            continue
        if any(pattern.search(body) for pattern in PATTERNS):
            print(f"REVIEW potential credential pattern: {name}"); failures += 1
    print("Common-pattern check finished. Values were not printed.")
    print("Still review domains/IPs, accounts, history, metadata, screenshots and all other secrets.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
