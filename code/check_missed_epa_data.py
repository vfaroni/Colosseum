#!/usr/bin/env python3
"""
Check what EPA data we missed by not going deep enough
"""

import requests
from bs4 import BeautifulSoup
import time

def check_directory(path, max_depth=3, current_depth=0):
    """Check an EPA directory for nested data"""
    if current_depth >= max_depth:
        return []
    
    url = f"https://edg.epa.gov/data/public/{path}/"
    print(f"\n{'  ' * current_depth}Checking: {path}/")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        findings = []
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.text.strip()
            
            if 'Parent Directory' in text or not href:
                continue
            
            # Check for files
            if '.' in href and not href.endswith('/'):
                # Found a file
                size_text = link.parent.parent.text if link.parent.parent else ''
                findings.append({
                    'path': f"{path}/{text}",
                    'file': text,
                    'type': 'file'
                })
                print(f"{'  ' * (current_depth + 1)}📄 {text}")
            
            # Check for subdirectories
            elif href.endswith('/') and not href.startswith('/'):
                subdir = href.rstrip('/')
                if 'metadata' not in subdir.lower():
                    # Recursively check subdirectory
                    sub_path = f"{path}/{subdir}" if path else subdir
                    time.sleep(0.5)  # Be nice
                    sub_findings = check_directory(sub_path, max_depth, current_depth + 1)
                    findings.extend(sub_findings)
        
        return findings
        
    except Exception as e:
        print(f"{'  ' * current_depth}❌ Error: {str(e)[:50]}")
        return []

print("="*80)
print("CHECKING MISSED EPA REGIONS FOR NESTED DATA")
print("="*80)

# Check regions that appeared empty but might have nested data
regions_to_check = {
    'R4': ['metadata', ''],  # You found metadata subdirectory
    'R2': [''],
    'R5': [''],
    'R6': [''],
    'R10': ['']
}

all_findings = {}

for region, subdirs in regions_to_check.items():
    print(f"\n🔍 REGION {region}:")
    print("-"*40)
    
    region_findings = []
    
    for subdir in subdirs:
        path = f"{region}/{subdir}" if subdir else region
        findings = check_directory(path, max_depth=2)
        region_findings.extend(findings)
        time.sleep(1)
    
    all_findings[region] = region_findings
    
    if region_findings:
        print(f"\n  ✅ Found {len(region_findings)} items in {region}")
    else:
        print(f"\n  ❌ No data found in {region}")

print("\n" + "="*80)
print("SUMMARY OF MISSED DATA:")
print("-"*40)

for region, findings in all_findings.items():
    if findings:
        print(f"\n{region}: {len(findings)} files found")
        # Show sample files
        for f in findings[:5]:
            print(f"  - {f['file']}")
        if len(findings) > 5:
            print(f"  ... and {len(findings) - 5} more")

print("\n" + "="*80)
print("CONCLUSION:")
print("-"*40)
print("The crawler should have gone at least 2-3 levels deep!")
print("We missed data in nested subdirectories, especially /metadata/ folders")
print("="*80)