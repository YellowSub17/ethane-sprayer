#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/irq.h"
#include "hardware/structs/systick.h"
#include "hardware/structs/scb.h"
#include "laser_timer.pio.h"

#include "pins.h"

static volatile uint32_t systick_overflows = 0;

// SysTick Exception Handler - fires every time 24-bit counter wraps (134ms)
void __not_in_flash_func(systick_isr)() {
    systick_overflows++;
}

// Set up 32-bit cycle counter driven by 125MHz CPU clock
void init_32bit_cycle_counter() {
    systick_hw->csr = 0; // Disable during setup
    systick_hw->rvr = 0x00FFFFFF; // Max 24-bit value
    systick_hw->cvr = 0;

    // Set SysTick handler directly in Vector Table
    // Exception 15 (SysTick) sits at VTOR offset 15
    ((void (**)(void))scb_hw->vtor)[15] = systick_isr;

    // Enable SysTick with Interrupts
    systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS |
                      M0PLUS_SYST_CSR_CLKSOURCE_BITS |
                      M0PLUS_SYST_CSR_TICKINT_BITS;
}

// Returns continuous 32-bit clock cycle count (0 to 4,294,967,295)
static inline uint32_t get_cycle_count_32() {
    uint32_t overflows = systick_overflows;
    uint32_t current_cvr = systick_hw->cvr;

    // Handle race condition if SysTick wraps right during register read
    if ((systick_hw->csr & M0PLUS_SYST_CSR_COUNTFLAG_BITS) && (current_cvr > 0x800000)) {
        overflows++;
    }

    uint64_t total_cycles = ((uint64_t)overflows * 0x01000000ULL) + (0x00FFFFFF - current_cvr);
    return (uint32_t)(total_cycles & 0xFFFFFFFF);
}

int laser_gate() {
    stdio_init_all();
    while (!stdio_usb_connected()) sleep_ms(100);

    init_32bit_cycle_counter();
    printf("Starting True 32-bit 125MHz (8ns) Dual-Gate Timer...\n");

    PIO pio = pio0;

    pio_gpio_init(pio, PIN_PHOTO_DIODE_1);
    pio_gpio_init(pio, PIN_PHOTO_DIODE_2);

    uint offset = pio_add_program(pio, &laser_gate_program);

    // Setup SM0 for Gate A (GPIO 13)
    pio_sm_config c0 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c0, PIN_PHOTO_DIODE_1);
    pio_sm_init(pio, 0, offset, &c0);

    // Setup SM1 for Gate B (GPIO 14)
    pio_sm_config c1 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, PIN_PHOTO_DIODE_2);
    pio_sm_init(pio, 1, offset, &c1);

    // Enable both SMs concurrently
    pio_set_sm_mask_enabled(pio, (1u << 0) | (1u << 1), true);

    uint32_t tick_a = 0;
    uint32_t tick_b = 0;

    while (1) {
        // Gate A tripped
        if (!pio_sm_is_rx_fifo_empty(pio, 0)) {
            tick_a = get_cycle_count_32();
            pio_sm_get_blocking(pio, 0);
            printf("[Gate A] Tripped at Cycle: %u\n", tick_a);
        }

        // Gate B tripped
        if (!pio_sm_is_rx_fifo_empty(pio, 1)) {
            tick_b = get_cycle_count_32();
            pio_sm_get_blocking(pio, 1);
            printf("[Gate B] Tripped at Cycle: %u\n", tick_b);
        }

        // Calculate delta when both have triggered
        if (tick_a != 0 && tick_b != 0) {
            uint32_t cycle_delta = (tick_b >= tick_a) ? (tick_b - tick_a) : (tick_a - tick_b);
            double ns_delta = cycle_delta * 8.0;

            printf("--> Flight Delta: %u cycles | %.2f ns (%.3f us)\n\n",
                   cycle_delta, ns_delta, ns_delta / 1000.0);

            tick_a = 0;
            tick_b = 0;
        }
    }
}


void laser_init(void){
    gpio_init(PIN_LASER_ENABLE);
    gpio_set_dir(PIN_LASER_ENABLE, GPIO_OUT);
    gpio_put(PIN_MOTOR_STEP, 0);

}

void laser_onoff(int laser_01){

    gpio_put(PIN_LASER_ENABLE, laser_01);
    sleep_us(5);



}
