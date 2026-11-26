# Notification Beam

Project phone notifications onto the wall. Born from Patient Zero's own words:
*"I miss about 50% of my iPhone notifications."*

## Architecture

```
iPhone  --BLE (ANCS)-->  ancs4linux  ----\
                                          +-->  org.freedesktop.Notifications (D-Bus)
Android --Wi-Fi------->  KDE Connect ----/                   |
                                                             v
                                           notification_listener.py (this module)
                                                             |
                                            /tmp/motibeam_notifications/queue.json
                                                             |
                                                             v
                                           spatial_os render hook  -->  wall card
```

One listener handles both phone platforms because both bridges deliver
notifications as standard desktop notifications. The listener claims the
notification-daemon bus name (the Pi is an appliance; there is no desktop UI
to compete with) and spools to a JSON file. The renderer polls the spool.
The two halves share nothing else — either can restart without touching the
other, and a malformed spool can never crash the render loop.

## Privacy & courtesy (configurable, `~/.config/motibeam/notification_beam.json`)

- **quiet_hours** — default 22:00–07:00, no cards.
- **app_allowlist / app_blocklist** — show only what matters.
- **privacy_mode** — `full` (title + preview), `title`, or `count`
  ("Messages — 1 notification") for guests in the room.
- Nothing leaves the device; the spool lives in `/tmp` (RAM, cleared on reboot).

## Install (on the Pi)

```bash
cd ~/MotiBeam-SpatialOS   # or ~/motibeam-spatial-os on the Pi 5
git fetch && git checkout notification-beam
bash modules/notification_beam/install_notification_beam.sh            # base listener
bash modules/notification_beam/install_notification_beam.sh --test     # fake notification -> spool
```

Then per phone platform:

```bash
bash modules/notification_beam/install_notification_beam.sh --iphone   # ancs4linux
bash modules/notification_beam/install_notification_beam.sh --android  # KDE Connect (large dep pull)
```

## iPhone pairing (ANCS) — the smartwatch pathway

1. `--iphone` install puts ancs4linux on the Pi (BlueZ required, present on Pi OS).
2. Start its advertising helper so the iPhone can discover the Pi, then pair
   from **iPhone Settings → Bluetooth** (the Pi appears as an accessory).
3. iOS asks to allow notification sharing — **Allow**. That's the ANCS grant;
   iOS treats the Pi exactly like a smartwatch.
4. Known caveats: BLE range (same room, ideally same wall), and iOS can drop
   rarely-used accessory pairings — re-pairing is a 30-second settings visit.

## Android pairing (KDE Connect)

1. Phone: install **KDE Connect** (free, Play Store). Same Wi-Fi as the Pi.
2. Pi: `kdeconnect-cli --list-available` → `kdeconnect-cli --pair -d <id>`.
3. Phone: accept pairing, then grant **notification access** when prompted.

## Wall rendering

`render_hook_example.py` is the reference renderer: top-right card, navy with
gold border, app name + title + 3-line preview, auto-dismiss (default 12 s).
Integration into `spatial_os.py` is **two lines** (init + per-frame draw) and
is applied by hand during the joint session, against the on-device file, with
a timestamped backup first — the on-device code is ahead of this repo, so the
graft happens there, not here.

## Joint-session checklist (~30 min, one Pi, founder's iPhone first)

1. `git fetch && git checkout notification-beam` on the target Pi
2. Base install + `--test` → entry appears in spool ✓
3. Graft the two-line render hook into on-device `spatial_os.py` (backup first)
4. `--test` again → card appears ON THE WALL ✓
5. `--iphone` install, pair founder's iPhone, send a real text → wall ✓
6. Tune config (quiet hours, blocklist), restart service, done
7. Roll to second Pi only after a week of daily use on the first

## Rollback

```bash
systemctl --user disable --now motibeam-notifications.service
# restore the timestamped spatial_os.py backup made in step 3
```
