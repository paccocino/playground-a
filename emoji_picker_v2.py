#!/usr/bin/env python3
"""
Emoji-Picker v2
===============
Kompaktes Kontextmenü mit favorisierten Emojis, das sich in der Naehe des
blinkenden Text-Cursors oeffnet. Auswahl per Klick oder Taste [1]-[0],
danach wird das Emoji per Zwischenablage in das zuletzt fokussierte
Textfeld eingefuegt und das Script beendet sich.

Voraussetzungen: Windows, Python 3 mit Tkinter (Standard bei python.org-
Installern). Keine zusaetzlichen pip-Pakete noetig, es wird ausschliesslich
ctypes fuer die Win32-API-Aufrufe verwendet.

Start ueber Tastenkombination (z.B. AHK v1 + Plugin "UserHotkeys"):
    Run, pythonw.exe "C:\pfad\zu\emoji_picker_v2.py"
"pythonw.exe" statt "python.exe" verwenden, damit kein Konsolenfenster
aufblitzt.
"""

import ctypes
from ctypes import wintypes
import sys
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# --- Favoriten-Emojis: Taste, Zeichen, Beschriftung -------------------------
EMOJIS = [
    ("1", "\u2b1c", "Offen"),       # ⬜
    ("2", "\u2705", "Erledigt"),    # ✅
    ("3", "\u274e", "In Arbeit"),   # ❎
    ("4", "\u274c", "Fehler"),      # ❌
    ("5", "\u26a0\ufe0f", "Warnung"),  # ⚠️
    ("6", "\u2b50", "Wichtig"),     # ⭐
    ("7", "\u2139\ufe0f", "Info"),  # ℹ️
    ("8", "\U0001f7e2", "Gruen"),   # 🟢
    ("9", "\U0001f7e1", "Gelb"),    # 🟡
    ("0", "\U0001f534", "Rot"),     # 🔴
]

CARET_OFFSET_X = -30
CARET_OFFSET_Y = -30

# --- Win32-API-Signaturen ----------------------------------------------------
# Explizite argtypes/restype sind auf 64-Bit-Windows noetig, da Handles/
# Pointer sonst auf 32 Bit abgeschnitten werden.

GUI_CARETBLINKING = 0x00000001


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]


user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetForegroundWindow.argtypes = []

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]

user32.GetGUIThreadInfo.restype = wintypes.BOOL
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]

user32.ClientToScreen.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]

user32.SetForegroundWindow.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]

user32.keybd_event.restype = None
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ctypes.c_void_p]

user32.OpenClipboard.restype = wintypes.BOOL
user32.OpenClipboard.argtypes = [wintypes.HWND]

user32.CloseClipboard.restype = wintypes.BOOL
user32.CloseClipboard.argtypes = []

user32.EmptyClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []

user32.GetClipboardData.restype = wintypes.HANDLE
user32.GetClipboardData.argtypes = [wintypes.UINT]

user32.SetClipboardData.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

kernel32.GlobalAlloc.restype = wintypes.HANDLE
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]

kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalLock.argtypes = [wintypes.HANDLE]

kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002


def get_caret_screen_pos():
    """Liefert (x, y) der linken oberen Ecke des blinkenden Carets in
    Bildschirmkoordinaten, oder None wenn das fokussierte Fenster gerade
    keinen aktiven Text-Caret hat (= kein Textfeld/Editor)."""
    hwnd_fg = user32.GetForegroundWindow()
    if not hwnd_fg:
        return None

    tid = user32.GetWindowThreadProcessId(hwnd_fg, None)
    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(tid, ctypes.byref(info)):
        return None
    if not (info.flags & GUI_CARETBLINKING) or not info.hwndCaret:
        return None

    pt = wintypes.POINT(info.rcCaret.left, info.rcCaret.top)
    user32.ClientToScreen(info.hwndCaret, ctypes.byref(pt))
    return pt.x, pt.y


