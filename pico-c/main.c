#include "pico/stdlib.h"
#include "hardware.h"  // Removed "src/" prefix

int main() {
    stdio_init_all();

    while (true) {
        // --- Option 1: Test LED ---
        blink_led();

        // --- Option 2: Test Laser Gate ---
        // uint32_t pulse = laser_read_gate_us();

        // --- Option 3: Test Motor ---
        // motor_step(200);
    }
    return 0;
}
