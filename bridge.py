import socket
import serial

# Configure Pi Hardware UART
# ser = serial.Serial('/dev/serial0', 115200, timeout=1)

# Set up TCP Server on Pi
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Bridge listening on port {PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Forward data directly to Pico via UART
                print(data.decode('utf-8'))

