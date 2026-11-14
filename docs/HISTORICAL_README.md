# Dairy time-series desktop architecture

## Architecture and maintenance

[Technical architecture, source boundaries, scalability decisions and verification](docs/ARCHITECTURE_MAINTENANCE.md) documents the current implementation and its limits. Maintenance dated 11 November 2026 is separate from the original study or project work.

### Persistence checks

```bash
python -m unittest discover -s tests -v
```

The repository is historical desktop source. Missing image assets and platform-specific file viewers currently limit full startup; consult the architecture document before reproducing the GUI or model-training paths.


Academic-style desktop source for dairy-herd activity and temperature modelling. The repository contains legacy experiments and model files; the maintenance work is dated 11 November 2026 and does not rewrite the original research history.
