import socket
import serial

import argparse


parser = argparse.ArgumentParser(
        description="TCP/UArt bridge between gui and pico for the ethane sprayer project"
        )
parser.add_argument("HOST",default='0.0.0.0')
parser.add_argument("PORT",default=5001)

args. parser.parse_args()



# Configure Pi Hardware UART
# ser = serial.Serial('/dev/serial0', 115200, timeout=1)

# Set up TCP Server on Pi
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((args.HOST, args.PORT))
    s.listen()
    print(f"Bridge listening on port {args.PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Forward data directly to Pico via UART
                # ser.write(data)
                print(data.decode('utf-8'))

