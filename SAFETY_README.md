# MotiBeam Spatial OS - Safety System

This safety system protects your working MotiBeam installation from breaking changes.

## 🎯 **Why Safety Tools Matter**

You have a **working system** with:
- ✅ Beautiful emoji rendering
- ✅ 6 fully functional realms
- ✅ Auto-boot on Pi startup
- ✅ Perfect for investor demos

**One bad code change can break everything.** These tools protect you.

---

## 🛡️ **Safety Tools Included**

### 1. **`safety.sh`** - Backup & Restore Script

One command to backup, test, or restore your working system.

```bash
./safety.sh backup    # Create timestamped backup
./safety.sh test      # Check Python syntax
./safety.sh status    # Show system status
./safety.sh restore   # Restore from backup
```

### 2. **`SAFETY_CHECKLIST.txt`** - Testing Checklist

Comprehensive checklist to verify nothing broke after changes:
- ✓ Emoji rendering still works
- ✓ Navigation still works
- ✓ All 6 realms still function
- ✓ Auto-boot still works

### 3. **This README** - How to Use Safely

Step-by-step workflow for making changes safely.

---

## 🚀 **Safe Change Workflow**

### **BEFORE Making Changes:**

```bash
# 1. Create backup
cd ~/motibeam-spatial-os
./safety.sh backup
```

This creates a timestamped backup like:
```
~/motibeam-backups/spatial_os_backup_20231201_143022.py
```

### **AFTER Making Changes:**

```bash
# 2. Test Python syntax
./safety.sh test
```

If syntax is valid, proceed. If not, fix errors or restore backup.

```bash
# 3. Manual testing
python3 spatial_os.py
# OR if auto-boot enabled:
sudo systemctl restart motibeam
```

Use `SAFETY_CHECKLIST.txt` to verify everything works.

### **IF Something Broke:**

```bash
# Restore backup
./safety.sh restore

# Choose from list of backups
# Example: ./safety.sh restore 20231201_143022
```

---

## 📋 **safety.sh Command Reference**

### **backup** - Create Backup

```bash
./safety.sh backup
```

Creates timestamped backup in `~/motibeam-backups/`

**When to use:**
- Before adding new features
- Before modifying emoji rendering
- Before changing navigation logic
- Before ANY code changes

### **test** - Test Syntax

```bash
./safety.sh test
```

Checks Python syntax without running the app.

**What it checks:**
- ✓ No syntax errors
- ✓ All imports valid
- ✓ Code can compile

**Does NOT check:**
- Runtime behavior
- Emoji rendering
- Navigation logic

Always follow with manual testing!

### **status** - Show Status

```bash
./safety.sh status
```

Shows:
- Main file location and size
- Number of backups available
- Most recent backup
- Service status (running/stopped)
- Quick syntax check

### **restore** - Restore Backup

```bash
# Show available backups
./safety.sh restore

# Restore specific backup
./safety.sh restore 20231201_143022
```

**Safety features:**
- Creates backup of current version first
- Shows available backups with timestamps
- Confirms restore completed

**After restore:**
- If auto-boot enabled: `sudo systemctl restart motibeam`
- If manual: `python3 spatial_os.py`

---

## 🧪 **Testing After Changes**

After making changes, test systematically using `SAFETY_CHECKLIST.txt`:

```bash
# Open checklist
cat SAFETY_CHECKLIST.txt

# Or open in editor
nano SAFETY_CHECKLIST.txt
```

**Critical tests:**
1. ✅ Emoji still render (not brackets)
2. ✅ Navigation works (arrow keys, Enter, ESC)
3. ✅ All 6 realms open and function
4. ✅ Live date/time displays
5. ✅ Auto-boot works (if enabled)

---

## 💡 **Common Scenarios**

### **Scenario 1: Adding Weather Integration**

```bash
# Before
./safety.sh backup

# Make changes (add weather API code)
nano spatial_os.py

# After
./safety.sh test
python3 spatial_os.py  # Manual test
# Use SAFETY_CHECKLIST.txt to verify

# If weather works and nothing broke:
./safety.sh backup  # New backup with weather

# If something broke:
./safety.sh restore  # Go back to before weather
```

### **Scenario 2: Changing Emoji Rendering**

```bash
# Before (CRITICAL - emoji is fragile!)
./safety.sh backup

# Make changes
nano spatial_os.py

# After
./safety.sh test
python3 spatial_os.py

# TEST EMOJI SPECIFICALLY:
# - Check home grid (12 emoji)
# - Open CircleBeam (👩👨👧📞✉️🚨)
# - Open Clinical (❤️🩸🫁🌡️✅⏰📞)
# - Open all other realms

# If ANY emoji broke:
./safety.sh restore  # Immediately restore!
```

