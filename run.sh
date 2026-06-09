#!/bin/bash
cd "$(dirname "$0")"
exec python3 -u spatial_os.py 2>&1 | tee /tmp/motibeam.log
