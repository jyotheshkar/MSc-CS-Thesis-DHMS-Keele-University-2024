# MSc Computer Science Thesis · DHMS Desktop

**Dairy Herd Monitoring System · Jyothesh Karnam · Keele University**

[![Desktop builds](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/actions/workflows/desktop.yml/badge.svg)](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/actions/workflows/desktop.yml)
[![Historical source checks](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/actions/workflows/maintenance.yml/badge.svg)](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/actions/workflows/maintenance.yml)

A **desktop application** for importing dairy-herd time-series data, exploring activity and temperature, comparing a chronological baseline, and exporting results. Data stays on your laptop.

**[Download DHMS Desktop](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/releases/latest)** · [Installation and first use](docs/DESKTOP_DOWNLOADS.md) · [CSV format](docs/DESKTOP_DATA.md) · [System design](docs/DESKTOP_ARCHITECTURE.md)

## What you can do

- Open a validated CSV or start with bundled synthetic data.
- Choose a cow and metric, inspect its time-series chart and descriptive statistics.
- Evaluate a labelled trailing-mean baseline on later observations and inspect its MAE.
- Export analysis explicitly, without modifying or deleting the input file.
- Cancel work and recover from bad inputs with useful error messages.

The supported entry point is `desktop/launch.py`. It runs without TensorFlow, missing GIF assets, personal Desktop paths or a fixed herd size. Background import/analysis keeps Tk updates on the UI thread. [Implementation decisions and limits](docs/DESKTOP_ARCHITECTURE.md) describe the separation of data, analysis, storage and view layers.

**Research data exploration only.** This edition does not diagnose animals, validate treatment decisions or claim neural-model accuracy. The historical neural-network application and model files remain available as academic source; their complete portable inference contract has not been established.

## Download for your laptop

Open [Releases](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/releases/latest), then select the package matching your OS and processor:

| Platform | Package | Start |
|---|---|---|
| Windows x64 | `DHMS-1.0.0-Windows-x64.zip` | Extract everything, then open `DHMS/DHMS.exe` |
| macOS Apple Silicon | `DHMS-1.0.0-macOS-arm64.zip` | Extract and open `DHMS.app` |
| macOS Intel | `DHMS-1.0.0-macOS-x64.zip` | Extract and open `DHMS.app` |
| Linux x64 | `DHMS-1.0.0-Linux-x64.tar.gz` | Extract and run `DHMS/DHMS` |

A SHA256 checksum accompanies each package. Keep the full extracted folder together. Packages are unsigned; use the [source option](docs/DESKTOP_DOWNLOADS.md#run-from-source) if your OS blocks them. See [build environments, compatibility and troubleshooting](docs/DESKTOP_DOWNLOADS.md).

To run from source with Python 3.11+ and Tk:

```bash
python desktop/launch.py
```

Use **Load sample** first. The included observations are synthetic. You do not need the historical `Codes/requirements.txt` environment for this edition.

## Academic foundation

| Academic record | Verified value |
|---|---|
| Programme | MSc Computer Science, Keele University |
| Academic year | 2023/24 |
| Project year | 2024 |
| Final module mark | **77%** |
| Credit | 60 CATS |
| Original project | Time-series Neural Network Software Suite and App Development for Dairy Herd Monitoring |
| Original delivery | Tkinter research application |

The mark was verified against the final academic transcript, page 2, issued 15 January 2025. It applies to the original module assessment. Portfolio maintenance and the web edition dated **14 November 2026** were completed later with AI assistance and were not assessed by Keele.

The repository year **2024** records the original dissertation, submitted **13 September 2024** during academic year **2023/24**. See the [original dissertation abstract and provenance](docs/original/student-dissertation-abstract.md). Later portfolio maintenance retains its own 2026 date.

The **2026 desktop edition**, tests, packaging and documentation are later AI-assisted portfolio work. They are separate from the assessed thesis and do not inherit its mark.

### Original source and documentation

- [Original dissertation abstract and provenance](docs/original/student-dissertation-abstract.md)
- [Student dissertation PDF](Project%20Documentation.pdf)
- [Historical research source](Codes/) — preserved experiments, GUI and model artifacts; not the supported launcher
- [Academic document provenance](docs/original/README.md)
- [Preserved supporting Dairy Herd import](original-work/Dairy-Herd-Monitoring/) and [final consolidation receipt](docs/consolidation/dairy-herd-final-receipt.json)
- [Earlier engineering review](docs/ENGINEERING.md) and [2026 source maintenance](docs/ARCHITECTURE_MAINTENANCE.md)
- [Separate synthetic browser study](web/README.md) — distinct from the desktop application

Skills developed through the original research include Python, time-series modelling, neural networks, desktop GUI design, evaluation and research methods. Later engineering adds explicit CSV contracts, cancellable workers, failure recovery, atomic user storage, bounded workloads, automated tests and native package builds.

## Verification

```bash
cd desktop
python -m unittest discover -s tests -v
cd ..
python desktop/launch.py --self-test
python desktop/scripts/gui_smoke.py
```

GUI smoke needs a graphical session; Linux CI uses Xvfb. [The desktop workflow](.github/workflows/desktop.yml) runs tests and native packaging on each platform, then publishes versioned downloads only after all builds pass.

Historical checks are retained separately: `python scripts/verify_import.py`, root persistence/provenance tests, imported sequence regressions and `node web/verify.cjs`. No passing test establishes veterinary validity or a complete neural-model deployment.

This is an independent portfolio project. University documents and third-party material retain their own notices; Keele branding does not imply endorsement.

