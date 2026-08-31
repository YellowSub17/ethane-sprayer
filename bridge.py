import socket
import serial

import argparse
import time


parser = argparse.ArgumentParser(
        description="TCP/UArt bridge between gui and pico for the ethane sprayer project"
        )
# parser.add_argument("HOST",default='0.0.0.0', type=str)
HOST = '0.0.0.0'
parser.add_argument("PORT",default=5001, type=int)

args = parser.parse_args()


pico = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)



# Configure Pi Hardware UART

# Set up TCP Server on Pi
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((HOST, args.PORT))
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
                print('Got data: ', data)

                command_str = data.decode('utf-8').strip()

                # If string came across wrapped with extra literal quotes or b'', clean them up:
                command_str = command_str.replace("b'", "").replace("'", "")

                print(f"Forwarding clean command to Pico: {command_str}")

                # Send clean string down to Pico over serial with a trailing newline
                pico.write(f"{command_str}\n".encode('utf-8'))

                # print(data.decode('utf-8'))
                # pico.write(f"{data}\n".encode('utf-8'))

