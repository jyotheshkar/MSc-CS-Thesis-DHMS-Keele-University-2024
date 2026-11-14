"""Extract the native archive and run its no-GUI self-test from another cwd."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile

HERE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", nargs="?", type=Path)
    args = parser.parse_args()
    candidates = sorted((HERE / "release").glob("*.tar.gz" if sys.platform == "linux" else "*.zip"))
    archive = args.archive.resolve() if args.archive else candidates[-1] if candidates else None
    if archive is None or not archive.is_file():
        raise FileNotFoundError("No packaged archive found")
    with tempfile.TemporaryDirectory(prefix="dhms-packaged-") as temporary:
        home = Path(temporary)
        extracted = home / "extracted"
        extracted.mkdir()
        if sys.platform == "darwin":
            subprocess.run(["ditto", "-x", "-k", str(archive), str(extracted)], check=True)
            executable = extracted / "DHMS.app/Contents/MacOS/DHMS"
        elif sys.platform == "linux":
            with tarfile.open(archive) as handle:
                handle.extractall(extracted, filter="data")
            executable = extracted / "DHMS/DHMS"
        else:
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(extracted)
            executable = extracted / "DHMS/DHMS.exe"
        if not executable.is_file():
            raise FileNotFoundError(f"Executable missing from archive: {executable}")
        unrelated = home / "unrelated-cwd"
        unrelated.mkdir()
        # This should exercise bundled resources and core analysis, not require a display.
        subprocess.run([str(executable), "--self-test"], cwd=unrelated,
                       timeout=60, check=True, env=os.environ.copy())
        # Verify that the bundled Tcl/Tk resources can construct and draw the UI.
        # CI supplies xvfb on Linux; Windows/macOS runners provide a desktop.
        subprocess.run([str(executable), "--smoke-gui"], cwd=unrelated,
                       timeout=60, check=True, env=os.environ.copy())
    print(f"Packaged core and Tk smoke tests passed after extraction: {archive.name}")


if __name__ == "__main__":
    main()
