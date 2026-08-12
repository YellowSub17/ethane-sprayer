from __future__ import annotations

import json
from typing import Any


class UartTransport:
    """Small newline-delimited JSON transport reserved for the Pico firmware."""

    def __init__(self, port: str = "/dev/serial0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self._serial = None

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self) -> None:
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Install pyserial before enabling UART") from exc
        self._serial = serial.Serial(self.port, self.baudrate, timeout=0.1)

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def send(self, command: str, **parameters: Any) -> None:
        if not self.connected:
            raise RuntimeError("UART is not connected")
        packet = {"command": command, "parameters": parameters}
        self._serial.write((json.dumps(packet) + "\n").encode("utf-8"))


class SimulationTransport:
    @property
    def connected(self) -> bool:
        return True

    def send(self, command: str, **parameters: Any) -> None:
        return None

