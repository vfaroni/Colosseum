#!/usr/bin/env python3
"""
Simple diagnostic to find out why your comprehensive extractor isn't working
"""

from pathlib import Path

def main():
    print("🔍 DEBUGGING YOUR COMPREHENSIVE EXTRACTOR")
    print("=" * 60)
    
    # Check the exact path from your code
    input_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data'
    
    print(f"📁 Checking input path: {input_path}")
    
    input_dir = Path(input_path)
    print(f"Directory exists: {input_dir.exists()}")
    
    if not input_dir.exists():
        print("❌ MAIN ISSUE: Input directory doesn't exist")
        print(f"Current working directory: {Path.cwd()}")
        
        # Check if it's a path issue
        parts = input_path.split('/')
        print("Checking path components:")
        
        current_path = Path('/')
        for part in parts[1:]:  # Skip empty first element
            current_path = current_path / part
            exists = current_path.exists()
            print(f"  {current_path}: {'✅' if exists else '❌'}")
            
            if not exists:
                print(f"  ❌ Path breaks at: {current_path}")
                
                # Show what's actually in the parent directory
                parent = current_path.parent
                if parent.exists():
                    print(f"  Contents of {parent}:")
                    for item in list(parent.iterdir())[:10]:
                        print(f"    - {item.name}")
                break
        return
    
    # Check for Excel files
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    print(f"Excel files found: {len(excel_files)}")
    
    if len(excel_files) == 0:
        print("❌ ISSUE: No Excel files in directory")
        all_files = list(input_dir.iterdir())[:10]
        print("Sample directory contents:")
        for item in all_files:
            print(f"  - {item.name}")
        return
    
    print(f"✅ Found {len(excel_files)} Excel files")
    print("Sample files:")
    for i, file in enumerate(excel_files[:3]):
        print(f"  {i+1}. {file.name}")
    
    # Test basic imports
    print(f"\n🐍 Testing imports...")
    try:
        import openpyxl
        print("✅ openpyxl imported")
        
        # Test opening one file
        test_file = excel_files[0]
        print(f"Testing file: {test_file.name}")
        
        workbook = openpyxl.load_workbook(test_file, data_only=True)
        print(f"✅ Successfully opened Excel file")
        print(f"Sheets found: {len(workbook.sheetnames)}")
        workbook.close()
        
    except Exception as e:
        print(f"❌ Import/file error: {e}")
        return
    
    print(f"\n🎯 CONCLUSION:")
    print(f"Your comprehensive extractor should work fine!")
    print(f"The issue is likely:")
    print(f"  1. The main() function isn't being called")
    print(f"  2. The extractor class isn't being instantiated")
    print(f"  3. There's a silent error during processing")
    
    print(f"\n💡 TO FIX:")
    print(f"  1. Make sure you're running: python enhanced_ctcac_extractor_complete-2.py")
    print(f"  2. Check that if __name__ == '__main__': main() is at the bottom")
    print(f"  3. Look for any error messages in the console output")

if __name__ == "__main__":
    main()
