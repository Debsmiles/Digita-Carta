"""Offline regression tests; temporary databases only."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from ledger import Ledger, proposal_digest

class LedgerTests(unittest.TestCase):
    def test_digest(self):
        identity = "a" * 64
        a = proposal_digest(identity, "reply", {"body":"test","thread":1})
        self.assertEqual(a, proposal_digest(identity,"reply",{"thread":1,"body":"test"}))
        self.assertNotEqual(a, proposal_digest(identity,"reply",{"thread":1,"body":"changed"}))
        self.assertNotEqual(a, proposal_digest(identity,"thread",{"thread":1,"body":"test"}))
        with self.assertRaises(ValueError):
            proposal_digest(identity,"reply",{"thread":1.0})
    def test_persistence_and_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            a, b = "a"*64, "b"*64
            ledger = Ledger(path)
            ledger.reserve(a)
            ledger.close()
            ledger = Ledger(path)
            try:
                with self.assertRaises(ValueError):
                    ledger.reserve(b)
                ledger.confirm(a,"synthetic-receipt")
                with self.assertRaises(sqlite3.IntegrityError):
                    ledger.reserve(a)
                ledger.reserve(b)
                with self.assertRaises(ValueError):
                    ledger.confirm(a,"other-receipt")
                with self.assertRaises(ValueError):
                    ledger.confirm(b,"")
                ledger.confirm(b,"synthetic-second-receipt")
            finally:
                ledger.close()

if __name__ == "__main__":
    unittest.main()
