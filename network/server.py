import socket
import threading
import serial
import time
import re
from pathlib import Path

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

class AnalogSaver:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.f = None
        self.rows = 0
        self.name = None

    def _next_name(self):
        nums = [int(m.group(1)) for p in self.folder.glob("analog*.csv")
                if (m := re.fullmatch(r"analog(\d+)\.csv", p.name))]
        return f"analog{max(nums, default=0) + 1}.csv"

    def feed(self, line):
        """None = inte analogdata. '' = svälj raden. Annars en statusrad att skicka vidare."""
        if line.startswith("AN_BEGIN"):
            if self.f:
                self.f.close()
            self.name = self._next_name()
            self.f = open(self.folder / self.name, "w", buffering=1 << 16)
            self.f.write("t_us,A_raw,B_raw\n")
            self.rows = 0
            return f"Saving analog series to {self.name}"
        if line.startswith("AN,") and self.f:
            self.f.write(line[3:] + "\n")
            self.rows += 1
            return ""
        if line.startswith("AN_END") and self.f:
            self.f.close()
            self.f = None
            return f"Saved {self.rows} rows to {self.name}"
        return None
    
class NetworkServer:
    def __init__(self, tcp_port=5001, serial_port='/dev/ttyACM0', baud=115200, debug=False):
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.baud = baud
        self.debug = debug
        self.saver = AnalogSaver("/home/ethanesprayer/ethane-sprayer/plots")
        self.running =False
        self.client_socket = None

        # Initialize Serial unless in DEBUG mode
        self.pico = None
        if not self.debug:
            try:
                self.pico = serial.Serial(self.serial_port, self.baud, timeout=0.1)
                time.sleep(2)  # Allow Pico to finish rebooting on connection
                print(f"[SERVER] Connected to Pico on {self.serial_port}.")
            except Exception as e:
                print(f"[SERVER] Serial Error: {e}.")
        else:
            print("[SERVER] Running in DEBUG mode (No physical UART required).")


    def start(self):
        """Starts the TCP listener and UART monitoring threads."""
        self.running = True

        # Thread 1: Listen for incoming TCP connection from Laptop
        threading.Thread(target=self._listen_tcp, daemon=True).start()

        # Thread 2: Continuously listen for incoming UART data from Pico
        if not self.debug:
            threading.Thread(target=self._listen_uart, daemon=True).start()

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
        """Sends a response/status string back to the connected client"""

        print(f"[SERVER] Sending message: '{message}'")
        if self.client_socket:
            if not message.endswith('\n'):
                message += '\n'
            try:
                self.client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"[SERVER] Failed to send message: '{e}'")

    # --- Private Worker Threads ---

    def _listen_tcp(self):
        """Listens for incoming client socket connections and reads GUI commands."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', self.tcp_port))
            s.listen()
            print(f"[SERVER] Bridge server listening on port {self.tcp_port}...")

            while self.running:
                sock, addr = s.accept()
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print(f"[SERVER] Connection from {addr}.")
                self.client_socket = sock

                buffer = ""
                while self.running:
                    try:
                        data = sock.recv(1024)
                        if not data:
                            print("[SERVER] Client disconnected.")
                            break

                        buffer += data.decode('utf-8', errors='ignore')
                        while "\n" in buffer:
                            command, buffer = buffer.split("\n", 1)
                            command = command.strip()
                            if command:
                                print(f"[SERVER] Received command: '{command}'")

                                # Send command down to Pico over serial
                                if not self.debug and self.pico:
                                    self.pico.write(f"{command}\n".encode('utf-8'))
                                elif self.debug:
                                    time.sleep(1)
                                    self.send(f'{command[::-1]}')

                                # time.sleep(1)
                                # self.send('Hello there! I am the server, I got your message, and this is my response I am sending.')


                    except Exception as e:
                        print(f"[SERVER] TCP error: '{e}'")
                        break

                self.client_socket = None

    def _listen_uart(self):
        """Reads responses from Pico UART and forwards them over TCP."""
        while self.running:
            try:
                got_data = False
                # Töm allt som finns, utan paus mellan raderna
                while self.pico and self.pico.in_waiting > 0:
                    got_data = True
                    response = self.pico.readline().decode('utf-8', errors='ignore').strip()
                    if not response:
                        continue
                    status = self.saver.feed(response)
                    if status is None:
                        self.send(response)      # vanlig rad
                    elif status:
                        self.send(status)        # bara statusrader från spararen
                if not got_data:
                    time.sleep(0.001)            # vila bara när det inte finns något att läsa
            except Exception as e:
                print(f"UART error: '{e}'")
                self.stop()
                time.sleep(2)
                self.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TCP/UART Bridge Server for Ethane Sprayer")
    parser.add_argument("PORT", nargs="?", default=5001, type=int)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (no serial port required).")
    args = parser.parse_args()

    server = NetworkServer(tcp_port=args.PORT, debug=args.debug)
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bridge server...")
        server.stop()
