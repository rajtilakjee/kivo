"""Hide the overlay from screen capture (Meet, Zoom, Teams, and similar)."""

from __future__ import annotations

import sys

WDA_EXCLUDEFROMCAPTURE = 0x11


def exclude_from_capture(hwnd: int) -> bool:
    """Exclude a native window from display capture APIs.

    Uses SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE), which Windows
    Graphics Capture and Chromium (Google Meet, Chrome tab/screen share)
    honor on Windows 10 2004 and later.
    """
    if sys.platform != "win32" or not hwnd:
        return False

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
    user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumChildWindows.argtypes = [wintypes.HWND, enum_proc, wintypes.LPARAM]
    user32.EnumChildWindows.restype = wintypes.BOOL

    ok = bool(user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE))

    def _each_child(child: int, _lparam: int) -> bool:
        user32.SetWindowDisplayAffinity(child, WDA_EXCLUDEFROMCAPTURE)
        return True

    callback = enum_proc(_each_child)
    user32.EnumChildWindows(hwnd, callback, 0)
    return ok
