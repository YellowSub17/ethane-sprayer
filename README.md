# Ethane Sprayer

Control software for running the ethane sprayer

## Requirements

sudo apt install picotool
matplotlib
numpy
pip install mpremote


## `run_gui.py`
Run the gui software to send tcp commands to the Raspberry Pi. Can be run locally on the pi as well. See `gui/` for more details.

## `bridge.py [PORT]`
TCP radio that listens for commands from the gui, and sends them to the pico via Serial/UArt.

## `pico/`
Code for the pico.



