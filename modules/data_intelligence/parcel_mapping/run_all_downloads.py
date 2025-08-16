#!/usr/bin/env python3

"""
Texas Regional Parcel Data - Master Download Script
Runs all 4 regional downloads in sequence
Priority Order: DFW -> San Antonio -> Austin -> Houston
"""

import subprocess
import sys
import os
from datetime import datetime

def run_download_script(script_name, region_name):
    """Run a download script and capture results"""
    print(f"\n🚀 STARTING {region_name.upper()} DOWNLOAD")
    print("=" * 60)
    
    script_path = f"/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/{script_name}"
    
    try:
        # Run the script and capture output
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=600)  # 10 minute timeout
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ STDERR OUTPUT:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {region_name} download completed successfully")
            return True
        else:
            print(f"❌ {region_name} download failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {region_name} download timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"💥 {region_name} download failed with error: {e}")
        return False

def main():
    """Run all Texas regional parcel downloads"""
    print("🏛️ TEXAS REGIONAL PARCEL DATA ACQUISITION")
    print("🚛 TRUCK MODE: Simple, Robust, Bulk Downloads")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ensure output directory exists
    output_dir = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/Texas/Parcels"
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Download scripts in priority order
    download_tasks = [
        ("download_dfw_parcels.py", "Dallas-Fort Worth"),
        ("download_san_antonio_parcels.py", "San Antonio"),
        ("download_austin_parcels.py", "Austin"),
        ("download_houston_parcels.py", "Houston")
    ]
    
    results = {}
    
    for script, region in download_tasks:
        success = run_download_script(script, region)
        results[region] = success
        
        if success:
            print(f"🎯 {region} data ready for bulk processing")
        else:
            print(f"⚠️ {region} data download incomplete - will need manual attention")
    
    # Summary report
    print("\n" + "=" * 70)
    print("📊 TEXAS REGIONAL PARCEL DOWNLOAD SUMMARY")
    print("=" * 70)
    
    total_regions = len(download_tasks)
    successful_regions = sum(results.values())
    
    print(f"✅ Successful downloads: {successful_regions}/{total_regions}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for region, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {region}: {status}")
    
    # Check output files
    print("\n📁 OUTPUT FILES:")
    expected_files = [
        "dfw_parcels.geojson",
        "san_antonio_parcels.geojson", 
        "austin_parcels.geojson",
        "houston_parcels.geojson"
    ]
    
    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            file_size_mb = round(os.path.getsize(filepath) / 1024 / 1024, 1)
            print(f"   ✅ {filename} ({file_size_mb} MB)")
        else:
            print(f"   ❌ {filename} (missing)")
    
    # Next steps
    print("\n🚀 NEXT STEPS:")
    if successful_regions >= 1:
        print("   1. Integration with environmental mapper")
        print("   2. Test with 155-site batch processing")
        print("   3. Performance validation vs API approach")
        print("   4. Validate accuracy with known D'Marco sites")
    else:
        print("   1. Check network connectivity")
        print("   2. Review data source URLs")
        print("   3. Manual download investigation required")
    
    if successful_regions == total_regions:
        print("\n🏆 ALL REGIONS DOWNLOADED SUCCESSFULLY!")
        print("Ready for bulk parcel analysis across Texas!")
    elif successful_regions > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: {successful_regions} of {total_regions} regions downloaded")
        print("Can proceed with available regions while troubleshooting others")
    else:
        print("\n💥 NO SUCCESSFUL DOWNLOADS")
        print("Manual intervention required for data acquisition")

if __name__ == "__main__":
    main()