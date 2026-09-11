
import tkinter as tk
from tkinter import ttk
from .style import *
from network.client import NetworkClient
import queue
import time
from tkinter import filedialog, messagebox





class NetworkConfigWindow(tk.Toplevel):

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

        ttk.Label(body, text='Local Port:').grid(row=0, column=0, padx=(0,10), pady=5, sticky="e")
        self.local_port_entry = ttk.Entry(body,)
        self.local_port_entry.insert(0, '5001')
        self.local_port_entry.grid(row=0, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='Host:').grid(row=1, column=0, padx=(0,10), pady=5, sticky='e')
        self.host_entry = ttk.Entry(body,)
        self.host_entry.insert(0, '130.238.39.32')
        self.host_entry.grid(row=1, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='Remote Port:').grid(row=2, column=0, padx=(0,10), pady=5, sticky="e")
        self.remote_port_entry = ttk.Entry(body,)
        self.remote_port_entry.insert(0, '5001')
        self.remote_port_entry.grid(row=2, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='SSH key:').grid(row=3, column=0, padx=(0,10), pady=5, sticky="e")
        self.ssh_key_path_entry = ttk.Entry(body,)
        self.ssh_key_path_entry.insert(0, '/Users/pat/.ssh/id_ed25519')
        self.ssh_key_path_entry.grid(row=3, column=1, pady=5, sticky='ew')

        ttk.Button(body, text='...', command=self.key_file_dialog).grid(row=3, column=3)


    def key_file_dialog(self):
        filepath = filedialog.askopenfilename(title="Select Private SSH Key")
        if filepath:
            self.ent_key.delete(0, tk.END)
            self.ent_key.insert(0, filepath)


    def _build_footer(self):

        footer = ttk.Frame(self)
        footer.grid(row=2, column=0)
        connect_button = ttk.Button(footer, text='Connect', command=self.connect)
        connect_button.grid(row=0,column=0)

        disconnect_button = ttk.Button(footer, text='Disconnect', command=self.disconnect)
        disconnect_button.grid(row=0,column=1)




    def connect(self):

        host = self.host_entry.get()
        local_port = self.local_port_entry.get()
        remote_port = self.remote_port_entry.get()
        ssh_key_path = self.ssh_key_path_entry.get()


        self.network_client.connect(host, local_port, remote_port, ssh_key_path)



    def disconnect(self):


        if self.network_client.connected:
            self.network_client.disconnect()


        self.after(200, self.parent._update_connection_status)
























class NetworkWindow_OLD(tk.Toplevel):

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
        self.host_entry.insert(0, 'ethanesprayer.local')
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


        # disconnect_button = ttk.Button(footer, text='Ping Server', command=self.ping_server)
        # disconnect_button.grid(row=1,column=1)

        # disconnect_button = ttk.Button(footer, text='Ping Server', command=self.ping_server)
        # disconnect_button.grid(row=1,column=1)

    def ping_server(self):
        self.network_client.send_message('PINGping!~~')


    def connect(self):

        host = self.host_entry.get()
        port = self.port_entry.get()

        self.network_client.connect(host, port)




    def disconnect(self):

        host = self.network_client.host
        port = self.network_client.port

        if self.network_client.connected:
            self.parent.network_client.disconnect()


        self.after(200, self.parent._update_connection_status)

















