BUILD_DIR = build
TARGET = main
JOBS = 4

export PICO_SDK_PATH ?= $(CURDIR)/pico-sdk
export CMAKE_PREFIX_PATH ?= /opt/homebrew
export PATH := /opt/homebrew/bin:$(PATH)

PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote

.PHONY: all build clean rebuild flash check

all: build


check:
	@export PICO_TOOLCHAIN_PATH="/opt/homebrew/opt/arm-none-eabi-gcc@9" && \
	export PATH="/opt/homebrew/opt/arm-none-eabi-binutils/bin:/opt/homebrew/opt/arm-none-eabi-gcc@9/bin:$(PATH)" && \
	cmake -B build -S . && \
	cmake --build build

build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake -DPICO_SDK_PATH=$(PICO_SDK_PATH) .. && $(MAKE) -j$(JOBS)

clean:
	@rm -rf $(BUILD_DIR)

rebuild: clean build
