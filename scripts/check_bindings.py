#!/usr/bin/env python3
"""Read Compose JSON on stdin; report only bindings, never environment values."""
import json
import sys

def main() -> int:
    try:
        model = json.load(sys.stdin)
        if not isinstance(model, dict) or not isinstance(model.get("services"), dict):
            raise ValueError("Expected a normalised Compose object with services")
        count = 0
        for name, service in model["services"].items():
            if not isinstance(service, dict):
                raise ValueError("Expected a normalised service object")
            if service.get("network_mode") == "host":
                raise ValueError(f"{name}: host networking is outside this lab policy")
            for port in service.get("ports", []):
                if not isinstance(port, dict):
                    raise ValueError(f"{name}: expected normalised JSON port object")
                ip = port.get("host_ip")
                if ip not in {"127.0.0.1", "::1"}:
                    raise ValueError(f"{name}: a port is not explicitly loopback-bound")
                print(f"CHECK {name}: {ip}:{port.get('published')} -> {port.get('target')}")
                count += 1
        if not count:
            raise ValueError("No published ports found; confirm the expected model")
        print("PASS: every published port is explicitly loopback-bound.")
        return 0
    except (ValueError, KeyError, TypeError) as exc:
        print(f"BINDING CHECK FAILED: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
