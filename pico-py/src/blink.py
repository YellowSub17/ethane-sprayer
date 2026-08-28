import time
from machine import Pin


def main():
    # GPIO 25 is the onboard LED on the standard Raspberry Pi Pico
    led = Pin(25, Pin.OUT)

    while True:
        # Blink 4 times (0.25s ON, 0.25s OFF)
        for _ in range(4):
            led.value(1)
            time.sleep(0.25)
            led.value(0)
            time.sleep(0.25)

        # Wait 1 second before repeating
        time.sleep(1.0)

if __name__=='__main__':
    main()
