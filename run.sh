#!/bin/bash

cd "$(dirname "$0")"

# Show professional boot splash instead of terminal text
./boot_splash.sh

python3 spatial_os.py
