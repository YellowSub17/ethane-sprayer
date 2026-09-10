cmake_minimum_required(VERSION 3.13)

# 1. Include Pico SDK import macro FIRST
include(pico_sdk_import.cmake)

# 2. Declare project
project(laser_timer C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# DELETE OR COMMENT OUT THIS LINE:
# set(PICOTOOL_FORCE_FETCH_FROM_GIT ON)

# 3. Initialize SDK
pico_sdk_init()

# 4. Source files & Includes
file(GLOB SRC_FILES "src/*.c")

# Treat implicit function declarations and missing headers as hard errors
add_compile_options($<$<COMPILE_LANGUAGE:C>:-Werror=implicit-function-declaration>)

add_executable(main
    main.c
    ${SRC_FILES}
)


target_include_directories(main PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/src
)

# 5. PIO Headers
pico_generate_pio_header(main ${CMAKE_CURRENT_LIST_DIR}/src/laser_timer.pio)

# 6. Stdio & Libraries
pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 0)

target_link_libraries(main
    pico_stdlib
    hardware_pio
    pico_multicore
    hardware_exception
)


# 7. Outputs (.uf2, .elf, etc.)
pico_add_extra_outputs(main)
