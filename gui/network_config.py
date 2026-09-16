
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .style import *


class NetworkConfigWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.parent = parent
        self.network_client = self.parent.network_client
        self.network_config_values = self.parent.network_config_values

        self.title("Network Configuration")

        self.configure(bg=BG)
        self.transient(parent)
        self.resizable(True, True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_body()
        self._build_footer()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_body(self):
        body = ttk.Frame(self, padding=(15,15,15,15))
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text='Host:').grid(row=0, column=0, padx=(0,10), pady=5, sticky='e')
        self.host_entry = ttk.Entry(body,)
        self.host_entry.insert(0, self.network_config_values["host"])
        self.host_entry.grid(row=0, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='Local Port:').grid(row=1, column=0, padx=(0,10), pady=5, sticky="e")
        self.local_port_entry = ttk.Entry(body,)
        self.local_port_entry.insert(0, self.network_config_values["local_port"])
        self.local_port_entry.grid(row=1, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='Remote Port:').grid(row=2, column=0, padx=(0,10), pady=5, sticky="e")
        self.remote_port_entry = ttk.Entry(body,)
        self.remote_port_entry.insert(0, self.network_config_values["remote_port"])
        self.remote_port_entry.grid(row=2, column=1, pady=5, sticky='ew')

    def _build_footer(self):
        footer = ttk.Frame(self, padding=(15, 15, 15, 15))
        footer.grid(row=1, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)

        connect_button = tk.Button(footer, text='Connect', height=2, default="disabled", command=self.connect)
        connect_button.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        disconnect_button = tk.Button(footer, text='Disconnect', height=2, default="disabled", command=self.disconnect)
        disconnect_button.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

    def connect(self):
        host = self.host_entry.get().strip()
        local_port = self.local_port_entry.get().strip()
        remote_port = self.remote_port_entry.get().strip()

        if not all([host, local_port, remote_port]):
            messagebox.showerror("Error", "Please fill in all connection fields.")
            return

        self.network_client.connect(host, local_port, remote_port)

    def disconnect(self):
        if self.network_client.connected:
            self.network_client.disconnect()

        self.after(200, self.parent._update_connection_status)

    def _save_values(self):
        self.network_config_values.update({
            "host": self.host_entry.get().strip(),
            "local_port": self.local_port_entry.get().strip(),
            "remote_port": self.remote_port_entry.get().strip(),
        })

    def on_close(self):
        self._save_values()
        self.destroy()
