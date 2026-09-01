#pragma once
#include "src/pins.h"
void init_cycle_counter();
void blink_led(int n);
void __not_in_flash_func(systick_isr)();
void init_32bit_cycle_counter();
int laser_gate();
void laser_init(void);
void laser_onoff(int laser_01);
void motor_start_homing_POT(void);
void motor_start_homing_NOT(void);
void motor_set_steps(int steps);
void motor_stop(void);
void motor_tick(void);
void motor_init(void);
#define INTERFACE 0
#define EXPORT_INTERFACE 0
#define LOCAL_INTERFACE 0
#define EXPORT
#define LOCAL static
#define PUBLIC
#define PRIVATE
#define PROTECTED
