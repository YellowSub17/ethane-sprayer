cmake_minimum_required(VERSION 3.13)

# Include Pico SDK macros
set(PICO_SDK_PATH "${CMAKE_CURRENT_LIST_DIR}/pico-sdk")
include(pico_sdk_import.cmake)

project(laser_timer C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PICOTOOL_FORCE_FETCH_FROM_GIT ON)

pico_sdk_init()

# 1. Grab all C source files inside src/
file(GLOB SRC_FILES "src/*.c")

# 2. Add executable with main.c + all src/*.c files
add_executable(main
    main.c
    ${SRC_FILES}
)

# 3. Add src/ to the include search paths
target_include_directories(main PRIVATE ${CMAKE_CURRENT_LIST_DIR}/src)

# 4. Generate PIO header file from src/laser_timer.pio
pico_generate_pio_header(main ${CMAKE_CURRENT_LIST_DIR}/src/laser_timer.pio)

# Enable USB stdio output, disable UART
pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 0)

# LINK HARDWARE LIBRARIES HERE
target_link_libraries(main
    pico_stdlib
    hardware_pio
)

# Create map/bin/hex/uf2 file outputs
pico_add_extra_outputs(main)
