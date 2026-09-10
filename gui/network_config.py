import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import time
from client import NetworkClient

class NetworkConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ethane Sprayer — Network Config")
        self.geometry("380x320")
        self.client = self.parent.network_client
        self.ssh_process = None

        # --- UI Form Fields ---
        tk.Label(self, text="Network Configuration", font=("Helvetica", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, fill="x")

        # Host (Pi IP or hostname)
        tk.Label(form_frame, text="SSH Host:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_host = tk.Entry(form_frame)
        self.ent_host.insert(0, "ethanesprayer.local")
        self.ent_host.grid(row=0, column=1, fill="x", pady=2)

        # SSH User
        tk.Label(form_frame, text="SSH User:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_user = tk.Entry(form_frame)
        self.ent_user.insert(0, "pi")
        self.ent_user.grid(row=1, column=1, fill="x", pady=2)

        # SSH Key File
        tk.Label(form_frame, text="SSH Key:").grid(row=2, column=0, sticky="w", pady=2)
        key_frame = tk.Frame(form_frame)
        key_frame.grid(row=2, column=1, fill="x", pady=2)

        self.ent_key = tk.Entry(key_frame, width=15)
        self.ent_key.pack(side="left", fill="x", expand=True)
        tk.Button(key_frame, text="...", command=self._browse_key).pack(side="right")

        # Local Port
        tk.Label(form_frame, text="Local Port:").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_local_port = tk.Entry(form_frame)
        self.ent_local_port.insert(0, "5001")
        self.ent_local_port.grid(row=3, column=1, fill="x", pady=2)

        # Remote Port (Pi Server Port)
        tk.Label(form_frame, text="Remote Port:").grid(row=4, column=0, sticky="w", pady=2)
        self.ent_remote_port = tk.Entry(form_frame)
        self.ent_remote_port.insert(0, "5001")
        self.ent_remote_port.grid(row=4, column=1, fill="x", pady=2)

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
        user = self.ent_user.get().strip()
        key_path = self.ent_key.get().strip()
        local_port = self.ent_local_port.get().strip()
        remote_port = self.ent_remote_port.get().strip()

        if not all([host, user, local_port, remote_port]):
            messagebox.showerror("Error", "Please fill in all connection fields.")
            return

        # 1. Launch SSH Tunnel Process
        try:
            ssh_cmd = ["ssh"]
            if key_path:
                ssh_cmd.extend(["-i", key_path])

            # Forward: local_port -> 127.0.0.1:remote_port on Pi
            ssh_cmd.extend([
                "-N",
                "-L", f"{local_port}:127.0.0.1:{remote_port}",
                f"{user}@{host}"
            ])

            self.ssh_process = subprocess.Popen(ssh_cmd)
            time.sleep(1.0)  # Short pause to allow SSH handshake to settle

            # Check if process died immediately (e.g., bad IP or key)
            if self.ssh_process.poll() is not None:
                raise ConnectionError("SSH process exited immediately. Check host/key.")

        except Exception as e:
            messagebox.showerror("SSH Error", f"Failed to start SSH Tunnel:\n{e}")
            self._close_tunnel()
            return

        # 2. Connect GUI NetworkClient to local tunnel endpoint
        try:
            self.client.connect("127.0.0.1", int(local_port))
            messagebox.showinfo("Connected", f"Tunnel established!\nConnected via 127.0.0.1:{local_port}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect client to tunnel:\n{e}")
            self.on_disconnect()

    def on_disconnect(self):
        # Disconnect TCP Client
        if self.client:
            self.client.disconnect()

        # Kill SSH Tunnel
        self._close_tunnel()

    def _close_tunnel(self):
        if self.ssh_process:
            self.ssh_process.terminate()
            self.ssh_process = None

    def on_close(self):
        self.on_disconnect()
        self.destroy()
