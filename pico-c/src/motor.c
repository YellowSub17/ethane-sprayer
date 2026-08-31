#include "pins.h"
#include "pico/stdlib.h"

// Delay in microseconds between steps (controls motor speed)
#define STEP_DELAY_US 3200

void motor_init(void) {
    gpio_init(PIN_MOTOR_STEP);
    gpio_set_dir(PIN_MOTOR_STEP, GPIO_OUT);
    gpio_put(PIN_MOTOR_STEP, 0);

    gpio_init(PIN_MOTOR_DIR);
    gpio_set_dir(PIN_MOTOR_DIR, GPIO_OUT);
    gpio_put(PIN_MOTOR_DIR, 0);
}

void motor_step(int steps) {
    static bool initialized = false;
    if (!initialized) {
        motor_init();
        initialized = true;
    }

    // Set direction: positive steps = forward (1), negative steps = reverse (0)
    if (steps >= 0) {
        gpio_put(PIN_MOTOR_DIR, 1);
    } else {
        gpio_put(PIN_MOTOR_DIR, 0);
        steps = -steps; // Convert to positive iteration count
    }

    // Give the driver direction setup time (min 200ns for A4988)
    sleep_us(5);

    // Pulse the STEP pin
    for (int i = 0; i < steps; i++) {
        gpio_put(PIN_MOTOR_STEP, 1);
        sleep_us(STEP_DELAY_US / 2);
        gpio_put(PIN_MOTOR_STEP, 0);
        sleep_us(STEP_DELAY_US / 2);
    }
}
