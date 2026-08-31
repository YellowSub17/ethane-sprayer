#include "pins.h"
#include "pico/stdlib.h"
#include <stdio.h>

// Delay in microseconds between steps (controls motor speed)
#define STEP_DELAY_US 3200

// Steps per revolution
#define DRIVER_MSTEP 200


typedef enum {
    STATE_IDLE,
    STATE_MOVING,
    STATE_HOMING
} MotorState;



static MotorState current_state = STATE_IDLE;
static int target_steps = 0;
static int current_dir = 1;
static int absolute_position = 0;
static uint64_t last_step_time = 0;

void motor_start_homing(void) {
    current_state = STATE_HOMING;
    printf("Starting homing sequence...\n");
}

void motor_set_steps(int steps) {
    if (steps == 0) return;
    current_dir = (steps >= 0) ? 1 : 0;
    target_steps = (steps >= 0) ? steps : -steps;
    gpio_put(PIN_MOTOR_DIR, current_dir);
    current_state = STATE_MOVING;
    printf("Stepping motor %d steps...\n", steps);
}

void motor_stop(void) {
    target_steps = 0;
    current_state = STATE_IDLE;
    printf("Motor stopped immediately.\n");
}



// Called on every iteration of the main loop (non-blocking)
void motor_tick(void) {
    uint64_t now = time_us_64();

   /* if (current_state == STATE_HOMING) {*/
        /*// Read active-low homing switch*/
        /*if (gpio_get(HOME_SWITCH_PIN) == 0) {*/
            /*current_state = STATE_IDLE;*/
            /*target_steps = 0;*/
            /*absolute_position = 0;*/
            /*printf("Homed successfully! Position = 0.\n");*/
            /*return;*/
        /*}*/

        /*if (now - last_step_time >= STEP_DELAY_US) {*/
            /*last_step_time = now;*/
            /*gpio_put(DIR_PIN, 0); // Reverse towards home switch*/
            /*gpio_put(PIN_MOTOR_STEP, 1);*/
            /*sleep_us(5);*/
            /*gpio_put(PIN_MOTOR_STEP, 0);*/
        /*}*/
        /*return;*/
    /*}*/

    if (current_state == STATE_MOVING && target_steps > 0) {
        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;

            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            target_steps--;
            absolute_position += (current_dir == 1) ? 1 : -1;

            if (target_steps == 0) {
                current_state = STATE_IDLE;
                printf("Motion complete. Absolute Position: %d\n", absolute_position);
            }
        }
    }
}

void motor_init(void) {
    gpio_init(PIN_MOTOR_STEP);
    gpio_set_dir(PIN_MOTOR_STEP, GPIO_OUT);
    gpio_put(PIN_MOTOR_STEP, 0);

    gpio_init(PIN_MOTOR_DIR);
    gpio_set_dir(PIN_MOTOR_DIR, GPIO_OUT);
    gpio_put(PIN_MOTOR_DIR, 0);


    gpio_init(PIN_MOTOR_POT);
    gpio_set_dir(PIN_MOTOR_POT, GPIO_IN);
    gpio_pull_up(PIN_MOTOR_POT);

    gpio_init(PIN_MOTOR_NOT);
    gpio_set_dir(PIN_MOTOR_NOT, GPIO_IN);
    gpio_pull_up(PIN_MOTOR_NOT);
}






/*void motor_step(int steps) {*/
    /*static bool initialized = false;*/
    /*if (!initialized) {*/
        /*motor_init();*/
        /*initialized = true;*/
    /*}*/

    /*// Set direction: positive steps = forward (1), negative steps = reverse (0)*/
    /*if (steps >= 0) {*/
        /*gpio_put(PIN_MOTOR_DIR, 1);*/
    /*} else {*/
        /*gpio_put(PIN_MOTOR_DIR, 0);*/
        /*steps = -steps; // Convert to positive iteration count*/
    /*}*/

    /*// Give the driver direction setup time (min 200ns for A4988)*/
    /*sleep_us(5);*/

    /*// Pulse the STEP pin*/
    /*for (int i = 0; i < steps; i++) {*/
        /*gpio_put(PIN_MOTOR_STEP, 1);*/
        /*sleep_us(STEP_DELAY_US / 2);*/
        /*gpio_put(PIN_MOTOR_STEP, 0);*/
        /*sleep_us(STEP_DELAY_US / 2);*/
    /*}*/
/*}*/


