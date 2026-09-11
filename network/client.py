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


    # def open_tunnel(self,ssh_key_path, local_port, remote_port, host):
        # self.ssh_key_path = ssh_key_path
        # self.local_port = local_port
        # self.remote_port = remote_port
        # self.host = host
        # cmd = [
            # "ssh",
            # "-i", self.ssh_key_path,
            # "-N",  # Do not execute a remote command (tunnel only)
            # "-L", f"{self.local_port}:127.0.0.1:{self.remote_port}",  # Local 5001 -> Pi 127.0.0.1:5001
            # f"{self.ssh_user}@{self.pi_ip}"
        # ]

        # self._tunnel_proc = subprocess.Popen(self.cmd)

        # if self._tunnel_proc.poll() is not None:
            # raise RuntimeError(f"SSH process failed immediately with exit code {self._tunnel_proc.returncode}")

    # def close_tunnel(self):
        # if self._tunnel_proc:
            # self._tunnel_proc.terminate()



    def connect(self, host: str, local_port: int, remote_port:int, ssh_key_path:str):
        """Initiates background connection."""
        self.disconnect(verbose=0)  # Ensure old connection is closed
        self.host = host
        self.local_port = int(local_port)
        self.remote_port = int(remote_port)
        self.ssh_key_path = ssh_key_path

        self._threads_running = True

        threading.Thread(target=self._connection_worker, daemon=True).start()

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
            self.log_queue.put(f'Disconnected from {self.host}:{self.remote_port}')
            print(f'Disconnected from {self.host}:{self.remote_port}')

        if self._tunnel_proc:
            self._tunnel_proc.terminate()



    def send_message(self, msg: str):
        """GUI calls this to push a message into the client's TX queue."""
        if self.connected:
            if not msg.endswith('\n'):
                msg += '\n'
            self.tx_queue.put(msg)
        else:
            self.log_queue.put(f"Couldn't send '{msg}', no connection.")


    # --- Private Worker Threads ---

    def _connection_worker(self):
        tunnel_cmd = [
            "ssh",
            "-i", self.ssh_key_path,
            "-N",  # Do not execute a remote command (tunnel only)
            "-L", f"{self.local_port}:127.0.0.1:{self.remote_port}",  # Local 5001 -> Pi 127.0.0.1:5001
            f"ethanesprayer@{self.host}"
        ]


        try:
            self._tunnel_proc = subprocess.Popen(tunnel_cmd)
            time.sleep(1)

            if self._tunnel_proc.poll() is not None:
                raise RuntimeError(f"SSH process failed immediately with exit code {self._tunnel_proc.returncode}")




            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3) #how long to wait trying to connect
            self.socket.connect(('127.0.0.1', self.local_port))
            self.socket.settimeout(None)  # Switch back to blocking mode

            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            self.connected = True
            self.log_queue.put(f'Connected to {self.host}:{self.remote_port} via local tunnel port {self.local_port}')
            print(f'Connected to {self.host}:{self.remote_port} via local tunnel port {self.local_port}')

            # Launch dedicated sender and receiver threads
            threading.Thread(target=self._tx_worker, daemon=True).start()
            threading.Thread(target=self._rx_worker, daemon=True).start()

        except Exception as e:
            self.connected = False
            self.log_queue.put(f'Failed to connect: {e}')
            print(f"Failed to connect: {e}")
            if self._tunnel_proc:
                self._tunnel_proc.terminate()

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
                self.log_queue.put(f"Send failed: {e}")
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
                    self.log_queue.put('Server disconnected')
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




