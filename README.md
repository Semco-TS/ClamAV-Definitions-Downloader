# ClamAV Definition Downloader

A lightweight Windows utility for downloading the latest official ClamAV virus definition databases from Cisco Talos and packaging them into a ZIP archive for transfer to air-gapped systems.

## Features

- Downloads the latest:
  - `main.cvd`
  - `daily.cvd`
  - `bytecode.cvd`
- Simple graphical interface
- Select output directory at runtime
- Remembers the last selected destination folder
- Creates a timestamped ZIP archive
- Automatically cleans up temporary files after completion

## Requirements

- Windows
- Python 3.10+
- Internet access for downloading ClamAV definitions

Install dependencies:

```bash
pip install -r requirements.txt
```

## Build

Create a standalone executable using PyInstaller:

```bash
pyinstaller .\clamav_gui_downloader.py --onefile
```

The executable will be generated in:

```text
dist\clamav_gui_downloader.exe
```

## Usage

1. Launch the executable.
2. Select a destination folder.
3. Click **Start Download**.
4. Wait for the download and ZIP creation to complete.
5. Copy the generated ZIP file to the target air-gapped system.

Generated archives are named:

```text
clamav_definitions_YYYYMMDD_HHMMSS.zip
```

## Dependencies

Runtime:

```text
cvdupdate >= 1.1.0
```

Build:

```text
pyinstaller >= 6.0.0
```

## Disclaimer

This utility downloads official ClamAV database files using the `cvdupdate` package and is intended to simplify the process of transferring updates to isolated or air-gapped environments.