def get_clipboard_text():
    text = None
    if not user32.OpenClipboard(0):
        return None
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if handle:
            ptr = kernel32.GlobalLock(handle)
            if ptr:
                text = ctypes.wstring_at(ptr)
                kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()
    return text


def set_clipboard_text(text):
    data = (text + "\0").encode("utf-16-le")
    if not user32.OpenClipboard(0):
        return
    try:
        user32.EmptyClipboard()
        hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not hglobal:
            return
        ptr = kernel32.GlobalLock(hglobal)
        ctypes.memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(hglobal)
        user32.SetClipboardData(CF_UNICODETEXT, hglobal)
    finally:
        user32.CloseClipboard()


def send_ctrl_v():
    user32.keybd_event(VK_CONTROL, 0, 0, None)
    user32.keybd_event(VK_V, 0, 0, None)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, None)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, None)


def insert_emoji(target_hwnd, emoji):
    """Fuegt das Emoji per Zwischenablage in das urspruenglich fokussierte
    Fenster ein (robuster als simulierte Unicode-Tastenanschlaege) und
    stellt danach den vorherigen Zwischenablage-Inhalt wieder her."""
    saved = get_clipboard_text()
    set_clipboard_text(emoji)
    user32.SetForegroundWindow(target_hwnd)
    time.sleep(0.05)
    send_ctrl_v()
    time.sleep(0.15)
    if saved is not None:
        set_clipboard_text(saved)


def show_picker(pos):
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg="#1e1e1e", highlightthickness=1, highlightbackground="#555555")

    selected = {"emoji": None}

    def choose(emoji):
        selected["emoji"] = emoji
        root.destroy()

    def cancel(event=None):
        root.destroy()

    frame = tk.Frame(root, bg="#1e1e1e", padx=3, pady=3)
    frame.pack()

    key_to_emoji = {}
    for key, emoji, label in EMOJIS:
        key_to_emoji[key] = emoji

        row = tk.Frame(frame, bg="#1e1e1e")
        row.pack(fill="x")

        key_lbl = tk.Label(row, text=key, width=2, fg="#888888", bg="#1e1e1e",
                            font=("Segoe UI", 9, "bold"), anchor="e")
        emo_lbl = tk.Label(row, text=emoji, width=2, bg="#1e1e1e",
                            font=("Segoe UI Emoji", 12))
        txt_lbl = tk.Label(row, text=label, fg="#e0e0e0", bg="#1e1e1e",
                            font=("Segoe UI", 9), anchor="w")

        key_lbl.pack(side="left", padx=(2, 4))
        emo_lbl.pack(side="left", padx=(0, 6))
        txt_lbl.pack(side="left", fill="x", expand=True, padx=(0, 6))

        widgets = (row, key_lbl, emo_lbl, txt_lbl)

        def on_enter(event, ws=widgets):
            for w in ws:
                w.configure(bg="#3a6ea5")

        def on_leave(event, ws=widgets):
            for w in ws:
                w.configure(bg="#1e1e1e")

        def on_click(event, em=emoji):
            choose(em)

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    def on_key(event):
        if event.keysym == "Escape":
            cancel()
        elif event.char in key_to_emoji:
            choose(key_to_emoji[event.char])

    root.bind("<Key>", on_key)
    root.bind("<FocusOut>", cancel)

    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = max(0, min(pos[0], screen_w - w))
    y = max(0, min(pos[1], screen_h - h))
    root.geometry(f"+{x}+{y}")

    root.deiconify()
    root.lift()
    root.focus_force()
    root.grab_set()

    root.mainloop()
    return selected["emoji"]


def main():
    caret = get_caret_screen_pos()
    if caret is None:
        return  # kein aktiver Text-Caret -> kein Textfeld, Menue nicht anzeigen

    target_hwnd = user32.GetForegroundWindow()
    pos = (caret[0] + CARET_OFFSET_X, caret[1] + CARET_OFFSET_Y)

    emoji = show_picker(pos)
    if emoji:
        insert_emoji(target_hwnd, emoji)


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("Dieses Script benoetigt Windows (win32 API).")
    main()
