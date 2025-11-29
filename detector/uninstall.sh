#!/bin/bash
#
# Stinercut Media Detector Uninstallation Script
#
# Usage: sudo ./uninstall.sh [--purge]
#   --purge  Also remove logs and stinercut group
#

set -e

INSTALL_DIR="/opt/stinercut-detector"
SERVICE_NAME="stinercut-detector"
GROUP_NAME="stinercut"
LOG_DIR="/var/log/stinercut"
PURGE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --purge)
            PURGE=true
            shift
            ;;
    esac
done

# Check for root
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (sudo)"
    exit 1
fi

echo "=== Stinercut Media Detector Uninstallation ==="
echo ""
echo "This will remove:"
echo "  - systemd service: $SERVICE_NAME"
echo "  - polkit rule: 50-stinercut-detector.rules"
echo "  - installation directory: $INSTALL_DIR"
if [[ "$PURGE" == true ]]; then
    echo "  - log directory: $LOG_DIR"
    echo "  - group: $GROUP_NAME"
fi
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Stop service
echo "Stopping service..."
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl stop "$SERVICE_NAME"
    echo "  Service stopped"
else
    echo "  Service not running"
fi

# Disable service
echo "Disabling service..."
if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl disable "$SERVICE_NAME"
    echo "  Service disabled"
else
    echo "  Service not enabled"
fi

# Remove systemd service file
echo "Removing systemd service file..."
if [[ -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
    rm "/etc/systemd/system/$SERVICE_NAME.service"
    echo "  Removed /etc/systemd/system/$SERVICE_NAME.service"
else
    echo "  Service file not found"
fi

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Remove polkit rule
echo "Removing polkit rule..."
if [[ -f "/etc/polkit-1/rules.d/50-stinercut-detector.rules" ]]; then
    rm "/etc/polkit-1/rules.d/50-stinercut-detector.rules"
    echo "  Removed /etc/polkit-1/rules.d/50-stinercut-detector.rules"
else
    echo "  Polkit rule not found"
fi

# Remove installation directory
echo "Removing installation directory..."
if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    echo "  Removed $INSTALL_DIR"
else
    echo "  Installation directory not found"
fi

# Purge mode: remove logs and group
if [[ "$PURGE" == true ]]; then
    echo "Removing log directory..."
    if [[ -d "$LOG_DIR" ]]; then
        rm -rf "$LOG_DIR"
        echo "  Removed $LOG_DIR"
    else
        echo "  Log directory not found"
    fi

    echo "Removing group..."
    if getent group "$GROUP_NAME" > /dev/null 2>&1; then
        groupdel "$GROUP_NAME"
        echo "  Removed group '$GROUP_NAME'"
    else
        echo "  Group '$GROUP_NAME' not found"
    fi
fi

echo ""
echo "=== Uninstallation Complete ==="
echo ""
if [[ "$PURGE" != true ]]; then
    echo "Note: Logs and '$GROUP_NAME' group were preserved."
    echo "      Run with --purge to remove them as well."
    echo ""
fi
