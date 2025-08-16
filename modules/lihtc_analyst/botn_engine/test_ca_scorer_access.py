#!/usr/bin/env python3
"""
Test CA LIHTC Scorer Access
Simple test to verify we can access the CA LIHTC Scorer system.
"""

import sys
import os
from pathlib import Path

# Test direct access to CA LIHTC Scorer
ca_scorer_path = Path(__file__).parent.parent / "priorcode/!VFupload/CALIHTCScorer"
print(f"CA LIHTC Scorer path: {ca_scorer_path}")
print(f"Path exists: {ca_scorer_path.exists()}")

if ca_scorer_path.exists():
    src_path = ca_scorer_path / "src"
    print(f"Src path: {src_path}")
    print(f"Src exists: {src_path.exists()}")
    
    core_path = src_path / "core"
    print(f"Core path: {core_path}")
    print(f"Core exists: {core_path.exists()}")
    
    site_analyzer_path = core_path / "site_analyzer.py"
    print(f"Site analyzer path: {site_analyzer_path}")
    print(f"Site analyzer exists: {site_analyzer_path.exists()}")
    
    # List files in directories
    if src_path.exists():
        print(f"\nFiles in src/: {list(src_path.iterdir())}")
    
    if core_path.exists():
        print(f"Files in core/: {list(core_path.iterdir())}")

# Test if we can read the site analyzer file
try:
    if site_analyzer_path.exists():
        with open(site_analyzer_path) as f:
            first_lines = f.readlines()[:10]
        print(f"\nFirst 10 lines of site_analyzer.py:")
        for i, line in enumerate(first_lines, 1):
            print(f"{i}: {line.rstrip()}")
except Exception as e:
    print(f"Error reading site_analyzer.py: {e}")

print("\n" + "="*50)
print("CA LIHTC Scorer System Access Test Complete")