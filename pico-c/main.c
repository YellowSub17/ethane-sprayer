#include "pico/stdlib.h"
#include "main.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/multicore.h"

static bool read_line(char *buffer, size_t max_len) {
    static size_t idx = 0;
    int c = getchar_timeout_us(0);

    while (c != PICO_ERROR_TIMEOUT)  {

        // Ignore carriage returns entirely to gracefully handle \r\n
        if (c == '\r') {
            c = getchar_timeout_us(0);
            continue;
        }

        if (c == '\n') {
            if (idx > 0) {
                buffer[idx] = '\0';
                idx = 0;
                return true;
            }
            // Ignore leading empty lines or orphan \n
            c = getchar_timeout_us(0);
            continue;
        }
        if (idx < max_len - 1) {
            buffer[idx++] = (char)c;
        } else {
            // Buffer overflow protection: reset and flush
            idx = 0;
            buffer[0] = '\0';
            return false;
        }
        c = getchar_timeout_us(0);
    }
    return false;
}

void core1_entry() {
    // Initialize hardware specifically isolated to Core 1 operations if needed

    while (true) {
        // High-frequency execution loop
        motor_tick();
    }
}

int main() {
    stdio_init_all();
    gpio_interrupts_init();
    laser_init();
    motor_init();
    photodiode_init();

    // Launch Core 1 execution loop
    multicore_launch_core1(core1_entry);

    char buffer[64];
    int val = 0;

    while (true) {
        // Service serial commands non-blockingly
        if (read_line(buffer, sizeof(buffer))) {
            if (strcmp(buffer, "MOTOR:HOME") == 0) {
                motor_start_homing_NOT();
            }
            else if (strcmp(buffer, "LASER:0") == 0) {
                laser_onoff(0);
            }
            else if (strcmp(buffer, "LASER:1") == 0) {
                laser_onoff(1);
            }
            else if (strcmp(buffer, "GATES:AB") == 0) {
                measure_gatesAB();
            }
            else if (strcmp(buffer, "GATES:ABC") == 0) {
                measure_gatesABC();
            }
            else if (strcmp(buffer, "MOTOR:STOP") == 0) {
                motor_stop();
            }
            else if (strcmp(buffer, "MOTOR:ENABLE") == 0) {
                motor_enable();
            }
            else if (strcmp(buffer, "MOTOR:DISABLE") == 0) {
                motor_disable();
            }
            else if (strncmp(buffer, "MOTOR:", 6) == 0) {
                val = atoi(buffer + 6); // Skip the 6 characters of "MOTOR=" and convert the rest
                motor_set_steps(val);
            }
        }
        sleep_us(100);
    }
    return 0;
}



