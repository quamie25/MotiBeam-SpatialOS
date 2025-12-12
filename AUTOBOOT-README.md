# MotiBeam Spatial OS - Auto-Boot Setup

This guide will configure your Raspberry Pi to automatically launch MotiBeam Spatial OS on boot, skipping the desktop environment entirely.

## ✨ What This Does

- **Auto-starts** MotiBeam on boot (no manual launching needed)
- **Skips desktop** - boots directly to console then launches MotiBeam
- **Auto-restarts** if MotiBeam crashes
- **Faster boot** - optimizes unnecessary services

## 🚀 Quick Installation

```bash
# Run from the MotiBeam-SpatialOS directory
cd ~/motibeam-spatial-os
sudo ./install-autoboot.sh
```

After installation, reboot to test:
```bash
sudo reboot
```

## 📋 What You'll See on Boot

1. **Raspberry Pi boot messages** (5-10 seconds)
2. **MotiBeam Spatial OS** launches automatically
3. **Live date/time** displayed on home screen

## 🎮 Managing the Service

### Check Status
```bash
sudo systemctl status motibeam
```

### Start/Stop Manually
```bash
sudo systemctl start motibeam   # Start now
sudo systemctl stop motibeam    # Stop service
sudo systemctl restart motibeam # Restart
```

### View Logs
```bash
sudo journalctl -u motibeam -f  # Follow live logs
sudo journalctl -u motibeam -n 50 # Last 50 lines
```

## 🔧 Troubleshooting

### MotiBeam won't start on boot

Check service status:
```bash
sudo systemctl status motibeam
```

Check logs for errors:
```bash
sudo journalctl -u motibeam -n 100
```

### Want to stop auto-boot temporarily

Disable the service:
```bash
sudo systemctl disable motibeam
```

Re-enable later:
```bash
sudo systemctl enable motibeam
```

### Return to desktop mode

```bash
sudo systemctl set-default graphical.target
sudo reboot
```

Then to go back to MotiBeam auto-boot:
```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

## 🎯 Manual Testing (Before Auto-Boot)

Test if the service works without rebooting:
```bash
sudo systemctl start motibeam
```

Stop it:
```bash
sudo systemctl stop motibeam
```

## 📝 Notes

- The service runs as user `motibeam` (or your current user)
- MotiBeam runs in fullscreen at 1920x1080
- Press Q or ESC to quit MotiBeam (it will auto-restart in 10 seconds)
- The service restarts automatically if it crashes
- Logs are stored in systemd journal

## 🔙 Complete Uninstall

```bash
sudo systemctl stop motibeam
sudo systemctl disable motibeam
sudo rm /etc/systemd/system/motibeam.service
sudo systemctl daemon-reload
sudo systemctl set-default graphical.target
```
