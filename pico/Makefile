# Directory settings
BUILD_DIR = build
JOBS = 4

# Target name (adjust if your target executable in CMakeLists.txt is different)
TARGET = main

# Detect mounted Pico directory (works across standard Ubuntu/Debian paths)
PICO_MOUNT ?= $(shell find /media/ /mnt/ -maxdepth 3 -name "RPI-RP2" 2>/dev/null | head -n 1)

.PHONY: all build clean rebuild flash

# Default target when typing 'make'
all: build

# Create build folder, configure CMake, and compile
build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. && $(MAKE) -j$(JOBS)

# Flash the compiled UF2 file to the Pico if in BOOTSEL mode
flash: build
	picotool load -f $(BUILD_DIR)/$(TARGET).uf2

# Clean out the build artifacts
clean:
	@rm -rf $(BUILD_DIR)

# Wipe build directory and do a fresh build
rebuild: clean build
