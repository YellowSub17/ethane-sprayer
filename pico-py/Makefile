BUILD_DIR = build
PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote
MICROPYTHON_URL = https://micropython.org/resources/firmware/RPI_PICO-20240222-v1.22.2.uf2
FIRMWARE_UF2 = $(BUILD_DIR)/micropython.uf2

.PHONY: flash install-firmware clean

flash:
	@if [ ! -e $(PORT) ] || ! timeout 2s $(VENV_PYTHON) connect $(PORT) exec "import sys" 2>/dev/null; then \
		echo "MicroPython REPL not found. Installing MicroPython firmware..."; \
		$(MAKE) install-firmware; \
	fi
	@echo "Uploading Python scripts..."
	@$(VENV_PYTHON) connect $(PORT) fs mkdir :src 2>/dev/null || true
	@$(VENV_PYTHON) connect $(PORT) fs cp main.py :main.py
	@for f in src/*.py; do \
		[ -e "$$f" ] || continue; \
		echo "Copying $$f to :src/..."; \
		$(VENV_PYTHON) connect $(PORT) fs cp $$f :src/$$(basename $$f); \
	done
	@echo "Resetting Pico into script execution..."
	@$(VENV_PYTHON) connect $(PORT) exec "import machine; machine.reset()" 2>/dev/null || true

install-firmware:
	@mkdir -p $(BUILD_DIR)
	@if [ ! -f $(FIRMWARE_UF2) ]; then \
		echo "Downloading MicroPython firmware to $(BUILD_DIR)..."; \
		wget -q -O $(FIRMWARE_UF2) $(MICROPYTHON_URL); \
	fi
	@echo "Rebooting Pico into BOOTSEL mode..."
	@timeout 2s $(VENV_PYTHON) connect $(PORT) bootloader 2>/dev/null || picotool reboot -f -u 2>/dev/null || true
	@sleep 1.5
	@echo "Flashing MicroPython firmware..."
	picotool load -f $(FIRMWARE_UF2)
	@echo "Rebooting Pico to launch MicroPython..."
	picotool reboot -f
	@sleep 3

clean:
	@rm -rf $(BUILD_DIR)
