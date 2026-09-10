import socket
import serial

import argparse
import time


HOST = '0.0.0.0'

parser = argparse.ArgumentParser(
        description="TCP/UArt bridge between gui and pico for the ethane sprayer project"
        )
parser.add_argument("PORT",default=5001, type=int)
parser.add_argument("--DEBUG", action="store_true", help="Enable debug mode. Only prints commands, but doesn't send anything.",)
args = parser.parse_args()



# Handle serial connection setup safely
pico = None
if not args.DEBUG:
    try:
        pico = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
        time.sleep(2)  # Allow Pico to finish rebooting on serial open
        print("Connected to Pico on /dev/ttyACM0")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit(1)
else:
    print("Running in DEBUG mode (No physical UART required)")

time.sleep(2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, args.PORT))
    s.listen()
    print(f"Bridge listening on port {args.PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        conn.setblocking(False)  # Non-blocking for bi-directional polling
        buffer = ""

        with conn:
            while True:
                # 1. Check for incoming data from TCP Client (GUI)
                try:
                    data = conn.recv(1024)
                    if not data:
                        print(f"Client {addr} disconnected.")
                        break

                    buffer += data.decode('utf-8', errors='ignore')

                    # Process complete lines terminated by newline
                    while "\n" in buffer:
                        command_str, buffer = buffer.split("\n", 1)
                        command_str = command_str.strip()

                        if command_str:
                            print(f"[GUI -> PICO]: {command_str}")
                            if not args.DEBUG and pico:
                                pico.write(f"{command_str}\n".encode('utf-8'))

                except BlockingIOError:
                    pass  # No new data available on TCP socket right now

                # 2. Check for incoming response/telemetry from Pico -> forward to GUI
                if not args.DEBUG and pico and pico.in_waiting > 0:
                    response = pico.readline().decode('utf-8', errors='ignore').strip()
                    if response:
                        print(f"[PICO -> GUI]: {response}")
                        try:
                            conn.sendall(f"{response}\n".encode('utf-8'))
                        except OSError:
                            break

                time.sleep(0.01)  # Prevent high CPU spinning
