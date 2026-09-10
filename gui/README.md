# Ethane Sprayer Control GUI — prototype 2

## This module/readme was originally AI generated, but I have cut a lot of it so this might not be up to date anymore ]

This is a hardware-free Raspberry Pi GUI prototype for the Ethane Sprayer setup.
It lets you develop and review the operator workflow before valves, laser
electronics, photodiodes, motors, or the RP2040 firmware are connected.

## What it does

- Shows the complete experimental sequence as a state machine.
- Edits and validates the main timing parameters.
- Selects the timing reference automatically from the requested delay.
- Simulates Gate 1, Gate 2, predicted arrival, laser trigger, arrival detection,
  plunging, completion, and faults.
- Logs every event with a relative timestamp.
- Provides an emergency-style **ABORT** control.
- Includes a UART transport class, but starts in safe simulation mode.
- Opens a live timing-diagram window inspired by Supplementary Figures S3–S5.

## Timing diagrams

Click **SHOW TIMELINES** to open three tabs:

- delays longer than 3 ms, referenced to the nitrogen-valve trigger
- delays from 0.3 to 3 ms, referenced to Gate 1
- delays shorter than 300 us, predicted from Gate 1 and Gate 2

The tab for the current requested delay is selected automatically. Its traces
update when parameters change. The other two tabs remain available as
representative examples. These are idealized simulated signals, not measured
photodiode data.

Defaults taken from the experiment description:

- condensation: 60 s
- settling: 200 ms minimum
- nitrogen valve pulse: 650 us
- gate spacing: 7.0 mm
- Gate 2 to sample effective distance: 0.92 mm
- activation temperature: 290 K
- jetting temperature: 95 K

Long physical waits are accelerated in simulation so that the complete workflow
can be reviewed quickly.

## Run on a Raspberry Pi 3

Use Raspberry Pi OS with the desktop environment:

```bash
sudo apt install python3-tk python3-serial
python3 run_gui.py
```

The GUI itself only needs Python and Tk. `pyserial` is only required when UART
is enabled later.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

## UART wiring for the later hardware phase

Both devices use 3.3 V logic:

| Raspberry Pi 3 | Pico RP2040 |
|---|---|
| GPIO14 / TXD, pin 8 | chosen Pico RX pin |
| GPIO15 / RXD, pin 10 | chosen Pico TX pin |
| GND, e.g. pin 6 | GND |

Cross TX to RX and connect ground. Do not connect 5 V or any valve/laser voltage
to either UART pin. The final pin numbers and protocol will be frozen when the
Pico firmware is added.

## Safety boundary

This prototype does not control real equipment. The eventual Pico must own the
real-time state machine, interlocks, timeouts, and safe output state. The Pi GUI
may request a shot, but it must never be the only safety layer.
