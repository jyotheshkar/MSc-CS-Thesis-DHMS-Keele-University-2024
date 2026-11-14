# Repository guidance

This repository preserves the 2024 Keele MSc dairy-herd monitoring research
application, a later synthetic browser demonstration and the supported DHMS Desktop edition.

- Read `docs/ENGINEERING.md` and `docs/ARCHITECTURE_MAINTENANCE.md` before changes.
- Keep assessed source, model artifacts, module marks and later maintenance
  clearly distinguishable. Do not invent predictive accuracy or clinical validity.
- Treat `original-work/Dairy-Herd-Monitoring/` as a preserved import. Its manifest
  records exact source bytes. Put new implementation outside that snapshot.
- Keep real herd datasets, credentials and session uploads out of version control.
- Make focused changes and report exact observed checks and remaining limitations.

## Supported desktop edition

- Read `docs/DESKTOP_ARCHITECTURE.md` and `docs/DESKTOP_DATA.md` before desktop changes.
- New code belongs in `desktop/`; do not modify the preserved original-work snapshot.
- Never interpret baseline MAE as health/clinical accuracy or silently reactivate legacy models.
- Keep source CSVs read-only and runtime state in a user workspace.
- Keep the UI responsive: worker results cross a queue; Tk updates stay on its main thread.
- Before release run desktop tests, source self-test, GUI smoke and native package smoke.
- Download filenames and version must match package metadata and release tag.

## Verification

Run from the repository root with Python 3.11+ and Node 22:

```sh
python scripts/verify_import.py
python -m unittest discover -s tests -v
node web/verify.cjs
```

Run imported sequence regressions separately from their own working directory:

```sh
cd original-work/Dairy-Herd-Monitoring
python -m pip install -r requirements-sequences.txt
python -m unittest discover -s tests -v
```

These checks do not start the historical Tkinter GUI, train TensorFlow models
or establish a veterinary deployment. Full GUI execution requires missing assets
and a separately reproduced historical environment.

