"""Package a native build with checksums and portable extraction instructions."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent
VERSION = "1.0.0"


def platform_name():
    machine = platform.machine().lower()
    architecture = "arm64" if machine in ("arm64", "aarch64") else "x64" if machine in ("x86_64", "amd64") else machine
    family = {"win32": "Windows", "darwin": "macOS", "linux": "Linux"}.get(sys.platform)
    if not family or architecture not in ("x64", "arm64"):
        raise RuntimeError(f"Unsupported release platform {sys.platform}/{machine}")
    return family + "-" + architecture


def main():
    family = platform_name()
    output = HERE / "release"
    output.mkdir(parents=True, exist_ok=True)
    bundle = HERE / "dist" / ("DHMS.app" if sys.platform == "darwin" else "DHMS")
    if not bundle.is_dir():
        raise FileNotFoundError(f"Build the application first: {bundle}")
    extension = ".tar.gz" if sys.platform == "linux" else ".zip"
    archive = output / f"DHMS-{VERSION}-{family}{extension}"
    if sys.platform == "darwin":
        # ditto retains the app bundle's symlinks and executable mode bits.
        subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(bundle), str(archive)], check=True)
    elif sys.platform == "linux":
        with tarfile.open(archive, "w:gz", dereference=False) as handle:
            handle.add(bundle, arcname="DHMS")
    else:
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
            for path in sorted(bundle.rglob("*")):
                if path.is_file():
                    handle.write(path, path.relative_to(bundle.parent))
    with archive.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    archive.with_name(archive.name + ".sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    manifest = {"version": VERSION, "platform": family, "python": platform.python_version(),
                "archive": archive.name, "sha256": digest, "bytes": archive.stat().st_size,
                "signing": "No trusted code-signing certificate or Apple notarisation claim.",
                "runtime": "Python and Tcl/Tk bundled; extract the complete folder/application before running."}
    (output / f"DHMS-{VERSION}-{family}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(archive)


if __name__ == "__main__":
    main()
