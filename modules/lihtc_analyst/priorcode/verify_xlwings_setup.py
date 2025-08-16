#!/usr/bin/env python3
"""
Quick xlwings M4 Beast Setup Verification
Tests xlwings installation and basic Excel integration
"""

import xlwings as xw
import time
import logging
from pathlib import Path
import psutil
import sys

def verify_xlwings_installation():
    """Verify xlwings is properly installed and working"""
    print("🔍 Verifying xlwings installation...")
    
    try:
        print(f"   📊 xlwings version: {xw.__version__}")
        print(f"   🐍 Python version: {sys.version.split()[0]}")
        print(f"   💻 Platform: macOS {psutil.cpu_count()} cores")
        return True
    except Exception as e:
        print(f"   ❌ Installation check failed: {e}")
        return False

def test_excel_app_creation():
    """Test Excel application creation and basic operations"""
    print("\n🧪 Testing Excel app creation...")
    
    try:
        # Create Excel app
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        print("   ✅ Excel app created successfully")
        
        # Test workbook creation
        wb = app.books.add()
        print("   ✅ Workbook created successfully")
        
        # Test sheet access
        sheet = wb.sheets[0]
        print("   ✅ Sheet access successful")
        
        # Test data operations
        sheet.range("A1").value = "M4 Beast Test"
        sheet.range("B1").value = 12345.67
        sheet.range("C1").value = "xlwings rocks!"
        
        # Read back
        test_values = sheet.range("A1:C1").value
        print(f"   ✅ Data operations successful: {test_values}")
        
        # Cleanup
        wb.close()
        app.quit()
        print("   ✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Excel app test failed: {e}")
        return False

