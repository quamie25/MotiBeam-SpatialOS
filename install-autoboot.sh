#!/bin/bash
# MotiBeam Spatial OS Auto-Boot Installer
# This script sets up MotiBeam to auto-start on boot

set -e

echo "=========================================="
echo "MotiBeam Spatial OS Auto-Boot Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $USER_HOME"
echo ""

# 1. Copy systemd service file
echo "[1/4] Installing systemd service..."
cat > /etc/systemd/system/motibeam.service <<EOF
[Unit]
Description=MotiBeam Spatial OS
After=multi-user.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$USER_HOME/motibeam-spatial-os
Environment="SDL_VIDEODRIVER="
ExecStart=/usr/bin/python3 $USER_HOME/motibeam-spatial-os/spatial_os.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "   ✓ Service file created"

# 2. Enable the service
echo "[2/4] Enabling auto-start..."
systemctl daemon-reload
systemctl enable motibeam.service
echo "   ✓ Auto-start enabled"

# 3. Configure boot to console (skip desktop)
echo "[3/4] Configuring boot to console mode..."
systemctl set-default multi-user.target
echo "   ✓ Console mode configured"

# 4. Disable unnecessary services for faster boot
echo "[4/4] Optimizing boot speed..."
systemctl disable bluetooth.service 2>/dev/null || true
echo "   ✓ Boot optimized"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "MotiBeam Spatial OS will now:"
echo "  • Auto-start on boot"
echo "  • Skip desktop environment"
echo "  • Auto-restart if it crashes"
echo ""
echo "Commands:"
echo "  sudo systemctl start motibeam    - Start now"
echo "  sudo systemctl stop motibeam     - Stop service"
echo "  sudo systemctl status motibeam   - Check status"
echo "  sudo reboot                      - Reboot to test"
echo ""
echo "To revert to desktop mode:"
echo "  sudo systemctl set-default graphical.target"
echo ""
