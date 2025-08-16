#!/usr/bin/env python3
"""Test transit data path resolution"""

from pathlib import Path
import os

print('Current dir:', os.getcwd())

# Test the path resolution
base_path = Path(__file__).parent.parent / "priorcode/!VFupload/CALIHTCScorer"
print('Calculated path:', base_path)
print('Exists:', base_path.exists())

transit_path = base_path / "data/transit/california_transit_stops_master.geojson"
print('Transit path:', transit_path)
print('Transit exists:', transit_path.exists())

# Test absolute path
abs_path = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/!VFupload/CALIHTCScorer/data/transit/california_transit_stops_master.geojson")
print('Absolute path exists:', abs_path.exists())