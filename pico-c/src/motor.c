#include "pins.h"
#include "../main.h"
#include "pico/stdlib.h"
#include <stdio.h>

// Delay in microseconds between steps (controls motor speed)
static int STEP_DELAY_US = 3200;

// Steps per revolution
#define DRIVER_MSTEP 400


typedef enum {
    STATE_IDLE,
    STATE_MOVING,
    STATE_HOMING_POT,
    STATE_HOMING_NOT,
    ACCURACY_TEST_NOT,
    ACCURACY_TEST_POT
} MotorState;

typedef void (*gpio_handler_t)(uint gpio, uint32_t events);
// Register a specific pin and its handler function with the central dispatcher
void gpio_register_handler(uint gpio, uint32_t events, gpio_handler_t handler);



static MotorState current_state = STATE_IDLE;
static bool homed = false;
static bool motor_enabled = false;

static int target_steps = 0;
static int current_dir = 0;
static int absolute_position = 0;

#define JET_SIGN         1      //prototype sequence variables
#define JET_OPEN_US      4000
#define JET_TIMEOUT_MS   200

typedef enum { JT_OFF, JT_MOVE1, JT_WAIT, JT_MOVE2,JT_MOVE3, JT_JET, JT_DELAY, JT_TO_POT } JetPhase;
static JetPhase jt_phase = JT_OFF;
static uint64_t jt_t0 = 0;

static int i = 0; // Index for the accuracy test results
int list[5][2] = {
    {100, 100},
    {100, 100},
    {100, 100},
    {100, 100},
    {100, 100}
};




static int znegative_limit = 0;
static int zpositive_limit = 500;

static uint64_t last_step_time = 0;


void motor_start_homing(void) {
    if (!motor_enabled) {
        printf("ERROR: Enable motor\n");
        fflush(stdout);
        return;
    }
    current_state = STATE_HOMING_NOT;
    printf("Starting homing sequence...\n");
    motor_set_dir(1);
    fflush(stdout);
}

void accuracy_test(void) {
    if (!motor_enabled || !homed) {
        printf("ERROR: Enable or calibrate motor\n");
        fflush(stdout);
        return;
    }
    current_state = ACCURACY_TEST_NOT;
    i = 0; // Reset the index for the accuracy test results
    printf("Starting accuracy test...\n");
    motor_set_dir(1);
    fflush(stdout);
}

void motor_set_steps(int steps) {
    if (steps == 0) return;
    if (!homed || !motor_enabled) {
        printf("ERROR: Motor must be calibrated or enabled\n");
        fflush(stdout);
        return;
    }

    int requested_position = absolute_position + steps; //new potential position after input steps

    if (requested_position > zpositive_limit-1) {
        printf("ERROR: Movement would go past POT limit.\n");
        printf("Current position: %d\n", absolute_position);
        printf("Requested position: %d\n", requested_position);
        fflush(stdout);
        return;
    }

    if (requested_position < 1) {
        printf("ERROR: Movement would go past NOT limit.\n");
        printf("Current position: %d\n", absolute_position);
        printf("Requested position: %d\n", requested_position);
        fflush(stdout);
        return;
    }

    if ( steps < 0 ) {
        motor_set_dir(1);
    } else {
        motor_set_dir(0);
    }
    target_steps = (steps >= 0) ? steps : -steps;
    current_state = STATE_MOVING;
    printf("Stepping motor %d steps...\n", steps);
    fflush(stdout);
}


void motor_set_dir(int dir){
    current_dir = dir;
    printf("Direction set to %d.\n", dir);
    gpio_put(PIN_MOTOR_DIR, dir);
}


void motor_stop(void) {
    target_steps = 0;
    current_state = STATE_IDLE;
    printf("Motor stopped.\n");
    fflush(stdout);
}

bool motor_enable(void) {

    if (gpio_get(PIN_MOTOR_POT_HARDLIMIT) == 0 ) {
        printf("Cannot enable motor: Hard limit POT switch is currently depressed!\n");
        fflush(stdout);
        return false; // Enable failed
    } else if (gpio_get(PIN_MOTOR_NOT_HARDLIMIT) == 0) {
        printf("Cannot enable motor: Hard limit NOT switch is currently depressed!\n");
        fflush(stdout);
        return false; // Enable failed
    }
    gpio_put(PIN_MOTOR_ENABLE, 1);
    motor_enabled = true;
    printf("Enabled motor.\n");
    fflush(stdout);
    return true;
}

void motor_disable(void) {
    gpio_put(PIN_MOTOR_ENABLE, 0);
    motor_enabled = false;
    printf("Disabled motor.\n");
    fflush(stdout);
}


