#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"

// --- Pin Definitions ---
#define UART_ID uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define TRIGGER_SENSOR_PIN 14  // Input signal from liquid jet sensor
#define LASER_GATE_PIN     15  // Output gate to laser pulse driver

// --- Shared Volatile Variables between Cores ---
volatile uint32_t laser_delay_us = 100; // Default 100 µs delay
volatile bool system_armed = false;

// ============================================================================
// CORE 1: Time-Critical Hardware Trigger Loop
// ============================================================================
void core1_entry() {
    gpio_init(TRIGGER_SENSOR_PIN);
    gpio_set_dir(TRIGGER_SENSOR_PIN, GPIO_IN);
    gpio_pull_down(TRIGGER_SENSOR_PIN);

    gpio_init(LASER_GATE_PIN);
    gpio_set_dir(LASER_GATE_PIN, GPIO_OUT);
    gpio_put(LASER_GATE_PIN, 0);

    while (1) {
        // Wait until the system is armed by the Pi
        if (system_armed) {

            // Tight polling loop waiting for input sensor HIGH
            // Deterministic response without interrupt latency
            while (!gpio_get(TRIGGER_SENSOR_PIN)) {
                tight_loop_contents();
            }

            // Precise Microsecond Delay
            sleep_us(laser_delay_us);

            // Pulse Laser Gate HIGH (e.g., 50 µs pulse width)
            gpio_put(LASER_GATE_PIN, 1);
            sleep_us(50);
            gpio_put(LASER_GATE_PIN, 0);

            // Disarm system after single shot for safety
            system_armed = false;
            printf("[Core 1] Laser Fired! System Disarmed.\n");
        }

        tight_loop_contents();
    }
}

// ============================================================================
// CORE 0: Communication & Parameter Parsing (UART / USB)
// ============================================================================
int main() {
    stdio_init_all(); // Initialize USB debug console

    // Setup UART interface connected to Raspberry Pi
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // Launch Core 1
    multicore_launch_core1(core1_entry);

    char buffer[64];
    int idx = 0;

    printf("Pico Control Firmware Initialized.\n");

    while (1) {
        // Read incoming characters from Pi over UART
        while (uart_is_readable(UART_ID)) {
            char c = uart_getc(UART_ID);

            if (c == '\n' || c == '\r') {
                buffer[idx] = '\0';

                // Parse command string e.g., "DELAY:120" or "ARM"
                if (strncmp(buffer, "DELAY:", 6) == 0) {
                    laser_delay_us = atoi(&buffer[6]);
                    printf("[Core 0] Updated Laser Delay to %lu us\n", laser_delay_us);
                }
                else if (strcmp(buffer, "ARM") == 0) {
                    system_armed = true;
                    printf("[Core 0] SYSTEM ARMED - Awaiting trigger sensor...\n");
                }
                else if (strcmp(buffer, "DISARM") == 0) {
                    system_armed = false;
                    printf("[Core 0] SYSTEM DISARMED\n");
                }

                idx = 0; // Reset buffer
            } else if (idx < sizeof(buffer) - 1) {
                buffer[idx++] = c;
            }
        }

        tight_loop_contents();
    }
}
