"""Offline fixtures only. No transport, signing, or secret access."""
import copy
import hashlib
import re
import unittest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PUBLIC = bytes.fromhex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
SIGNATURE = bytes.fromhex('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155' '5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
IDENTITY = hashlib.sha256(PUBLIC).hexdigest()
NOW = 1700000000
PAYLOAD = {'thread': 9, 'body': 'Synthetic fixture only.'}

def validate_fixture(response):
    if type(response) is not dict or response.get('ok') is not True or type(response.get('data')) is not dict:
        raise ValueError('invalid envelope')
    d = response['data']
    token = d.get('token')
    if type(token) is not str or not re.fullmatch(r'synthetic-[!-~]{1,100}', token):
        raise ValueError('not a synthetic token')
    if d.get('work_prefix') != f'glp-ai-forum-v1\n{token}\n' or d.get('identity') != IDENTITY:
        raise ValueError('prefix or identity mismatch')
    if type(d.get('expires')) is not int or not NOW < d['expires'] <= NOW + 600:
        raise ValueError('invalid expiry')
    if type(d.get('difficulty_bits')) is not int or not 1 <= d['difficulty_bits'] <= 12:
        raise ValueError('invalid fixture difficulty')
    p = d.get('payload')
    if type(p) is not dict or p.keys() != PAYLOAD.keys() or any(type(p[k]) is not type(v) or p[k] != v for k,v in PAYLOAD.items()):
        raise ValueError('payload mismatch')
    h = d.get('payload_sha256')
    if type(h) is not str or not re.fullmatch('[0-9a-f]{64}', h):
        raise ValueError('invalid hash shape')
    # Shape only: server serialization is not documented.
    return True

class OfflineTests(unittest.TestCase):
    def test_rfc8032(self):
        key = Ed25519PublicKey.from_public_bytes(PUBLIC)
        key.verify(SIGNATURE, b'')
        with self.assertRaises(InvalidSignature):
            key.verify(SIGNATURE, b'x')
    def test_challenge(self):
        fixture = {'ok': True, 'data': {'token':'synthetic-test', 'work_prefix':'glp-ai-forum-v1\nsynthetic-test\n', 'identity':IDENTITY, 'expires':NOW+600, 'difficulty_bits':10, 'payload':PAYLOAD, 'payload_sha256':'0'*64}}
        self.assertTrue(validate_fixture(fixture))
        for field, value in [('token','real-token'), ('work_prefix','wrong'), ('identity','wrong'), ('expires',NOW), ('expires',NOW+601), ('difficulty_bits',True), ('difficulty_bits',20), ('payload',{'thread':9.0,'body':PAYLOAD['body']}), ('payload',{'thread':9,'body':'changed'}), ('payload_sha256','bad')]:
            bad = copy.deepcopy(fixture)
            bad['data'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate_fixture(bad)
        with self.assertRaises(ValueError):
            validate_fixture({'ok':False,'data':fixture['data']})

if __name__ == '__main__':
    unittest.main()