### **Scenario 3: Updating Navigation**

```bash
# Before
./safety.sh backup

# Make changes
nano spatial_os.py

# After - test navigation thoroughly:
./safety.sh test
python3 spatial_os.py

# TEST:
# - Arrow keys (all 4 directions)
# - Enter key (opens all realms)
# - ESC key (goes back from realms)
# - Number keys (1-9 quick select)
# - Navigation stack (home -> realm -> ESC -> home)

# If navigation broke:
./safety.sh restore
```

---

## 🎯 **Best Practices**

### **DO:**

✅ **Always backup before changes**
- Every single time, no exceptions
- Backups are cheap, broken demos are expensive

✅ **Test with checklist**
- Use SAFETY_CHECKLIST.txt systematically
- Don't skip tests to save time

✅ **Restore immediately if broken**
- Don't try to "fix" broken code during demo prep
- Restore working version, fix later

✅ **Keep multiple backups**
- Script keeps all backups timestamped
- Backups in `~/motibeam-backups/` are safe

### **DON'T:**

❌ **Make changes without backup**
- "It's just a small change" - famous last words
- Always backup first

❌ **Skip syntax testing**
- Running broken code wastes time
- `./safety.sh test` takes 1 second

❌ **Deploy untested changes**
- Manual testing is required
- Syntax test ≠ functionality test

❌ **Delete old backups**
- Disk space is cheap
- You might need to go back several versions

---

## 🔧 **Troubleshooting**

### **"Backup failed - file not found"**

Check file location:
```bash
ls ~/motibeam-spatial-os/spatial_os.py
```

If wrong location, edit `safety.sh` line:
```bash
WORK_DIR="$HOME/motibeam-spatial-os"  # Update this path
```

### **"Syntax test passed but app crashes"**

Syntax test only checks Python syntax, not logic. Issues could be:
- Import errors (missing modules)
- Runtime errors (bad logic)
- Emoji font issues
- pygame errors

**Solution:** Restore backup, then investigate

### **"Don't know which backup to restore"**

```bash
# Show all backups with timestamps
./safety.sh restore

# Most recent is usually what you want
# Look for backup right before changes
```

### **"Auto-boot won't restart after restore"**

```bash
# Manually restart service
sudo systemctl restart motibeam

# Check status
sudo systemctl status motibeam

# View logs
sudo journalctl -u motibeam -n 50
```

---

## 📦 **Backup Storage**

**Location:** `~/motibeam-backups/`

**Format:** `spatial_os_backup_YYYYMMDD_HHMMSS.py`

**Example:**
```
spatial_os_backup_20231201_143022.py  # Dec 1, 2023 at 2:30:22 PM
spatial_os_backup_20231201_151545.py  # Dec 1, 2023 at 3:15:45 PM
```

**How many to keep:**
- Script keeps all backups
- Manually delete old ones if needed
- Recommend keeping at least 10 most recent

**Backup before major events:**
```bash
# Before investor demo
./safety.sh backup

# Before adding new features
./safety.sh backup

# Before grant application deadline
./safety.sh backup
```

---

## 🚨 **Emergency Recovery**

### **System completely broken?**

1. **Stop the service** (if auto-boot enabled)
   ```bash
   sudo systemctl stop motibeam
   ```

2. **Restore most recent working backup**
   ```bash
   ./safety.sh restore
   # Choose most recent backup before breakage
   ```

3. **Test manually first**
   ```bash
   python3 ~/motibeam-spatial-os/spatial_os.py
   # Verify it works before restarting service
   ```

4. **Restart service**
   ```bash
   sudo systemctl start motibeam
   ```

### **Lost all backups?**

If `~/motibeam-backups/` is empty, check git:

```bash
cd ~/motibeam-spatial-os
git log --oneline  # See commit history
git checkout <commit-hash> spatial_os.py  # Restore from git
```

---

## 📚 **Additional Resources**

- **Auto-boot setup:** See `AUTOBOOT-README.md`
- **Git history:** `git log` to see all commits
- **Service logs:** `sudo journalctl -u motibeam -f`
- **systemd control:** `sudo systemctl status motibeam`

---

## ✅ **Quick Reference**

```bash
# Standard workflow
./safety.sh backup           # Before changes
# [make changes]
./safety.sh test             # Test syntax
python3 spatial_os.py        # Test manually
# [if broken] ./safety.sh restore

# Check status
./safety.sh status

# List backups
./safety.sh restore

# Restore specific backup
./safety.sh restore 20231201_143022
```

---

**Remember:** The goal is to protect your working demo system. When in doubt, backup. When broken, restore. Never risk your working version!
