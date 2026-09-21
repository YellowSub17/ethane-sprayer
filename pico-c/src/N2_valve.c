#include <stdio.h>
#include "pico/stdlib.h"
#include "../main.h"
#include "pins.h"


void N2_valve_init(void){
    printf("N2 Valve init\n");
    gpio_init(PIN_VALVE_3);
    gpio_set_dir(PIN_VALVE_3, GPIO_OUT);
    gpio_put(PIN_VALVE_3, 0);
    
}

void N2_valve(void){
    printf("N2 valve open\n");
    gpio_put(PIN_VALVE_3, 1);
    sleep_ms(500);
    gpio_put(PIN_VALVE_3, 0);
    printf("N2 valve closing\n");
    sleep_ms(100);
}