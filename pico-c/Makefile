BUILD_DIR = build
TARGET = main
JOBS = 4

export PICO_SDK_PATH ?= $(CURDIR)/pico-sdk
export PICOTOOL_FORCE_FETCH_FROM_GIT = 1

PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote

.PHONY: all build clean rebuild flash

all: build

build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. && $(MAKE) -j$(JOBS)

clean:
	@rm -rf $(BUILD_DIR)

rebuild: clean build

flash: build
	@echo "Rebooting Pico into BOOTSEL mode..."
	@timeout 2s $(VENV_PYTHON) connect $(PORT) bootloader 2>/dev/null || picotool reboot -f -u 2>/dev/null || true
	@sleep 1.5
	@echo "Flashing C binary ($(TARGET).uf2)..."
	picotool load -x -f $(BUILD_DIR)/$(TARGET).uf2
