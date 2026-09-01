#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/structs/systick.h"
#include "hardware/irq.h"
#include "laser_timer.pio.h"

#define GATE_A_PIN 13
#define GATE_B_PIN 14

static volatile uint32_t tick_a = 0;
static volatile uint32_t tick_b = 0;
static volatile bool gate_a_hit = false;
static volatile bool gate_b_hit = false;

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
}

void init_cycle_counter() {
    systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS | M0PLUS_SYST_CSR_CLKSOURCE_BITS;
    systick_hw->rvr = 0x00FFFFFF;
}

int main() {
    stdio_init_all();
    while (!stdio_usb_connected()) sleep_ms(100);

    init_cycle_counter();

    PIO pio = pio0;
    uint offset = pio_add_program(pio, &laser_gate_program);

    // Setup SM0 (Gate A)
    pio_gpio_init(pio, GATE_A_PIN);
    pio_sm_set_consecutive_pindirs(pio, 0, GATE_A_PIN, 1, false); // Set as INPUT
    pio_sm_config c0 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c0, GATE_A_PIN);
    pio_sm_init(pio, 0, offset, &c0);

    // Setup SM1 (Gate B)
    pio_gpio_init(pio, GATE_B_PIN);
    pio_sm_set_consecutive_pindirs(pio, 1, GATE_B_PIN, 1, false); // Set as INPUT
    pio_sm_config c1 = laser_gate_program_get_default_config(offset);
    sm_config_set_in_pins(&c1, GATE_B_PIN);
    pio_sm_init(pio, 1, offset, &c1);

    // Enable RX FIFO Interrupts on PIO0
    pio_set_irq0_source_enabled(pio, pis_sm0_rx_fifo_not_empty, true);
    pio_set_irq0_source_enabled(pio, pis_sm1_rx_fifo_not_empty, true);
    irq_set_exclusive_handler(PIO0_IRQ_0, pio_irq_handler);
    irq_set_enabled(PIO0_IRQ_0, true);

    // Synchronously start both SMs
    // 1. Drain any stale garbage in FIFOs
    pio_sm_clear_fifos(pio, 0);
    pio_sm_clear_fifos(pio, 1);

    // 2. Restart internal clock dividers & state machine execution state
    pio_enable_sm_mask_in_sync(pio, (1u << 0) | (1u << 1));

    // 3. Enable SMs together synchronously
    pio_set_sm_mask_enabled(pio, (1u << 0) | (1u << 1), true);

    while (1) {
        if (gate_a_hit && gate_b_hit) {
            // SysTick counts DOWN: delta = tick_a - tick_b
            uint32_t cycle_delta = (tick_a - tick_b) & 0x00FFFFFF;

            double ns_delta = cycle_delta * 8.0;
            printf("Flight Delta: %u cycles | %.2f ns (%.3f us)\n",
                   cycle_delta, ns_delta, ns_delta / 1000.0);

            gate_a_hit = false;
            gate_b_hit = false;
        }
        tight_loop_contents();
    }
}
/*#include <stdio.h>*/
/*#include "pico/stdlib.h"*/
/*#include "hardware/pio.h"*/
/*#include "hardware/structs/systick.h"*/
/*#include "laser_timer.pio.h"*/

/*#define GATE_A_PIN 13*/
/*#define GATE_B_PIN 14*/

/*// Enable ARM Cortex-M0+ cycle counter (runs at exact 125MHz / 8ns per count)*/
/*void init_cycle_counter() {*/
    /*systick_hw->csr = M0PLUS_SYST_CSR_ENABLE_BITS | M0PLUS_SYST_CSR_CLKSOURCE_BITS;*/
    /*systick_hw->rvr = 0x00FFFFFF; // 24-bit timer auto-reload*/
/*}*/

