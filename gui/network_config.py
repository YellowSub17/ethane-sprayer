import tkinter as tk
from tkinter import filedialog, messagebox

class NetworkConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Ethane Sprayer — Network Config")
        self.geometry("380x320")
        self.network_client = self.parent.network_client
        self.network_config_values = self.parent.network_config_values

        # --- UI Form Fields ---
        tk.Label(self, text="Network Configuration", font=("Helvetica", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, fill="x")

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

        form_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15, fill="x", padx=20)

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
