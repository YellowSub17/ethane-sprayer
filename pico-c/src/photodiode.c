#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "laser_timer.pio.h"

#include "pins.h"
#include "../main.h"

// Each gate has its own PIO state machine running laser_gate. The SM keeps a
// down-counter in X (one tick every 2 sys cycles) and pushes it to its RX FIFO
// when the beam breaks, so timestamps are taken in hardware with no interrupt
// latency. gates_arm() resets all counters to the same value and starts the
// SMs in sync, which makes the timestamps from different gates comparable.

#define NUM_GATES        3
#define CYCLES_PER_TICK  2      // cycles per X decrement in laser_gate

static const PIO gate_pio = pio0;
static const uint gate_pins[NUM_GATES] = {
    PIN_PHOTO_DIODE_1,  // Gate A, SM0
    PIN_PHOTO_DIODE_2,  // Gate B, SM1
    PIN_PHOTO_DIODE_3,  // Gate C, SM2
};
static const uint gate_sm_mask = (1u << NUM_GATES) - 1;
static uint gate_offset;

void photodiode_init() {
    gate_offset = pio_add_program(gate_pio, &laser_gate_program);

    for (uint sm = 0; sm < NUM_GATES; sm++) {
        uint pin = gate_pins[sm];
        gpio_pull_up(pin);
        pio_gpio_init(gate_pio, pin);
        pio_sm_claim(gate_pio, sm);
        pio_sm_set_consecutive_pindirs(gate_pio, sm, pin, 1, false);

        pio_sm_config c = laser_gate_program_get_default_config(gate_offset);
        sm_config_set_in_pins(&c, pin);
        sm_config_set_jmp_pin(&c, pin);
        sm_config_set_fifo_join(&c, PIO_FIFO_JOIN_RX);
        pio_sm_init(gate_pio, sm, gate_offset, &c);
    }
}

// Reset every gate's counter to 0xFFFFFFFF and start all SMs on the same cycle.
// Each SM first waits for its beam to be present, so a gate that is already
// blocked when armed is only captured on its next break.
static void gates_arm(void) {
    pio_set_sm_mask_enabled(gate_pio, gate_sm_mask, false);
    for (uint sm = 0; sm < NUM_GATES; sm++) {
        pio_sm_clear_fifos(gate_pio, sm);
        pio_sm_restart(gate_pio, sm);
        pio_sm_exec(gate_pio, sm, pio_encode_mov_not(pio_x, pio_null));
        pio_sm_exec(gate_pio, sm, pio_encode_jmp(gate_offset + laser_gate_offset_wait_high));
    }
    pio_enable_sm_mask_in_sync(gate_pio, gate_sm_mask);
}

// Wait until every gate in `want` has fired, or timeout_us has passed since
// `start_us` (timeout_us == 0 waits forever). Stores the first timestamp of
// each gate in ts[] and returns the mask of gates that fired.
static uint gates_wait(uint want, uint32_t start_us, uint32_t timeout_us, uint32_t ts[NUM_GATES]) {
    uint hit = 0;
    while ((hit & want) != want) {
        for (uint sm = 0; sm < NUM_GATES; sm++) {
            if (!(hit & (1u << sm)) && !pio_sm_is_rx_fifo_empty(gate_pio, sm)) {
                ts[sm] = pio_sm_get(gate_pio, sm);
                hit |= 1u << sm;
            }
        }
        if (timeout_us && (uint32_t)(time_us_32() - start_us) >= timeout_us) break;
    }
    return hit;
}

// Cycles from gate `from` to gate `to`. X counts down, so a later hit has a
// smaller value. Negative means `to` fired first. Valid for |delay| < ~34 s.
static int64_t gate_delay_cycles(const uint32_t ts[NUM_GATES], uint from, uint to) {
    return (int64_t)(int32_t)(ts[from] - ts[to]) * CYCLES_PER_TICK;
}

static double ns_per_cycle(void) {
    return 1e9 / clock_get_hz(clk_sys);
}

