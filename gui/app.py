
import time
import tkinter as tk
from tkinter import messagebox, ttk

from .model import ExperimentConfig, SIMULATION_SEQUENCE, ShotState, SEQUENCE_TT
from .network import NetworkWindow
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
        self.network_window= None
        self.network_client = None

        self.host: str = 'localhost'
        self.port: int = 5001

        self._build_header()
        self._build_body()
        self._build_footer()

        _configure_styles(self)

        # self.open_network_window()


    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 12))
        ttk.Label(header, text="ETHANE SPRAYER", style="Title.TLabel").pack(side="left")



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

        laser1 = ttk.Button(body_left,text='LASER 1', command=lambda: self.send_tcp_msg('LASER=1')).grid(row=0, column=0)

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
            bg="#0c141a",
            fg="#bfd0d8",
            insertbackground=TEXT,
            relief="flat",
            font=("DejaVu Sans Mono", 9),
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
        self.network_window = NetworkWindow(self)

    def process_rx_queue(self):
        """Polls the network client's rx_queue safely on the main UI thread."""
        try:
          # Drain all pending messages without blocking the GUI
          while True:
            message = self.network_client.rx_queue.get_nowait()
            self._log(message)
        except queue.Empty:
          pass

        # Schedule next check in 100ms
        self.after(100, self.process_rx_queue)


    def _log(self, text) -> None:
        self.log.configure(state='normal')
        self.log.insert(tk.END, text)
        self.log.insert(tk.END, '\n')
        self.log.configure(state='disabled')

    def _clear_log(self,) -> None:
        self.log.configure(state='normal')
        self.log.delete(1.0, tk.END)
        self.log.configure(state='disabled')


    def send_tcp_msg(self, msg: str ):

        """Connects to the TCP server, sends the message, and closes the connection."""
        ## need to add \n to the end of the msg

        try:
            # Create a TCP/IP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set a timeout so the UI doesn't freeze indefinitely if the port is unreachable
                s.settimeout(2.0)
                s.connect((self.host, self.port))

                # Strings must be encoded to bytes before sending over socket
                s.sendall(msg.encode("utf-8"))
                self._log(f'Sent TCP message to {self.host}:{self.port}')
                self._log(f'Message: "{msg}"')


        except Exception as e:
            self._log(f"Failed to send TCP message to {self.host}:{self.port}")
            self._log(f'Message: "{msg}"')





def main() -> None:
    app = EthaneControlApp()
    app.mainloop()
