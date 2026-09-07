import socket
import threading
import queue
import time

import builtins
from datetime import datetime

# Save the original print function
_original_print = builtins.print

def timestamped_print(*args, **kwargs):
    # Format current time (e.g., 2026-09-05 17:06:42.123)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    _original_print(f"[{now}]", *args, **kwargs)

# Override built-in print globally for this file
print = timestamped_print

class NetworkClient:
    def __init__(self):
        self.host = None
        self.port = None
        self.socket = None
        self.connected = False

        self.tx_queue = queue.Queue()  # GUI -> Network Client (Commands)
        self.rx_queue = queue.Queue()  # Network Client -> GUI (Responses)
        self.log_queue = queue.Queue()

        # Worker threads
        self._threads_running = False

    def connect(self, host: str, port: int):
        """Initiates background connection."""
        self.disconnect(verbose=0)  # Ensure old connection is closed
        self.host = host
        self.port = int(port)
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

        if verbose:
            self.log_queue.put(f'Disconnected from {self.host}:{self.port}')
            print(f'Disconnected from {self.host}:{self.port}')

    def send_message(self, msg: str):
        """GUI calls this to push a message into the client's TX queue."""
        if self.connected:
            if not msg.endswith('\n'):
                msg += '\n'
            self.tx_queue.put(msg)
        else:
            self.log_queue.put(f"Couldn't send '{msg}', no connection.")

    # def get_response(self):
        # """GUI calls this to retrieve incoming responses (returns None if empty)."""
        # try:
            # return self.rx_queue.get_nowait()
        # except queue.Empty:
            # return None

    # --- Private Worker Threads ---

    def _connection_worker(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3) #how long to wait trying to connect
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Switch back to blocking mode

            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            self.connected = True
            self.log_queue.put(f'Connected to {self.host}:{self.port}')
            print(f'Connected to {self.host}:{self.port}')

            # Launch dedicated sender and receiver threads
            threading.Thread(target=self._tx_worker, daemon=True).start()
            threading.Thread(target=self._rx_worker, daemon=True).start()

        except Exception as e:
            self.connected = False
            self.log_queue.put(f'Failed to connect: {e}')
            print(f"Failed to connect: {e}")

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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test NetworkClient Connection")
    parser.add_argument("HOST", nargs="?", default='localhost', type=str)
    parser.add_argument("PORT", nargs="?", default=5001, type=int)
    args = parser.parse_args()

    client = NetworkClient()
    client.connect(args.HOST, args.PORT)
    print(f"[CLIENT] Starting background client for {args.HOST}:{args.PORT}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()


