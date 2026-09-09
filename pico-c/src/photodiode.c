#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/structs/systick.h"
#include "hardware/irq.h"
#include "laser_timer.pio.h"

#include "pins.h"
#include "../main.h"

static volatile uint32_t tick_a = 0;
static volatile uint32_t tick_b = 0;
static volatile uint32_t tick_c = 0;
static volatile bool gate_a_hit = false;
static volatile bool gate_b_hit = false;
static volatile bool gate_c_hit = false;

void pio_irq_handler() {
    // Check if State Machine 0 (Gate A) pushed data
    if (!pio_sm_is_rx_fifo_empty(pio0, 0)) {
        tick_a = systick_hw->cvr; // Capture IMMEDIATELY in IRQ
        pio_sm_get(pio0, 0);      // Drain FIFO
        gate_a_hit = true;
    }
    // Check if State Machine 1 (Gate B) pushed data
    if (!pio_sm_is_rx_fifo_empty(pio0, 1)) {
        tick_b = systick_hw->cvr; // Capture IMMEDIATELY in IRQ
        pio_sm_get(pio0, 1);      // Drain FIFO
        gate_b_hit = true;
    }
    // Check if State Machine 2 (Gate C) pushed data
    if (!pio_sm_is_rx_fifo_empty(pio0, 2)) {
        tick_b = systick_hw->cvr; // Capture IMMEDIATELY in IRQ
        pio_sm_get(pio0, 1);      // Drain FIFO
        gate_c_hit = true;
    }


}

void init_cycle_counter() {
    systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS | M0PLUS_SYST_CSR_CLKSOURCE_BITS;
    systick_hw->rvr = 0x00FFFFFF;
}


void photodiode_init() {
    PIO pio = pio0;
    uint offset = pio_add_program(pio, &laser_gate_program);

    // Force input pins to pull-up so floating pins sit at 3.3V
    gpio_pull_up(PIN_PHOTO_DIODE1);
    gpio_pull_up(PIN_PHOTO_DIODE2);
    gpio_pull_up(PIN_PHOTO_DIODE3);

    // Setup SM1 (Gate A)
    pio_gpio_init(pio, PIN_PHOTO_DIODE1);
    pio_sm_set_consecutive_pindirs(pio, 0, PIN_PHOTO_DIODE1, 1, false);
    pio_sm_config c0 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c0, PIN_PHOTO_DIODE1);
    pio_sm_init(pio, 0, offset, &c0);

    // Setup SM1 (Gate B)
    pio_gpio_init(pio, PIN_PHOTO_DIODE2);
    pio_sm_set_consecutive_pindirs(pio, 1, PIN_PHOTO_DIODE2, 1, false);
    pio_sm_config c1 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, PIN_PHOTO_DIODE2);
    pio_sm_init(pio, 1, offset, &c1);

    // Setup SM2 (Gate C)
    pio_gpio_init(pio, PIN_PHOTO_DIODE3);
    pio_sm_set_consecutive_pindirs(pio, 2, PIN_PHOTO_DIODE3, 1, false);
    pio_sm_config c2 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, PIN_PHOTO_DIODE3);
    pio_sm_init(pio, 2, offset, &c2);

    // Enable RX FIFO Interrupts
    pio_set_irq0_source_enabled(pio, pis_sm0_rx_fifo_not_empty, true);
    pio_set_irq0_source_enabled(pio, pis_sm1_rx_fifo_not_empty, true);
    pio_set_irq0_source_enabled(pio, pis_sm2_rx_fifo_not_empty, true);
    irq_set_exclusive_handler(PIO0_IRQ_0, pio_irq_handler);
    irq_set_enabled(PIO0_IRQ_0, true);

    // Start State Machines synchronously while pulse generator is OFF
    pio_enable_sm_mask_in_sync(pio, (1u << 0) | (1u << 1) | (1u<<2));

    // Clear any startup edge noise
    sleep_ms(10);
    pio_sm_clear_fifos(pio, 0);
    pio_sm_clear_fifos(pio, 1);
    pio_sm_clear_fifos(pio, 2);
}


int measure_gatesABC() {

    init_cycle_counter();


    while (!gate_a_hit || !gate_b_hit || !gate_c_hit){
    }

    // Calculate signed difference (handling 24-bit SysTick down-counter wrap)
    int32_t diffBA = (int32_t)tick_a - (int32_t)tick_b;
    int32_t diffCB = (int32_t)tick_b - (int32_t)tick_c;

    // Handle 24-bit down-counter wrap-around
    /*if (diff > 0x7FFFFF)  diff -= 0x1000000;*/
    /*if (diff < -0x7FFFFF) diff += 0x1000000;*/

    double ns_deltaBA = diffBA * 8.0;
    double ns_deltaCB = diffCB * 8.0;

    printf("A-to-B Delta: %d cycles\t%.2f ns\t(%.3f us)\n",
           diffBA, ns_deltaBA, ns_deltaBA / 1000.0);
    stdio_flush();

    printf("B-to-C Delta: %d cycles\t%.2f ns\t(%.3f us)\n",
           diffCB, ns_deltaCB, ns_deltaCB / 1000.0);
    stdio_flush();

    gate_a_hit = false;
    gate_b_hit = false;
    gate_c_hit = false;
}

int measure_gatesAB() {

    init_cycle_counter();


    while (!gate_a_hit || !gate_b_hit || !gate_c_hit){
    }

    // Calculate signed difference (handling 24-bit SysTick down-counter wrap)
    int32_t diffBA = (int32_t)tick_a - (int32_t)tick_b;
    int32_t diffCB = (int32_t)tick_b - (int32_t)tick_c;

    // Handle 24-bit down-counter wrap-around
    /*if (diff > 0x7FFFFF)  diff -= 0x1000000;*/
    /*if (diff < -0x7FFFFF) diff += 0x1000000;*/

    double ns_deltaBA = diffBA * 8.0;
    double ns_deltaCB = diffCB * 8.0;

    printf("A-to-B Delta: %d cycles\t%.2f ns\t(%.3f us)\n",
           diffBA, ns_deltaBA, ns_deltaBA / 1000.0);
    stdio_flush();

    printf("B-to-C Delta: %d cycles\t%.2f ns\t(%.3f us)\n",
           diffCB, ns_deltaCB, ns_deltaCB / 1000.0);
    stdio_flush();

    gate_a_hit = false;
    gate_b_hit = false;
    gate_c_hit = false;
}




