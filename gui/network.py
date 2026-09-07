
import tkinter as tk
from tkinter import ttk
from .style import *
from network.client import NetworkClient
import queue
import time






class NetworkWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.parent = parent
        self.network_client = self.parent.network_client
        self._log = self.parent._log

        self.title("Ethane Sprayer — Network Configuration")

        self.configure(bg=BG)
        self.transient(parent)

        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self):
        header = ttk.Frame(self, padding=(15,15,15,5))
        header.grid(row=0, column=0, sticky='ew')
        ttk.Label(header, text="Network Configuration", style="Title.TLabel").grid(row=0, column=0, columnspan=1)

    def _build_body(self):
        body = ttk.Frame(self, padding=(15,5,15,15))
        body.grid(row=1, column=0, sticky="nsew")

        self.host_label = ttk.Label(body, text='Host:')
        self.host_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky='e')
        self.host_entry = ttk.Entry(body,)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.grid(row=0, column=1, pady=5, sticky='ew')


        self.port_label = ttk.Label(body, text='Port:')
        self.port_label.grid(row=1, column=0, padx=(0,10), pady=5, sticky="e")
        self.port_entry = ttk.Entry(body,)
        self.port_entry.insert(0, '5001')
        self.port_entry.grid(row=1, column=1, pady=5, sticky='ew')


    def _build_footer(self):

        footer = ttk.Frame(self)
        footer.grid(row=2, column=0)
        connect_button = ttk.Button(footer, text='Connect', command=self.connect)
        connect_button.grid(row=0,column=0)

        disconnect_button = ttk.Button(footer, text='Disconnect', command=self.disconnect)
        disconnect_button.grid(row=0,column=1)

        disconnect_button = ttk.Button(footer, text='Ping Server', command=self.ping_server)
        disconnect_button.grid(row=0,column=2)

    def ping_server(self):
        self.network_client.send_message('PINGping!~~')

    def connect(self):

        host = self.host_entry.get()
        port = self.port_entry.get()

        self.network_client.connect(host, port)
        self.parent.process_log_queue()




    def disconnect(self):

        host = self.network_client.host
        port = self.network_client.port

        if self.network_client.connected:
            self.parent.network_client.disconnect()


        self.after(200, self.parent._update_connection_status)

















