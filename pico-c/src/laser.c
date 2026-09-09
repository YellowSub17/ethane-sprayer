#include <stdio.h>
#include "pico/stdlib.h"

#include "../main.h"
#include "pins.h"



void laser_init(void){
    gpio_init(PIN_LASER_ENABLE);
    gpio_set_dir(PIN_LASER_ENABLE, GPIO_OUT);
    gpio_put(PIN_MOTOR_STEP, 0);

}

void laser_onoff(int laser_01){

    gpio_put(PIN_LASER_ENABLE, laser_01);
    sleep_us(5);
    if (laser_01==0){
        printf("Laser turned off\n");
    } else {
        printf("Laser turned on\n");
    }




}
