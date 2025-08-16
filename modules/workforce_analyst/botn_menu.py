#!/usr/bin/env python3
"""
BOTN Menu Creator
Simple menu to create BOTN files for all available deals

Author: Claude Code Assistant
Date: 2025-08-04
"""

import json
import os
from botn_file_creator import BOTNFileCreator

def create_all_botn_files():
    """Create BOTN files for all cached deals"""
    cache_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/deal_cache"
    
    # Deal name mapping
    deal_mapping = {
        "Sunset-Gardens-El-Cajon-CA.json": "Sunset Gardens - El Cajon, CA",
        "mResidences-Olympic-and-Olive-Los-Angeles-CA.json": "mResidences Olympic and Olive - Los Angeles, CA",
        "San-Pablo-Suites-Oakland-CA.json": "San Pablo Suites - Oakland, CA",
        "Baxter-Los-Angeles-CA.json": "Baxter - Los Angeles, CA"
    }
    
    creator = BOTNFileCreator()
    results = []
    
    print("🏗️ Creating BOTN files for all cached deals...")
    print("=" * 60)
    
    for filename, deal_name in deal_mapping.items():
        file_path = os.path.join(cache_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  Skipping {deal_name} - cache file not found")
            continue
            
        try:
            # Load deal data
            with open(file_path, 'r') as f:
                deal_data = json.load(f)
            
            print(f"\n📊 Processing: {deal_name}")
            print(f"   Property: {deal_data['data'].get('Property Name', 'N/A')}")
            print(f"   Units: {deal_data['data'].get('Number of Units', deal_data['data'].get('Total Units', 'N/A'))}")
            print(f"   Year Built: {deal_data['data'].get('Year Built', 'N/A')}")
            
            # Create BOTN file
            result = creator.create_botn_file(deal_name, deal_data['data'])
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result['filename']}")
                results.append(f"✅ {deal_name} → {result['filename']}")
            else:
                print(f"   ❌ FAILED: {result['error']}")
                results.append(f"❌ {deal_name} → Failed")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(f"❌ {deal_name} → Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 BOTN Creation Summary:")
    print("=" * 60)
    
    for result in results:
        print(f"  {result}")
    
    successful = len([r for r in results if r.startswith("✅")])
    total = len(results)
    
    print(f"\n🎯 Results: {successful}/{total} BOTN files created successfully")
    
    if successful > 0:
        print(f"\n📂 BOTN files are located in:")
        print(f"   /Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/")
        print(f"   [Deal Name]/BOTN/")

if __name__ == "__main__":
    print("🏢 BOTN Batch Creator")
    print("Creating BOTN files for all available deals...")
    print()
    
    create_all_botn_files()
    
    print(f"\n✨ All done! Check your Deals folder for the BOTN files.")