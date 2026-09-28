import asyncio
import unittest

from dossier.providers import DEFAULT_PROVIDERS
from dossier.scanner import check_email_footprints, scan_username


class DossierTests(unittest.TestCase):
    def test_username_provider_formats(self):
        provider = DEFAULT_PROVIDERS[0]
        self.assertIn("alice", provider.pattern.format(username="alice"))

    def test_scan_username_returns_results(self):
        results = asyncio.run(scan_username(["alice"], timeout=1.0, concurrency=2))
        self.assertTrue(results)
        self.assertEqual(results[0].target, "alice")

    def test_email_scan_returns_results(self):
        results = asyncio.run(check_email_footprints("alice@example.com", timeout=1.0, concurrency=2))
        self.assertTrue(results)
        self.assertEqual(results[0].target, "alice%40example.com")


if __name__ == "__main__":
    unittest.main()
