
import tkinter as tk
<<<<<<< HEAD
from tkinter import filedialog, messagebox
=======
from tkinter import ttk
from .style import *
from network.client import NetworkClient
import queue
import time
from tkinter import filedialog, messagebox




>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6

class NetworkConfigWindow(tk.Toplevel):

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.parent = parent
<<<<<<< HEAD
        self.title("Ethane Sprayer — Network Config")
        self.geometry("380x320")
        self.network_client = self.parent.network_client
        self.network_config_values = self.parent.network_config_values
=======
        self.network_client = self.parent.network_client
        self._log = self.parent._log
>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6

        self.title("Ethane Sprayer — Network Configuration")

        self.configure(bg=BG)
        self.transient(parent)

<<<<<<< HEAD
        # Host (Pi IP or hostname)
        tk.Label(form_frame, text="SSH Host:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_host = tk.Entry(form_frame)
        self.ent_host.insert(0, self.network_config_values["host"])
        self.ent_host.grid(row=0, column=1, sticky="ew", pady=2)

        # SSH Key File (disabled — ssh falls back to the default identity/agent)
        # tk.Label(form_frame, text="SSH Key:").grid(row=1, column=0, sticky="w", pady=2)
        # key_frame = tk.Frame(form_frame)
        # key_frame.grid(row=1, column=1, sticky="ew", pady=2)

        # self.ent_key = tk.Entry(key_frame, width=15)
        # self.ent_key.insert(0, self.network_config_values["key_path"])
        # self.ent_key.pack(side="left", fill="x", expand=True)
        # tk.Button(key_frame, text="...", command=self._browse_key).pack(side="right")

        # Local Port
        tk.Label(form_frame, text="Local Port:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_local_port = tk.Entry(form_frame)
        self.ent_local_port.insert(0, self.network_config_values["local_port"])
        self.ent_local_port.grid(row=2, column=1, sticky="ew", pady=2)

        # Remote Port (Pi Server Port)
        tk.Label(form_frame, text="Remote Port:").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_remote_port = tk.Entry(form_frame)
        self.ent_remote_port.insert(0, self.network_config_values["remote_port"])
        self.ent_remote_port.grid(row=3, column=1, sticky="ew", pady=2)
=======
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
>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6

        ttk.Label(body, text='Remote Port:').grid(row=2, column=0, padx=(0,10), pady=5, sticky="e")
        self.remote_port_entry = ttk.Entry(body,)
        self.remote_port_entry.insert(0, '5001')
        self.remote_port_entry.grid(row=2, column=1, pady=5, sticky='ew')

        ttk.Label(body, text='SSH key:').grid(row=3, column=0, padx=(0,10), pady=5, sticky="e")
        self.ssh_key_path_entry = ttk.Entry(body,)
        self.ssh_key_path_entry.insert(0, '/Users/pat/.ssh/id_ed25519')
        self.ssh_key_path_entry.grid(row=3, column=1, pady=5, sticky='ew')

<<<<<<< HEAD
        left_col = tk.Frame(btn_frame)
        left_col.pack(side="left", fill="x", expand=True, padx=2)

        right_col = tk.Frame(btn_frame)
        right_col.pack(side="right", fill="x", expand=True, padx=2)

        self.btn_connect = tk.Button(left_col, text="Connect", command=self.on_connect, height=2)
        self.btn_connect.pack(fill="x")

        # self.btn_pat = tk.Button(left_col, text="PAT", command=self.on_pat, height=2)
        # self.btn_pat.pack(fill="x", pady=(5, 0))

        self.btn_disconnect = tk.Button(right_col, text="Disconnect", command=self.on_disconnect, height=2)
        self.btn_disconnect.pack(fill="x")

        # self.btn_jon = tk.Button(right_col, text="JON", command=self.on_jon, height=2)
        # self.btn_jon.pack(fill="x", pady=(5, 0))

        # Handle window close X button
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # def _browse_key(self):
    #     filepath = filedialog.askopenfilename(title="Select Private SSH Key")
    #     if filepath:
    #         self.ent_key.delete(0, tk.END)
    #         self.ent_key.insert(0, filepath)

    def on_connect(self):
        host = self.ent_host.get().strip()
        key_path = ""  # SSH key entry disabled — ssh uses its default identity/agent
        local_port = self.ent_local_port.get().strip()
        remote_port = self.ent_remote_port.get().strip()

        if not all([host, local_port, remote_port]):
            messagebox.showerror("Error", "Please fill in all connection fields.")
            return

        self.network_client.connect(host, local_port, remote_port, key_path)

    def on_disconnect(self):
        if self.network_client.connected:
            self.network_client.disconnect()

    # def on_pat(self):
    #     self.ent_key.delete(0, tk.END)
    #     self.ent_key.insert(0, "/Users/pat/.ssh/id_ed25519")

    # def on_jon(self):
    #     self.ent_key.delete(0, tk.END)
    #     self.ent_key.insert(0, r"C:\Users\jon\.ssh\id_ed25519")

    def _save_values(self):
        self.network_config_values.update({
            "host": self.ent_host.get().strip(),
            # "key_path": self.ent_key.get().strip(),
            "local_port": self.ent_local_port.get().strip(),
            "remote_port": self.ent_remote_port.get().strip(),
        })

    def on_close(self):
        self._save_values()
        self.destroy()
=======
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
















>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6
