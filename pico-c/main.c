#include "pico/stdlib.h"
#include "main.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static bool read_line(char *buffer, size_t max_len) {
    static size_t idx = 0;
    int c = getchar_timeout_us(0);

    while (c != PICO_ERROR_TIMEOUT) {
        if (c == '\r' || c == '\n') {
            if (idx > 0) {
                buffer[idx] = '\0';
                idx = 0;
                return true;
            }
        } else if (idx < max_len - 1) {
            buffer[idx++] = (char)c;
        }
        c = getchar_timeout_us(0);
    }
    return false;
}

int main() {
    stdio_init_all();
    motor_init();
    laser_init();

    char buffer[64];
    int val = 0;

    while (true) {
        // Service serial commands non-blockingly
        if (read_line(buffer, sizeof(buffer))) {
            if (strcmp(buffer, "HOME") == 0) {
                motor_start_homing();
            }
            else if (sscanf(buffer, "STEPS=%d", &val) == 1) {
                motor_set_steps(val);
            }
            else if (sscanf(buffer, "LASER=%d", &val) == 1) {
                laser_onoff(val);
                printf("Laser toggled: %d\n", val);
            }
            else if (strcmp(buffer, "STOP") == 0) {
                motor_stop();
            }
        }

        // Service motor hardware tick
        motor_tick();
    }

    return 0;
}
