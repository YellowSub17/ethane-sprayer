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
    STATE_HOMING_POT,
    STATE_HOMING_NOT,
} MotorState;



static MotorState current_state = STATE_IDLE;

static int target_steps = 0;
static int current_dir = 1;
static int absolute_position = 0;


static int znegative_limit = 0;
static int zpositive_limit = 500;

static uint64_t last_step_time = 0;

void motor_start_homing_POT(void) {
    current_state = STATE_HOMING_POT;
    printf("Starting POT homing sequence...\n");
}

void motor_start_homing_NOT(void) {
    current_state = STATE_HOMING_NOT;
    printf("Starting NOT homing sequence...\n");
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

    if (current_state == STATE_HOMING_NOT) {
        // Read active-low NOT homing switch
        if (gpio_get(PIN_MOTOR_NOT) == 0) {
            absolute_position = 0;
            target_steps = DRIVER_MSTEP * 2;
            current_state = STATE_HOMING_POT;
            printf("Finished Homing NOT\n");
            return;
        }

        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;
            gpio_put(PIN_MOTOR_DIR, 1); // Reverse/CCW/-Z towards NOT switch
            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);
        }
        return;
    }

    if (current_state == STATE_HOMING_POT) {
        // Read active-low POT homing switch
        if (gpio_get(PIN_MOTOR_POT) == 0) {
            target_steps = 0;
            current_state = STATE_IDLE;
            zpositive_limit = absolute_position;
            printf("Finished Homing POT\n");
            printf("Negative Limit: %d\n", znegative_limit );
            printf("Positive Limit: %d\n", zpositive_limit );

            motor_set_steps(-zpositive_limit/2);


            return;
        }

        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;
            gpio_put(PIN_MOTOR_DIR, 0); // Forward/CW/+Z towards POT switch
            // step foward one step
            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            // increment abosolute position
            absolute_position++;
        }
        return;
    }

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






