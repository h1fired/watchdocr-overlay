# OCR Overlay

A real-time Optical Character Recognition (OCR) overlay and screen translation tool built with Python and PySide6. The application captures a designated screen region, processes text extraction through pluggable OCR backends, translates the content, and renders it as an on-screen overlay in real time.

This application was created as a pet project, inspired by the frequent frustration in games (and other applications) where text cannot be selected, copied, or translated on the fly.

---

## Key Features

- **Overlay**: Seamless HUD overlays rendering translated text directly over windows (supports windowed or borderless modes; exclusive fullscreen is not supported).
- **Windows Media OCR**: Pluggable backend utilizing an unofficial Windows OCR wrapper/backend for native, fast, and lightweight text extraction on Windows.
- **Dynamic Translation**: Real-time translation utilizing an unofficial Google Translation endpoint.
- **Flexible Workflows**:
  - **One-time Mode**: Capture and translate on-demand.
  - **Live Mode**: Continuously capture and translate a screen region at user-defined polling frequencies.

---

## Installation & Setup

### Requirements
- **Python**: 3.11.9
- **Qt**: 6.9.3 installed on the system
- **Dependency Manager**: [uv](https://github.com/astral-sh/uv)

### 1. Install Dependencies
Run the following command to configure the virtual environment and install package dependencies:
```bash
uv sync
```

### 2. Compile Resource Files (Automatically handled on launch)
The application compiles `.qrc` resource bundles automatically in `DEBUG` mode on startup:
```bash
uv run .\main.py
```

---

## Feedback & Contributing

If you encounter any bugs, have feature suggestions, or want to contribute, feel free to open an issue or submit a pull request. Any feedback is welcome and highly appreciated!