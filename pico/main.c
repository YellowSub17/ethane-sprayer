#include "pico/stdlib.h"

int main() {
    stdio_init_all();

    // Initialize the onboard LED pin (GPIO 25)
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    while (true) {
        // Blink 3 times (0.25s ON, 0.25s OFF)
        for (int i = 0; i < 3; i++) {
            gpio_put(PICO_DEFAULT_LED_PIN, 1);
            sleep_ms(250);
            gpio_put(PICO_DEFAULT_LED_PIN, 0);
            sleep_ms(250);
        }

        // Wait 1 second before repeating pattern
        sleep_ms(1000);
    }

    return 0;
}
