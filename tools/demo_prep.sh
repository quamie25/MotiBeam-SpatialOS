#!/bin/bash
# MotiBeam demo prep — run ON each Pi (Nov 2026, MacroFab demo).
#
#   curl -sL https://raw.githubusercontent.com/quamie25/motibeam-spatialos/main/tools/demo_prep.sh -o /tmp/demo_prep.sh
#   bash /tmp/demo_prep.sh                # autostart + display report
#   bash /tmp/demo_prep.sh "HotspotName"  # also join phone hotspot (prompts for its password)
#
# Does three things:
#   1. Installs desktop autostart for MotiBeam Spatial OS (survives reboot).
#   2. Prints a display report (resolution/overscan) to diagnose off-center projection.
#   3. Optionally joins a phone hotspot and remembers it (for the demo venue).
# Additive only — changes nothing else. Safe to re-run.

set -u

echo "======================================"
echo "  MotiBeam Demo Prep — $(hostname)"
echo "======================================"

# ── Locate the repo ───────────────────────────────────────────────────────────
LAUNCHER="$(find "$HOME" -maxdepth 3 -name run_pygame.sh -path "*spatialos*" 2>/dev/null | head -1)"
[ -z "$LAUNCHER" ] && LAUNCHER="$(find "$HOME" -maxdepth 3 -name run_pygame.sh 2>/dev/null | head -1)"
if [ -z "$LAUNCHER" ]; then
    echo "✗ Could not find run_pygame.sh under $HOME — is the MotiBeam repo cloned?"
    exit 1
fi
REPO_DIR="$(dirname "$LAUNCHER")"
chmod +x "$LAUNCHER" 2>/dev/null
echo "✓ MotiBeam repo: $REPO_DIR"

# ── 1. Autostart ──────────────────────────────────────────────────────────────
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/motibeam.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=MotiBeam Spatial OS
Comment=Launch MotiBeam projection OS at login
Exec=/bin/bash $LAUNCHER
Path=$REPO_DIR
X-GNOME-Autostart-enabled=true
EOF
echo "✓ Autostart installed: ~/.config/autostart/motibeam.desktop"

# Desktop autologin so the autostart actually fires on boot
if command -v raspi-config >/dev/null 2>&1; then
    if sudo -n true 2>/dev/null || sudo -v; then
        sudo raspi-config nonint do_boot_behaviour B4 2>/dev/null \
            && echo "✓ Boot set to: Desktop, auto-login" \
            || echo "⚠ Could not set desktop autologin (set via: sudo raspi-config → System → Boot/Auto Login → Desktop Autologin)"
    fi
else
    echo "⚠ raspi-config not found — ensure boot goes to desktop with auto-login"
fi

# ── 2. Display report ─────────────────────────────────────────────────────────
echo ""
echo "── Display report (paste this back) ──"
echo "User: $USER  ·  Model: $(tr -d '\0' </proc/device-tree/model 2>/dev/null || echo unknown)"
export DISPLAY="${DISPLAY:-:0}"
if command -v xrandr >/dev/null 2>&1 && xrandr >/dev/null 2>&1; then
    xrandr | grep -E "connected|\*" | sed 's/^/  /'
else
    echo "  (xrandr unavailable — Wayland or no X session from SSH)"
    command -v wlr-randr >/dev/null 2>&1 && wlr-randr 2>/dev/null | sed 's/^/  /'
fi
for CFG in /boot/firmware/config.txt /boot/config.txt; do
    if [ -f "$CFG" ]; then
        echo "  $CFG (display lines):"
        grep -E "^(hdmi_|disable_overscan|overscan_|framebuffer_|dtoverlay=vc4)" "$CFG" | sed 's/^/    /' || echo "    (none set)"
        break
    fi
done
grep -nE "SCREEN_WIDTH|SCREEN_HEIGHT" "$REPO_DIR/spatial_os.py" 2>/dev/null | head -2 | sed 's/^/  spatial_os.py: /'

# ── 3. Optional: join phone hotspot ──────────────────────────────────────────
if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
    SSID="$1"
    echo ""
    echo "── Joining hotspot: $SSID ──"
    if command -v nmcli >/dev/null 2>&1; then
        sudo nmcli device wifi rescan 2>/dev/null; sleep 3
        if sudo nmcli --ask device wifi connect "$SSID"; then
            sudo nmcli connection modify "$SSID" connection.autoconnect yes \
                connection.autoconnect-priority 20 2>/dev/null
            echo "✓ Joined and remembered '$SSID' (high priority — will auto-join at the venue)"
        else
            echo "✗ Join failed — check the hotspot is on and the password"
        fi
    else
        echo "⚠ nmcli not found (older OS) — add the hotspot via: sudo raspi-config → System → Wireless LAN"
    fi
fi

echo ""
echo "Done. Reboot to test autostart:  sudo reboot"
