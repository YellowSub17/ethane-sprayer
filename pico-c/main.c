#include "pico/stdlib.h"
#include "main.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>



int main() {
    stdio_init_all();

    char buffer[64];
    int step_count = 0;
    int laser_01 = 0;

    while (true) {


        if (fgets(buffer, sizeof(buffer), stdin) != NULL) {
            buffer[strcspn(buffer, "\r\n")] = 0;

             printf("Got transmission: %s\n", buffer);

            // Parse 'STEPS=' followed by an integer (positive or negative)
            if (sscanf(buffer, "STEPS=%d", &step_count) == 1) {
                printf("Stepping motor %d steps...\n", step_count);
                motor_step(step_count);
                printf("Done.\n");

            } else if (sscanf(buffer, "LASER=%d", &laser_01) == 1) {

                printf("Setting laser to %d...\n", laser_01);
                laser_onoff(laser_01);
                printf("Done.\n");



            }else {
                printf("Unknown command: %s\n", buffer);
            }
        }


        /*motor_step(200);*/
        /*sleep_ms(1000);*/
        /*motor_step(-100);*/
        /*sleep_ms(1000);*/


        blink_led(2);

    }
    return 0;
}


