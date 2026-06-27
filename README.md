# Kivo

A lightweight desktop teleprompter built with **PySide6**.

Kivo provides a clean, always-on-top reading overlay for scripts, AI-generated content, presentations, and video recordings.

> **Status:** 🚧 MVP (v0.1.0)

---

## Features

* Frameless, always-on-top overlay
* Modern rounded UI with a translucent background
* Draggable window
* Open any text (`.txt`) file
* Automatically reloads when the file changes
* Smooth teleprompter-style auto-scrolling
* Adjustable scrolling speed
* Pause and resume scrolling
* Lightweight and distraction-free

---

## Keyboard Shortcuts

| Shortcut | Action                   |
| -------- | ------------------------ |
| `Esc`    | Close Kivo               |
| `Space`  | Pause / Resume scrolling |
| `↑`      | Increase scrolling speed |
| `↓`      | Decrease scrolling speed |

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/kivo.git
cd kivo
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## Building

Create a standalone executable using PyInstaller:

```bash
pyinstaller --onefile --windowed --name Kivo main.py
```

The executable will be generated inside the `dist/` directory.

---

## Project Structure

```text
kivo/
├── main.py
├── ui/
│   ├── __init__.py
│   ├── mainwindow.py
│   └── selector.py
├── assets/
└── README.md
```

---

## Roadmap

* Settings window
* Global hotkeys
* Remember last opened file
* Font customization
* Adjustable opacity
* Scroll speed presets
* Mirror mode
* Multiple themes
* Custom teleprompter rendering
* Cross-platform releases

---

## Tech Stack

* Python 3
* PySide6 (Qt for Python)

---

## License

This project is licensed under the MIT License.
