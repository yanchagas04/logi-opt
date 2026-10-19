# logi-opt

A modern, lightweight Linux desktop application built with **Python** and **Qt (PySide6)** to configure and customize Logitech gaming mice, with a primary focus on the **Logitech G PRO** lineup.

---

## Motivation & Goals

While Logitech provides official software (Logitech G HUB) for Windows and macOS, Linux users often lack a clean, native, and dedicated GUI to manage their mouse settings without relying on heavy workarounds or limited CLI utilities.

**logi-opt** aims to bridge this gap by delivering:
- A clean, modern Linux GUI interface built with **Qt** (Qt Quick / QML & PySide6).
- Low-level device communication via USB/HID raw protocols (e.g., Logitech HID++ 1.0 / 2.0+).
- Fast and native performance without web runtime bloat (like Electron).
- First-class support for the **Logitech G PRO** family and expandable support for other Logitech devices.

---

## Features (Planned & In Progress)

- [ ] **DPI Management**: Configure DPI steps, active DPI, shift DPI, and custom DPI levels.
- [ ] **Polling Rate Adjustment**: Switch between 125Hz, 250Hz, 500Hz, and 1000Hz (or higher for compatible sensors).
- [ ] **Battery & Power Monitoring**: Real-time battery percentage monitoring and power-saving sleep timeouts.
- [ ] **Onboard Profiles**: Read and write profiles directly to onboard mouse memory.
- [ ] **RGB / LIGHTSYNC (if supported)**: Control lighting effects, colors, and brightness.
- [ ] **Modern Qt/QML Interface**: Sleek, responsive, and adaptive UI styled for Linux desktop environments.

---

## Tech Stack

- **Language:** Python 3.12+
- **GUI Toolkit:** [PySide6](https://wiki.qt.io/Qt_for_Python) (Qt Quick / QML & QtWidgets)
- **Package & Environment Manager:** [uv](https://github.com/astral-sh/uv)
- **Protocol:** Linux HID / HID++ (Logitech HID++ protocol)

---

## Getting Started

### Prerequisites

Ensure you have:
- Linux OS with `udev` support.
- Python `>= 3.12` installed.
- [`uv`](https://docs.astral.sh/uv/) installed (recommended fast package installer and resolver).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yanchagas04/logi-opt.git
   cd logi-opt
   ```

2. **Set up the virtual environment and install dependencies:**
   ```bash
   uv sync
   ```

### Running the Project

Run the application:
```bash
uv run logi-opt
```

To run exploratory Qt test scripts:
```bash
# Qt Quick / QML demo
uv run python qt-tests/qt_quick_example.py

# QtWidgets demo
uv run python qt-tests/qt_widget_example.py
```
## 🤝 Contributing

Contributions, bug reports, and device test reports are welcome! If you own a Logitech mouse (especially Logitech G PRO variants) and want to test or contribute, feel free to open an issue or pull request.