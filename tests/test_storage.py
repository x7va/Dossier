import tempfile
import unittest
from pathlib import Path

from dossier.storage import CaseStore


class CaseStoreTests(unittest.TestCase):
    def test_round_trip_investigation_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CaseStore(Path(directory) / "case.sqlite3")
            investigation = {
                "id": "case-1",
                "started": "2026-01-01T00:00:00+00:00",
                "completed": "2026-01-01T00:00:01+00:00",
                "target": "alice",
                "target_type": "username",
                "profile": "standard",
                "duration": "1s",
                "providers": 1,
                "matches": 1,
                "modules": 1,
                "entities": 1,
                "relationships": 0,
                "findings": 1,
                "manifest": "abc123",
                "analysis": None,
                "categories": {"Social Media": [1, 1]},
                "results": [
                    {
                        "provider": "github",
                        "target": "alice",
                        "url": "https://github.com/alice",
                        "status": "exists",
                        "http_status": 200,
                        "title": "Alice",
                        "note": None,
                        "payload": {"description": "GitHub profile"},
                    }
                ],
            }

            store.save_investigation(investigation)
            loaded = store.get_investigation("case-1")

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["target"], "alice")
            self.assertEqual(loaded["results"][0]["provider"], "github")
            self.assertEqual(store.list_investigations()[0]["id"], "case-1")


if __name__ == "__main__":
    unittest.main()
