#!/bin/bash
# RabbitMirror Virtual Environment Activation Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Show activation message
echo "🐰 RabbitMirror virtual environment activated!"
echo "📍 Project directory: $SCRIPT_DIR"
echo "🔧 Python: $(which python)"
echo "🎯 RabbitMirror: $(which rabbitmirror)"
echo ""
echo "💡 You can now run:"
echo "   rabbitmirror tui          # Launch TUI"
echo "   rabbitmirror --help       # Show help"
echo "   deactivate                # Exit virtual environment"
echo ""
