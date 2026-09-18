#!/usr/bin/env python3
"""Create an untracked .env with independently generated secrets; never overwrite."""
from pathlib import Path
import os
import secrets


def main() -> int:
    core = Path(__file__).resolve().parents[1] / "labs" / "core"
    text = (core / ".env.example").read_text(encoding="utf-8")
    for key in ("NC_ADMIN_PASSWORD", "NC_DB_PASSWORD"):
        text = text.replace(f"{key}=GENERATE_LOCALLY", f"{key}={secrets.token_hex(24)}")
    target = core / ".env"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("Refusing to overwrite existing .env; preserve your working secrets.")
        return 2
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(text)
    print("Created local .env with fresh passwords. No secret values were printed.")
    print("Read it privately for the Nextcloud login. Never share or commit it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
