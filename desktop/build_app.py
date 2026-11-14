"""Build the desktop app natively with the pinned PyInstaller toolchain."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
APP_NAME = "DHMS"
VERSION = "1.0.0"


def main():
    # Always target folders under desktop/, regardless of the caller's cwd.
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onedir", "--windowed", "--noupx", "--name", APP_NAME,
               "--paths", str(HERE), "--add-data", f"{HERE / 'samples'}:samples",
               "--distpath", str(HERE / "dist"),
               "--workpath", str(HERE / "build"),
               "--specpath", str(HERE / "build")]
    if sys.platform == "darwin":
        command += ["--osx-bundle-identifier", "com.jyotheshkarnam.dhms"]
    command.append(str(HERE / "launch.py"))
    subprocess.run(command, cwd=HERE, check=True)
    print(f"Built {APP_NAME} {VERSION} for {sys.platform}. Native build, no cross-compilation.")


if __name__ == "__main__":
    main()
