


import tkinter as tk
from tkinter import ttk

BG = "#101820"
PANEL = "#17232d"
TEXT = "#e8f0f2"
MUTED = "#8fa5b2"
GREEN = "#47d18c"
AMBER = "#f1b84b"
ORANGE = "#f07a3f"
MAGENTA = "#ef4da8"
BLUE = "#72a7e8"

CYAN = "#35c4d8"
GREEN = "#47d18c"
RED = "#ef6461"



LOG_BG="#0c141a",
LOG_FG="#bfd0d8",

def _configure_styles(self) -> None:
    style = ttk.Style(self)
    style.theme_use("clam")
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("TLabel", background=PANEL, foreground=TEXT, font=("Arial", 10))
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Arial", 22, "bold"))
    style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Arial", 10))
    style.configure("Status.TLabel", background=PANEL, foreground=CYAN, font=("Arial", 20, "bold"))
    style.configure("TEntry", fieldbackground="#22333f", foreground=TEXT, insertcolor=TEXT)
    style.configure(
        "TButton",
        font=("Arial", 10),
        padding=(14, 8),
        relief="flat",
        borderwidth=0,
        background="#22333f",
        foreground=TEXT,
    )
    style.map(
        "TButton",
        background=[("active", "#2c4353"), ("pressed", "#1a2731")],
    )
    style.configure("Start.TButton", font=("Arial", 12, "bold"), padding=10)






