import subprocess
import time

class SSHTunnel:
    def __init__(self):
        self.ssh_key_path = './id_ed25519'
        self.ssh_user = 'ethanesprayer'
        self.pi_ip = 'ethanesprayer.local'
        self.local_port = 5001
        self.remote_port = 5001

        self.cmd = [
            "ssh",
            "-i", self.ssh_key_path,
            "-N",  # Do not execute a remote command (tunnel only)
            "-L", f"{self.local_port}:127.0.0.1:{self.remote_port}",  # Local 5001 -> Pi 127.0.0.1:5001
            f"{self.ssh_user}@{self.pi_ip}"
        ]
        self.process = None

    def start(self):

        # Spawn the process
        self.process = subprocess.Popen(self.cmd)

        # 1. Check if process died immediately (e.g., bad command args)
        if self.process.poll() is not None:
            raise RuntimeError(f"SSH process failed immediately with exit code {self.process.returncode}")

        # 2. Poll the local port to verify the tunnel is accepting traffic
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                raise RuntimeError("SSH tunnel process exited unexpectedly while connecting.")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((self.host, self.port)) == 0:
                    return  # Tunnel is live and ready
            time.sleep(0.2)

        raise TimeoutError(f"SSH tunnel did not open port {self.port} within {timeout} seconds.")


    def stop(self):
        if self.process:
            self.process.terminate()
