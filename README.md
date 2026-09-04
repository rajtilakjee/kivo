# Kivo

![GitHub release (with filter)](https://img.shields.io/github/v/release/rajtilakjee/kivo) &nbsp; ![GitHub License](https://img.shields.io/github/license/rajtilakjee/kivo) &nbsp; ![GitHub Repo stars](https://img.shields.io/github/stars/rajtilakjee/kivo) &nbsp; ![GitHub forks](https://img.shields.io/github/forks/rajtilakjee/kivo) &nbsp; ![GitHub repo size](https://img.shields.io/github/repo-size/rajtilakjee/kivo)

A lightweight desktop teleprompter built with **PySide6**.

Kivo provides a clean, always-on-top reading overlay for scripts, AI-generated content, presentations, and video recordings.

> **Status:** 🚧 MVP (v0.2.0)

---

https://github.com/user-attachments/assets/eaa42e1f-77f2-406f-9cee-83f556f3c61d

## Features

* Frameless, always-on-top glass overlay
* Header with script name, live/paused state, and speed
* Draggable and resizable window
* Open `.txt` or `.md` files, with `Ctrl+O` to switch scripts
* Reloads automatically when the file changes
* Smooth teleprompter-style auto-scrolling
* Click or drag the progress bar to jump
* Adjustable scroll speed, font size, and opacity
* Remembers window size, speed, font, and opacity
* Hidden from screen sharing in Meet, Zoom, Teams, and similar apps
* Lightweight and distraction-free

---

## Keyboard Shortcuts

| Shortcut | Action                   |
| -------- | ------------------------ |
| `?` / `H` / `F1` | Show or hide controls |
| `Esc`    | Close help, or close Kivo |
| `Space`  | Pause / Resume scrolling |
| `↑` / `↓` | Increase / decrease speed |
| `←` / `→` | Skip backward / forward |
| `+` / `-` | Increase / decrease font size |
| `[` / `]` | Decrease / increase opacity |
| `R`      | Restart from the top     |
| `Ctrl+O` | Open another script      |
| `Ctrl+Scroll` | Change font size    |
| `Scroll` | Nudge the script         |

---

## Installation

Install [uv](https://docs.astral.sh/uv/), then clone the repository:

```bash
git clone https://github.com/rajtilakjee/kivo.git
cd kivo
```

Sync the environment and run the application:

```bash
uv sync
uv run python main.py
```

---

## Building

Create a standalone executable using PyInstaller:

```bash
uv sync --group dev
uv run pyinstaller --onefile --windowed --name Kivo main.py
```

The executable will be generated inside the `dist/` directory.

---

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run python main.py
```

---

## Star History

<a href="https://www.star-history.com/?repos=rajtilakjee%2Fkivo&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=rajtilakjee/kivo&type=date&legend=top-left" />
 </picture>
</a>

---

## Roadmap

* Settings window
* Global hotkeys
* Reopen the last script on launch
* Font family picker
* Scroll speed presets
* Mirror mode
* Multiple themes
* Custom teleprompter rendering
* Cross-platform releases

---

## Tech Stack

* Python 3.10+
* PySide6 (Qt for Python)
* uv for environments and dependencies

---

## License

This project is licensed under the MIT License.
