# CLAUDE.md — MotiBeam-SpatialOS

Read this at the start of every session. It describes the project, the
two-Pi hardware reality, what NOT to touch, and the current known issues.
Updated June 9 2026 after a repo-reconciliation + voice-fix session.

---

## What this project is

MotiBeamOS is the **native projection-native ambient computing engine** for
MotiBeam Technologies — Python + Pygame, running on Raspberry Pi, turning
surfaces into interactive displays. This is the patent-bearing core. It is NOT
a web app; do not add web frameworks, browser runtimes, or cloud dependencies.

The main file is **`spatial_os.py`**. (Note: an older `EDITING_RULES.md` may
mark it "Never Touch" — that rule is STALE. spatial_os.py is the active
development file. `spatial_os_pygame.py` is the archived one.)

---

## CRITICAL: This is a TWO-Pi system, and they are configured differently

There are two physical Raspberry Pis, and they do NOT match. This mismatch has
caused real bugs. Always know which Pi you are working on.

### Pi 4 — the wake-word LISTENER
- IP: `192.168.1.203`, hostname `raspberrypi`
- Repo folder: `/home/motibeam/MotiBeam-SpatialOS`
- Commit (as of Jun 9 2026): **`f52eef1`** — BEHIND the Pi 5
- Launched by: systemd `motibeam.service`, which runs
  `python3 -u spatial_os.py` in a `while true` loop, logging to
  **`/tmp/motibeam.log`** (this is the real runtime log — check it, not just journalctl)
- Voice: USB mic on **card 3** (`UACDemoV1.0`). Vosk model at `/home/motibeam/vosk-model/`
- Has a machine-local **`~/.asoundrc`** that routes the default capture device
  to `hw:3,0` (the USB mic). THIS FILE IS NOT IN GIT — it lives only on the Pi 4.
  Without it, Vosk listens to the wrong device and hears nothing. Do not assume
  the repo contains the audio fix; it doesn't, by design (machine-specific hardware).
- Role: hears "call dad" / "nudge dad", triggers local presence flow AND
  broadcasts PRESENCE_CALL to the Pi 5.

### Pi 5 — the presence RECEIVER
- IP: `192.168.1.156`, hostname `motibeamOS`
- Repo folder: `~/motibeam-spatial-os`
- Commit (as of Jun 9 2026): **`6d17ff4`** — the reconciled trunk (AHEAD of Pi 4)
- Receives PRESENCE_CALL; user answers with "A"; both walls then show present.
- Known fragility: holds stale presence sockets when idle for hours, currently
  needs a REBOOT to reconnect. This is the original idle-disconnect bug. The
  resilient-link work (heartbeat + auto-reconnect) is meant to fix it for good.

**The two Pis are on different commits (`f52eef1` vs `6d17ff4`). They must be
synced to the same commit for bidirectional CircleBeam to be reliable.** This is
the top open task.

---

## Git facts

- Remote: `https://github.com/quamie25/MotiBeam-SpatialOS.git`
- Trunk branch: `claude/polish-spatial-os-01DqQhWBaHTZx3pA8ProEtpG` at `6d17ff4`
- **Safety backup branch: `backup-pi-april30-2026` (at `92680e8`) — NEVER force-push over this.** It is the Pi 5's pre-reconciliation snapshot.
- Another branch exists: `claude/fix-realm-crashes-Nu95h` — work-in-progress on
  realm crashes (likely the S-key crash). Review before merging.
- Two stashes exist on the Pi 5: "WIP before S-key crash fix" and "local tweaks
  before pulling education + circlebeam updates." Check whether they hold
  anything useful before dropping.

---

## DO NOT TOUCH (hard rules)

1. **Do not modify the render loop, resolution/scaling, or font handling**
   unless explicitly asked. Projection visual quality is good. The global font
   cache (prevents per-frame SysFont crashes on Pi 4 ARM) and Surface caching are
   hard-won fixes — do not "clean them up."
2. **Do not change CircleBeam protocol semantics** (PRESENCE_CALL/ACCEPT/END).
   Wrap or extend, never redefine. Both Pis must agree on the protocol.
3. **Never force-push over `backup-pi-april30-2026`.**
4. **Never commit secrets or business/legal/financial documents** (business
   plans, patent filings, VR&E/SBIR paperwork). If found in the repo, flag for removal.
5. **No military / USCG identity in any consumer-facing copy or UI.** Reserved
   for federal/VR&E/SBIR/investor materials only.
6. **Do not add cloud dependencies or telemetry.** Offline-first, Pi-native.
7. **Do not push directly to `main`.** Feature branches; show diffs before commit.
8. **Do not install new dependencies without approval** (ARM Pi build constraints).
9. **When syncing the two Pis, back up the target Pi's current state FIRST**
   (commit + push to a backup branch) before any reset. We lost nothing tonight
   because we did this; keep doing it.

---

## Code change workflow
1. State the plan before editing (files, change, why).
2. Work on a feature branch, never directly on main.
3. Test on the relevant Pi where possible.
4. Show the `git diff` and summarize risk.
5. Commit only after approval. Push only after approval. Never force-push the backup branch.

## Verification notes
- Voice test (Pi 4): `tail -f /tmp/motibeam.log`, say "call dad", look for
  `[Voice:HEARD] call dad`. Recognition is currently FLAKY (see known issues).
- Bidirectional test: clean "call dad" on Pi 4 → Pi 5 wall reacts → answer "A"
  → both walls show present. Confirmed working from a fresh reboot Jun 9 2026.
- Many checks are physical (projection clarity, mic, ToF sensor). Claude CANNOT
  verify these — ask the human to confirm on hardware. Never assume a visual result.

---

## KNOWN ISSUES (current, as of Jun 9 2026)

1. **Pi 4 / Pi 5 commit mismatch** — Pi 4 on `f52eef1`, Pi 5 on `6d17ff4`.
   Sync Pi 4 up to `6d17ff4` (back it up first). TOP PRIORITY — affects
   bidirectional reliability.
2. **Flaky wake-word matching (Pi 4)** — Vosk hears the user but matching is too
   strict. "call dad" is transcribed as "cause dad", "call that", "cause that"
   most of the time; exact match only fires occasionally. Make the matcher
   fuzzy/tolerant for "call dad" and "nudge dad".
3. **Pi 5 idle-disconnect** — presence link goes stale after hours idle, needs a
   reboot to recover. Fix with: Wi-Fi power-save OFF on Pi 5, heartbeat/keepalive
   (~20-30s), auto-reconnect with backoff, clean socket teardown (SO_REUSEADDR).
   The real networking (`PresenceNode`, PRESENCE_CALL) is confirmed present and
   working when fresh — build the resilience around it.
4. **S-key crash (Productivity / Education)** — historically the "S" key caused a
   crash. Check current state on `6d17ff4`; may be addressed on the
   `fix-realm-crashes` branch.
5. **Possible duplicate-launch** — verify only one launch path (systemd vs desktop
   autostart). Add a single-instance lock if needed.
6. **`.backup` clutter + `~/.asoundrc` not in git** — ~35 `spatial_os.py.backup*`
   files in the Pi 5 working dir (consider a `.gitignore`). The Pi 4 mic fix
   (`~/.asoundrc`) is machine-local and intentionally outside git.
