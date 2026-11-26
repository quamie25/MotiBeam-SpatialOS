#!/usr/bin/env python3
"""
MotiBeam Notification Beam — unified phone-notification listener.

One daemon, two phone platforms, one D-Bus surface:

  iPhone  --BLE/ANCS-->  ancs4linux  --------\
                                              +--> org.freedesktop.Notifications --> THIS DAEMON --> spool JSON --> MotiBeamOS wall card
  Android --Wi-Fi----->  KDE Connect --------/

Both bridges deliver phone notifications as standard desktop notifications.
This daemon claims the org.freedesktop.Notifications bus name (the Pi is a
dedicated appliance — there is no desktop notification UI to compete with)
and spools every notification to a JSON file that spatial_os renders as a
wall card. If another daemon already owns the name, we fall back to
monitor (eavesdrop) mode automatically.

Spool file: /tmp/motibeam_notifications/queue.json  (atomic replace, newest
last, capped). spatial_os polls it each frame — see render_hook_example.py.

Config: ~/.config/motibeam/notification_beam.json (created with defaults on
first run): quiet hours, app allow/block lists, privacy mode, preview length.

No notification content ever leaves the device. Nothing is logged to disk
beyond the rolling spool, which lives in /tmp (RAM-backed, gone on reboot).
"""

import json
import os
import re
import sys
import time
import tempfile
from datetime import datetime

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

BUS_NAME = "org.freedesktop.Notifications"
OBJECT_PATH = "/org/freedesktop/Notifications"

SPOOL_DIR = "/tmp/motibeam_notifications"
SPOOL_FILE = os.path.join(SPOOL_DIR, "queue.json")
SPOOL_MAX = 20  # newest N kept

CONFIG_PATH = os.path.expanduser("~/.config/motibeam/notification_beam.json")
DEFAULT_CONFIG = {
    "enabled": True,
    # 24h clock, local time. Cards are suppressed inside this window.
    "quiet_hours": {"start": "22:00", "end": "07:00"},
    # If non-empty, ONLY these apps show (match against app name, case-insensitive substring).
    "app_allowlist": [],
    # These never show. Sensible defaults: system noise.
    "app_blocklist": ["software update", "system"],
    # "full" = title + body preview; "title" = title only; "count" = app name + "1 notification"
    "privacy_mode": "full",
    "max_preview_chars": 120,
    # Seconds a card stays on the wall (renderer reads this from each spool entry).
    "card_seconds": 12,
}


# --------------------------------------------------------------------------- config

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        return merged
    except FileNotFoundError:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"[notification_beam] wrote default config -> {CONFIG_PATH}")
        return dict(DEFAULT_CONFIG)
    except Exception as exc:  # malformed config must never kill the daemon
        print(f"[notification_beam] config error ({exc}); using defaults")
        return dict(DEFAULT_CONFIG)


def in_quiet_hours(cfg, now=None):
    try:
        qh = cfg.get("quiet_hours") or {}
        start, end = qh.get("start"), qh.get("end")
        if not start or not end:
            return False
        now = now or datetime.now()
        cur = now.hour * 60 + now.minute
        s_h, s_m = (int(x) for x in start.split(":"))
        e_h, e_m = (int(x) for x in end.split(":"))
        s, e = s_h * 60 + s_m, e_h * 60 + e_m
        if s <= e:
            return s <= cur < e
        return cur >= s or cur < e  # window crosses midnight
    except Exception:
        return False


def app_filtered(cfg, app_name):
    name = (app_name or "").lower()
    allow = [a.lower() for a in cfg.get("app_allowlist") or []]
    block = [b.lower() for b in cfg.get("app_blocklist") or []]
    if any(b in name for b in block):
        return True
    if allow and not any(a in name for a in allow):
        return True
    return False


# --------------------------------------------------------------------------- spool