static void motor_limit_isr(uint gpio, uint32_t events) { //funky with pins 21 and 6 fluctuating, pot triggers not too, not doesn't have the same problem
    if (gpio == PIN_MOTOR_NOT_HARDLIMIT && motor_enabled) {
        target_steps = 0;
        current_state = STATE_IDLE;
        motor_disable();
        printf("Negative hardlimit hit! Motor disabled via Interrupt.\n");
        fflush(stdout);
        return;
    }
    if (gpio == PIN_MOTOR_POT_HARDLIMIT && motor_enabled) {
        target_steps = 0;
        current_state = STATE_IDLE;
        motor_disable();
        printf("Positive hardlimit hit! Motor disabled via Interrupt.\n");
        fflush(stdout);
        return;
    }
}

void motor_reset(void) {
    gpio_put(PIN_MOTOR_ENABLE, 0);
    motor_enabled = false;

    current_state = STATE_IDLE;
    homed = false;

    target_steps = 0;
    absolute_position = 0;
    znegative_limit = 0;
    zpositive_limit = 500;
    last_step_time = 0;
    i = 0;
    current_dir = 0;
    gpio_put(PIN_MOTOR_DIR, 0);
    printf("Motor parameters reset. Re-home before moving.\n");
    fflush(stdout);
}

void step_time(int time) {      // Set the delay between steps in microseconds
    if (time < 200 || time > 10000) {
        printf("ERROR: invalid step time: 200<steptime<10,000\n");
        fflush(stdout);
        return;
    }
    STEP_DELAY_US = time;
    printf("Step time set to %dus\n", time);
    fflush(stdout);
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
    gpio_pull_down(PIN_MOTOR_POT);

    gpio_init(PIN_MOTOR_NOT);
    gpio_set_dir(PIN_MOTOR_NOT, GPIO_IN);
    gpio_pull_down(PIN_MOTOR_NOT);

    gpio_init(PIN_MOTOR_POT_HARDLIMIT);
    gpio_set_dir(PIN_MOTOR_POT_HARDLIMIT, GPIO_IN);
    gpio_disable_pulls(PIN_MOTOR_POT_HARDLIMIT);

    gpio_init(PIN_MOTOR_NOT_HARDLIMIT);
    gpio_set_dir(PIN_MOTOR_NOT_HARDLIMIT, GPIO_IN);
    gpio_disable_pulls(PIN_MOTOR_NOT_HARDLIMIT);

    // Register handler with the central coordinator
    gpio_register_handler(PIN_MOTOR_POT_HARDLIMIT, GPIO_IRQ_EDGE_FALL, motor_limit_isr);
    gpio_register_handler(PIN_MOTOR_NOT_HARDLIMIT, GPIO_IRQ_EDGE_FALL, motor_limit_isr);
}

void motor_jet_test(void) {
    if (!motor_enabled || !homed) {
        printf("ERROR: Enable and home the motor first\n");
        fflush(stdout);
        return;
    }
    jt_phase = JT_MOVE1;
    printf("JETTEST: Sample applied - moving to blotting position\n");
    fflush(stdout);
    step_time(2000); 
    motor_set_steps(JET_SIGN * 50);
    if (current_state != STATE_MOVING) {      // motor_set_steps refused (limit)
        jt_phase = JT_OFF;
        printf("JETTEST: aborted\n");
        fflush(stdout);
    }
}

static void jet_test_next(void) {
    switch (jt_phase) {
    case JT_MOVE1:
        jt_phase = JT_WAIT;
        jt_t0 = time_us_64();
        printf("JETTEST: Blotting...\n");
        fflush(stdout);
        break;
    case JT_MOVE2:
        jt_phase = JT_MOVE3;
        printf("JETTEST: 50 steps to laser level\n");
        fflush(stdout);
        STEP_DELAY_US = 5000;
        motor_set_steps(JET_SIGN * 50);
        if (current_state != STATE_MOVING) { STEP_DELAY_US = 3200; jt_phase = JT_OFF; }
        break;
    case JT_MOVE3:
        jt_phase = JT_JET;                  // jetsekvensen körs i nästa tick
        break;
    case JT_TO_POT:
        jt_phase = JT_OFF;
        printf("JETTEST: done");
        fflush(stdout);
        break;
    default:
        break;
    }
}



