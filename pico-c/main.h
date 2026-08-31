#pragma once
#include "src/pins.h"
void blink_led(int n);
void __not_in_flash_func(systick_isr)();
void init_32bit_cycle_counter();
int laser_gate();
void laser_init(void);
void laser_onoff(int laser_01);
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
