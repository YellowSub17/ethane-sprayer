# Directory settings
BUILD_DIR = build
JOBS = 4

# Target name
TARGET = main

# Export PICO_SDK_PATH relative to Makefile location
export PICO_SDK_PATH ?= $(CURDIR)/pico-sdk

# MicroPython firmware source
MICROPYTHON_URL = https://micropython.org/resources/firmware/RPI_PICO-20240222-v1.22.2.uf2
MICROPYTHON_UF2 = $(BUILD_DIR)/micropython.uf2

# Serial and Virtual Environment settings
PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote

.PHONY: all build clean rebuild flash-c flash-py install-micropython

all: build

build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. && $(MAKE) -j$(JOBS)

clean:
	@rm -rf $(BUILD_DIR)

rebuild: clean build


flash-c: build
	@echo "Rebooting Pico into BOOTSEL mode..."
	@timeout 2s $(VENV_PYTHON) connect $(PORT) bootloader 2>/dev/null || picotool reboot -f -u || true
	@sleep 1.5
	@echo "Flashing C binary ($(TARGET).uf2)..."
	picotool load -x -f $(BUILD_DIR)/$(TARGET).uf2

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


flash-py:
	@if [ ! -e $(PORT) ] || ! timeout 2s $(VENV_PYTHON) connect $(PORT) exec "import sys" 2>/dev/null; then \
		echo "MicroPython REPL not detected on $(PORT). Installing MicroPython firmware..."; \
		$(MAKE) install-micropython; \
	fi
	@echo "Clearing potential serial locks..."
	@sudo fuser -k $(PORT) 2>/dev/null || true
	@sleep 1
	@echo "Uploading main.py to Pico..."
	$(VENV_PYTHON) connect $(PORT) fs cp main.py :main.py
	$(VENV_PYTHON) connect $(PORT) reset