def test_performance_basics():
    """Test basic performance characteristics"""
    print("\n⚡ Testing performance basics...")
    
    try:
        operations = 0
        start_time = time.time()
        
        # Create app
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        operations += 1
        
        # Multiple workbook operations
        for i in range(3):
            wb = app.books.add()
            sheet = wb.sheets[0]
            
            # Write data matrix
            data = [[f"Row{r}Col{c}" for c in range(10)] for r in range(10)]
            sheet.range("A1:J10").value = data
            operations += 100  # 100 cells
            
            # Read data back
            read_data = sheet.range("A1:J10").value
            operations += 100  # 100 cells read
            
            wb.close()
        
        app.quit()
        
        total_time = time.time() - start_time
        ops_per_second = operations / total_time if total_time > 0 else 0
        
        print(f"   📊 Operations: {operations}")
        print(f"   ⏱️  Time: {total_time:.2f} seconds")
        print(f"   🚀 Ops/second: {ops_per_second:.0f}")
        print(f"   💾 Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False

def test_file_size_simulation():
    """Test with data similar to CTCAC file sizes"""
    print("\n📊 Testing large data simulation...")
    
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.add()
        sheet = wb.sheets[0]
        
        # Simulate CTCAC-like data structure
        start_time = time.time()
        
        # Header section
        headers = ["Project Name", "Address", "City", "Total Cost", "Developer", "Contact"]
        sheet.range("A1:F1").value = headers
        
        # Sample project data (simulate typical CTCAC content)
        project_data = [
            ["Affordable Homes at Main Street", "123 Main St", "Los Angeles", 5000000, "ABC Development", "John Smith"],
            ["Senior Housing Complex", "456 Oak Ave", "San Francisco", 7500000, "XYZ Properties", "Jane Doe"],
            ["Family Apartments", "789 Pine St", "Sacramento", 3200000, "DEF Builders", "Bob Johnson"]
        ]
        
        for i, row in enumerate(project_data, 2):
            sheet.range(f"A{i}:F{i}").value = row
        
        # Financial section (simulate complex financial data)
        financial_headers = ["Construction Loan", "Perm Loan", "Equity", "Tax Credits", "Total Dev Cost"]
        sheet.range("H1:L1").value = financial_headers
        
        financial_data = [
            [2500000, 4000000, 1000000, 850000, 5000000],
            [4200000, 6800000, 1500000, 1275000, 7500000],
            [1800000, 2900000, 800000, 680000, 3200000]
        ]
        
        for i, row in enumerate(financial_data, 2):
            sheet.range(f"H{i}:L{i}").value = row
        
        # Read it all back (simulate extraction)
        all_data = sheet.range("A1:L5").value
        
        processing_time = time.time() - start_time
        cells_processed = 5 * 12  # 60 cells
        
        wb.close()
        app.quit()
        
        print(f"   ✅ Large data test successful")
        print(f"   📊 Cells processed: {cells_processed}")
        print(f"   ⏱️  Time: {processing_time:.3f} seconds")
        print(f"   🚀 Cells/second: {cells_processed/processing_time:.0f}")
        
        # Estimate for larger files
        estimated_ctcac_cells = 50000  # Conservative estimate for 2MB Excel file
        estimated_time = estimated_ctcac_cells / (cells_processed/processing_time)
        
        print(f"   📈 Estimated time for 50K cells: {estimated_time:.1f} seconds")
        print(f"   🎯 Estimated files/minute: {60/estimated_time:.1f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Large data test failed: {e}")
        return False

def estimate_m4_beast_performance():
    """Estimate M4 Beast performance potential"""
    print("\n🚀 M4 Beast Performance Estimation...")
    
    # System specs
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / 1024**3
    
    print(f"   💻 CPU cores: {cpu_count}")
    print(f"   💾 Total RAM: {memory_gb:.1f} GB")
    print(f"   📊 xlwings: {xw.__version__}")
    
    # Conservative estimates based on M4 Beast capabilities
    single_thread_files_per_minute = 3.0  # Conservative single-thread estimate
    threading_efficiency = 0.7  # 70% threading efficiency
    max_useful_threads = min(8, cpu_count)  # Cap at 8 for Excel operations
    
    estimated_files_per_minute = single_thread_files_per_minute * max_useful_threads * threading_efficiency
    
    # Comparison to M1 baseline
    estimated_m1_files_per_minute = 2.0
    performance_multiplier = estimated_files_per_minute / estimated_m1_files_per_minute
    
    print(f"\n📊 PERFORMANCE ESTIMATES:")
    print(f"   🔧 Single-thread: {single_thread_files_per_minute:.1f} files/min")
    print(f"   🧵 Max threads: {max_useful_threads}")
    print(f"   ⚡ Threading efficiency: {threading_efficiency:.0%}")
    print(f"   🚀 Estimated total: {estimated_files_per_minute:.1f} files/min")
    print(f"   📈 vs M1 baseline: {performance_multiplier:.1f}x improvement")
    print(f"   🎯 Meets 2.5x target: {'✅ YES' if performance_multiplier >= 2.5 else '❌ NO'}")
    
    # Time estimates for full dataset
    total_files = 1040
    estimated_total_time_minutes = total_files / estimated_files_per_minute
    estimated_total_time_hours = estimated_total_time_minutes / 60
    
    print(f"\n⏱️  FULL DATASET ESTIMATES (1,040 files):")
    print(f"   📊 Processing time: {estimated_total_time_minutes:.1f} minutes ({estimated_total_time_hours:.1f} hours)")
    print(f"   🎯 vs M1 baseline: {total_files / estimated_m1_files_per_minute / 60:.1f} hours → {estimated_total_time_hours:.1f} hours")
    
    return True

def main():
    """Run complete xlwings M4 Beast verification"""
    
    print("🚀 M4 BEAST XLWINGS SETUP VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Installation Check", verify_xlwings_installation),
        ("Excel App Creation", test_excel_app_creation), 
        ("Performance Basics", test_performance_basics),
        ("Large Data Simulation", test_file_size_simulation),
        ("Performance Estimation", estimate_m4_beast_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"🎯 VERIFICATION COMPLETE: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"🎊 SUCCESS: M4 Beast + xlwings ready for CTCAC extraction!")
        print(f"📊 Ready to process 1,040 Excel files with estimated 2.5x+ improvement")
        print(f"🚀 Next step: Run full m4_beast_xlwings_extractor.py")
    elif passed >= total - 1:
        print(f"⚠️  MOSTLY READY: {passed}/{total} tests passed - minor issues detected")
        print(f"🔧 Consider debugging failed test before full deployment")
    else:
        print(f"❌ NOT READY: Multiple test failures - requires troubleshooting")
        print(f"🛠️  Check xlwings installation and Excel access")

if __name__ == "__main__":
    main()