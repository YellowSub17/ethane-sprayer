#pragma once

#include "pico/stdlib.h"

// Central Interrupt Handler Typedef
typedef void (*gpio_handler_t)(uint gpio, uint32_t events);
