#!/bin/bash
# MotiBeam Spatial OS - Safety & Backup Tool
# Protects your working system before making changes

set -e

BACKUP_DIR="$HOME/motibeam-backups"
WORK_DIR="$HOME/motibeam-spatial-os"
MAIN_FILE="$WORK_DIR/spatial_os.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function: Create backup
backup() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}MotiBeam Safety Tool - BACKUP${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [ ! -f "$MAIN_FILE" ]; then
        echo -e "${RED}ERROR: spatial_os.py not found!${NC}"
        exit 1
    fi

    # Create timestamped backup
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/spatial_os_backup_$TIMESTAMP.py"

    cp "$MAIN_FILE" "$BACKUP_FILE"

    echo -e "${GREEN}✓ Backup created successfully!${NC}"
    echo ""
    echo "Backup location: $BACKUP_FILE"
    echo "Timestamp: $(date)"
    echo ""

    # Show recent backups
    echo "Recent backups:"
    ls -lht "$BACKUP_DIR" | head -6
    echo ""
    echo -e "${YELLOW}TIP: To restore this backup later, run:${NC}"
    echo "  ./safety.sh restore $TIMESTAMP"
    echo ""
}

# Function: Restore backup
restore() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}MotiBeam Safety Tool - RESTORE${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [ -z "$1" ]; then
        # Show available backups
        echo "Available backups:"
        echo ""
        ls -lht "$BACKUP_DIR" | grep spatial_os_backup | head -10
        echo ""
        echo -e "${YELLOW}To restore a backup, run:${NC}"
        echo "  ./safety.sh restore TIMESTAMP"
        echo ""
        echo "Example: ./safety.sh restore 20231201_143022"
        echo ""
        return
    fi

    TIMESTAMP=$1
    BACKUP_FILE="$BACKUP_DIR/spatial_os_backup_$TIMESTAMP.py"

    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}ERROR: Backup not found: $BACKUP_FILE${NC}"
        echo ""
        echo "Available backups:"
        ls -lht "$BACKUP_DIR" | grep spatial_os_backup | head -10
        exit 1
    fi

    # Safety check - create backup of current version first
    SAFETY_BACKUP="$BACKUP_DIR/spatial_os_before_restore_$(date +%Y%m%d_%H%M%S).py"
    cp "$MAIN_FILE" "$SAFETY_BACKUP"
    echo -e "${GREEN}✓ Created safety backup: $SAFETY_BACKUP${NC}"
    echo ""

    # Restore
    cp "$BACKUP_FILE" "$MAIN_FILE"

    echo -e "${GREEN}✓ Restored successfully!${NC}"
    echo ""
    echo "Restored from: $BACKUP_FILE"
    echo "Current file: $MAIN_FILE"
    echo ""
    echo -e "${YELLOW}IMPORTANT: If auto-boot is enabled, restart the service:${NC}"
    echo "  sudo systemctl restart motibeam"
    echo ""
}

# Function: Test syntax
test_syntax() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}MotiBeam Safety Tool - SYNTAX TEST${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [ ! -f "$MAIN_FILE" ]; then
        echo -e "${RED}ERROR: spatial_os.py not found!${NC}"
        exit 1
    fi

    echo "Testing Python syntax..."
    echo ""

    if python3 -m py_compile "$MAIN_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓ Syntax check PASSED!${NC}"
        echo ""
        echo "File: $MAIN_FILE"
        echo "Status: No syntax errors detected"
        echo ""
        echo -e "${GREEN}Safe to run or deploy.${NC}"
        echo ""
    else
        echo -e "${RED}✗ Syntax check FAILED!${NC}"
        echo ""
        echo "Python syntax errors detected. Running detailed check:"
        echo ""
        python3 -m py_compile "$MAIN_FILE"
        echo ""
        echo -e "${YELLOW}FIX REQUIRED: Restore backup or fix syntax errors before running.${NC}"
        echo ""
        exit 1
    fi
}

# Function: Quick status
status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}MotiBeam Safety Tool - STATUS${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Check file exists
    if [ -f "$MAIN_FILE" ]; then
        echo -e "${GREEN}✓ Main file exists${NC}"
        ls -lh "$MAIN_FILE"
    else
        echo -e "${RED}✗ Main file NOT found!${NC}"
    fi
    echo ""

    # Count backups
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/spatial_os_backup_*.py 2>/dev/null | wc -l)
    echo "Backups available: $BACKUP_COUNT"
    echo ""

    # Show most recent backup
    if [ $BACKUP_COUNT -gt 0 ]; then
        echo "Most recent backup:"
        ls -lht "$BACKUP_DIR"/spatial_os_backup_*.py | head -1
        echo ""
    fi

    # Check if service is running
    if systemctl is-active --quiet motibeam 2>/dev/null; then
        echo -e "${GREEN}✓ MotiBeam service is RUNNING${NC}"
    else
        echo -e "${YELLOW}⚠ MotiBeam service is NOT running${NC}"
    fi
    echo ""

    # Quick syntax test
    if python3 -m py_compile "$MAIN_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓ Python syntax is valid${NC}"
    else
        echo -e "${RED}✗ Python syntax errors detected!${NC}"
    fi
    echo ""
}

# Function: Show help
show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}MotiBeam Safety Tool${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Protects your working MotiBeam system before making changes."
    echo ""
    echo "USAGE:"
    echo "  ./safety.sh <command>"
    echo ""
    echo "COMMANDS:"
    echo "  backup          Create timestamped backup of spatial_os.py"
    echo "  restore [TIME]  Restore from backup (shows list if no timestamp)"
    echo "  test            Test Python syntax (safe to run?)"
    echo "  status          Show system status and backup info"
    echo "  help            Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  ./safety.sh backup                    # Create backup before changes"
    echo "  ./safety.sh test                      # Test syntax after changes"
    echo "  ./safety.sh restore                   # Show available backups"
    echo "  ./safety.sh restore 20231201_143022   # Restore specific backup"
    echo ""
    echo "WORKFLOW:"
    echo "  1. ./safety.sh backup      # Before making ANY changes"
    echo "  2. [Make your changes]"
    echo "  3. ./safety.sh test        # Verify syntax is valid"
    echo "  4. Test manually           # Run and verify it works"
    echo "  5. ./safety.sh restore     # If something broke"
    echo ""
    echo "Backups stored in: $BACKUP_DIR"
    echo ""
}

# Main command router
case "${1:-help}" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    test)
        test_syntax
        ;;
    status)
        status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
