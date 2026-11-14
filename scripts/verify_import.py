"""Verify the preserved Dairy Herd files against their Git blob identities."""
import hashlib
import json
from pathlib import Path, PurePosixPath

SNAPSHOT = "original-work/Dairy-Herd-Monitoring"


def verify_snapshot(snapshot_dir):
    """Return the number of verified files; raise ValueError on a mismatch."""
    snapshot_dir = Path(snapshot_dir).resolve()
    manifest = json.loads(
        (snapshot_dir / "IMPORT_PROVENANCE.json").read_text(encoding="utf-8")
    )
    files = manifest["files"]
    if not files:
        raise ValueError("The provenance manifest must contain files")
    seen = set()
    for entry in files:
        relative = PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in entry["path"]:
            raise ValueError(f"Unsafe import path: {entry['path']}")
        if entry["path"] in seen:
            raise ValueError(f"Duplicate import path: {entry['path']}")
        seen.add(entry["path"])
        path = snapshot_dir.joinpath(*relative.parts).resolve()
        if not path.is_relative_to(snapshot_dir):
            raise ValueError(f"Import path escapes snapshot: {entry['path']}")
        if not path.is_file():
            raise ValueError(f"Missing imported file: {entry['path']}")
        content = path.read_bytes()
        # Git hashes the object header plus raw bytes, not the bytes alone.
        header = f"blob {len(content)}\0".encode("ascii")
        actual = hashlib.sha1(header + content).hexdigest()
        if len(content) != entry["size"] or actual != entry["sha"]:
            raise ValueError(f"Imported file differs: {entry['path']}")
    return len(files)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    count = verify_snapshot(root / SNAPSHOT)
    print(f"Verified {count} preserved Dairy Herd files by size and Git blob SHA.")
