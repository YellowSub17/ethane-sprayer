import socket
import threading
import serial
import time

class NetworkServer:
    def __init__(self, port=5001, serial_port='/dev/ttyACM0', baud=115200, debug=False):
        self.port = port
        self.serial_port = serial_port
        self.baud = baud
        self.debug = debug
        self.running = False
        self.client_socket = None

        # Initialize Serial unless in DEBUG mode
        self.pico = None
        if not self.debug:
            self._init_serial()
        else:
            print("Running in DEBUG mode (No physical UART required)")

    def _init_serial(self):
        try:
            self.pico = serial.Serial(self.serial_port, self.baud, timeout=0.1)
            time.sleep(2)  # Allow Pico to finish rebooting on connection
            print(f"Connected to Pico on {self.serial_port}")
        except Exception as e:
            print(f"Serial Error: {e}")

    def start(self):
        """Starts the TCP listener and Pico UART monitoring threads."""
        self.running = True

        # Thread 1: Listen for incoming TCP connection from Laptop
        threading.Thread(target=self._listen_tcp, daemon=True).start()

        # Thread 2: Continuously listen for incoming UART data from Pico
        if not self.debug:
            threading.Thread(target=self._listen_pico, daemon=True).start()

    def stop(self):
        """Stops server loops and closes sockets/serial connections."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except OSError:
                pass
        if self.pico and self.pico.is_open:
            self.pico.close()

    def send(self, message: str):
        """Sends a response/status string back to the connected laptop GUI."""
        if self.client_socket:
            if not message.endswith('\n'):
                message += '\n'
            try:
                self.client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Failed to send: {e}")

    # --- Private Worker Threads ---

    def _listen_tcp(self):
        """Listens for incoming client socket connections and reads GUI commands."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
            s.listen()
            print(f"Bridge server listening on port {self.port}...")

            while self.running:
                sock, addr = s.accept()
                print(f"Connection from {addr}")
                self.client_socket = sock

                buffer = ""
                while self.running:
                    try:
                        data = sock.recv(1024)
                        if not data:
                            print("Client disconnected.")
                            break

                        buffer += data.decode('utf-8', errors='ignore')
                        while "\n" in buffer:
                            command, buffer = buffer.split("\n", 1)
                            command = command.strip()
                            if command:
                                print(f"[Server Received]: {command}")

                                # Send command down to Pico over serial
                                if not self.debug and self.pico:
                                    self.pico.write(f"{command}\n".encode('utf-8'))

                                time.sleep(1)
                                self.send('Hello there! I am the server, I got your message, and this is my response I am sending.')


                    except Exception as e:
                        print(f"TCP error: {e}")
                        break

                self.client_socket = None

    def _listen_pico(self):
        """Reads responses from Pico UART and forwards them over TCP."""
        while self.running:
            try:
                if self.pico and self.pico.in_waiting > 0:
                    response = self.pico.readline().decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"[Server Sending]: {response}")
                        self.send(response)
            except Exception as e:
                print(f"UART error: {e}")

            time.sleep(0.01)  # Prevent CPU spinning


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TCP/UART Bridge Server for Ethane Sprayer")
    parser.add_argument("PORT", nargs="?", default=5001, type=int)
    parser.add_argument("--DEBUG", action="store_true", help="Enable debug mode (no serial port required).")
    args = parser.parse_args()

    server = NetworkServer(port=args.PORT, debug=args.DEBUG)
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bridge server...")
        server.stop()
