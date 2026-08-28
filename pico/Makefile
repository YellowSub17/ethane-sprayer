# Directory settings
BUILD_DIR = build
JOBS = 4

# Target name (adjust if your target executable in CMakeLists.txt is different)
TARGET = main

# MicroPython firmware source
MICROPYTHON_URL = https://micropython.org/resources/firmware/RPI_PICO-20240222-v1.22.2.uf2
MICROPYTHON_UF2 = $(BUILD_DIR)/micropython.uf2

# Serial and Virtual Environment settings
PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote

.PHONY: all build clean rebuild flash-c flash-py install-micropython

# Default target when typing 'make'
all: build

# Create build folder, configure CMake, and compile C code
build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. && $(MAKE) -j$(JOBS)

# Clean out the build artifacts
clean:
	@rm -rf $(BUILD_DIR)

# Wipe build directory and do a fresh build
rebuild: clean build

# ------------------------------------------------------------------------------
# C Flashing Workflow
# ------------------------------------------------------------------------------

# Flash the compiled C UF2 file to the Pico (forces reboot into BOOTSEL mode if running)
flash-c: build
	@echo "Flashing C binary ($(TARGET).uf2)..."
	@picotool reboot -f -u || true
	@sleep 1
	picotool load -x -f $(BUILD_DIR)/$(TARGET).uf2

# ------------------------------------------------------------------------------
# MicroPython Flashing Workflow
# ------------------------------------------------------------------------------


# Download and load MicroPython interpreter onto the Pico
install-micropython:
	@mkdir -p $(BUILD_DIR)
	@if [ ! -f $(MICROPYTHON_UF2) ]; then \
		echo "Downloading MicroPython firmware..."; \
		wget -q -O $(MICROPYTHON_UF2) $(MICROPYTHON_URL); \
	fi
	@echo "Rebooting Pico into BOOTSEL mode..."
	@picotool reboot -f -u || true
	@sleep 1
	@echo "Flashing MicroPython firmware..."
	picotool load -x -f $(MICROPYTHON_UF2)
	@echo "Waiting for USB serial interface (/dev/ttyACM0) to initialize..."
	@sleep 3

# Upload main.py via mpremote (auto-installs MicroPython if missing)
flash-py:
	@if [ ! -e $(PORT) ]; then \
		echo "Port $(PORT) not found. Installing MicroPython firmware first..."; \
		$(MAKE) install-micropython; \
	fi
	@echo "Clearing potential serial locks..."
	@sudo fuser -k $(PORT) 2>/dev/null || true
	@sleep 1
	@echo "Uploading main.py to Pico..."
	$(VENV_PYTHON) connect $(PORT) fs cp main.py :main.py
	$(VENV_PYTHON) connect $(PORT) soft-reset

