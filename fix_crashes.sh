#!/bin/bash
# Fix realm crashes - disable ENTER in Marketplace and Education

cd ~/motibeam-spatial-os

# Backup
cp spatial_os.py spatial_os.py.before-crash-fix

# Fix Marketplace ENTER (line ~1051)
sed -i "/def handle_marketplace_input/,/^    def / {
  s/self.realm_data\['marketplace'\]\['preview_open'\] = not preview_open/pass  # Disabled - panel rendering causes Pi reboot/
}" spatial_os.py

# Fix Education ENTER (line ~1410)  
sed -i "/def handle_education_input/,/^    def / {
  s/self.realm_data\['education'\]\['panel_open'\] = not panel_open/pass  # Disabled - panel rendering causes Pi reboot/
}" spatial_os.py

echo "Fixes applied! Test with: python3 spatial_os.py"
