import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/verify_import.py"
spec = importlib.util.spec_from_file_location("verify_import", SOURCE)
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)


class ImportProvenanceTests(unittest.TestCase):
    def make_snapshot(self, root, content=b"original\r\nbytes\x00"):
        (root / "example.bin").write_bytes(content)
        sha = hashlib.sha1(
            f"blob {len(content)}\0".encode("ascii") + content
        ).hexdigest()
        manifest = {"files": [
            {"path": "example.bin", "size": len(content), "sha": sha}
        ]}
        (root / "IMPORT_PROVENANCE.json").write_text(json.dumps(manifest))
        return manifest

    def test_raw_bytes_match(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            self.make_snapshot(root)
            self.assertEqual(verification.verify_snapshot(root), 1)

    def test_tampered_or_missing_file_fails(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            self.make_snapshot(root)
            (root / "example.bin").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "differs"):
                verification.verify_snapshot(root)
            (root / "example.bin").unlink()
            with self.assertRaisesRegex(ValueError, "Missing"):
                verification.verify_snapshot(root)

    def test_manifest_cannot_escape_snapshot(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            manifest = self.make_snapshot(root)
            manifest["files"][0]["path"] = "../example.bin"
            (root / "IMPORT_PROVENANCE.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                verification.verify_snapshot(root)


if __name__ == "__main__":
    unittest.main()
