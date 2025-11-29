.PHONY: help setup start-backend start-iot start-mobile train-ml test clean

help:
	@echo "Privacy-Focused Digital Wellbeing System - Make Commands"
	@echo "========================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Run full project setup"
	@echo "  make install-mqtt   - Install MQTT broker (requires sudo)"
	@echo ""
	@echo "Development:"
	@echo "  make start-backend  - Start backend API server"
	@echo "  make start-iot      - Start IoT device client"
	@echo "  make start-mobile   - Start mobile app"
	@echo "  make start-all      - Start all services (use tmux)"
	@echo ""
	@echo "AI/ML:"
	@echo "  make train-ml       - Train notification classifier"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Test backend only"
	@echo "  make test-iot       - Test IoT device only"
	@echo "  make test-mobile    - Test mobile app only"
	@echo ""
	@echo "Utilities:"
	@echo "  make mqtt-listen    - Listen to all MQTT messages"
	@echo "  make mqtt-test      - Test MQTT connection"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make docs           - Open documentation"
	@echo ""

setup:
	@echo "🚀 Running setup script..."
	@./setup.sh

install-mqtt:
	@echo "📡 Installing MQTT broker..."
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo apt update && sudo apt install -y mosquitto mosquitto-clients; \
		sudo systemctl start mosquitto; \
		sudo systemctl enable mosquitto; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		brew install mosquitto; \
		brew services start mosquitto; \
	else \
		echo "Unsupported OS. Please install Mosquitto manually."; \
	fi

start-backend:
	@echo "🔧 Starting Backend API..."
	@cd backend-api && source venv/bin/activate && python app/main.py

start-iot:
	@echo "🤖 Starting IoT Device..."
	@cd iot-device && source venv/bin/activate && python mqtt_client.py

start-mobile:
	@echo "📱 Starting Mobile App..."
	@cd mobile-app && npm start

start-all:
	@echo "🚀 Starting all services..."
	@echo "Note: This requires tmux to be installed"
	@tmux new-session -d -s wellbeing 'cd backend-api && source venv/bin/activate && python app/main.py'
	@tmux split-window -h 'cd iot-device && source venv/bin/activate && python mqtt_client.py'
	@tmux split-window -v 'cd mobile-app && npm start'
	@tmux attach-session -t wellbeing

train-ml:
	@echo "🧠 Training ML models..."
	@cd ai-models && source venv/bin/activate && python training/train_notification_classifier.py

test:
	@echo "🧪 Running all tests..."
	@make test-backend
	@make test-iot

test-backend:
	@echo "Testing backend..."
	@cd backend-api && source venv/bin/activate && pytest

test-iot:
	@echo "Testing IoT device..."
	@cd iot-device && source venv/bin/activate && pytest

test-mobile:
	@echo "Testing mobile app..."
	@cd mobile-app && npm test

mqtt-listen:
	@echo "👂 Listening to all MQTT messages (Ctrl+C to stop)..."
	@mosquitto_sub -h localhost -t "wellbeing/#" -v

mqtt-test:
	@echo "📤 Testing MQTT connection..."
	@mosquitto_pub -h localhost -t "wellbeing/test" -m "Hello from Makefile"
	@echo "✅ Message sent. Check mqtt-listen to verify."

clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend-api/app/__pycache__ 2>/dev/null || true
	@rm -rf iot-device/__pycache__ 2>/dev/null || true
	@echo "✅ Cleaned!"

docs:
	@echo "📚 Opening documentation..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open docs/PROJECT_SUMMARY.md; \
	elif command -v open > /dev/null; then \
		open docs/PROJECT_SUMMARY.md; \
	else \
		cat docs/PROJECT_SUMMARY.md; \
	fi

check-status:
	@echo "System Status Check"
	@echo "==================="
	@echo ""
	@echo -n "Python 3: "
	@python3 --version 2>/dev/null && echo "✅" || echo "❌ Not found"
	@echo -n "Node.js: "
	@node --version 2>/dev/null && echo "✅" || echo "❌ Not found"
	@echo -n "npm: "
	@npm --version 2>/dev/null && echo "✅" || echo "❌ Not found"
	@echo -n "MQTT Broker: "
	@mosquitto -h 2>/dev/null | head -1 && echo "✅" || echo "❌ Not found"
	@echo ""
	@echo -n "Backend venv: "
	@[ -d "backend-api/venv" ] && echo "✅" || echo "❌ Not setup"
	@echo -n "IoT venv: "
	@[ -d "iot-device/venv" ] && echo "✅" || echo "❌ Not setup"
	@echo -n "AI venv: "
	@[ -d "ai-models/venv" ] && echo "✅" || echo "❌ Not setup"
	@echo -n "Mobile node_modules: "
	@[ -d "mobile-app/node_modules" ] && echo "✅" || echo "❌ Not setup"
