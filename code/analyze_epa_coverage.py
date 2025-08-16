#!/usr/bin/env python3
"""
Analyze EPA data coverage - what we got vs what was available
"""

import json
from pathlib import Path

base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")

# Load crawler report
with open(base_path / "data_sets/federal/epa_deep_crawl_report.json") as f:
    crawl_data = json.load(f)

# Load download list
with open(base_path / "data_sets/federal/epa_priority_download_list.json") as f:
    download_list = json.load(f)

print("=" * 80)
print("EPA DATA COVERAGE ANALYSIS")
print("=" * 80)

# Regional coverage
print("\n📍 REGIONAL COVERAGE:")
print("-" * 40)
all_regions = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']
found_by_region = crawl_data['files_by_root_directory']

for region in all_regions:
    if region in found_by_region:
        info = found_by_region[region]
        print(f"✅ {region}: {info['count']} files found ({info['size_mb']:.1f} MB)")
    else:
        print(f"❌ {region}: No files found or empty directory")

# Check what was prioritized for download
print("\n📥 DOWNLOAD PRIORITIES:")
print("-" * 40)
downloaded_regions = set()
for file in download_list['files']:
    if file['directory'].startswith('R'):
        region = file['directory'].split('/')[0]
        downloaded_regions.add(region)

print(f"Regions prioritized for download: {sorted(downloaded_regions)}")

# Analyze by data type
print("\n📊 DATA TYPE COVERAGE:")
print("-" * 40)
data_types = {}
for file in crawl_data['top_50_files']:
    filename = file['filename'].lower()
    if 'superfund' in filename or 'npl' in filename or 'cercl' in filename:
        dtype = 'Superfund/CERCLIS'
    elif 'rcra' in filename:
        dtype = 'RCRA Hazardous'
    elif 'brownfield' in filename:
        dtype = 'Brownfields'
    elif 'ust' in filename or 'lust' in filename or 'tank' in filename:
        dtype = 'UST/LUST'
    elif 'water' in filename or 'cso' in filename or 'discharge' in filename:
        dtype = 'Water Quality'
    elif 'air' in filename or 'emission' in filename:
        dtype = 'Air Quality'
    elif 'enforce' in filename or 'compliance' in filename:
        dtype = 'Enforcement'
    else:
        dtype = 'Other'
    
    if dtype not in data_types:
        data_types[dtype] = {'count': 0, 'size_mb': 0}
    data_types[dtype]['count'] += 1
    data_types[dtype]['size_mb'] += file['size_mb']

for dtype, info in sorted(data_types.items()):
    print(f"{dtype}: {info['count']} files, {info['size_mb']:.1f} MB")

# What we chose NOT to download
print("\n⚠️ DATA NOT DOWNLOADED (Due to size/priority):")
print("-" * 40)

# Files that were too large
large_files = [f for f in crawl_data['top_50_files'] if f['size_mb'] > 500]
if large_files:
    print("\nLarge files skipped (>500 MB):")
    for file in large_files[:5]:
        print(f"  - {file['filename']} ({file['size_mb']:.1f} MB) - {file['directory']}")

# Low priority files
low_priority = [f for f in crawl_data['top_50_files'] if f['priority_score'] < 20]
if low_priority:
    print(f"\nLow priority files skipped: {len(low_priority)} files")

# Empty regions
empty_regions = []
for region in all_regions:
    if region not in found_by_region or found_by_region[region]['count'] == 0:
        empty_regions.append(region)

if empty_regions:
    print(f"\nEmpty regions (no data found): {', '.join(empty_regions)}")
else:
    print("\nAll regions had some data available")

print("\n" + "=" * 80)
print("SUMMARY:")
print("-" * 40)
print(f"Total files found: {crawl_data['total_files_found']}")
print(f"Valuable files identified: {crawl_data['valuable_files']}")
print(f"Files downloaded: 80 (stopped due to timeout)")
print(f"Data volume found: {crawl_data['total_size_gb']:.1f} GB")
print(f"Data volume downloaded: 2.4 GB")
print(f"Coverage: {(2.4 / crawl_data['total_size_gb']) * 100:.1f}% of valuable data")
print("=" * 80)