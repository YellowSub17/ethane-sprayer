#include "pico/stdlib.h"
#include "hardware.h"
#include <stdio.h>


void other_function() {
    printf("wowee");
}



int main() {
    stdio_init_all();
    printf("hello");
    other_function();

    while (true) {
        // --- Option 1: Test LED ---
        /*blink_led();*/

        // --- Option 2: Test Laser Gate ---
        // uint32_t pulse = laser_read_gate_us();

        // --- Option 3: Test Motor ---
         /*motor_step(200);*/
         /*sleep_ms(1000);*/

        laser_gate();

    }
    return 0;
}


