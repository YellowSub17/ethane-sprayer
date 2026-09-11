
import time
import tkinter as tk
from tkinter import messagebox, ttk

from .network_config import NetworkConfigWindow
from network.client import NetworkClient
# from .color_scheme import *

from .style import *
from .style import _configure_styles
# from .jetspeed import JetSpeedWindow

import socket
import queue



class EthaneControlApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ethane Sprayer Control")
        self.geometry("1120x720")
        self.minsize(980, 640)
        self.configure(bg=BG)

        self.network_client = NetworkClient()

        self.network_window= None


        self._build_header()
        self._build_body()
        self._build_footer()

        _configure_styles(self)

        self.process_log_queue()
        self.open_network_window()


    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 12))
        ttk.Label(header, text="ETHANE SPRAYER", style="Title.TLabel").pack(side="left")

        # Canvas for the status indicator circle
        self.status_canvas = tk.Canvas(
            header,
            width=16,
            height=16,
            highlightthickness=0,
            bd=0
        )
        self.status_canvas.pack(side="left", padx=(10, 0))

        # Draw the initial circle (x1, y1, x2, y2)
        self.status_indicator = self.status_canvas.create_oval(2, 2, 14, 14, fill="red")

        # Set initial color based on state
        self._update_connection_status()

    def _update_connection_status(self) -> None:
        """Updates the indicator circle color based on self.network_client.connected."""
        color = "green" if self.network_client.connected else "red"
        self.status_canvas.itemconfig(self.status_indicator, fill=color)

        self.after(500, self._update_connection_status)





    def _build_body(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=22)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        body_left = ttk.Frame(body, style="Panel.TFrame", padding=18)
        body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        body_left.columnconfigure(0, weight=1)
        body_left.rowconfigure(2, weight=1)

        laser0 = ttk.Button(body_left,text='LASER:0', command=lambda: self.network_client.send_message('LASER:0')).grid(row=0, column=0)
        laser1 = ttk.Button(body_left,text='LASER:1', command=lambda: self.network_client.send_message('LASER:1')).grid(row=0, column=1)

        steps20 = ttk.Button(body_left,text='MOTOR:20', command=lambda: self.network_client.send_message('MOTOR:20')).grid(row=1, column=0)
        steps20 = ttk.Button(body_left,text='MOTOR:-20', command=lambda: self.network_client.send_message('MOTOR:-20')).grid(row=1, column=1)

        steps20 = ttk.Button(body_left,text='MOTOR:ENABLE', command=lambda: self.network_client.send_message('MOTOR:ENABLE')).grid(row=2, column=0)
        steps20 = ttk.Button(body_left,text='MOTOR:DISABLE', command=lambda: self.network_client.send_message('MOTOR:DISABLE')).grid(row=2, column=1)



        cmd_entry = ttk.Entry(body_left,)
        cmd_entry.grid(row=3, column=0)
        cmd_entry.insert(0, 'CMD')
        send = ttk.Button(body_left,text='SEND', command=lambda: self.network_client.send_message(cmd_entry.get())).grid(row=3, column=1)



        body_right = ttk.Frame(body, style="Panel.TFrame", padding=18)
        body_right.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        body_right.columnconfigure(1, weight=1)
        body_right.rowconfigure(12, weight=1)

        ttk.Label(body_right, text="EVENT LOG", foreground=MUTED).grid(
            row=11, column=0, sticky="w"
        )
        ttk.Button(body_right, text="Clear Log", command = self._clear_log).grid(
            row=11, column=1, sticky="e"
                )
        self.log = tk.Text(
            body_right,
            height=10,
            bg=LOG_BG,
            fg=LOG_FG,
            insertbackground=TEXT,
            relief="flat",
            font=("Courier", 12),
            state="disabled",
        )
        self.log.grid(row=12, column=0, columnspan=3, sticky="nsew", pady=(7, 0))


        # laser1 = tkk.Button(command=lambda: self.send_tcp_msg('LASER=1')




    def _build_footer(self) -> None:
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=22, pady=16)
        # ttk.Button(footer, text="Measure Jet Speed", command=self.open_jet_speed_window).pack(side="left")
        ttk.Button(footer, text="Network", command=self.open_network_window).pack(side='left')



    def open_network_window(self) -> None:
        if self.network_window is not None and self.network_window.winfo_exists():
            self.network_window.lift()
            self.network_window.focus_force()
            return
        self.network_window = NetworkConfigWindow(self)


    def _log(self, text) -> None:
        self.log.configure(state='normal')
        self.log.insert(tk.END, text)
        self.log.insert(tk.END, '\n')
        self.log.configure(state='disabled')
        self.log.see("end")


    def _clear_log(self,) -> None:
        self.log.configure(state='normal')
        self.log.delete(1.0, tk.END)
        self.log.configure(state='disabled')

    def process_log_queue(self):
        """Polls the network client's rx_queue safely on the main UI thread."""
        try:
          # Drain all pending messages without blocking the GUI
          while True:
            message = self.network_client.log_queue.get_nowait()
            self._log(message)
        except queue.Empty:
          pass

        # Schedule next check in 100ms
        self.after(100, self.process_log_queue)










def main() -> None:
    app = EthaneControlApp()
    app.mainloop()
