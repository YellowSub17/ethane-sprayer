#include <stdio.h>
#include "pico/stdlib.h"
#include "../main.h"
#include "pins.h"


void valve_init(void){
    printf("Valve init\n");
    gpio_init(PIN_VALVE_1);
    gpio_set_dir(PIN_VALVE_1, GPIO_OUT);
    gpio_put(PIN_VALVE_1, 0);
    
}



void valve1(void){
    printf("Valve 1 open\n");
    gpio_put(PIN_VALVE_1, 1);
    sleep_ms(500);
    gpio_put(PIN_VALVE_1, 0);
    printf("Valve 1 closing\n");
    sleep_ms(100);
}