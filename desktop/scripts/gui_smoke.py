"""Bounded real-Tk construction/drawing smoke check; not manual UX validation."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dhms.app import smoke_test


def main():
    smoke_test()


if __name__ == "__main__":
    main()
