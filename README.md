# Kivo

![GitHub release (with filter)](https://img.shields.io/github/v/release/rajtilakjee/kivo) &nbsp; ![GitHub License](https://img.shields.io/github/license/rajtilakjee/kivo) &nbsp; ![GitHub Repo stars](https://img.shields.io/github/stars/rajtilakjee/kivo) &nbsp; ![GitHub forks](https://img.shields.io/github/forks/rajtilakjee/kivo) &nbsp; ![GitHub repo size](https://img.shields.io/github/repo-size/rajtilakjee/kivo)

A lightweight desktop teleprompter built with **PySide6**.

Kivo provides a clean, always-on-top reading overlay for scripts, AI-generated content, presentations, and video recordings.

> **Status:** 🚧 MVP (v0.1.0)

---

https://github.com/user-attachments/assets/eaa42e1f-77f2-406f-9cee-83f556f3c61d

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
git clone https://github.com/rajtilakjee/kivo.git
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

## Star History

<a href="https://www.star-history.com/?repos=rajtilakjee%2Fkivo&type=timeline&logscale=&legend=bottom-right">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=timeline&theme=dark&logscale&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=timeline&logscale&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=timeline&logscale&legend=top-left" />
 </picture>
</a>

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
