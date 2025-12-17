#!/bin/bash

cd "$(dirname "$0")"

# Launch directly - pygame splash handles the boot screen
# Suppress all output to hide any pygame initialization messages
python3 spatial_os.py >/dev/null 2>&1
