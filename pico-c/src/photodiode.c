#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/exception.h"
#include "hardware/structs/systick.h"
#include "hardware/irq.h"
#include "laser_timer.pio.h"

#include "pins.h"
#include "../main.h"

// Direct raw vector assignment for Cortex-M SysTick Exception (Vector Index 15)
#include "hardware/structs/scb.h"

static volatile uint32_t systick_overflows = 0;

static volatile uint32_t tick_a = 0;
static volatile uint32_t tick_b = 0;
static volatile uint32_t tick_c = 0;

static volatile bool gate_a_hit = false;
static volatile bool gate_b_hit = false;
static volatile bool gate_c_hit = false;

// SysTick Rollover ISR: Increments every ~134.22 ms
void isr_systick() {
    systick_overflows++;
}

// Extension function to compute continuous 32-bit up-counting cycles (8 ns resolution)
static inline uint32_t get_cycle32() {
    uint32_t overflows = systick_overflows;
    uint32_t cvr = systick_hw->cvr;

    // Handle wrap-around race condition if ISR hasn't executed yet
    if ((systick_hw->csr & M0PLUS_SYST_CSR_COUNTFLAG_BITS) && (cvr > 0x7FFFFF)) {
        overflows++;
    }

    return (overflows << 24) | (0x00FFFFFF - cvr);
}

void pio_irq_handler() {
    // Check Gate A (SM0)
    if (!pio_sm_is_rx_fifo_empty(pio0, 0)) {
        tick_a = get_cycle32();
        pio_sm_get(pio0, 0);
        gate_a_hit = true;
    }
    // Check Gate B (SM1)
    if (!pio_sm_is_rx_fifo_empty(pio0, 1)) {
        tick_b = get_cycle32();
        pio_sm_get(pio0, 1);
        gate_b_hit = true;
    }
    // Check Gate C (SM2)
    if (!pio_sm_is_rx_fifo_empty(pio0, 2)) {
        tick_c = get_cycle32(); // FIXED: captured to tick_c
        pio_sm_get(pio0, 2);    // FIXED: drained SM2 FIFO
        gate_c_hit = true;
    }
}



#include "pico/platform.h"
void init_cycle_counter() {
    systick_overflows = 0;
    systick_hw->rvr = 0x00FFFFFF;
    systick_hw->cvr = 0;

    // Set the SysTick interrupt handler
    exception_set_exclusive_handler(SYSTICK_EXCEPTION, isr_systick);
    // Enable Counter, Interrupts, and CPU Clock Source
    systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS |
                      M0PLUS_SYST_CSR_CLKSOURCE_BITS |
                      M0PLUS_SYST_CSR_TICKINT_BITS;
}

void photodiode_init() {
    PIO pio = pio0;
    uint offset = pio_add_program(pio, &laser_gate_program);

    gpio_pull_up(PIN_PHOTO_DIODE_1);
    gpio_pull_up(PIN_PHOTO_DIODE_2);
    gpio_pull_up(PIN_PHOTO_DIODE_3);

    // Setup SM0 (Gate A)
    pio_gpio_init(pio, PIN_PHOTO_DIODE_1);
    pio_sm_set_consecutive_pindirs(pio, 0, PIN_PHOTO_DIODE_1, 1, false);
    pio_sm_config c0 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c0, PIN_PHOTO_DIODE_1);
    pio_sm_init(pio, 0, offset, &c0);

    // Setup SM1 (Gate B)
    pio_gpio_init(pio, PIN_PHOTO_DIODE_2);
    pio_sm_set_consecutive_pindirs(pio, 1, PIN_PHOTO_DIODE_2, 1, false);
    pio_sm_config c1 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, PIN_PHOTO_DIODE_2);
    pio_sm_init(pio, 1, offset, &c1);

    // Setup SM2 (Gate C)
    pio_gpio_init(pio, PIN_PHOTO_DIODE_3);
    pio_sm_set_consecutive_pindirs(pio, 2, PIN_PHOTO_DIODE_3, 1, false);
    pio_sm_config c2 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c2, PIN_PHOTO_DIODE_3); // FIXED: applied c2 config
    pio_sm_init(pio, 2, offset, &c2);

    // Enable RX FIFO Interrupts
    pio_set_irq0_source_enabled(pio, pis_sm0_rx_fifo_not_empty, true);
    pio_set_irq0_source_enabled(pio, pis_sm1_rx_fifo_not_empty, true);
    pio_set_irq0_source_enabled(pio, pis_sm2_rx_fifo_not_empty, true);
    irq_set_exclusive_handler(PIO0_IRQ_0, pio_irq_handler);
    irq_set_enabled(PIO0_IRQ_0, true);

    // Start State Machines synchronously
    pio_enable_sm_mask_in_sync(pio, (1u << 0) | (1u << 1) | (1u << 2));

    // Clear startup noise
    sleep_ms(10);
    pio_sm_clear_fifos(pio, 0);
    pio_sm_clear_fifos(pio, 1);
    pio_sm_clear_fifos(pio, 2);
}

int measure_gatesABC() {
    init_cycle_counter();

    while (!gate_a_hit || !gate_b_hit || !gate_c_hit) {
        // waiting for all gates
    }

    // Standard 32-bit unsigned subtraction auto-handles up to 34.3s delta
    uint32_t diffBA = tick_b - tick_a;
    uint32_t diffCB = tick_c - tick_b;

    double ns_deltaBA = (double)diffBA * 8.0;
    double ns_deltaCB = (double)diffCB * 8.0;

    printf("A-to-B Delta: %u cycles\t%.2f ns\t(%.3f us)\n",
           diffBA, ns_deltaBA, ns_deltaBA / 1000.0);
    stdio_flush();

    printf("B-to-C Delta: %u cycles\t%.2f ns\t(%.3f us)\n",
           diffCB, ns_deltaCB, ns_deltaCB / 1000.0);
    stdio_flush();

    gate_a_hit = false;
    gate_b_hit = false;
    gate_c_hit = false;

    return 0;
}

int measure_gatesAB() {
    init_cycle_counter();

    while (!gate_a_hit || !gate_b_hit) {
        // waiting for gates A and B
    }

    uint32_t diffBA = tick_b - tick_a;
    double ns_deltaBA = (double)diffBA * 8.0;

    printf("A-to-B Delta: %u cycles\t%.2f ns\t(%.3f us)\n",
           diffBA, ns_deltaBA, ns_deltaBA / 1000.0);
    stdio_flush();

    gate_a_hit = false;
    gate_b_hit = false;

    return 0;
}