// Called on every iteration of the main loop (non-blocking)
void motor_tick(void) {

    uint64_t now = time_us_64();

        if (jt_phase == JT_WAIT && now - jt_t0 >= 5000000) {
        jt_phase = JT_MOVE2;
        printf("JETTEST: Moving to jet stage\n");
        fflush(stdout);
        step_time(1500); 
        motor_set_steps(JET_SIGN * 150);
        if (current_state != STATE_MOVING) jt_phase = JT_OFF;
        return;
    }
    if (jt_phase == JT_JET) {
        jt_phase = JT_DELAY;
        printf("JETTEST: jet sequence at position %d\n", absolute_position);
        fflush(stdout);
        jet_timing_sequence_AB(JET_OPEN_US, JET_TIMEOUT_MS);   // blockerar ca 0,3 s
        jt_t0 = time_us_64();
        return;
    }
    if (jt_phase == JT_DELAY && now - jt_t0 >= 200000) {
        jt_phase = JT_TO_POT;
        printf("JETTEST: going to POT (200 steps)\n");
        fflush(stdout);
        step_time(2000); //set the plunging speed here
        motor_set_steps(200);
        if (current_state != STATE_MOVING) jt_phase = JT_OFF;
        return;
    }
    if (current_state == STATE_HOMING_NOT) {

        if (gpio_get(PIN_MOTOR_NOT) == 1) {
            sleep_ms(1000);
            absolute_position=0;
            printf("Finished Homing NOT\n");
            motor_set_dir(0);
            fflush(stdout);

            printf("Stepping 40:\n");
            for (int step_i=0; step_i<40;step_i++){
                sleep_us(6400);
                gpio_put(PIN_MOTOR_STEP, 1);
                sleep_us(5);
                gpio_put(PIN_MOTOR_STEP, 0);
                printf("Step: %d\n", step_i);
            }

            sleep_ms(1000);
            printf("Finished stepping 40\n");

            current_state = STATE_HOMING_POT;
            absolute_position +=40;

            return;
        }

        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;
            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);
        }
        return;
    }

    if (current_state == STATE_HOMING_POT) {
        if (gpio_get(PIN_MOTOR_POT) == 1) {
            target_steps = 0;
            current_state = STATE_IDLE;
            zpositive_limit = absolute_position;
            homed = true;
            printf("Finished Homing POT\n");
            sleep_ms(1000);
            motor_set_steps(-(zpositive_limit/2)); // Move back to NOT switch
            printf("Negative Limit: %d\n", 0 );
            printf("Positive Limit: %d\n", zpositive_limit );
            fflush(stdout);

            return;
        }

        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;
            /*gpio_put(PIN_MOTOR_DIR, 0); // Forward/CW/-Z towards NOT switch*/
            // step foward one step
            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            // increment abosolute position
            absolute_position++;
        }
        return;
    }
        // Accuracy test state machine
    if (current_state == ACCURACY_TEST_NOT) {
        if (gpio_get(PIN_MOTOR_NOT) == 1) {
            printf("%d\n", absolute_position);
            list[i][0] = absolute_position;
            sleep_ms(1000);
            motor_set_dir(0);
            printf("Stepping 40:\n");

            for (int step_i=0; step_i<40;step_i++){
                sleep_us(6400);
                gpio_put(PIN_MOTOR_STEP, 1);
                sleep_us(5);
                gpio_put(PIN_MOTOR_STEP, 0);
            }
            printf("Stepping done\n");

            now = time_us_64(); // Reset the timer to avoid immediate stepping in the next state
            last_step_time = now;
            sleep_ms(1000);

            current_state = ACCURACY_TEST_POT;
            absolute_position +=40;
            fflush(stdout);
            return;
        }
        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;

            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            absolute_position += (current_dir == 0) ? 1 : -1;

            }
    }

    if (current_state == ACCURACY_TEST_POT) {
        if (gpio_get(PIN_MOTOR_POT) == 1) {
            printf("%d\n", absolute_position);
            list[i][1] = absolute_position - zpositive_limit;
            sleep_ms(1000);

            i++;
            if (i >= 5) {
                current_state = STATE_IDLE;
                printf("\nAccuracy test results:\n");
                printf("----------------------------\n");
                printf("Diff    NOT       POT\n");
                printf("----------------------------\n");
                for (int j = 0; j < 5; j++) {
                    printf("%-7d %-9d %d\n",
                    j + 1,
                    list[j][0],
                    list[j][1]);
                }
                printf("----------------------------\n");
            } else {

                motor_set_dir(1);
                printf("Stepping 40:\n");
                for (int step_i=0; step_i<40;step_i++){
                    sleep_us(6400);
                    gpio_put(PIN_MOTOR_STEP, 1);
                    sleep_us(5);
                    gpio_put(PIN_MOTOR_STEP, 0);
                }

                absolute_position -=40;
                now = time_us_64(); // Reset the timer to avoid immediate stepping in the next state
                last_step_time = now;
                sleep_ms(1000);
                printf("Finished stepping 40\n");

                current_state = ACCURACY_TEST_NOT;
                fflush(stdout);
                return;
            }
        }
        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;

            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            absolute_position += (current_dir == 0) ? 1 : -1;

        }
    }

    if (current_state == STATE_MOVING && target_steps > 0) {

        if (now - last_step_time >= STEP_DELAY_US) {
            last_step_time = now;

            gpio_put(PIN_MOTOR_STEP, 1);
            sleep_us(5);
            gpio_put(PIN_MOTOR_STEP, 0);

            target_steps--;
            absolute_position += (current_dir == 0) ? 1 : -1;

            if (target_steps == 0) {
                current_state = STATE_IDLE;
                printf("Motion complete. Absolute Position: %d\n", absolute_position);
                fflush(stdout);
                jet_test_next();
            }
        }
    }
}






