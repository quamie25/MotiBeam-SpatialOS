# Add to git (if you want)
git add EDITING_RULES.md
git commit -m "Add editing protocol for collaborators"
```

**Now whenever Claude Code (or any developer) works on your code:**

"Before you start, read EDITING_RULES.md"

---

## 🎯 SUGGESTED ADDITIONS TO THE RULES

**You might also want to specify:**

### **Directory Structure Rules:**
```
DIRECTORY STRUCTURE:
--------------------
~/motibeam-spatial-os/
├── spatial_os_pygame.py          [LIVE] Main UI
├── run_pygame.sh                 [LIVE] Launcher script
├── core/
│   ├── notification_banner.py    [LIVE] Header
│   ├── realm_card.py             [LIVE] Card rendering
│   └── ...
├── realms/
│   ├── circlebeam.py             [LIVE] CircleBeam realm
│   ├── marketplace.py            [LIVE] Marketplace realm
│   └── ...
├── ui/
│   ├── animations.py             [LIVE] Animation system
│   └── ...
└── [OLD FILES]
    ├── motibeam_spatial_os.py    [ARCHIVE] Don't touch
    ├── spatial_os_pygame.py      [ARCHIVE] Don't touch
    └── ...

RULE: Files in core/, realms/, ui/ are live code.
      Files in root with 'old' names are archives.
```

---

### **Before/After Test Protocol:**
```
BEFORE MAKING ANY CHANGE:
-------------------------
1. Run: ./run_pygame.sh
2. Take screenshot of current state
3. Note what you're about to change
4. Make the change
5. Run: ./run_pygame.sh
6. Take screenshot of new state
7. Compare: Did your change take effect?
   - YES: Change successful, commit it
   - NO: You edited wrong file, revert and find correct file

This prevents "I made 50 changes and don't know which file is live" situations.
```

---

## 🚀 NOW BACK TO ADAPTER STRATEGY

**Git protocol: DONE ✅**  
**Editing rules: DOCUMENTED ✅**  
**Claude Code: INSTRUCTED ✅**

**Next priority: MAKE MONEY 💰**

---

## 📋 THIS WEEK'S ACTUAL TASKS (UPDATED)

### **Today (Monday):**

**Morning (2 hours):**
- [ ] Give Claude Code the editing rules document
- [ ] Have Claude Code verify it can edit spatial_os_pygame.py correctly
- [ ] Test: Add "v2" to header, confirm it works

**Afternoon (4 hours):**
- [ ] Order 10× Pi Zero 2 W from Adafruit/Amazon ($150)
- [ ] Draft HomeschoolBeam product description (for Kickstarter)
- [ ] Film 30 seconds of realm grid demo (current state)

**Evening (2 hours):**
- [ ] Apply to Warrior Rising grant (warriorrising.org)
- [ ] Email VA Innovation Center (vhainnovation@va.gov)

---

### **Tuesday:**

**Morning:**
- [ ] Claude Code: Add large emoji to realm cards (64px icons)
- [ ] Test on projection: Are icons visible from 10 feet?
- [ ] If yes: Film updated realm grid

**Afternoon:**
- [ ] Draft ClinicalBeam product description
- [ ] Apply to StreetShares Foundation grant
- [ ] Contact Bunker Labs Houston

**Evening:**
- [ ] Research Pi Zero 2 W enclosure options (3D print or buy)
- [ ] Plan adapter prototype build (Wednesday)

---

### **Wednesday:**

**Morning:**
- [ ] Receive Pi Zero 2 W (if 1-day Amazon shipping)
- [ ] Install MotiBeam OS on Pi Zero 2 W
- [ ] Test: Does it run spatial_os_pygame.py?

**Afternoon:**
- [ ] If working: Build simple adapter prototype
- [ ] Film adapter demo (plug into projector, show MotiBeam starting)
- [ ] Film HomeschoolBeam scenario (math problem projection)

**Evening:**
- [ ] Film ClinicalBeam scenario (medication reminder)
- [ ] Update Kickstarter page with adapter tiers

---

### **Thursday:**

**Morning:**
- [ ] Contact Anker Nebula re: partnership (email + LinkedIn)
- [ ] Contact Goodee re: co-branded bundle
- [ ] Review all demo footage

**Afternoon:**
- [ ] Start editing Kickstarter video (DaVinci Resolve)
- [ ] Add text overlays, music, transitions
- [ ] Export draft 1

**Evening:**
- [ ] Watch draft 1, take notes
- [ ] Re-film anything that doesn't look professional
- [ ] Plan Friday filming (B-roll, testimonials)

---

### **Friday:**

**Morning:**
- [ ] Film B-roll (adapter closeups, projection on wall, you talking)
- [ ] Film "founder story" segment (veteran, Coast Guard, VA denial, patents)
- [ ] Capture all remaining demo footage

**Afternoon:**
- [ ] Edit final Kickstarter video (12-15 min)
- [ ] Export high quality (1080p)
- [ ] Upload to private YouTube link

**Evening:**
- [ ] Watch final video, get feedback
- [ ] Prepare Kickstarter launch assets
- [ ] Schedule launch for Monday Dec 16

---

## 💎 WEEK 1 SUCCESS METRICS

**By Friday Dec 13, you should have:**

✅ Editing protocol documented (for Claude Code)  
✅ Large emoji added to realm cards  
✅ Pi Zero 2 W adapter prototype working  
✅ 3 demo videos filmed (realm grid, HomeschoolBeam, ClinicalBeam)  
✅ Kickstarter video edited (12-15 min, professional quality)  
✅ 2 grant applications submitted  
✅ VA Innovation Center contacted  
✅ 2 OEM partnership emails sent  
✅ Navy Federal LOC application started  

**Revenue potential by end of Week 1:** $0 (applications pending)  
**Revenue potential by end of Week 4:** $40-60K (grants + LOC + pre-orders)  
**Revenue potential by end of Week 8:** $200K+ (Kickstarter closes)

---

## 🎖️ FINAL CHECKLIST FOR CLAUDE CODE

**Send Claude Code this message:**
```
I've created editing rules for MotiBeam Spatial OS. Please read and confirm you understand:

LIVE FILES (Edit Only These):
1. spatial_os.py - main UI (active development file as of May 2026)
2. core/notification_banner.py - header

ARCHIVE FILES (Never Touch):
- motibeam_spatial_os.py
- spatial_os_pygame.py
- Any other old versions

VERIFICATION TEST:
Before any edit, change header to "v2" in core/notification_banner.py,
run ./run_pygame.sh, confirm header shows "v2" on projection.

Please confirm:
1. You understand these rules
2. You will only edit spatial_os_pygame.py and core/notification_banner.py
3. You will run the v2 test before making changes
4. You will ask me if unsure which file to edit

Once confirmed, first task: Add 64px emoji to realm cards in spatial_os_pygame.py
