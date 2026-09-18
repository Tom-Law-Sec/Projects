#!/usr/bin/env python3
"""Check this pack's narrow Xray SERVER template policy, not general Xray security.

Only reads a local file. Prints no credential values. --ready also rejects
unfilled placeholders and checks the allowlisted peer is one overlay IPv4.
You must still run the selected Xray core's parser and live allow/deny tests.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
from pathlib import Path

DENIED = {
    '0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8',
    '169.254.0.0/16', '172.16.0.0/12', '192.0.0.0/24', '192.0.2.0/24',
    '192.168.0.0/16', '198.18.0.0/15', '198.51.100.0/24', '203.0.113.0/24',
    '224.0.0.0/4', '240.0.0.0/4', '::/0',
}


def check(model: object, ready: bool = False) -> list[str]:
    """Return fixed diagnostic labels; never include input credential values."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return ['Expected a JSON object.']
    try:
        outs = model['outbounds']
        if not isinstance(outs, list) or len(outs) != 3:
            errors.append('Expected exactly three documented outbounds.')
        else:
            expected = [
                {'tag': 'mullvad', 'protocol': 'socks',
                 'settings': {'address': '10.64.0.1', 'port': 1080}},
                {'tag': 'netbird', 'protocol': 'freedom', 'settings': {}},
                {'tag': 'deny', 'protocol': 'blackhole', 'settings': {}},
            ]
            if outs != expected:
                errors.append('Outbound defaults or options differ from the narrow template.')
        routing = model['routing']
        if routing.get('domainStrategy') != 'AsIs' or routing.get('balancers'):
            errors.append('Routing resolution or balancing differs from the baseline.')
        rules = routing['rules']
        if not isinstance(rules, list) or len(rules) != 5:
            errors.append('Expected the five ordered baseline rules.')
        else:
            if rules[0] != {'type': 'field', 'network': 'udp', 'outboundTag': 'deny'}:
                errors.append('The first rule must deny UDP.')
            allow = rules[1]
            if set(allow) != {'type', 'ip', 'port', 'network', 'outboundTag'} or \
                    allow.get('type') != 'field' or allow.get('network') != 'tcp' or \
                    allow.get('port') != '8088' or allow.get('outboundTag') != 'netbird':
                errors.append('Private allow must be TCP 8088 only.')
            ips = allow.get('ip')
            if not isinstance(ips, list) or len(ips) != 1 or not isinstance(ips[0], str):
                errors.append('Private allow must contain one IPv4 /32.')
            elif ips[0] == 'REPLACE_LAB_PEER_IPV4/32' and not ready:
                pass
            else:
                try:
                    net = ipaddress.ip_network(ips[0], strict=True)
                    allowed = [ipaddress.ip_network(s) for s in
                               ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '100.64.0.0/10']]
                    if net.version != 4 or net.prefixlen != 32 or not any(net.subnet_of(n) for n in allowed):
                        raise ValueError
                except (ValueError, TypeError):
                    errors.append('The selected peer must be a private/overlay IPv4 /32.')
            deny = rules[2]
            if set(deny) != {'type', 'ip', 'outboundTag'} or \
                    deny.get('type') != 'field' or deny.get('outboundTag') != 'deny' or \
                    not isinstance(deny.get('ip'), list) or set(deny['ip']) != DENIED:
                errors.append('The private/reserved/literal-IPv6 deny rule changed.')
            if rules[3] != {'type': 'field', 'domain': ['domain:lab.test', 'domain:home.arpa',
                                'domain:localhost', 'domain:local'], 'outboundTag': 'deny'}:
                errors.append('The private-name deny rule changed.')
            if rules[4] != {'type': 'field', 'network': 'tcp', 'outboundTag': 'mullvad'}:
                errors.append('The final TCP rule must use provider egress.')
        ins = model['inbounds']
        if not isinstance(ins, list) or len(ins) != 1:
            errors.append('Expected one authenticated inbound.')
        else:
            inbound = ins[0]
            if inbound.get('protocol') != 'vless' or inbound.get('port') != 8443:
                errors.append('Unexpected listener protocol or port.')
            stream = inbound['streamSettings']
            if stream.get('security') != 'reality' or stream.get('method') != 'raw':
                errors.append('The documented REALITY transport is required.')
            reality = stream['realitySettings']
            if reality.get('target') != '127.0.0.1:443' or reality.get('show') is not False:
                errors.append('Owned local TLS target and non-debug setting are required.')
            if not reality.get('privateKey') or not reality.get('serverNames') or not reality.get('shortIds'):
                errors.append('Required REALITY identity fields are missing.')
            settings = inbound['settings']
            users = settings['users']
            if settings.get('decryption') != 'none' or not isinstance(users, list) or len(users) != 1 or \
                    not users[0].get('id') or users[0].get('flow') != 'xtls-rprx-vision':
                errors.append('Expected one deliberately provisioned VLESS user.')
        if ready and 'REPLACE_' in json.dumps(model):
            errors.append('Unfilled template placeholders remain.')
    except (KeyError, TypeError, AttributeError):
        errors.append('Missing or malformed configuration fields.')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--ready', action='store_true')
    args = parser.parse_args()
    try:
        model = json.loads(args.file.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print('FAIL: could not read valid JSON. Input content was not printed.')
        return 2
    errors = check(model, args.ready)
    for error in errors:
        print('REVIEW:', error)
    if errors:
        return 1
    print('PASS: limited template-policy checks. No credential values were printed.')
    print('Still required: Xray core validation, host guards and actual routing/failure tests.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
