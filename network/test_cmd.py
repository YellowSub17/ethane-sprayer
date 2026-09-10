# test_cmd.py
import argparse
import time
from client import NetworkClient

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


def main():
    parser = argparse.ArgumentParser(description="Send single command to Ethane Sprayer")
    parser.add_argument("HOST", nargs="?", default='localhost', type=str)
    parser.add_argument("PORT", nargs="?", default=5001, type=int)
    parser.add_argument("COMMAND", nargs="?", default='LASER=1', type=str)
    args = parser.parse_args()

    client = NetworkClient()
    client.connect(args.HOST, args.PORT)

    # 1. Wait for connection
    time.sleep(0.1)
    if not client.connected:
        print("[TEST] Connection failed.")
        return

    # 2. Send command
    print(f"[TEST] Sending: '{args.COMMAND}'")

    client.send_command(args.COMMAND)
    try:
        while True:
            event = client.get_response()
            if event:
                if event.startswith("[RX]"):
                    print(f"[TEST] Server Reply: {event[5:]}")
                    break
                elif event.startswith("[SYS]") or not client.connected:
                    print("[TEST] Connection lost while waiting.")
                    break

            time.sleep(0.01)  # Keep CPU idle between queue checks
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user.")


    client.disconnect()

if __name__ == "__main__":
    main()
