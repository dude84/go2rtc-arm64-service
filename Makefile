.PHONY: update run stop restart service-install service-uninstall status

# Variables
BINARY = ./bin/go2rtc
CONFIG = ./bin/go2rtc.yaml
GO2RTC_URL = https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64
SERVICE_NAME = go2rtc
SERVICE_TEMPLATE = go2rtc.service
WORKING_DIR = $(shell pwd)

# Download and update go2rtc binary
update:
	@echo "Downloading latest go2rtc for ARM64..."
	@mkdir -p bin
	@wget $(GO2RTC_URL) -O $(BINARY)
	@chmod +x $(BINARY)
	@echo "✓ go2rtc updated successfully"

# Run go2rtc as daemon
run:
	@if pgrep -x go2rtc > /dev/null; then \
		echo "go2rtc is already running"; \
		exit 1; \
	fi
	@echo "Starting go2rtc daemon..."
	@$(BINARY) -c $(CONFIG) -d
	@sleep 1
	@if pgrep -x go2rtc > /dev/null; then \
		echo "✓ go2rtc started successfully"; \
	else \
		echo "✗ Failed to start go2rtc"; \
		exit 1; \
	fi

# Stop go2rtc daemon
stop:
	@if pgrep -x go2rtc > /dev/null; then \
		echo "Stopping go2rtc..."; \
		pkill -x go2rtc; \
		sleep 1; \
		if pgrep -x go2rtc > /dev/null; then \
			echo "✗ Failed to stop go2rtc gracefully, forcing..."; \
			pkill -9 -x go2rtc; \
		fi; \
		echo "✓ go2rtc stopped"; \
	else \
		echo "go2rtc is not running"; \
	fi

# Restart go2rtc daemon
restart: stop
	@sleep 1
	@$(MAKE) run

# Check status of go2rtc
status:
	@if pgrep -x go2rtc > /dev/null; then \
		echo "go2rtc is running (PID: $$(pgrep -x go2rtc))"; \
	else \
		echo "go2rtc is not running"; \
	fi

# Install systemd service
service-install:
	@echo "Installing go2rtc systemd service..."
	@if [ ! -f $(BINARY) ]; then \
		echo "✗ Binary not found. Run 'make update' first."; \
		exit 1; \
	fi
	@if [ ! -f $(SERVICE_TEMPLATE) ]; then \
		echo "✗ Service template not found: $(SERVICE_TEMPLATE)"; \
		exit 1; \
	fi
	@sed -e 's|USER_PLACEHOLDER|$(USER)|g' \
	     -e 's|WORKING_DIR_PLACEHOLDER|$(WORKING_DIR)|g' \
	     $(SERVICE_TEMPLATE) | sudo tee /etc/systemd/system/$(SERVICE_NAME).service > /dev/null
	@sudo systemctl daemon-reload
	@sudo systemctl enable $(SERVICE_NAME)
	@sudo systemctl start $(SERVICE_NAME)
	@echo "✓ Service installed, enabled, and started"
	@echo "  Check status: sudo systemctl status $(SERVICE_NAME)"

# Uninstall systemd service
service-uninstall:
	@echo "Uninstalling go2rtc systemd service..."
	@if [ -f /etc/systemd/system/$(SERVICE_NAME).service ]; then \
		sudo systemctl stop $(SERVICE_NAME) 2>/dev/null || true; \
		sudo systemctl disable $(SERVICE_NAME) 2>/dev/null || true; \
		sudo rm /etc/systemd/system/$(SERVICE_NAME).service; \
		sudo systemctl daemon-reload; \
		echo "✓ Service uninstalled"; \
	else \
		echo "Service not installed"; \
	fi

# Help target
help:
	@echo "Available targets:"
	@echo "  make update            - Download latest go2rtc binary"
	@echo "  make run               - Start go2rtc as daemon"
	@echo "  make stop              - Stop go2rtc daemon"
	@echo "  make restart           - Restart go2rtc daemon"
	@echo "  make status            - Check if go2rtc is running"
	@echo "  make service-install   - Install systemd service (requires sudo)"
	@echo "  make service-uninstall - Remove systemd service (requires sudo)"
	@echo "  make help              - Show this help message"
