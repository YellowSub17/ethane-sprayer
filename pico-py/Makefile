PORT ?= /dev/ttyACM0
VENV_PYTHON = ../venv/bin/mpremote
MICROPYTHON_URL = https://micropython.org/resources/firmware/RPI_PICO-20240222-v1.22.2.uf2
FIRMWARE_UF2 = micropython.uf2

.PHONY: flash install-firmware clean

flash:
	@if [ ! -e $(PORT) ] || ! timeout 2s $(VENV_PYTHON) connect $(PORT) exec "import sys" 2>/dev/null; then \
		echo "MicroPython REPL not found. Installing MicroPython firmware..."; \
		$(MAKE) install-firmware; \
	fi
	@echo "Uploading all Python scripts to Pico..."
	@for f in *.py; do \
		echo "Copying $$f..."; \
		$(VENV_PYTHON) connect $(PORT) fs cp $$f :$$f; \
	done
	$(VENV_PYTHON) connect $(PORT) reset

install-firmware:
	@if [ ! -f $(FIRMWARE_UF2) ]; then \
		echo "Downloading MicroPython firmware..."; \
		wget -q -O $(FIRMWARE_UF2) $(MICROPYTHON_URL); \
	fi
	@echo "Rebooting Pico into BOOTSEL mode..."
	@picotool reboot -f -u 2>/dev/null || true
	@sleep 1
	@echo "Flashing MicroPython firmware..."
	picotool load -x -f $(FIRMWARE_UF2)
	@sleep 3

clean:
	@echo "Clearing board MicroPython filesystem..."
	@$(VENV_PYTHON) connect $(PORT) fs rm :main.py 2>/dev/null || true
	@$(VENV_PYTHON) connect $(PORT) fs rm :blink.py 2>/dev/null || true
