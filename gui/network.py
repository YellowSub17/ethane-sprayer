
import tkinter as tk
from tkinter import ttk
from .color_scheme import *




class NetworkWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.title("Ethane Sprayer — Network Configuration")
        self.geometry("500x100")
        self.minsize(500, 100)
        self.configure(bg=BG)
        self.transient(parent)



