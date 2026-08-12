
import tkinter as tk
from tkinter import ttk
from .color_scheme import *

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




class JetSpeedWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.title("Ethane Sprayer — Measure Jet Speed")
        self.geometry("600x600")
        self.minsize(500, 500)
        self.configure(bg=BG)
        self.transient(parent)

        self._build_header()
        self._build_body()

        self._build_footer()

    def _build_header(self):
        header = ttk.Frame(self)
        header.grid(row=0, column=0)
        ttk.Label(header, text="Liquid Jet Timeline", style="Title.TLabel").grid(row=0, column=0, columnspan=1)



    def _build_body(self):
        upper_body = tk.Frame(self)
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(-0.05, 1.1)
        self.ax.set_xlim(-5, 110)
        self.ax.grid(True)
        x = np.linspace(-5, 100, 1000)

        y_t0 = pulse(x, 0, 1)
        (self.line1,) = self.ax.plot(x, y_t0, color="tab:blue", lw=2, label='Jet start')

        y_t1 = sigmoid(x, 20, 1)
        (self.line2,) = self.ax.plot(x, y_t1, color="tab:red", lw=2, label='Gate 1 PD')

        y_t2 = sigmoid(x, 60, 1)
        (self.line2,) = self.ax.plot(x, y_t2, color="tab:orange", lw=2, label='Gate 2 PD')

        y_t3 = sigmoid(x, 90, 1)
        (self.line2,) = self.ax.plot(x, y_t3, color="black", lw=2, label='Arrival PD')
        self.ax.legend(loc='lower center',       # Anchor point on the legend box
    bbox_to_anchor=(0.5, 1.02), # Coordinates relative to axes (x=center, y=slightly above top)
    ncol=4)

        # 4. Canvas Embedding
        self.figcanvas = FigureCanvasTkAgg(self.fig, master=upper_body)
        self.figcanvas.draw()
        self.figcanvas.get_tk_widget().grid(row=0, column=0,columnspan=1 )
        upper_body.grid(row=1, column=0)

        lower_body = tk.Frame(self)
        lower_body.grid(row=2,column=0)

        ttk.Button(lower_body, text="JET", style='Title.TLabel').grid(row=0, column=0, rowspan=3)


        values_display = tk.Frame(master=lower_body)
        values_display.grid(row=0, column=1)

        tk.Label(master=values_display, text='X1').grid(row=0, column=0)
        tk.Entry(master=values_display, text='').grid(row=0, column=1)

        tk.Label(master=values_display, text='X2').grid(row=1, column=0)
        tk.Entry(master=values_display, text='').grid(row=1, column=1)

        tk.Label(master=values_display, text='X3').grid(row=2, column=0)
        tk.Entry(master=values_display, text='').grid(row=2, column=1)

        tk.Label(master=values_display, text='T1').grid(row=0, column=2)
        tk.Entry(master=values_display, text='').grid(row=0, column=3)

        tk.Label(master=values_display, text='T2').grid(row=1, column=2)
        tk.Entry(master=values_display, text='').grid(row=1, column=3)

        tk.Label(master=values_display, text='T3').grid(row=2, column=2)
        tk.Entry(master=values_display, text='').grid(row=2, column=3)











    # def _build_body(self):
        # self.body = tk.Frame(master=self)
        # ttk.Button(self.body, text="JET", style="Title.TLabel").pack(side=tk.BOTTOM)

        # self.value_display = tk.Frame(master=self.body)
        # self.value_display.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        # .grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        # self.



    def _build_footer(self):
        pass




def sigmoid(x, xc, w):
    return -1.0 / (1.0 + np.exp(-(x - xc) / w)) + 1

def pulse(x, xc, w):
    return 1 * np.exp(- ((x - xc) / w)**2)
