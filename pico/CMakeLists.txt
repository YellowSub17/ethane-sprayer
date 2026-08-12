cmake_minimum_required(VERSION 3.13)

# 1. Explicitly tell CMake where the SDK lives before initializing it
set(PICO_SDK_PATH "${CMAKE_CURRENT_LIST_DIR}/pico-sdk")

# 2. Include the SDK's internal setup script directly
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(ethan_sprayer_pico C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Disable picotool auto-build
#set(PICO_NO_PICOTOOL 1)

# 3. Initialize the SDK
pico_sdk_init()

# 4. Define your executable and linked libraries
add_executable(pico_firmware main.c)

target_link_libraries(pico_firmware
    pico_stdlib
    pico_multicore
    hardware_uart
    hardware_gpio
)

pico_enable_stdio_usb(pico_firmware 1)
pico_enable_stdio_uart(pico_firmware 0)

pico_add_extra_outputs(pico_firmware)
