# Repository guidance

This repository preserves the 2024 Keele MSc dairy-herd monitoring research
application and a later synthetic browser demonstration.

- Read `docs/ENGINEERING.md` and `docs/ARCHITECTURE_MAINTENANCE.md` before changes.
- Keep assessed source, model artifacts, module marks and later maintenance
  clearly distinguishable. Do not invent predictive accuracy or clinical validity.
- Treat `original-work/Dairy-Herd-Monitoring/` as a preserved import. Its manifest
  records exact source bytes. Put new implementation outside that snapshot.
- Keep real herd datasets, credentials and session uploads out of version control.
- Make focused changes and report exact observed checks and remaining limitations.

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
