"""Offline transaction ledger; no transport, credentials or automatic retry."""
import hashlib
import json
import sqlite3

def proposal_digest(identity, action, payload):
    if not isinstance(identity, str) or len(identity)!=64 or any(c not in '0123456789abcdef' for c in identity):
        raise ValueError("invalid identity")
    if action not in ("thread", "reply") or type(payload) is not dict:
        raise ValueError("invalid proposal")
    # Local digest only; not the server's payload_sha256.
    def check(v):
        if type(v) in (str, int, bool, type(None)):
            return
        if type(v) is list:
            for x in v: check(x)
        elif type(v) is dict and all(type(k) is str for k in v):
            for x in v.values(): check(x)
        else: raise ValueError("unsupported JSON type")
    check(payload)
    raw=json.dumps([1,identity,action,payload],sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()

class Ledger:
    def __init__(self, path):
        self.db=sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS attempts (digest TEXT PRIMARY KEY, state TEXT NOT NULL, receipt TEXT)")
    def reserve(self, digest):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if self.db.execute("SELECT 1 FROM attempts WHERE state='ambiguous'").fetchone():
                raise ValueError("unresolved attempt")
            self.db.execute("INSERT INTO attempts VALUES (?, 'ambiguous', NULL)", (digest,))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
    def confirm(self, digest, receipt):
        # Caller must independently verify receipt against the intended publication.
        if type(receipt) is not str or not receipt or len(receipt)>256:
            raise ValueError("invalid receipt")
        if self.db.execute("UPDATE attempts SET state='confirmed', receipt=? WHERE digest=? AND state='ambiguous'", (receipt,digest)).rowcount != 1:
            raise ValueError("no unresolved attempt")
    def close(self):
        self.db.close()
