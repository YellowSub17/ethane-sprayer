#include "hardware/gpio.h"
#include "../main.h"

#define MAX_GPIO_PINS 30

// Function signature for subsystem handlers




// Lookup table storing function pointers for each GPIO pin
static gpio_handler_t gpio_handlers[MAX_GPIO_PINS] = { NULL };

// The central dispatcher registered with the Pico SDK
static void global_gpio_callback(uint gpio, uint32_t events) {
    if (gpio < MAX_GPIO_PINS && gpio_handlers[gpio] != NULL) {
        gpio_handlers[gpio](gpio, events); // Dispatch directly to the registered module
    }
}

void gpio_interrupts_init(void) {
    // First call to gpio_set_irq_enabled_with_callback sets the global handler
    // We pass dummy pin 0 disabled, just to register global_gpio_callback with the SDK
    gpio_set_irq_enabled_with_callback(0, GPIO_IRQ_EDGE_FALL, true, &global_gpio_callback);
}

void gpio_register_handler(uint gpio, uint32_t events, gpio_handler_t handler) {
    if (gpio >= MAX_GPIO_PINS) return;

    gpio_handlers[gpio] = handler;
    gpio_set_irq_enabled(gpio, events, true);
}
