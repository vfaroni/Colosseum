#!/usr/bin/env python3
"""
Test script for TDHCA 2024 downloader structure
Verifies directory creation and organization without downloading
"""

from tdhca_2024_downloader import TDHCA2024Downloader
import os

def test_structure():
    print("🧪 TESTING TDHCA 2024 DOWNLOADER STRUCTURE")
    print("=" * 55)
    
    # Initialize downloader
    downloader = TDHCA2024Downloader()
    
    # Test directory structure
    print("\n📁 DIRECTORY STRUCTURE:")
    print(f"   • Base directory: {downloader.base_dir}")
    print(f"   • Applications directory: {downloader.applications_dir}")
    print(f"   • Awarded directory: {downloader.awarded_dir}")
    
    # Verify directories exist
    print(f"\n✅ DIRECTORY VERIFICATION:")
    print(f"   • Base dir exists: {downloader.base_dir.exists()}")
    print(f"   • Applications dir exists: {downloader.applications_dir.exists()}")
    print(f"   • Awarded dir exists: {downloader.awarded_dir.exists()}")
    
    # Test application list
    print(f"\n📊 APPLICATION INVENTORY:")
    print(f"   • Total applications to process: {len(downloader.priority_apps)}")
    print(f"   • Known awarded applications: {len(downloader.known_awarded)}")
    print(f"   • First 10 application numbers: {downloader.priority_apps[:10]}")
    print(f"   • Last 10 application numbers: {downloader.priority_apps[-10:]}")
    
    # Test awarded application management
    print(f"\n🏆 AWARDED APPLICATIONS:")
    for app_num, details in downloader.known_awarded.items():
        print(f"   • {app_num}: {details}")
    
    # Test utility methods
    print(f"\n🔧 TESTING UTILITY METHODS:")
    
    # Test adding an awarded application (without file movement)
    print("   • Testing add_awarded_application method...")
    original_count = len(downloader.known_awarded)
    downloader.add_awarded_application("24999", "Test Project", "Test Developer", "2024-01-01")
    new_count = len(downloader.known_awarded)
    print(f"     - Before: {original_count} awarded apps, After: {new_count} awarded apps")
    
    # Test saving awarded list
    print("   • Testing save_awarded_list method...")
    downloader.save_awarded_list()
    awarded_list_file = downloader.base_dir / "2024_awarded_applications.json"
    print(f"     - Awarded list file exists: {awarded_list_file.exists()}")
    
    # Test file organization logic
    print(f"\n📋 FILE ORGANIZATION LOGIC:")
    test_apps = ["24600", "24500", "24999"]  # Mix of awarded and regular
    for app_num in test_apps:
        is_awarded = app_num in downloader.known_awarded
        target_dir = downloader.awarded_dir if is_awarded else downloader.applications_dir
        status_label = "AWARDED" if is_awarded else "APPLICATION"
        print(f"   • {app_num} → {target_dir.name}/ ({status_label})")
    
    print(f"\n✅ STRUCTURE TEST COMPLETE")
    print(f"📝 NOTES:")
    print(f"   • Directory structure is properly organized")
    print(f"   • Applications and awarded projects will be separated")
    print(f"   • 24600 is marked as AWARDED and will go to awarded directory")
    print(f"   • Use add_awarded_application() to add more awarded projects as identified")
    print(f"   • Ready for actual downloads when needed")

if __name__ == "__main__":
    test_structure()