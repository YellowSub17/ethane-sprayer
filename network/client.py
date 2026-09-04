import socket
import threading
import queue
import time

class NetworkClient:
    def __init__(self):
        self.host = None
        self.port = None
        self.socket = None
        self.connected = False

        self.tx_queue = queue.Queue()  # GUI -> Network Client (Commands)
        self.rx_queue = queue.Queue()  # Network Client -> GUI (Responses)

        # Worker threads
        self._threads_running = False

    def connect(self, host: str, port: int):
        """Initiates background connection."""
        self.disconnect()  # Ensure old connection is closed
        self.host = host
        self.port = int(port)
        self._threads_running = True

        threading.Thread(target=self._connection_worker, daemon=True).start()

    def disconnect(self):
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

    def send_command(self, cmd: str):
        """GUI calls this to push a message into the client's TX queue."""
        if not cmd.endswith('\n'):
            cmd += '\n'
        self.tx_queue.put(cmd)

    def get_response(self):
        """GUI calls this to retrieve incoming responses (returns None if empty)."""
        try:
            return self.rx_queue.get_nowait()
        except queue.Empty:
            return None

    # --- Private Worker Threads ---

    def _connection_worker(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3.0)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Switch back to blocking mode

            self.connected = True
            self.rx_queue.put(f"[Client SYS] Connected to {self.host}:{self.port}")

            # Launch dedicated sender and receiver threads
            threading.Thread(target=self._tx_worker, daemon=True).start()
            threading.Thread(target=self._rx_worker, daemon=True).start()

        except Exception as e:
            self.connected = False
            self.rx_queue.put(f"[ERR] Failed to connect: {e}")

    def _tx_worker(self):
        """Monitors tx_queue and writes commands to the socket."""
        while self.connected and self._threads_running:
            try:
                # Wait for command from GUI (times out every second to check connected status)
                cmd = self.tx_queue.get(timeout=1.0)
                if self.socket and self.connected:
                    self.socket.sendall(cmd.encode('utf-8'))
                    self.rx_queue.put(f"[Client Sent] {cmd.strip()}")
            except queue.Empty:
                continue
            except Exception as e:
                self.rx_queue.put(f"[Client ERR] Send failed: {e}")
                self.connected = False
                break

    def _rx_worker(self):
        """Monitors socket for incoming data and pushes it to rx_queue."""
        buffer = ""
        while self.connected and self._threads_running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    self.rx_queue.put("[Client SYS] Server closed connection.")
                    self.connected = False
                    break

                buffer += data.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self.rx_queue.put(f"[RX] {line.strip()}")
            except Exception:
                self.connected = False
                break




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TCP/UART Bridge Server for Ethane Sprayer")
    parser.add_argument("HOST", nargs="?", default='ethanesprayer.local', type=str)
    parser.add_argument("PORT", nargs="?", default=5001, type=int)
    parser.add_argument("COMMAND", nargs="?", default='LASER=1', type=str)
    args = parser.parse_args()

    # Instantiate the client
    client = NetworkClient()

    print(f"Connecting to {args.HOST}:{args.PORT}...")
    client.connect(args.HOST, args.PORT)

    # Wait briefly for connection worker thread to establish socket
    time.sleep(2)

    if not client.connected:
        print("Failed to establish connection. Checking response queue:")
        response = client.get_response()
        if response:
            print(f"  {response}")
        exit()

    # 2. Send command
    print(f"Sending command: '{args.COMMAND}'")
    client.send_command(args.COMMAND)

    # 3. Wait for response (polling the RX queue with a timeout)
    timeout_seconds = 5.0
    start_time = time.time()
    response_received = False

    print("Waiting for response from Pico...")
    while time.time() - start_time < timeout_seconds:
        response = client.get_response()
        if response:
            print(f"Received Response: {response}")

            # Check if this event contains a response from the Pico
            if "[RX]" in response:
                response_received = True
                break

        time.sleep(0.05)  # Avoid tight spinning CPU loop

    if not response_received:
        print("Timed out waiting for response.")

    # 4. Clean up connection
    print("Disconnecting...")
    client.disconnect()
    print("Done.")

