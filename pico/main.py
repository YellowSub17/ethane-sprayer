import _thread
import time
from machine import Pin

# --- PIN CONFIGURATION ---
# Adjust pin numbers to match your Pico wiring
STEP_PIN = Pin(2, Pin.OUT)
DIR_PIN = Pin(3, Pin.OUT)
EN_PIN = Pin(4, Pin.OUT)  # Optional: drive low/high if EN is wired

# --- SHARED CONTROL VARIABLES ---
motor_running = False
step_delay_us = 500  # Pulse interval (lower = faster rotation)
motor_direction = 1  # 1 = Clockwise, 0 = Counter-Clockwise

def core1_stepper_worker():
    """Dedicated background loop running exclusively on Core 1."""
    global motor_running, step_delay_us, motor_direction

    while True:
        if motor_running:
            # Set direction pin state
            DIR_PIN.value(motor_direction)

            # Generate single step pulse (5us HIGH pulse width)
            STEP_PIN.high()
            time.sleep_us(5)
            STEP_PIN.low()

            # Wait for speed delay interval
            time.sleep_us(step_delay_us)
        else:
            # Yield Core 1 when motor is idle to save power
            time.sleep_ms(10)

# Launch the motor loop on Core 1
_thread.start_new_thread(core1_stepper_worker, ())

# --- CORE 0: TEST SEQUENCER ---
print("Starting Stepper Motor Test Sequence...")

# Optional: Enable driver output if EN wire is used
# EN_PIN.low()  # Many drivers use LOW for Enabled

# Test 1: Run Forward at Moderate Speed
print("Moving forward (CW)...")
motor_direction = 1
step_delay_us = 600
motor_running = True
time.sleep(3)  # Run for 3 seconds

# Test 2: Pause Motor
print("Stopping motor for 1 second...")
motor_running = False
time.sleep(1)

# Test 3: Run Reverse at Faster Speed
print("Moving reverse (CCW) faster...")
motor_direction = 0
step_delay_us = 300
motor_running = True
time.sleep(3)

# Test 4: Stop Motor
print("Test complete. Disabling motor.")
motor_running = False
