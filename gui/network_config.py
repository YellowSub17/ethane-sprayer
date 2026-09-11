import tkinter as tk
from tkinter import filedialog, messagebox

class NetworkConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Ethane Sprayer — Network Config")
        self.geometry("380x320")
        self.client = self.parent.network_client

        # --- UI Form Fields ---
        tk.Label(self, text="Network Configuration", font=("Helvetica", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, fill="x")

        # Host (Pi IP or hostname)
        tk.Label(form_frame, text="SSH Host:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_host = tk.Entry(form_frame)
        self.ent_host.insert(0, "130.238.39.32")
        self.ent_host.grid(row=0, column=1, sticky="ew", pady=2)

        # SSH Key File
        tk.Label(form_frame, text="SSH Key:").grid(row=1, column=0, sticky="w", pady=2)
        key_frame = tk.Frame(form_frame)
        key_frame.grid(row=1, column=1, sticky="ew", pady=2)

        self.ent_key = tk.Entry(key_frame, width=15)
        self.ent_key.pack(side="left", fill="x", expand=True)
        tk.Button(key_frame, text="...", command=self._browse_key).pack(side="right")

        # Local Port
        tk.Label(form_frame, text="Local Port:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_local_port = tk.Entry(form_frame)
        self.ent_local_port.insert(0, "5001")
        self.ent_local_port.grid(row=2, column=1, sticky="ew", pady=2)

        # Remote Port (Pi Server Port)
        tk.Label(form_frame, text="Remote Port:").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_remote_port = tk.Entry(form_frame)
        self.ent_remote_port.insert(0, "5001")
        self.ent_remote_port.grid(row=3, column=1, sticky="ew", pady=2)

        form_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15, fill="x", padx=20)

        self.btn_connect = tk.Button(btn_frame, text="Connect", command=self.on_connect, height=2)
        self.btn_connect.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_disconnect = tk.Button(btn_frame, text="Disconnect", command=self.on_disconnect, height=2)
        self.btn_disconnect.pack(side="right", fill="x", expand=True, padx=2)

        # Handle window close X button
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _browse_key(self):
        filepath = filedialog.askopenfilename(title="Select Private SSH Key")
        if filepath:
            self.ent_key.delete(0, tk.END)
            self.ent_key.insert(0, filepath)

    def on_connect(self):
        host = self.ent_host.get().strip()
        key_path = self.ent_key.get().strip()
        local_port = self.ent_local_port.get().strip()
        remote_port = self.ent_remote_port.get().strip()

        if not all([host, local_port, remote_port]):
            messagebox.showerror("Error", "Please fill in all connection fields.")
            return

        self.client.connect(host, local_port, remote_port, key_path)

    def on_disconnect(self):
        if self.client.connected:
            self.client.disconnect()

    def on_close(self):
        self.destroy()
