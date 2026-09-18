#pragma once
#include "src/pins.h"

#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"  // Provides uint, gpio_irq_callback_t, etc.

// Define the missing callback type used by your IRQ dispatcher
typedef void (*gpio_handler_t)(uint gpio, uint32_t events);
// Function declarations
void gpio_register_handler(uint gpio, uint32_t events, gpio_handler_t handler);
bool motor_enable(void);
void core1_entry();
void blink_led(int n);
void gpio_interrupts_init(void);
void gpio_register_handler(uint gpio,uint32_t events,gpio_handler_t handler);
void gpio_register_handler(uint gpio,uint32_t events,gpio_handler_t handler);
void laser_init(void);
void laser_onoff(int laser_01);
void motor_start_homing_POT(void);
void motor_start_homing_NOT(void);
void motor_set_steps(int steps);
void motor_stop(void);
bool motor_enable(void);
void motor_disable(void);
void motor_init(void);
void motor_tick(void);
void valve_init(void); //new
void valve1(void);      //new
void isr_systick();
void pio_irq_handler();
void init_cycle_counter();
void photodiode_init();
int measure_gatesABC();
int measure_gatesAB();
#define INTERFACE 0
#define EXPORT_INTERFACE 0
#define LOCAL_INTERFACE 0
#define EXPORT
#define LOCAL static
#define PUBLIC
#define PRIVATE
#define PROTECTED
