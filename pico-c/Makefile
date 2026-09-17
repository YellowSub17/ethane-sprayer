BUILD_DIR = build
TARGET = main
JOBS = 4

export PICO_SDK_PATH ?= $(CURDIR)/pico-sdk
export CMAKE_PREFIX_PATH ?= /opt/homebrew
export PATH := /opt/homebrew/bin:$(PATH)

PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote

.PHONY: all build-pi build-mac clean flash headers

all: flash

#headers:
	#@echo "#pragma once" > main.h
	#@echo '#include "src/pins.h"' >> main.h
	#@echo '#include "src/aux.h"' >> main.h
	#@makeheaders -h main.c src/*.c >> main.h


build-mac: headers
	@echo "Building headers..."
	@export PICO_TOOLCHAIN_PATH="/opt/homebrew/opt/arm-none-eabi-gcc@9" && \
	export PATH="/opt/homebrew/opt/arm-none-eabi-binutils/bin:/opt/homebrew/opt/arm-none-eabi-gcc@9/bin:$(PATH)" && \
	cmake -B $(BUILD_DIR) -S . && \
	cmake --build $(BUILD_DIR) -j$(JOBS)

build-pi: #headers
	@echo "Building src..."
	@cmake -B $(BUILD_DIR) -S . -DPICO_SDK_PATH=$(PICO_SDK_PATH) -DPICOTOOL_FORCE_FETCH_FROM_GIT=1
	@cmake --build $(BUILD_DIR) -j$(JOBS)

clean:
	@echo "Deleting build directory."
	@rm -rf $(BUILD_DIR) main.h

flash: build-pi
	@echo "Rebooting Pico into BOOTSEL mode."
	@timeout 2s $(VENV_PYTHON) connect $(PORT) bootloader 2>/dev/null || picotool reboot -f -u 2>/dev/null || true
	@sleep 1.5
	@echo "Flashing C binary ($(TARGET).uf2)"
	@picotool load -x -f $(BUILD_DIR)/$(TARGET).uf2
