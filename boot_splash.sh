#!/bin/bash
# MotiBeam Professional Boot Splash
# Hides all terminal output and shows clean branded screen

# Clear screen and hide cursor
clear
tput civis

# Set colors
CYAN='\033[0;36m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
RESET='\033[0m'

# Get terminal size
ROWS=$(tput lines)
COLS=$(tput cols)

# Calculate center position
CENTER_ROW=$((ROWS / 2 - 6))

# Function to print centered text
print_centered() {
    local text="$1"
    local color="$2"
    local padding=$(( (COLS - ${#text}) / 2 ))
    printf "%${padding}s" ""
    echo -e "${color}${text}${RESET}"
}

# Move to center
for i in $(seq 1 $CENTER_ROW); do echo ""; done

# Display logo
print_centered "████████████████████████████████████████████████████████" "$CYAN"
print_centered "█                                                      █" "$CYAN"
print_centered "█           ███╗   ███╗ ██████╗ ████████╗██╗           █" "$CYAN"
print_centered "█           ████╗ ████║██╔═══██╗╚══██╔══╝██║           █" "$CYAN"
print_centered "█           ██╔████╔██║██║   ██║   ██║   ██║           █" "$CYAN"
print_centered "█           ██║╚██╔╝██║██║   ██║   ██║   ██║           █" "$CYAN"
print_centered "█           ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║           █" "$CYAN"
print_centered "█           ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝           █" "$CYAN"
print_centered "█                                                      █" "$CYAN"
print_centered "█               ██████╗ ███████╗ █████╗ ███╗   ███╗   █" "$WHITE"
print_centered "█               ██╔══██╗██╔════╝██╔══██╗████╗ ████║   █" "$WHITE"
print_centered "█               ██████╔╝█████╗  ███████║██╔████╔██║   █" "$WHITE"
print_centered "█               ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║   █" "$WHITE"
print_centered "█               ██████╔╝███████╗██║  ██║██║ ╚═╝ ██║   █" "$WHITE"
print_centered "█               ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝   █" "$WHITE"
print_centered "█                                                      █" "$CYAN"
print_centered "█                    SPATIAL OS v1.0                   █" "$BLUE"
print_centered "█            Human-Centered Computing Platform         █" "$BLUE"
print_centered "█                                                      █" "$CYAN"
print_centered "████████████████████████████████████████████████████████" "$CYAN"

echo ""
print_centered "Initializing System..." "$WHITE"
echo ""

# Simple loading animation
print_centered "▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ Loading..." "$CYAN"
sleep 1

# Clear and ready
clear
tput cnorm  # Show cursor again
