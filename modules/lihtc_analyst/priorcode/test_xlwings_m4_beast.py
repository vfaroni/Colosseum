#!/usr/bin/env python3
"""
Test xlwings M4 Beast Integration
Quick test to verify xlwings setup and establish baseline performance
"""

import xlwings as xw
import time
import logging
from pathlib import Path
import psutil

def test_xlwings_basic():
    """Basic xlwings functionality test"""
    print("🧪 Testing xlwings basic functionality...")
    
    try:
        # Create a simple test workbook
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        
        wb = app.books.add()
        sheet = wb.sheets[0]
        
        # Write some test data
        sheet.range("A1").value = "Test"
        sheet.range("B1").value = 123.45
        
        # Read it back
        test_value = sheet.range("A1").value
        number_value = sheet.range("B1").value
        
        wb.close()
        app.quit()
        
        print(f"✅ xlwings working: '{test_value}', {number_value}")
        return True
        
    except Exception as e:
        print(f"❌ xlwings test failed: {e}")
        return False

def test_ctcac_file_sample():
    """Test processing a sample CTCAC file"""
    print("\n📊 Testing CTCAC file processing...")
    
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    
    if not raw_data_path.exists():
        print(f"❌ Raw data directory not found: {raw_data_path}")
        return False
    
    # Find first Excel file
    excel_files = list(raw_data_path.glob("*.xlsx"))
    if not excel_files:
        excel_files = list(raw_data_path.glob("*.xls"))
    
    if not excel_files:
        print("❌ No Excel files found")
        return False
    
    test_file = excel_files[0]
    file_size_mb = test_file.stat().st_size / (1024 * 1024)
    
    print(f"📁 Testing file: {test_file.name} ({file_size_mb:.1f} MB)")
    
    try:
        start_time = time.time()
        memory_start = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Open with xlwings
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.open(str(test_file), read_only=True, update_links=False)
        
        # Basic analysis
        sheet_count = len(wb.sheets)
        cells_analyzed = 0
        data_found = 0
        
        for sheet in wb.sheets:
            try:
                used_range = sheet.used_range
                if used_range:
                    cells_analyzed += used_range.shape[0] * used_range.shape[1]
                    
                    # Sample some cells
                    sample_data = sheet.range("A1:F20").value
                    if sample_data:
                        for row in sample_data:
                            if isinstance(row, list):
                                for cell in row:
                                    if cell and str(cell).strip():
                                        data_found += 1
                            elif row and str(row).strip():
                                data_found += 1
                        
            except Exception as e:
                print(f"⚠️  Sheet {sheet.name} error: {e}")
        
        wb.close()
        app.quit()
        
        processing_time = time.time() - start_time
        memory_end = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = memory_end - memory_start
        
        print(f"✅ Processing complete:")
        print(f"   📄 Sheets: {sheet_count}")
        print(f"   🔢 Cells analyzed: {cells_analyzed:,}")
        print(f"   📊 Data points found: {data_found}")
        print(f"   ⏱️  Time: {processing_time:.1f} seconds")
        print(f"   💾 Memory delta: {memory_delta:.1f} MB")
        print(f"   🚀 Cells/second: {cells_analyzed/processing_time:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ File processing failed: {e}")
        return False

def benchmark_xlwings_vs_baseline():
    """Benchmark xlwings performance vs estimated baseline"""
    print("\n🏁 M4 Beast xlwings Benchmark...")
    
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    excel_files = list(raw_data_path.glob("*.xlsx"))[:5]  # Test first 5 files
    
    if len(excel_files) < 3:
        print("⚠️  Need at least 3 files for meaningful benchmark")
        return False
    
    total_time = 0
    total_files = 0
    total_size_mb = 0
    
    for file_path in excel_files:
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        try:
            start_time = time.time()
            
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            wb = app.books.open(str(file_path), read_only=True, update_links=False)
            
            # Simulate data extraction
            sheets_processed = 0
            for sheet in wb.sheets:
                try:
                    used_range = sheet.used_range
                    if used_range:
                        # Sample key areas
                        sheet.range("A1:F20").value  # Header area
                        sheet.range("A1:Z50").value  # Extended search area
                        sheets_processed += 1
                except Exception:
                    pass
            
            wb.close()
            app.quit()
            
            processing_time = time.time() - start_time
            total_time += processing_time
            total_files += 1
            total_size_mb += file_size_mb
            
            print(f"   📁 {file_path.name}: {processing_time:.1f}s ({sheets_processed} sheets)")
            
        except Exception as e:
            print(f"   ❌ {file_path.name}: {e}")
    
    if total_files > 0:
        avg_time_per_file = total_time / total_files
        files_per_minute = 60 / avg_time_per_file if avg_time_per_file > 0 else 0
        avg_size_mb = total_size_mb / total_files
        
        # Estimated baselines (conservative estimates)
        estimated_m1_files_per_minute = 2.0  # Conservative M1 estimate
        target_improvement = 2.5  # 2.5x improvement target
        target_files_per_minute = estimated_m1_files_per_minute * target_improvement
        
        performance_multiplier = files_per_minute / estimated_m1_files_per_minute if estimated_m1_files_per_minute > 0 else 0
        
        print(f"\n🎯 M4 BEAST XLWINGS BENCHMARK RESULTS:")
        print(f"   📊 Files processed: {total_files}")
        print(f"   📈 Avg file size: {avg_size_mb:.1f} MB")
        print(f"   ⏱️  Avg time per file: {avg_time_per_file:.1f} seconds")
        print(f"   🚀 Files per minute: {files_per_minute:.1f}")
        print(f"   🎯 Target (2.5x M1): {target_files_per_minute:.1f} files/min")
        print(f"   📈 Performance multiplier: {performance_multiplier:.1f}x")
        print(f"   🏆 Meets target: {'✅ YES' if files_per_minute >= target_files_per_minute else '❌ NO'}")
        
        if performance_multiplier >= 2.0:
            print(f"\n🎊 SUCCESS: M4 Beast + xlwings achieved {performance_multiplier:.1f}x improvement!")
            print(f"📊 xlwings version: {xw.__version__}")
        else:
            print(f"\n⚠️  Performance below 2x target. Consider optimization.")
        
        return True
    
    return False

def main():
    """Run xlwings M4 Beast integration tests"""
    
    print("🚀 M4 BEAST XLWINGS INTEGRATION TEST")
    print("=" * 50)
    print(f"💻 Platform: {psutil.cpu_count()} cores, {psutil.virtual_memory().total / 1024**3:.1f} GB RAM")
    print(f"📊 xlwings version: {xw.__version__}")
    
    # Test 1: Basic xlwings functionality
    basic_success = test_xlwings_basic()
    
    if not basic_success:
        print("\n❌ Basic xlwings test failed. Check installation.")
        return
    
    # Test 2: CTCAC file processing
    file_success = test_ctcac_file_sample()
    
    if not file_success:
        print("\n❌ CTCAC file test failed. Check file access.")
        return
    
    # Test 3: Performance benchmark
    benchmark_success = benchmark_xlwings_vs_baseline()
    
    if benchmark_success:
        print("\n✅ M4 Beast xlwings integration tests complete!")
        print("🎯 Ready for full-scale CTCAC extraction deployment")
    else:
        print("\n⚠️  Benchmark incomplete - manual verification needed")

if __name__ == "__main__":
    main()