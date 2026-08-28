#include "motor.h"
#include "pico/stdlib.h"

// Adjust pin numbers to match your wiring
#define STEP_PIN 15
/*#define DIR_PIN  15*/

// Delay in microseconds between steps (controls motor speed)
#define STEP_DELAY_US 3200

void motor_init(void) {
    gpio_init(STEP_PIN);
    gpio_set_dir(STEP_PIN, GPIO_OUT);
    gpio_put(STEP_PIN, 0);

    /*gpio_init(DIR_PIN);*/
    /*gpio_set_dir(DIR_PIN, GPIO_OUT);*/
    /*gpio_put(DIR_PIN, 0);*/
}

void motor_step(int steps) {
    static bool initialized = false;
    if (!initialized) {
        motor_init();
        initialized = true;
    }

   /* // Set direction: positive steps = forward (1), negative steps = reverse (0)*/
    /*if (steps >= 0) {*/
        /*gpio_put(DIR_PIN, 1);*/
    /*} else {*/
        /*gpio_put(DIR_PIN, 0);*/
        /*steps = -steps; // Convert to positive iteration count*/
    /*}*/

    // Give the driver direction setup time (min 200ns for A4988)
    sleep_us(5);

    // Pulse the STEP pin
    for (int i = 0; i < steps; i++) {
        gpio_put(STEP_PIN, 1);
        sleep_us(STEP_DELAY_US / 2);
        gpio_put(STEP_PIN, 0);
        sleep_us(STEP_DELAY_US / 2);
    }
}
