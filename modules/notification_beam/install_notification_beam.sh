#!/usr/bin/env bash
# MotiBeam Notification Beam — one-paste installer.
#
# Usage (on the Pi, as user motibeam):
#   bash install_notification_beam.sh              # listener only (safe base)
#   bash install_notification_beam.sh --iphone     # + ancs4linux (iPhone via BLE/ANCS)
#   bash install_notification_beam.sh --android    # + KDE Connect (Android via Wi-Fi)
#   bash install_notification_beam.sh --test       # send a fake notification at the listener
#
# Installs NOTHING into spatial_os. The wall-card render hook is applied
# separately, by hand, during the joint session (see README.md).
set -euo pipefail

WANT_IPHONE=0
WANT_ANDROID=0
DO_TEST=0
for arg in "$@"; do
  case "$arg" in
    --iphone)  WANT_IPHONE=1 ;;
    --android) WANT_ANDROID=1 ;;
    --test)    DO_TEST=1 ;;
    *) echo "unknown flag: $arg"; exit 1 ;;
  esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/motibeam-notifications.service"

echo "== Notification Beam installer =="
echo "module dir: $REPO_DIR"

if [ "$DO_TEST" = "1" ]; then
  echo "-- sending test notification"
  command -v notify-send >/dev/null || sudo apt-get install -y libnotify-bin
  notify-send "Mike Martin" "This is what an iPhone text will look like on the wall."
  sleep 1
  echo "-- spool contents:"
  cat /tmp/motibeam_notifications/queue.json 2>/dev/null || echo "(spool empty — is the service running?)"
  exit 0
fi

echo "-- installing base dependencies (python3-dbus, python3-gi)"
sudo apt-get update -qq
sudo apt-get install -y python3-dbus python3-gi libnotify-bin

echo "-- installing systemd user service"
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=MotiBeam Notification Beam listener
After=graphical-session.target

[Service]
ExecStart=/usr/bin/python3 $REPO_DIR/notification_listener.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now motibeam-notifications.service
sleep 1
systemctl --user --no-pager status motibeam-notifications.service || true

if [ "$WANT_IPHONE" = "1" ]; then
  echo "-- installing ancs4linux (iPhone / ANCS over BLE)"
  sudo apt-get install -y python3-pip bluez
  sudo pip3 install --break-system-packages ancs4linux
  echo "   Pairing happens interactively — see README.md 'iPhone pairing'."
fi

if [ "$WANT_ANDROID" = "1" ]; then
  echo "-- installing KDE Connect (Android via Wi-Fi)"
  echo "   NOTE: pulls KDE libraries (~a few hundred MB). Ctrl-C now if that's a surprise."
  sleep 3
  sudo apt-get install -y kdeconnect
  echo "   Pairing: install 'KDE Connect' from the Play Store on the phone,"
  echo "   same Wi-Fi as the Pi, then: kdeconnect-cli --list-available && kdeconnect-cli --pair -d <device-id>"
fi

echo
echo "== Done. Verify with: bash $REPO_DIR/install_notification_beam.sh --test =="
