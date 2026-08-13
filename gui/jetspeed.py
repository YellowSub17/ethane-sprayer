
import tkinter as tk
from tkinter import ttk
from .color_scheme import *

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import random




class JetSpeedWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.parent = parent
        self.title("Ethane Sprayer — Measure Jet Speed")
        # self.geometry("600x600")
        # self.minsize(500, 500)
        self.configure(bg=BG)
        self.transient(parent)

        self._build_header()
        self._build_body()


    def _build_header(self):
        header = ttk.Frame(self)
        header.grid(row=0, column=0)
        ttk.Label(header, text="Liquid Jet Timeline", style="Title.TLabel").grid(row=0, column=0, columnspan=1)


    def setup_axes(self):
        for ax in self.axes:
            ax.clear()
            ax.set_ylim(0, 1.0)
            # ax.set_xlim(-500, 12500)
            ax.set_xlim(8000, 12500)
            ax.grid(True)
            ax.tick_params(left=False, labelleft=False)
            # ax.set_xlabel('Time (?s)')
            # ax.set_ylabel('Signal (V)')

    def _build_body(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        upper_body = tk.Frame(self)
        upper_body.columnconfigure(0, weight=1)
        upper_body.rowconfigure(0, weight=1)
        upper_body.grid(row=1, column=0, )

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.axes = self.fig.subplots(nrows=3, ncols=1, sharex=True)
        # self.ax = self.fig.add_subplot(111)
        self.setup_axes()

        # 4. Canvas Embedding
        self.figcanvas = FigureCanvasTkAgg(self.fig, master=upper_body)
        self.figcanvas.draw()

        self.figcanvas.get_tk_widget().grid(row=0, column=0,columnspan=1, sticky='nsew' )




        lower_body = ttk.Frame(self)
        lower_body.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        button_container = ttk.Frame(lower_body)
        button_container.grid(row=0, column=0)

        ttk.Button(button_container, text="JET", command=self.measure_jet).grid(row=0, column=0, rowspan=1)
        ttk.Button(button_container, text="Plot", command=self.update_plot).grid(row=0, column=1, rowspan=1)
        # --- Section B: x1, x2, x3 Inputs ---
        self.entries = {}
        for idx, label_text in enumerate(["x1", "x2", "x3"]):
            lbl = ttk.Label(lower_body, text=label_text)
            lbl.grid(row=idx, column=1, padx=(0, 5), pady=3, sticky="e")

            ent = ttk.Entry(lower_body, width=12)
            ent.grid(row=idx, column=2, padx=(0, 15), pady=3, sticky="w")
            self.entries[label_text] = ent

        # --- Section C: t1, t2, t3 Inputs ---
        for idx, label_text in enumerate(["t1", "t2", "t3"]):
            lbl = ttk.Label(lower_body, text=label_text)
            lbl.grid(row=idx, column=3, padx=(0, 5), pady=3, sticky="e")

            ent = ttk.Entry(lower_body, width=12)
            ent.grid(row=idx, column=4, padx=(0, 15), pady=3, sticky="w")
            self.entries[label_text] = ent

        lbl = ttk.Label(lower_body, text='tp')
        lbl.grid(row=0, column=5, padx=(0, 5), pady=3, sticky="e")
        ent = ttk.Entry(lower_body, width=12)
        ent.grid(row=0, column=6, padx=(0, 15), pady=3, sticky="w")
        self.entries['tp'] = ent

        lbl = ttk.Label(lower_body, text='ta')
        lbl.grid(row=1, column=5, padx=(0, 5), pady=3, sticky="e")
        ent = ttk.Entry(lower_body, width=12)
        ent.grid(row=1, column=6, padx=(0, 15), pady=3, sticky="w")
        self.entries['ta'] = ent

        self.entries['x1'].insert(0,2)
        self.entries['x2'].insert(0,7.0)
        self.entries['x3'].insert(0,0.92)
        self.entries['x2'].configure(state="disabled")

        self.entries['ta'].insert(0,100.5)




    def get_float_val(self, entry_widget: ttk.Entry, default: float = 0.0) -> float:
        raw_text = entry_widget.get().strip()
        try:
            return float(raw_text)
        except ValueError:
            # User typed something invalid (like "abc") or left it blank
            print(f"Warning: Invalid float '{raw_text}'. Falling back to default: {default}")
            return default


    def measure_jet(self):

        self.parent._log('Spraying Jet')
        self.parent.send_tcp_msg('Hello World')

        t1 = round(random.gauss(8575, 50),3) #8.575 ms
        t2 = round(random.gauss(11000, 50),3) #11 ms
        t3 = round(random.gauss(11319, 50),3) #11.318714285 ms


        tp = round(self.predicted_arrival_us(t1,t2),3)

        self.entries['t1'].delete(0, tk.END)
        self.entries['t2'].delete(0, tk.END)
        self.entries['t3'].delete(0, tk.END)
        self.entries['tp'].delete(0, tk.END)

        self.entries['t1'].insert(0, t1)
        self.entries['t2'].insert(0, t2)
        self.entries['t3'].insert(0, t3)
        self.entries['tp'].insert(0, tp)



    def _update_entry(self, key, value):
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, value)









    def update_plot(self):
        self.measure_jet()
        self.setup_axes()
        t1 = self.get_float_val(self.entries['t1'])
        t2 = self.get_float_val(self.entries['t2'])
        t3 = self.get_float_val(self.entries['t3'])
        tp = self.get_float_val(self.entries['tp'])
        ta = tp-self.get_float_val(self.entries['ta'])

        # self.axes[0].vlines(0,  ymin=0,ymax=1, color="tab:blue", lw=2, label='Jet')

        self.axes[0].axvspan(t1,t2,color='black', alpha=0.3)
        self.axes[0].vlines(t1,  ymin=0,ymax=1, color="black", lw=2)
        self.axes[0].vlines(t2,  ymin=0,ymax=1, color="black", lw=2, label='PD1 to PD2')

        self.axes[1].vlines(ta,  ymin=0,ymax=1, color="green", lw=2, linestyle='solid', label='Pump Laser')
        if t3>tp:
            self.axes[1].vlines(tp,  ymin=0,ymax=1, color="red", lw=2, linestyle='dashed', label='Predicted Jet Arrival')
            self.axes[1].vlines(t3,  ymin=0,ymax=1, color="red", lw=2, linestyle='solid', label='Actual Jet Arrival (Late)')
            self.axes[1].axvspan(tp,t3,color='red', alpha=0.3, ec=None)
        else:
            self.axes[1].vlines(tp,  ymin=0,ymax=1, color="blue", lw=2, linestyle='dashed', label='Predicted Jet Arrival')
            self.axes[1].vlines(t3,  ymin=0,ymax=1, color="blue", lw=2, linestyle='solid', label='Actual Jet Arrival (Early)')
            self.axes[1].axvspan(t3,tp,color='blue', alpha=0.3, ec=None)


        self.axes[2].axvspan(ta, tp, ymin=0.5, ymax=1, color='green', ec=None, alpha=0.3)
        self.axes[2].axvspan(ta, t3, ymin=0, ymax=0.5, color='green', ec=None, alpha=0.3)

        self.axes[2].vlines(ta,  ymin=0,ymax=1, color="green", lw=2, linestyle='solid')
        self.axes[2].vlines(tp, ymin=0.5, ymax=1, color='green', linestyle='dashed',label='Planned Delay')
        self.axes[2].vlines(t3, ymin=0, ymax=0.5, color='green', linestyle='solid', label='Actual Delay')



        self.axes[0].legend()
        self.axes[1].legend()
        self.axes[2].legend()
        self.figcanvas.draw()









    def predicted_arrival_us(self, gate_1_us: float, gate_2_us: float) -> float:
        x2 = self.get_float_val(self.entries['x2'])
        x3 = self.get_float_val(self.entries['x3'])

        if gate_2_us <= gate_1_us:
            raise ValueError("Gate 2 timestamp must be later than Gate 1")
        transit_us = gate_2_us - gate_1_us
        return gate_2_us + transit_us * (x3 / x2)


    def _build_footer(self):
        pass




def sigmoid(x, xc, w):
    return -1.0 / (1.0 + np.exp(-(x - xc) / w)) + 1

def pulse(x, xc, w):
    return 1 * np.exp(- ((x - xc) / w)**2)
