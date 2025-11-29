#!/bin/bash
#
# Stinercut Media Detector Installation Script
#
# Usage: sudo ./install.sh [API_URL]
#   API_URL - Optional backend API URL (default: http://localhost:8000)
#

set -e

INSTALL_DIR="/opt/stinercut-detector"
SERVICE_NAME="stinercut-detector"
GROUP_NAME="stinercut"
API_URL="${1:-http://localhost:8000}"

# Check for root
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (sudo)"
    exit 1
fi

# Check for python3-venv
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "Error: python3-venv is required but not installed."
    echo "Install it with: sudo apt install python3-venv"
    exit 1
fi

echo "=== Stinercut Media Detector Installation ==="
echo ""

# Create stinercut group for non-root service management
echo "Creating '$GROUP_NAME' group..."
if ! getent group "$GROUP_NAME" > /dev/null 2>&1; then
    groupadd "$GROUP_NAME"
    echo "  Group '$GROUP_NAME' created"
else
    echo "  Group '$GROUP_NAME' already exists"
fi

# Add the user who ran sudo to the group
if [[ -n "$SUDO_USER" ]]; then
    echo "Adding user '$SUDO_USER' to '$GROUP_NAME' group..."
    usermod -aG "$GROUP_NAME" "$SUDO_USER"
    echo "  User '$SUDO_USER' added to '$GROUP_NAME' group"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
cp stinercut_detector.py "$INSTALL_DIR/"
cp config.ini "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# Update API URL in config
if [[ "$API_URL" != "http://localhost:8000" ]]; then
    echo "Setting API URL to: $API_URL"
    sed -i "s|url = http://localhost:8000|url = $API_URL|" "$INSTALL_DIR/config.ini"
fi

# Create Python virtual environment and install dependencies
echo "Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
echo "Installing Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create log directory
echo "Creating log directory..."
mkdir -p /var/log/stinercut
touch /var/log/stinercut/detector.log
chmod 644 /var/log/stinercut/detector.log

# Install systemd service
echo "Installing systemd service..."
cp stinercut-detector.service /etc/systemd/system/

# Install systemd path watcher for remote start trigger
echo "Installing systemd path watcher..."
cp stinercut-detector-watcher.path /etc/systemd/system/
cp stinercut-detector-watcher.service /etc/systemd/system/

# Install polkit rule for non-root service management
echo "Installing polkit rule..."
install -m 644 50-stinercut-detector.rules /etc/polkit-1/rules.d/
# Restart polkit to pick up new rules
systemctl restart polkit

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling service for auto-start..."
systemctl enable "$SERVICE_NAME"

# Enable path watcher
echo "Enabling path watcher..."
systemctl enable stinercut-detector-watcher.path
systemctl start stinercut-detector-watcher.path

# Start service
echo "Starting service..."
systemctl start "$SERVICE_NAME"

# Check status
echo ""
echo "=== Installation Complete ==="
echo ""
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "Service management (no sudo required after re-login):"
echo "  View logs:    journalctl -u $SERVICE_NAME -f"
echo "  Stop:         systemctl stop $SERVICE_NAME"
echo "  Start:        systemctl start $SERVICE_NAME"
echo "  Restart:      systemctl restart $SERVICE_NAME"
echo "  Status:       systemctl status $SERVICE_NAME"
echo ""
if [[ -n "$SUDO_USER" ]]; then
    echo "NOTE: User '$SUDO_USER' must log out and back in for group membership to take effect."
    echo "      Until then, use 'sudo' for service commands."
    echo ""
fi
echo "To add other users to manage the service:"
echo "  sudo usermod -aG $GROUP_NAME <username>"
echo ""