// Pulse the N2 valve for open_us (exact busy-wait, max 20 ms)
static uint32_t pulse_valve(uint32_t open_us) {
    if (open_us > 20000) open_us = 20000;

    printf("PV: enter open_us=%u func=%d dir=%d\n",
           open_us, gpio_get_function(PIN_VALVE_3), gpio_get_dir(PIN_VALVE_3));
    fflush(stdout);

    uint32_t t0 = time_us_32();
    gpio_put(PIN_VALVE_3, 1);
    while ((uint32_t)(time_us_32() - t0) < open_us) tight_loop_contents();
    gpio_put(PIN_VALVE_3, 0);
    uint32_t t1 = time_us_32();

    printf("PV: done, actual=%u us\n", t1 - t0);
    fflush(stdout);
    return t0;
}

        //prototype jet timing sequence
int jet_timing_sequence_AB(uint32_t open_us, uint32_t timeout_ms) {
    laser_onoff(1); // Turn on the laser for the timing sequence
    sleep_ms(100); // Give the laser a moment to stabilize
    uint32_t ts[NUM_GATES];
    gates_arm();
    uint32_t t0 = pulse_valve(open_us);
    uint hit = gates_wait(0b011, t0, timeout_ms * 1000, ts);

    if ((hit & 0b011) == 0b011) {
        int64_t AB = gate_delay_cycles(ts, 0, 1);
        printf("JET_RESULT:\tA_to_B=%lld cycles\tA_to_B_ns=%.1f\tABus=%.6fms\n",
               AB, AB * ns_per_cycle(), AB*ns_per_cycle()*1e6);
    } else {
        printf("JET_TIMEOUT hitA=%d hitB=%d\n", !!(hit & 1), !!(hit & 2));
    }
    laser_onoff(0); // Turn off the laser after the timing sequence
    stdio_flush();
    return 0;
}

        //prototype jet timing sequence
int jet_timing_sequence(uint32_t open_us, uint32_t timeout_ms) {
    uint32_t ts[NUM_GATES];
    gates_arm();
    uint32_t t0 = pulse_valve(open_us);
    uint hit = gates_wait(0b111, t0, timeout_ms * 1000, ts);

    if (hit == 0b111) {
        double ns = ns_per_cycle();
        int64_t AB = gate_delay_cycles(ts, 0, 1);
        int64_t BC = gate_delay_cycles(ts, 1, 2);
        printf("JET_RESULT A_to_B=%lld B_to_C=%lld cycles ns_per_cycle=%.3f A_to_B_ns=%.1f B_to_C_ns=%.1f\n",
               AB, BC, ns, AB * ns, BC * ns);
    } else {
        printf("JET_TIMEOUT hitA=%d hitB=%d hitC=%d\n", !!(hit & 1), !!(hit & 2), !!(hit & 4));
    }
    stdio_flush();
    return 0;
}

int measure_gatesABC() {
    uint32_t ts[NUM_GATES];
    gates_arm();
    gates_wait(0b111, 0, 0, ts);    // waits forever

    double ns = ns_per_cycle();
    int64_t diffBA = gate_delay_cycles(ts, 0, 1);
    int64_t diffCB = gate_delay_cycles(ts, 1, 2);

    printf("A-to-B Delta: %lld cycles\t%.2f ns\t(%.3f us)\n",
           diffBA, diffBA * ns, diffBA * ns / 1000.0);
    printf("B-to-C Delta: %lld cycles\t%.2f ns\t(%.3f us)\n",
           diffCB, diffCB * ns, diffCB * ns / 1000.0);
    stdio_flush();
    return 0;
}

int measure_gatesAB() {
    uint32_t ts[NUM_GATES];
    gates_arm();
    gates_wait(0b011, 0, 0, ts);    // waits forever

    double ns = ns_per_cycle();
    int64_t diffBA = gate_delay_cycles(ts, 0, 1);

    printf("A-to-B Delta: %lld cycles\t%.2f ns\t%.3f us\t%.6f s\n",
           diffBA, diffBA * ns, diffBA * ns / 1000.0, diffBA * ns / 1e9);
    stdio_flush();
    return 0;
}