# class NetworkClientOLD:
    # def __init__(self):
        # self.host = None
        # self.port = None
        # self.socket = None
        # self.connected = False

        # self.tx_queue = queue.Queue()  # GUI -> Network Client (Commands)
        # self.rx_queue = queue.Queue()  # Network Client -> GUI (Responses)
        # self.log_queue = queue.Queue()

        # # Worker threads
        # self._threads_running = False

    # def connect(self, host: str, port: int):
        # """Initiates background connection."""
        # self.disconnect(verbose=0)  # Ensure old connection is closed
        # self.host = host
        # self.port = int(port)
        # self._threads_running = True

        # threading.Thread(target=self._connection_worker, daemon=True).start()

    # def disconnect(self, verbose=1):
        # """Disconnects socket and stops background worker loops."""
        # self._threads_running = False
        # self.connected = False
        # if self.socket:
            # try:
                # self.socket.shutdown(socket.SHUT_RDWR)
                # self.socket.close()
            # except OSError:
                # pass
            # self.socket = None

        # if verbose:
            # self.log_queue.put(f'Disconnected from {self.host}:{self.port}')
            # print(f'Disconnected from {self.host}:{self.port}')

    # def send_message(self, msg: str):
        # """GUI calls this to push a message into the client's TX queue."""
        # if self.connected:
            # if not msg.endswith('\n'):
                # msg += '\n'
            # self.tx_queue.put(msg)
        # else:
            # self.log_queue.put(f"Couldn't send '{msg}', no connection.")

    # # def get_response(self):
        # # """GUI calls this to retrieve incoming responses (returns None if empty)."""
        # # try:
            # # return self.rx_queue.get_nowait()
        # # except queue.Empty:
            # # return None

    # # --- Private Worker Threads ---

    # def _connection_worker(self):
        # try:
            # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.socket.settimeout(3) #how long to wait trying to connect
            # self.socket.connect((self.host, self.port))
            # self.socket.settimeout(None)  # Switch back to blocking mode

            # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            # self.connected = True
            # self.log_queue.put(f'Connected to {self.host}:{self.port}')
            # print(f'Connected to {self.host}:{self.port}')

            # # Launch dedicated sender and receiver threads
            # threading.Thread(target=self._tx_worker, daemon=True).start()
            # threading.Thread(target=self._rx_worker, daemon=True).start()

        # except Exception as e:
            # self.connected = False
            # self.log_queue.put(f'Failed to connect: {e}')
            # print(f"Failed to connect: {e}")

    # def _tx_worker(self):
        # """Monitors tx_queue and writes commands to the socket."""
        # while self.connected and self._threads_running:
            # try:
                # # Wait for command from GUI (times out every second to check connected status)
                # cmd = self.tx_queue.get(timeout=1.0)
                # if self.socket and self.connected:
                    # self.socket.sendall(cmd.encode('utf-8'))

                    # now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    # self.log_queue.put(f"[{now}] TX: {cmd.strip()}")
                    # print(f"[{now}] TX: {cmd.strip()}")
            # except queue.Empty:
                # continue
            # except Exception as e:
                # self.log_queue.put(f"Send failed: {e}")
                # print(f"Send failed: {e}")
                # self.connected = False
                # break

    # def _rx_worker(self):
        # """Monitors socket for incoming data and pushes it to rx_queue."""
        # buffer = ""
        # while self.connected and self._threads_running:
            # try:
                # data = self.socket.recv(1024)
                # if not data:
                    # self.connected = False
                    # self.log_queue.put('Server disconnected')
                    # print('Server disconnected')
                    # break

                # buffer += data.decode('utf-8', errors='ignore')
                # while "\n" in buffer:
                    # line, buffer = buffer.split("\n", 1)
                    # if line.strip():
                        # now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        # self.log_queue.put(f"[{now}] RX: {line.strip()}")
                        # self.rx_queue.put(f"[RX] {line.strip()}")
                        # print(f"[{now}] RX: {line.strip()}")
            # except Exception:
                # self.connected = False
                # break




# if __name__ == "__main__":
    # import argparse

    # parser = argparse.ArgumentParser(description="Test NetworkClient Connection")
    # parser.add_argument("HOST", nargs="?", default='localhost', type=str)
    # parser.add_argument("PORT", nargs="?", default=5001, type=int)
    # args = parser.parse_args()

    # client = NetworkClient()
    # client.connect(args.HOST, args.PORT)
    # print(f"[CLIENT] Starting background client for {args.HOST}:{args.PORT}")
    # try:
        # while True:
            # time.sleep(1)
    # except KeyboardInterrupt:
        # client.disconnect()


