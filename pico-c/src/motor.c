#include "pins.h"
#include "../main.h"
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


typedef void (*gpio_handler_t)(uint gpio, uint32_t events);
// Register a specific pin and its handler function with the central dispatcher
void gpio_register_handler(uint gpio, uint32_t events, gpio_handler_t handler);



static MotorState current_state = STATE_IDLE;

static int target_steps = 0;
static int current_dir = 1;
static int absolute_position = 0;


static volatile bool limit_tripped = false;

static int znegative_limit = 0;
static int zpositive_limit = 500;

static uint64_t last_step_time = 0;

void motor_start_homing_POT(void) {
    current_state = STATE_HOMING_POT;
    printf("Starting POT homing sequence...\n");
    fflush(stdout);
}

void motor_start_homing_NOT(void) {
    current_state = STATE_HOMING_NOT;
    printf("Starting NOT homing sequence...\n");
    fflush(stdout);
}

void motor_set_steps(int steps) {
    if (steps == 0) return;
    current_dir = (steps >= 0) ? 1 : 0;
    target_steps = (steps >= 0) ? steps : -steps;
    gpio_put(PIN_MOTOR_DIR, current_dir);
    current_state = STATE_MOVING;
    printf("Stepping motor %d steps...\n", steps);
    fflush(stdout);
}

void motor_stop(void) {
    target_steps = 0;
    current_state = STATE_IDLE;
    printf("Motor stopped immediately.\n");
    fflush(stdout);
}

bool motor_enable(void) {

    if (gpio_get(PIN_MOTOR_HARDLIMIT) == 0) {
        printf("Cannot enable motor: Hard limit switch is currently depressed!\n");
        fflush(stdout);
        return false; // Enable failed
    }
    gpio_put(PIN_MOTOR_ENABLE, 1);
    limit_tripped=false;
    printf("Enabled motor.\n");
    fflush(stdout);
    return true;
}

void motor_disable(void) {
    gpio_put(PIN_MOTOR_ENABLE, 0);
    printf("Disabled motor.\n");
    fflush(stdout);
}

static void motor_limit_isr(uint gpio, uint32_t events) {
    if (gpio == PIN_MOTOR_HARDLIMIT) {

        if (limit_tripped) {
            return;
        }
        limit_tripped=true;
        motor_disable();
        printf("Hardlimit hit! Motor disabled via Interrupt.\n");
        fflush(stdout);
    }
}



void motor_init(void) {
    gpio_init(PIN_MOTOR_STEP);
    gpio_set_dir(PIN_MOTOR_STEP, GPIO_OUT);
    gpio_put(PIN_MOTOR_STEP, 0);

    gpio_init(PIN_MOTOR_DIR);
    gpio_set_dir(PIN_MOTOR_DIR, GPIO_OUT);
    gpio_put(PIN_MOTOR_DIR, 0);

    gpio_init(PIN_MOTOR_ENABLE);
    gpio_set_dir(PIN_MOTOR_ENABLE, GPIO_OUT);
    gpio_put(PIN_MOTOR_ENABLE, 0);


    gpio_init(PIN_MOTOR_POT);
    gpio_set_dir(PIN_MOTOR_POT, GPIO_IN);
    gpio_pull_up(PIN_MOTOR_POT);

    gpio_init(PIN_MOTOR_NOT);
    gpio_set_dir(PIN_MOTOR_NOT, GPIO_IN);
    gpio_pull_up(PIN_MOTOR_NOT);

    gpio_init(PIN_MOTOR_HARDLIMIT);
    gpio_set_dir(PIN_MOTOR_HARDLIMIT, GPIO_IN);
    gpio_disable_pulls(PIN_MOTOR_HARDLIMIT);

    // Register handler with the central coordinator
    gpio_register_handler(PIN_MOTOR_HARDLIMIT, GPIO_IRQ_EDGE_FALL, motor_limit_isr);
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
            fflush(stdout);
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
            fflush(stdout);

            motor_set_steps(zpositive_limit/2);


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
                fflush(stdout);

            }
        }
    }
}






