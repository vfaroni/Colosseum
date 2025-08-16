#!/usr/bin/env python3
"""
Fixed CTCAC Extractor with proper Excel instance management
Addresses: Multiple Excel instances opening and not closing properly
"""

import xlwings as xw
import time
from pathlib import Path
from wingman_ctcac_extractor_v2 import WingmanCTCACExtractor

class ExcelCleanupExtractor(WingmanCTCACExtractor):
    """
    Enhanced extractor that properly manages Excel instances
    - Uses single Excel app for multiple files
    - Properly closes workbooks after each file
    - Prevents Excel instance accumulation
    """
    
    def __init__(self, performance_mode="optimized"):
        super().__init__(performance_mode)
        self.excel_app = None
        self.files_processed = 0
        
    def _initialize_excel_app(self):
        """Initialize single Excel application instance"""
        if self.excel_app is None:
            print("🚀 Initializing single Excel application...")
            self.excel_app = xw.App(visible=False, add_book=False)
            self.excel_app.display_alerts = False
            self.excel_app.screen_updating = False
            if hasattr(self.excel_app, 'calculation'):
                self.excel_app.calculation = "manual"
            print("   ✅ Excel app initialized")
        return self.excel_app
    
    def extract_single_file(self, file_path):
        """
        Extract data from single file with proper Excel cleanup
        """
        start_time = time.time()
        result = None
        wb = None
        
        try:
            # Convert to Path object if string
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            print(f"📊 Processing: {file_path.name}")
            
            # Initialize Excel app (reuse existing if available)
            app = self._initialize_excel_app()
            
            # Open workbook
            wb = app.books.open(str(file_path), read_only=True, update_links=False)
            print(f"   📋 Total sheets: {len(wb.sheets)}")
            
            # Use parent class extraction logic
            result = self._extract_with_workbook(wb, file_path)
            
            # Processing stats
            processing_time = time.time() - start_time
            self.files_processed += 1
            
            print(f"   ⏱️  Processing time: {processing_time:.2f}s")
            print(f"   📊 Files processed in session: {self.files_processed}")
            
        except Exception as e:
            print(f"   ❌ Extraction error: {e}")
            if result is None:
                result = self._create_error_result(file_path, str(e))
        
        finally:
            # CRITICAL: Always close workbook but keep app open
            if wb is not None:
                try:
                    wb.close()
                    print(f"   ✅ Workbook closed: {file_path.name}")
                except Exception as e:
                    print(f"   ⚠️  Workbook close warning: {e}")
        
        return result
    
    def extract_batch_2025_4pct(self, max_files=5):
        """
        Extract batch of 2025 4% applications with proper cleanup
        """
        print("🎯 BATCH EXTRACTION - 2025 4% APPLICATIONS ONLY")
        print("=" * 60)
        
        # Find 2025 4% files
        raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
        
        # Filter for 2025 4% files
        pattern = "*2025*4pct*.xlsx"
        files_2025_4pct = list(raw_data_path.glob(pattern))
        
        print(f"🔍 Found {len(files_2025_4pct)} files matching pattern: {pattern}")
        
        if not files_2025_4pct:
            print("❌ No 2025 4% files found")
            return []
        
        # Limit to max_files for testing
        test_files = files_2025_4pct[:max_files]
        print(f"📋 Processing {len(test_files)} files for testing:")
        for i, file_path in enumerate(test_files, 1):
            print(f"   {i}. {file_path.name}")
        
        # Process files with single Excel instance
        results = []
        
        try:
            for i, file_path in enumerate(test_files, 1):
                print(f"\n🏗️  File {i}/{len(test_files)}: {file_path.name}")
                result = self.extract_single_file(file_path)
                if result:
                    results.append(result)
                
                # Small delay to prevent overload
                time.sleep(0.5)
        
        finally:
            # Close Excel application at end of batch
            self._cleanup_excel_app()
        
        print(f"\n✅ BATCH COMPLETE: {len(results)} files successfully processed")
        return results
    
    def _cleanup_excel_app(self):
        """Properly close Excel application"""
        if self.excel_app is not None:
            try:
                print("🔄 Closing Excel application...")
                self.excel_app.quit()
                self.excel_app = None
                print("   ✅ Excel application closed")
            except Exception as e:
                print(f"   ⚠️  Excel cleanup warning: {e}")
    
    def _extract_with_workbook(self, wb, file_path):
        """
        Extract data using existing workbook (reuse parent logic)
        """
        # This method contains the main extraction logic from parent class
        # but without opening/closing the workbook
        
        # Import required classes
        from ctcac_data_structures import CTCACExtractionResult
        from datetime import datetime
        import psutil
        
        result = CTCACExtractionResult()
        
        # Initialize result metadata
        result.filename = file_path.name
        result.file_path = str(file_path)
        result.file_size_mb = file_path.stat().st_size / (1024 * 1024)
        result.extraction_start_time = datetime.now().isoformat()
        
        # Memory tracking
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        # Find and extract Sources & Uses
        sources_uses_sheet = self._find_sources_uses_sheet(wb)
        if sources_uses_sheet:
            print(f"   🎯 Found Sources & Uses sheet: '{sources_uses_sheet.name}'")
            sources_uses_data = self._extract_sources_uses_budget(sources_uses_sheet)
            if sources_uses_data:
                result.sources_uses_data = sources_uses_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Sources & Uses extraction: {sources_uses_data.data_completeness_percent:.1f}% complete")
        
        # Find and extract Basis Breakdown
        basis_sheet = self._find_sources_uses_sheet(wb)  # Often same sheet
        if basis_sheet:
            basis_data = self._extract_basis_breakdown(basis_sheet)
            if basis_data:
                result.basis_breakdown_data = basis_data
                result.sections_successfully_extracted += 1
                validation_status = "PASSED" if basis_data.basis_mathematical_check else "FAILED"
                print(f"   ✅ Mathematical validation: {validation_status}")
        
        # Enhanced Application extraction
        app_sheet = self._find_application_sheet(wb)
        if app_sheet:
            print(f"   🎯 Enhanced Application extraction starting...")
            print(f"   🎯 Found Application sheet: '{app_sheet.name}'")
            app_data = self.enhanced_app_extractor.extract_application_data(app_sheet)
            if app_data:
                result.application_data = app_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Enhanced extraction: {app_data.fields_extracted}/35 fields ({app_data.extraction_confidence:.1f}% confidence)")
        
        # Additional tabs (Points, Tie-Breaker, etc.)
        print(f"   🎯 Phase 1B: Additional application tabs...")
        
        # Calculate final metrics
        final_memory = process.memory_info().rss / (1024 * 1024)
        result.memory_usage_mb = final_memory - initial_memory
        result.total_processing_time_seconds = time.time() - time.time()  # Will be set by caller
        
        # Mathematical validation
        if result.sources_uses_data:
            validation_result = self._validate_mathematical_accuracy(result.sources_uses_data)
            result.mathematical_validation_passed = validation_result.passed
        
        return result
    
    def _create_error_result(self, file_path, error_message):
        """Create error result for failed extractions"""
        from ctcac_data_structures import CTCACExtractionResult
        
        result = CTCACExtractionResult()
        result.filename = file_path.name if hasattr(file_path, 'name') else str(file_path)
        result.extraction_error = error_message
        result.mathematical_validation_passed = False
        return result

def test_excel_cleanup():
    """Test the Excel cleanup functionality"""
    print("🧪 TESTING EXCEL CLEANUP EXTRACTOR")
    print("=" * 50)
    
    extractor = ExcelCleanupExtractor(performance_mode="optimized")
    
    # Test with 2025 4% applications
    results = extractor.extract_batch_2025_4pct(max_files=3)
    
    print(f"\n📊 TEST RESULTS:")
    for i, result in enumerate(results, 1):
        if hasattr(result, 'filename'):
            math_status = "✅" if result.mathematical_validation_passed else "❌"
            print(f"   {i}. {result.filename}: {math_status} Math validation")
    
    return results

if __name__ == "__main__":
    test_results = test_excel_cleanup()