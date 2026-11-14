# Download and run DHMS Desktop

DHMS Desktop is a local desktop application for exploring dairy-herd activity and temperature time series. The supported application is under `desktop/`. The historical `Codes/main.py` is research source and is not the supported launcher.

## Portable application

Open [the latest desktop release](https://github.com/jyotheshkar/MSc-CS-Thesis-DHMS-Keele-University-2024/releases/latest). Choose the archive that matches your operating system and processor; GitHub's automatic **Source code** archive is the developer option, not the ready-to-run application.

| Platform | Version 1.0.0 download | Run after extraction |
|---|---|---|
| Windows x64 | `DHMS-1.0.0-Windows-x64.zip` | Open the extracted `DHMS` folder and run `DHMS.exe` |
| macOS Apple Silicon | `DHMS-1.0.0-macOS-arm64.zip` | Open the extracted `DHMS.app` |
| macOS Intel | `DHMS-1.0.0-macOS-x64.zip` | Open the extracted `DHMS.app` |
| Linux x64 | `DHMS-1.0.0-Linux-x64.tar.gz` | Extract, open `DHMS`, run `./DHMS` |

Keep the entire extracted folder together. On Windows, `_internal` contains required runtime files; moving only the `.exe` breaks the application. Extract to a writable folder you own. The bundles include Python, Tk and the synthetic sample; no TensorFlow installation, account, API key or administrator installation is required.

The native build runners are Windows Server 2022 x64, Ubuntu 22.04 x64, macOS 15 arm64 and macOS 15 Intel. These are the verified build/test environments, not a guarantee for every OS version or laptop. Other architectures and older operating systems are unverified. Linux may need its distribution's normal X11/Tk system libraries and a graphical session.

The packages are **unsigned**, and macOS builds are not notarised. If your operating system blocks an application, do not disable its security protections. Use the source option below or obtain a signed release when available. No claim of signing or universal laptop compatibility is made.

## Check the download

Each release archive has a matching `.sha256` text file. Compare its expected hash with the downloaded file:

```powershell
# Windows PowerShell
Get-FileHash .\DHMS-1.0.0-Windows-x64.zip -Algorithm SHA256
```

```bash
# macOS
shasum -a 256 DHMS-1.0.0-macOS-arm64.zip
# Linux
sha256sum DHMS-1.0.0-Linux-x64.tar.gz
```

A checksum detects a changed/corrupted download; it does not replace a trusted source or code signing. Download from this repository's release page.

## First use

1. Start **DHMS Desktop** and select **Load sample**. The bundled data is synthetic.
2. Choose a cow and either activity or temperature. Inspect the chart and summary.
3. Adjust the trailing-window size and run the baseline backtest. MAE describes one-step historical predictions, not clinical accuracy.
4. Select **Open CSV** to import your own data. See [the CSV contract](DESKTOP_DATA.md).
5. Use **Export analysis** to save results to a destination you choose. Your input file is never overwritten or deleted.

No data is transmitted to a server. Preferences are stored in your operating system's user application-data directory. Source files remain where you selected them. The application does not diagnose animals or recommend treatment.

## Run from source

Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/) with Tk support. On Windows and the standard python.org macOS installer, Tk is normally included; on Linux, install the distribution's `python3-tk` package if needed.

Download **Source code** from the release, extract it, then run from the repository directory:

```bash
python desktop/launch.py
```

On Windows, `py desktop/launch.py` is also suitable if the Python Launcher is installed. On systems where Python is named `python3`, use `python3 desktop/launch.py`.

The supported desktop edition uses the Python standard library. Do **not** install the large historical `Codes/requirements.txt` to run it. That environment belongs to the earlier neural-network research application.

## Troubleshooting

| Symptom | Action |
|---|---|
| App closes immediately | Re-extract the full archive; check platform/processor match; try the source command from a terminal to see the error |
| `No module named tkinter` | Install Python/Tk using the official installer or OS package manager |
| CSV rejected | Read the row-specific error; check column names, timestamps, duplicate cow/timestamp pairs and finite values |
| Not enough history | Choose a smaller window or provide more observations for that cow/metric |
| Import cancelled or failed | The previous dataset remains selected; correct the file and retry |
| Export fails | Choose a writable destination and close any spreadsheet holding the output file open |
| OS blocks unsigned app | Keep the protection enabled and use the source option |

For a bug report, include OS/architecture, app version, exact error and a small **synthetic** CSV reproducer. Do not attach private herd records or personal identifiers. See [architecture and limits](DESKTOP_ARCHITECTURE.md).
