import socket
import threading
import queue
import time
import subprocess

from datetime import datetime



class NetworkClient:
    def __init__(self):
        self.host = None
        self.local_port = None
        self.remote_port = None
        self.ssh_key_path = None
        self.socket = None
        self.connected = False

        self.tx_queue = queue.Queue()  # GUI -> Network Client (Commands)
        self.rx_queue = queue.Queue()  # Network Client -> GUI (Responses)
        self.log_queue = queue.Queue()

        # Worker threads
        self._threads_running = False
        self._tunnel_proc= None
        self._worker_thread = None




    def connect(self, host: str, local_port: int, remote_port:int, ssh_key_path:str):
        """Initiates background connection."""
        self.disconnect(verbose=0)  # Ensure old connection is closed
        self.host = host
        self.local_port = int(local_port)
        self.remote_port = int(remote_port)
        self.ssh_key_path = ssh_key_path

        self._threads_running = True

        self._worker_thread = threading.Thread(target=self._connection_worker, daemon=True)
        self._worker_thread.start()

    def disconnect(self, verbose=1):
        """Disconnects socket and stops background worker loops."""
        self._threads_running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except OSError:
                pass
            self.socket = None

        if self._tunnel_proc:
            try:
                self._tunnel_proc.terminate()
                self._tunnel_proc.wait(timeout=2)
            except Exception:
                pass
            self._tunnel_proc = None



        if verbose:
            self.log_queue.put(f'[INFO]\tDisconnected from {self.host}:{self.remote_port}')
            print(f'Disconnected from {self.host}:{self.remote_port}')

        # Wait for any in-flight connection attempt to finish assigning
        # _tunnel_proc before touching it, so a fast reconnect can't race
        # a previous attempt and leave its ssh process untracked/orphaned.
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5)
        self._worker_thread = None

        if self._tunnel_proc:
            self._tunnel_proc.terminate()
            try:
                self._tunnel_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._tunnel_proc.kill()
                self._tunnel_proc.wait()
            self._tunnel_proc = None



    def send_message(self, msg: str):
        """GUI calls this to push a message into the client's TX queue."""
        if self.connected:
            if not msg.endswith('\n'):
                msg += '\n'
            self.tx_queue.put(msg)
        else:
            self.log_queue.put(f"[ERROR]\tCannot send '{msg}': not connected.")


    # --- Private Worker Threads ---

    def _connection_worker(self):
        tunnel_cmd = [
            "ssh",
            # "-i", self.ssh_key_path,  # disabled — ssh falls back to the default identity/agent
            "-N",  # Do not execute a remote command (tunnel only)
            "-o", "ControlMaster=no",  # Don't join/create a persistent background master
            "-o", "ControlPath=none",  # so terminating this process always frees the port
            "-o", "ExitOnForwardFailure=yes",  # exit immediately if the port bind fails
            "-L", f"{self.local_port}:127.0.0.1:{self.remote_port}",  # Local 5001 -> Pi 127.0.0.1:5001
            f"ethanesprayer@{self.host}"
        ]

<<<<<<< HEAD
        self._tunnel_proc = subprocess.Popen(tunnel_cmd, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self._ssh_stderr_worker, daemon=True).start()

        time.sleep(1)  # Give SSH a moment to authenticate and bind the local port

        if self._tunnel_proc.poll() is not None:
            self.log_queue.put(f"[ERROR]\tSSH tunnel failed to start (exit code {self._tunnel_proc.returncode}).")
            print(f"SSH tunnel failed to start (exit code {self._tunnel_proc.returncode}).")
            return
=======
>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6

        try:
            self._tunnel_proc = subprocess.Popen(tunnel_cmd)
            time.sleep(1)

            if self._tunnel_proc.poll() is not None:
                raise RuntimeError(f"SSH process failed immediately with exit code {self._tunnel_proc.returncode}")




            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3) #how long to wait trying to connect
<<<<<<< HEAD
            self.socket.connect(("127.0.0.1", self.local_port))  # Through the SSH tunnel
=======
            self.socket.connect(('127.0.0.1', self.local_port))
>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6
            self.socket.settimeout(None)  # Switch back to blocking mode

            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            self.connected = True
<<<<<<< HEAD
            self.log_queue.put(f'[INFO]\tConnected to {self.host}:{self.remote_port}')
            print(f'Connected to {self.host}:{self.remote_port}')
=======
            self.log_queue.put(f'Connected to {self.host}:{self.remote_port} via local tunnel port {self.local_port}')
            print(f'Connected to {self.host}:{self.remote_port} via local tunnel port {self.local_port}')
>>>>>>> 271c227cc1cfc27ccaf65f0056a2a1d9733552c6

            # Launch dedicated sender and receiver threads
            threading.Thread(target=self._tx_worker, daemon=True).start()
            threading.Thread(target=self._rx_worker, daemon=True).start()

        except Exception as e:
            self.connected = False
            self.log_queue.put(f'[ERROR]\tFailed to connect: {e}')
            print(f"Failed to connect: {e}")
            if self._tunnel_proc:
                self._tunnel_proc.terminate()

    def _ssh_stderr_worker(self):
        """Forwards the SSH tunnel process's stderr output into the log queue."""
        proc = self._tunnel_proc
        for line in proc.stderr:
            line = line.strip()
            if line:
                self.log_queue.put(f"[SSH]\t{line}")

    def _tx_worker(self):
        """Monitors tx_queue and writes commands to the socket."""
        while self.connected and self._threads_running:
            try:
                # Wait for command from GUI (times out every second to check connected status)
                cmd = self.tx_queue.get(timeout=1.0)
                if self.socket and self.connected:
                    self.socket.sendall(cmd.encode('utf-8'))

                    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    self.log_queue.put(f"[{now}] TX: {cmd.strip()}")
                    print(f"[{now}] TX: {cmd.strip()}")
            except queue.Empty:
                continue
            except Exception as e:
                self.log_queue.put(f"[ERROR]\tSend failed: {e}")
                print(f"Send failed: {e}")
                self.connected = False
                break

    def _rx_worker(self):
        """Monitors socket for incoming data and pushes it to rx_queue."""
        buffer = ""
        while self.connected and self._threads_running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    self.connected = False
                    if self._threads_running:
                        # Socket closed on its own (not from a user-initiated disconnect)
                        self.log_queue.put('[ERROR]\tServer disconnected')
                        print('Server disconnected')
                    break

                buffer += data.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        self.log_queue.put(f"[{now}] RX: {line.strip()}")
                        self.rx_queue.put(f"[RX] {line.strip()}")
                        print(f"[{now}] RX: {line.strip()}")
            except Exception:
                self.connected = False
                break




