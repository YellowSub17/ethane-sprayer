#include <stdio.h>
#include "pico/stdlib.h"
#include "../main.h"
#include "pins.h"

typedef enum {
    VALVE_CLOSED,
    VALVE_OPEN,
} ValveState;

static ValveState valve_state = VALVE_CLOSED;
static uint64_t valve_start_time = 0;

void N2_valve_init(void){
    printf("N2 Valve init\n");
    gpio_init(PIN_VALVE_3);
    gpio_set_dir(PIN_VALVE_3, GPIO_OUT);
    gpio_put(PIN_VALVE_3, 0);

}

void N2_valve(void){
    if (valve_state != VALVE_CLOSED) {
        return;
    }
    gpio_put(PIN_VALVE_3, 1);
    valve_start_time = time_us_64();
    valve_state = VALVE_OPEN;
    printf("N2 valve open\n");
}

void N2_valve_var(int time){
    printf("N2 valve open\n");
    gpio_put(PIN_VALVE_3, 1);
    sleep_ms(time);
    gpio_put(PIN_VALVE_3, 0);
    printf("N2 valve closing\n");
    sleep_ms(100);
}

N2_valve_tick(void){
    if (valve_state == VALVE_OPEN) {
        uint64_t now = time_us_64();
        if (now -valve_start_time >= 5000000) { 
            gpio_put(PIN_VALVE_3, 0);
            valve_state = VALVE_CLOSED;
            printf("N2 valve closing\n");
        }
    }
}
