#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"


const uint LED_PIN = PICO_DEFAULT_LED_PIN;

const uint PD1_PIN = 13;
const uint PD2_PIN = 14;
const uint PD3_PIN = 15;

const uint LED1_PIN = 10;
const uint LED2_PIN = 11;
const uint LED3_PIN = 12;


const uint PD_PINS[] = {PD1_PIN,PD2_PIN,PD3_PIN};
const ssize_t NUM_SENSORS=3;

#define DEBOUNCE_US 50000


static uint64_t last_trigger_time[30] = {0};





void gpio_callback(uint gpio, uint32_t events) {
    When trigger on gpio is detected, call this function.

    uint64_t now = time_us_64();

    // Check if enough time has passed since the last trigger on THIS specific pin
    if ((now - last_trigger_time[gpio]) < DEBOUNCE_US) {
        return; // Ignore contact bounce noise!
    }

    if (events & GPIO_IRQ_EDGE_FALL) {
        // Record the valid trigger time
        last_trigger_time[gpio] = now;

        double timestamp_sec = now / 1000000.0;
        printf("Dark Detected | Pin: %2d | Time: %.6f s\n", gpio, timestamp_sec);
    }
}


void setup_pins(){
    for (size_t i=0; i<NUM_SENSORS; i++) {
        uint pin = PD_PINS[i];
        gpio_init(pin);
        gpio_set_dir(pin, GPIO_IN);
        gpio_pull_up(pin);
        gpio_set_irq_enabled_with_callback(pin, GPIO_IRQ_EDGE_FALL, true, &gpio_callback);

    }

}

int main(){
    stdio_init_all();

    setup_pins();

    sleep_ms(2000);
    printf("\n");
    printf("Starting Light Sensor Logging\n");
    printf("_____________________________\n");
        while (true) {
        sleep_ms(1000);
    }


    return 0;
}

int hello() {
    // Initialize standard I/O over USB/UART based on CMake config
    stdio_init_all();

    // Initialize the onboard LED
    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    uint64_t count = 0;

    while (true) {
        gpio_put(LED_PIN, 1);
        printf("Hello from Pico C SDK! Count: %llu\n", count++);
        sleep_ms(500);

        gpio_put(LED_PIN, 0);
        sleep_ms(500);
    }

    return 0;
}
