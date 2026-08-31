#pragma once
#include "src/pins.h"
void other_function();
void hello_world(void);
void blink_led(void);
void __not_in_flash_func(systick_isr)();
void init_32bit_cycle_counter();
int laser_gate();
void motor_init(void);
void motor_step(int steps);
#define INTERFACE 0
#define EXPORT_INTERFACE 0
#define LOCAL_INTERFACE 0
#define EXPORT
#define LOCAL static
#define PUBLIC
#define PRIVATE
#define PROTECTED