/*int main() {*/
    /*stdio_init_all();*/
    /*while (!stdio_usb_connected()) sleep_ms(100);*/

    /*init_cycle_counter();*/
    /*printf("Starting Dual-Gate Timer with 8ns Hardware Cycle Accuracy...\n");*/

    /*PIO pio = pio0;*/

    /*pio_gpio_init(pio, GATE_A_PIN);*/
    /*pio_gpio_init(pio, GATE_B_PIN);*/

    /*uint offset = pio_add_program(pio, &laser_gate_program);*/

    /*// Setup SM0 for Gate A (GPIO 13)*/
    /*pio_sm_config c0 = laser_gate_program_get_default_config(offset);*/
    /*sm_config_set_in_pins(&c0, GATE_A_PIN);*/
    /*pio_sm_init(pio, 0, offset, &c0);*/

    /*// Setup SM1 for Gate B (GPIO 14)*/
    /*pio_sm_config c1 = laser_gate_program_get_default_config(offset);*/
    /*sm_config_set_in_pins(&c1, GATE_B_PIN);*/
    /*pio_sm_init(pio, 1, offset, &c1);*/

    /*// Enable both SMs concurrently*/
    /*pio_set_sm_mask_enabled(pio, (1u << 0) | (1u << 1), true);*/

    /*uint32_t tick_a = 0;*/
    /*uint32_t tick_b = 0;*/

    /*while (1) {*/
        /*// Gate A tripped*/
        /*if (!pio_sm_is_rx_fifo_empty(pio, 0)) {*/
            /*tick_a = systick_hw->cvr; // Read current 8ns hardware cycle register*/
            /*pio_sm_get_blocking(pio, 0);*/
            /*printf("[Gate A] Tripped at Cycle: %u\n", tick_a);*/
        /*}*/

        /*// Gate B tripped*/
        /*if (!pio_sm_is_rx_fifo_empty(pio, 1)) {*/
            /*tick_b = systick_hw->cvr; // Read current 8ns hardware cycle register*/
            /*pio_sm_get_blocking(pio, 1);*/
            /*printf("[Gate B] Tripped at Cycle: %u\n", tick_b);*/
        /*}*/

        /*// Calculate delta when both have triggered*/
        /*if (tick_a != 0 && tick_b != 0) {*/
            /*// SysTick counts DOWN from 0xFFFFFF*/
            /*int32_t cycle_delta = (int32_t)(tick_a - tick_b);*/
            /*if (cycle_delta < 0) cycle_delta += 0x1000000; // Handle 24-bit wrap*/

            /*double ns_delta = cycle_delta * 8.0;*/
            /*printf("--> Flight Delta: %d cycles | %.2f ns (%.3f us)\n\n",*/
                   /*cycle_delta, ns_delta, ns_delta / 1000.0);*/

            /*tick_a = 0;*/
            /*tick_b = 0;*/
        /*}*/
    /*}*/
/*}*/



/*[>#include "pico/stdlib.h"<]*/
/*[>#include "main.h"<]*/
/*[>#include <stdio.h><]*/
/*[>#include <string.h><]*/
/*[>#include <stdlib.h><]*/

/*[>static bool read_line(char *buffer, size_t max_len) {<]*/
    /*[>static size_t idx = 0;<]*/
    /*[>int c = getchar_timeout_us(0);<]*/

    /*[>while (c != PICO_ERROR_TIMEOUT) {<]*/
        /*[>if (c == '\r' || c == '\n') {<]*/
            /*[>if (idx > 0) {<]*/
                /*[>buffer[idx] = '\0';<]*/
                /*[>idx = 0;<]*/
                /*[>return true;<]*/
            /*[>}<]*/
        /*[>} else if (idx < max_len - 1) {<]*/
            /*[>buffer[idx++] = (char)c;<]*/
        /*[>}<]*/
        /*[>c = getchar_timeout_us(0);<]*/
    /*[>}<]*/
    /*[>return false;<]*/
/*[>}<]*/

/*[>int main() {<]*/
    /*[>stdio_init_all();<]*/
    /*[>motor_init();<]*/
    /*[>laser_init();<]*/

    /*[>char buffer[64];<]*/
    /*[>int val = 0;<]*/

    /*[>while (true) {<]*/
        /*[>// Service serial commands non-blockingly<]*/
        /*[>if (read_line(buffer, sizeof(buffer))) {<]*/
            /*[>if (strcmp(buffer, "HOME") == 0) {<]*/
                /*[>motor_start_homing_NOT();<]*/
            /*[>}<]*/
            /*[>else if (sscanf(buffer, "STEPS=%d", &val) == 1) {<]*/
                /*[>motor_set_steps(val);<]*/
            /*[>}<]*/
            /*[>else if (sscanf(buffer, "LASER=%d", &val) == 1) {<]*/
                /*[>laser_onoff(val);<]*/
                /*[>printf("Laser toggled: %d\n", val);<]*/
            /*[>}<]*/
            /*[>else if (strcmp(buffer, "STOP") == 0) {<]*/
                /*[>motor_stop();<]*/
            /*[>}<]*/
        /*[>}<]*/
        /*[>// Service motor hardware tick<]*/
        /*[>motor_tick();<]*/
    /*[>}<]*/
    /*[>return 0;<]*/
/*[>/*}*/
