"""Local deterministic helper/template tests. No network or server deployment."""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('proxy_check', ROOT/'scripts/check_proxy.py')
proxy = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(proxy)
TEMPLATE = json.loads((ROOT/'labs/proxy/server.json.example').read_text())


def run_script(name: str, payload: object) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT/'scripts'/name)],
                          input=json.dumps(payload), text=True, capture_output=True, timeout=10)


class BindingTests(unittest.TestCase):
    def model(self, ip='127.0.0.1'):
        return {'services': {'caddy': {'ports': [{'host_ip': ip, 'published': '8443', 'target': 443}]}}}
    def test_loopback_ipv4(self):
        self.assertEqual(run_script('check_bindings.py', self.model()).returncode, 0)
    def test_loopback_ipv6(self):
        self.assertEqual(run_script('check_bindings.py', self.model('::1')).returncode, 0)
    def test_unspecified_address_denied(self):
        self.assertNotEqual(run_script('check_bindings.py', self.model(None)).returncode, 0)
    def test_wildcard_denied(self):
        self.assertNotEqual(run_script('check_bindings.py', self.model('0.0.0.0')).returncode, 0)
    def test_host_network_denied(self):
        m=self.model();m['services']['caddy']['network_mode']='host'
        self.assertNotEqual(run_script('check_bindings.py',m).returncode,0)
    def test_no_published_port_is_flagged(self):
        self.assertNotEqual(run_script('check_bindings.py',{'services':{'x':{}}}).returncode,0)
    def test_malformed_input(self):
        self.assertNotEqual(run_script('check_bindings.py',[]).returncode,0)
    def test_environment_values_not_printed(self):
        m=self.model();m['services']['caddy']['environment']={'SECRET':'LOCAL_TEST_MARKER_ONLY'}
        r=run_script('check_bindings.py',m)
        self.assertNotIn('LOCAL_TEST_MARKER_ONLY',r.stdout+r.stderr)


class ProxyTests(unittest.TestCase):
    def setUp(self): self.model=copy.deepcopy(TEMPLATE)
    def test_example_policy_accepted(self): self.assertEqual(proxy.check(self.model),[])
    def test_ready_rejects_placeholders(self): self.assertTrue(proxy.check(self.model,ready=True))
    def test_no_default_direct_outbound(self):
        self.model['outbounds'].reverse();self.assertTrue(proxy.check(self.model))
    def test_extra_outbound_flagged(self):
        self.model['outbounds'].append({'protocol':'freedom'});self.assertTrue(proxy.check(self.model))
    def test_broad_private_range_rejected(self):
        self.model['routing']['rules'][1]['ip']=['100.64.0.0/10'];self.assertTrue(proxy.check(self.model))
    def test_extra_private_port_rejected(self):
        self.model['routing']['rules'][1]['port']='22,8088';self.assertTrue(proxy.check(self.model))
    def test_udp_deny_required(self):
        self.model['routing']['rules'][0]['outboundTag']='mullvad';self.assertTrue(proxy.check(self.model))
    def test_private_block_required(self):
        self.model['routing']['rules'][2]['ip'].remove('10.0.0.0/8');self.assertTrue(proxy.check(self.model))
    def test_reality_required(self):
        self.model['inbounds'][0]['streamSettings']['security']='none';self.assertTrue(proxy.check(self.model))
    def test_malformed_model_rejected(self): self.assertTrue(proxy.check(None))
    def test_client_loopback_single_outbound(self):
        c=json.loads((ROOT/'labs/proxy/client.json.example').read_text())
        self.assertEqual(c['inbounds'][0]['listen'],'127.0.0.1')
        self.assertFalse(c['inbounds'][0]['settings']['udp'])
        self.assertEqual(len(c['outbounds']),1)
        self.assertEqual(c['outbounds'][0]['protocol'],'vless')


class SecretGenerationTests(unittest.TestCase):
    def test_generation_permissions_and_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'scripts').mkdir();(root/'labs/core').mkdir(parents=True)
            shutil.copy(ROOT/'scripts/init_env.py',root/'scripts/init_env.py')
            shutil.copy(ROOT/'labs/core/.env.example',root/'labs/core/.env.example')
            cmd=[sys.executable,str(root/'scripts/init_env.py')]
            first=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(first.returncode,0)
            env=root/'labs/core/.env';body=env.read_bytes()
            values=dict(line.split('=',1) for line in body.decode().splitlines() if '=' in line and not line.startswith('#'))
            a,b=values['NC_ADMIN_PASSWORD'],values['NC_DB_PASSWORD']
            self.assertNotEqual(a,b);self.assertEqual(len(a),48)
            self.assertNotIn(a,first.stdout+first.stderr)
            if os.name=='posix': self.assertEqual(stat.S_IMODE(env.stat().st_mode),0o600)
            second=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertNotEqual(second.returncode,0);self.assertEqual(env.read_bytes(),body)


@unittest.skipUnless(shutil.which('git'), 'Git required for staged-file helper tests')
class PublicationTests(unittest.TestCase):
    def check_file(self,name,body):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q'],cwd=p,check=True,capture_output=True)
            f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
            subprocess.run(['git','add','--',name],cwd=p,check=True,capture_output=True)
            return subprocess.run([sys.executable,str(ROOT/'scripts/check_publish.py')],cwd=p,
                                  capture_output=True,text=True,timeout=10)
    def test_ordinary_document_allowed(self):
        self.assertEqual(self.check_file('README.md','Class lab notes').returncode,0)
    def test_local_env_rejected(self):
        self.assertNotEqual(self.check_file('.env','TEST=not-a-secret').returncode,0)
    def test_filled_transport_profile_rejected(self):
        self.assertNotEqual(self.check_file('client.json','{}').returncode,0)
    def test_token_pattern_not_echoed(self):
        token='gh'+'p_'+'Z'*40
        r=self.check_file('notes.txt',token)
        self.assertNotEqual(r.returncode,0);self.assertNotIn(token,r.stdout+r.stderr)


class HardeningTests(unittest.TestCase):
    def test_ssh_keeps_local_forwarding_and_disables_password(self):
        s=(ROOT/'labs/hardening/00-classlab.conf.example').read_text()
        for value in ['AllowTcpForwarding local','PasswordAuthentication no',
                      'PermitRootLogin no','KbdInteractiveAuthentication no']:
            self.assertIn(value,s)
    def test_guards_are_narrow_not_global_flush(self):
        for path in ['labs/hardening/ssh-guard.nft.example','labs/proxy/proxy-guard.nft.example']:
            lines=(ROOT/path).read_text().splitlines()
            self.assertFalse(any(line.strip().startswith('flush ruleset') for line in lines))
            self.assertIn('counter reject','\n'.join(lines))
    def test_proxy_service_requires_guard_and_no_root(self):
        s=(ROOT/'labs/proxy/xray-lab.service').read_text()
        self.assertIn('User=xraylab',s);self.assertIn('Requires=classlab-proxy-guard.service',s)
        self.assertIn('NoNewPrivileges=true',s)
    def test_selective_wireguard_has_no_default_route(self):
        s=(ROOT/'labs/proxy/wg-lab.conf.example').read_text()
        self.assertIn('AllowedIPs = 10.64.0.1/32',s)
        self.assertNotIn('AllowedIPs = 0.0.0.0/0',s)
        self.assertFalse(any(line.startswith('DNS =') for line in s.splitlines()))


if __name__=='__main__': unittest.main()
