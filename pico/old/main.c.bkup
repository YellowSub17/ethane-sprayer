#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/structs/systick.h"
#include "laser_timer.pio.h"

#define GATE_A_PIN 13
#define GATE_B_PIN 14

// Enable ARM Cortex-M0+ cycle counter (runs at exact 125MHz / 8ns per count)
void init_cycle_counter() {
    systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS | M0PLUS_SYST_CSR_CLKSOURCE_BITS;
    systick_hw->rvr = 0x00FFFFFF; // 24-bit timer auto-reload
}

int main() {
    stdio_init_all();
    while (!stdio_usb_connected()) sleep_ms(100);

    init_cycle_counter();
    printf("Starting Dual-Gate Timer with 8ns Hardware Cycle Accuracy...\n");

    PIO pio = pio0;

    pio_gpio_init(pio, GATE_A_PIN);
    pio_gpio_init(pio, GATE_B_PIN);

    uint offset = pio_add_program(pio, &laser_gate_program);

    // Setup SM0 for Gate A (GPIO 13)
    pio_sm_config c0 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c0, GATE_A_PIN);
    pio_sm_init(pio, 0, offset, &c0);

    // Setup SM1 for Gate B (GPIO 14)
    pio_sm_config c1 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, GATE_B_PIN);
    pio_sm_init(pio, 1, offset, &c1);

    // Enable both SMs concurrently
    pio_set_sm_mask_enabled(pio, (1u << 0) | (1u << 1), true);

    uint32_t tick_a = 0;
    uint32_t tick_b = 0;

    while (1) {
        // Gate A tripped
        if (!pio_sm_is_rx_fifo_empty(pio, 0)) {
            tick_a = systick_hw->cvr; // Read current 8ns hardware cycle register
            pio_sm_get_blocking(pio, 0);
            printf("[Gate A] Tripped at Cycle: %u\n", tick_a);
        }

        // Gate B tripped
        if (!pio_sm_is_rx_fifo_empty(pio, 1)) {
            tick_b = systick_hw->cvr; // Read current 8ns hardware cycle register
            pio_sm_get_blocking(pio, 1);
            printf("[Gate B] Tripped at Cycle: %u\n", tick_b);
        }

        // Calculate delta when both have triggered
        if (tick_a != 0 && tick_b != 0) {
            // SysTick counts DOWN from 0xFFFFFF
            int32_t cycle_delta = (int32_t)(tick_a - tick_b);
            if (cycle_delta < 0) cycle_delta += 0x1000000; // Handle 24-bit wrap

            double ns_delta = cycle_delta * 8.0;
            printf("--> Flight Delta: %d cycles | %.2f ns (%.3f us)\n\n",
                   cycle_delta, ns_delta, ns_delta / 1000.0);

            tick_a = 0;
            tick_b = 0;
        }
    }
}
