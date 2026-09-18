#include <stdio.h>
#include "pico/stdlib.h"
#include "../main.h"
#include "pins.h"


void valve_1_init(void){
    printf("Ethane valve init\n");
    gpio_init(PIN_VALVE_1);
    gpio_set_dir(PIN_VALVE_1, GPIO_OUT);
    gpio_put(PIN_VALVE_1, 0);
    
}



void ethane_valve_1(void){
    printf("Ethane Valve 1 open\n");
    gpio_put(PIN_VALVE_1, 1);
    sleep_ms(500);
    gpio_put(PIN_VALVE_1, 0);
    printf("Ethane Valve 1 closing\n");
    sleep_ms(100);
}