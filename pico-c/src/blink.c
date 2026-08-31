#include "pins.h"
#include "pico/stdlib.h"
#include <stdio.h>




void blink_led(int n) {
    // static flag ensures pin init runs only once
    static bool initialized = false;
    if (!initialized) {
        gpio_init(PIN_PICO_LED);
        gpio_set_dir(PIN_PICO_LED, GPIO_OUT);
        initialized = true;
    }

    for (int i = 0; i < n; i++) {
        gpio_put(PIN_PICO_LED, 1);
        sleep_ms(250);
        gpio_put(PIN_PICO_LED, 0);
        sleep_ms(250);
    }
    sleep_ms(1000);
}