def _strip_markup(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def spool_write(entry):
    os.makedirs(SPOOL_DIR, exist_ok=True)
    queue = []
    try:
        with open(SPOOL_FILE) as f:
            queue = json.load(f)
        if not isinstance(queue, list):
            queue = []
    except Exception:
        queue = []
    queue.append(entry)
    queue = queue[-SPOOL_MAX:]
    fd, tmp = tempfile.mkstemp(dir=SPOOL_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(queue, f)
        os.replace(tmp, SPOOL_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def handle_notification(cfg_loader, app_name, summary, body):
    cfg = cfg_loader()
    if not cfg.get("enabled", True):
        return
    if in_quiet_hours(cfg):
        print(f"[notification_beam] quiet hours — suppressed: {app_name}")
        return
    if app_filtered(cfg, app_name):
        print(f"[notification_beam] filtered app: {app_name}")
        return

    mode = cfg.get("privacy_mode", "full")
    summary = _strip_markup(str(summary))
    body = _strip_markup(str(body))
    limit = int(cfg.get("max_preview_chars", 120))
    if mode == "count":
        summary, body = "1 notification", ""
    elif mode == "title":
        body = ""
    if len(body) > limit:
        body = body[: limit - 1] + "…"

    entry = {
        "ts": time.time(),
        "app": str(app_name) or "Phone",
        "title": summary,
        "body": body,
        "card_seconds": int(cfg.get("card_seconds", 12)),
    }
    try:
        spool_write(entry)
        print(f"[notification_beam] spooled: [{entry['app']}] {entry['title']}")
    except Exception as exc:
        print(f"[notification_beam] spool write failed: {exc}")


# --------------------------------------------------------------------------- daemon mode (owns the bus name)

class NotificationDaemon(dbus.service.Object):
    """Minimal org.freedesktop.Notifications implementation.

    Accepts Notify() from ancs4linux / KDE Connect / notify-send and spools
    it for the wall renderer. No popups of its own — the wall IS the popup.
    """

    def __init__(self, bus, cfg_loader):
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus, do_not_queue=True)
        super().__init__(bus_name, OBJECT_PATH)
        self._cfg_loader = cfg_loader
        self._next_id = 1

    @dbus.service.method(BUS_NAME, in_signature="susssasa{sv}i", out_signature="u")
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        handle_notification(self._cfg_loader, app_name, summary, body)
        nid = replaces_id or self._next_id
        if not replaces_id:
            self._next_id += 1
        return dbus.UInt32(nid)

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="as")
    def GetCapabilities(self):
        return ["body"]

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="ssss")
    def GetServerInformation(self):
        return ("MotiBeam Notification Beam", "MotiBeam Technologies", "0.1", "1.2")

    @dbus.service.method(BUS_NAME, in_signature="u", out_signature="")
    def CloseNotification(self, nid):
        pass


# --------------------------------------------------------------------------- monitor mode (another daemon owns the name)

def start_monitor(bus, cfg_loader):
    bus.add_match_string_non_blocking(
        "interface='org.freedesktop.Notifications',member='Notify',type='method_call',eavesdrop='true'"
    )

    def _filter(_bus, message):
        try:
            if message.get_member() != "Notify":
                return
            args = message.get_args_list()
            if len(args) >= 5:
                handle_notification(cfg_loader, args[0], args[3], args[4])
        except Exception as exc:
            print(f"[notification_beam] monitor parse error: {exc}")

    bus.add_message_filter(_filter)
    print("[notification_beam] monitor mode: eavesdropping on Notify()")


# --------------------------------------------------------------------------- main

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    cfg_loader = load_config  # re-read each notification so edits apply live

    load_config()  # ensure default config exists before first notification

    try:
        NotificationDaemon(bus, cfg_loader)
        print(f"[notification_beam] owning {BUS_NAME} (daemon mode)")
    except dbus.exceptions.NameExistsException:
        print(f"[notification_beam] {BUS_NAME} already owned — falling back to monitor mode")
        start_monitor(bus, cfg_loader)

    print(f"[notification_beam] spooling to {SPOOL_FILE}")
    GLib.MainLoop().run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
