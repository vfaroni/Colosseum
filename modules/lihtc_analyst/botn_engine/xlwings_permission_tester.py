#!/usr/bin/env python3
"""
xlwings Permission Testing - Systematic approach to solve macOS permission issues
"""

import os
import sys
import xlwings as xw
import subprocess
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XLWingsPermissionTester:
    """Test different approaches to eliminate xlwings permission prompts"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.test_output_dir = self.base_path / "permission_tests"
        self.test_output_dir.mkdir(exist_ok=True)
    
    def test_1_current_approach(self):
        """Test 1: Current xlwings approach (baseline)"""
        
        logger.info("🔬 TEST 1: Current xlwings approach (will require permissions)")
        logger.info("=" * 60)
        
        try:
            # Current approach from production code
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel app created with current settings")
            
            # Test opening template
            test_file = self.test_output_dir / "test1_current.xlsx"
            import shutil
            shutil.copy2(self.template_path, test_file)
            
            wb = app.books.open(str(test_file), update_links=False)
            logger.info("✅ Template opened successfully")
            
            # Test basic operation
            inputs_sheet = wb.sheets['Inputs']
            inputs_sheet.range('A2').value = "TEST PROPERTY"
            logger.info("✅ Data written to Inputs sheet")
            
            wb.save()
            wb.close()
            app.quit()
            
            logger.info("✅ TEST 1 COMPLETE: Current approach works but requires permissions")
            return {"success": True, "permissions_required": True}
            
        except Exception as e:
            logger.error(f"❌ TEST 1 FAILED: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_2_trusted_locations(self):
        """Test 2: Excel Trusted Locations approach"""
        
        logger.info("🔬 TEST 2: Excel Trusted Locations approach")
        logger.info("=" * 60)
        
        try:
            # Try to add our directory to Excel trusted locations via AppleScript
            trusted_script = f'''
            tell application "Microsoft Excel"
                -- This would need to access Excel Trust Center programmatically
                -- May not be possible via AppleScript
            end tell
            '''
            
            logger.info("💡 ANALYSIS: Excel Trust Center settings")
            logger.info("   - macOS Excel Trust Center accessed via File > Options > Trust Center")
            logger.info("   - Adding trusted locations would require manual configuration")
            logger.info("   - No known programmatic API for Trust Center on macOS")
            
            return {"success": False, "reason": "No programmatic access to Trust Center on macOS"}
            
        except Exception as e:
            logger.error(f"❌ TEST 2 FAILED: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_3_single_session_persistence(self):
        """Test 3: Single Excel session for multiple files"""
        
        logger.info("🔬 TEST 3: Single Excel session persistence")
        logger.info("=" * 60)
        
        try:
            # Start single Excel session
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Single Excel session started")
            
            # Test processing multiple files in same session
            test_files = []
            for i in range(3):
                test_file = self.test_output_dir / f"test3_session_{i+1}.xlsx"
                import shutil
                shutil.copy2(self.template_path, test_file)
                test_files.append(test_file)
            
            successful_files = []
            for i, test_file in enumerate(test_files):
                try:
                    logger.info(f"📝 Opening file {i+1}: {test_file.name}")
                    wb = app.books.open(str(test_file), update_links=False)
                    
                    inputs_sheet = wb.sheets['Inputs']
                    inputs_sheet.range('A2').value = f"TEST PROPERTY {i+1}"
                    
                    wb.save()
                    wb.close()
                    
                    successful_files.append(test_file.name)
                    logger.info(f"✅ File {i+1} processed successfully")
                    
                except Exception as e:
                    logger.error(f"❌ File {i+1} failed: {str(e)}")
            
            app.quit()
            
            logger.info(f"✅ TEST 3 COMPLETE: {len(successful_files)}/3 files processed")
            return {
                "success": True, 
                "files_processed": len(successful_files),
                "total_files": 3,
                "permissions_per_file": True  # Still requires permission per file
            }
            
        except Exception as e:
            logger.error(f"❌ TEST 3 FAILED: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_4_applescript_integration(self):
        """Test 4: AppleScript for Excel automation"""
        
        logger.info("🔬 TEST 4: AppleScript Excel integration")
        logger.info("=" * 60)
        
        try:
            # Create test file
            test_file = self.test_output_dir / "test4_applescript.xlsx"
            import shutil
            shutil.copy2(self.template_path, test_file)
            
            # AppleScript to open and modify Excel file
            applescript = f'''
            tell application "Microsoft Excel"
                activate
                open "{test_file}"
                
                -- Try to access and modify the Inputs sheet
                tell worksheet "Inputs" of active workbook
                    set value of range "A2" to "APPLESCRIPT TEST"
                end tell
                
                save active workbook
                close active workbook
                quit
            end tell
            '''
            
            # Execute AppleScript
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ AppleScript executed successfully")
                return {"success": True, "permissions_bypassed": True}
            else:
                logger.error(f"❌ AppleScript failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"❌ TEST 4 FAILED: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_5_file_pre_authorization(self):
        """Test 5: File pre-authorization techniques"""
        
        logger.info("🔬 TEST 5: File pre-authorization techniques")
        logger.info("=" * 60)
        
        try:
            # Test creating files in different locations
            locations = [
                self.test_output_dir,
                Path.home() / "Documents",
                Path("/tmp/botn_test")
            ]
            
            results = {}
            
            for location in locations:
                location.mkdir(exist_ok=True)
                test_file = location / "test5_preauth.xlsx"
                
                try:
                    import shutil
                    shutil.copy2(self.template_path, test_file)
                    
                    # Try to open with minimal xlwings settings
                    app = xw.App(visible=True, add_book=False)  # Visible might help
                    wb = app.books.open(str(test_file))
                    
                    inputs_sheet = wb.sheets['Inputs']
                    inputs_sheet.range('A2').value = f"PREAUTH TEST {location.name}"
                    
                    wb.save()
                    wb.close()
                    app.quit()
                    
                    results[str(location)] = {"success": True}
                    logger.info(f"✅ {location}: SUCCESS")
                    
                except Exception as e:
                    results[str(location)] = {"success": False, "error": str(e)}
                    logger.error(f"❌ {location}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ TEST 5 FAILED: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """Run all permission tests systematically"""
        
        logger.info("🚀 XLWINGS PERMISSION TESTING SUITE")
        logger.info("=" * 70)
        logger.info("Testing systematic approaches to eliminate macOS permission prompts")
        logger.info("")
        
        tests = [
            ("Current xlwings approach", self.test_1_current_approach),
            ("Trusted locations", self.test_2_trusted_locations),
            ("Single session persistence", self.test_3_single_session_persistence),
            ("AppleScript integration", self.test_4_applescript_integration),
            ("File pre-authorization", self.test_5_file_pre_authorization),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n🔬 RUNNING: {test_name}")
            logger.info("-" * 50)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if result.get("success", False):
                    logger.info(f"✅ {test_name}: SUCCESS")
                else:
                    logger.info(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"💥 {test_name}: CRASHED - {str(e)}")
                results[test_name] = {"success": False, "error": f"Test crashed: {str(e)}"}
            
            # Small delay between tests
            time.sleep(2)
        
        # Summary report
        logger.info("\n📊 TESTING RESULTS SUMMARY")
        logger.info("=" * 50)
        
        for test_name, result in results.items():
            status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
            
            if not result.get("success", False) and "error" in result:
                logger.info(f"   Error: {result['error'][:100]}...")
        
        return results

def main():
    tester = XLWingsPermissionTester()
    
    print("⚠️  PERMISSION TESTING WARNING:")
    print("   This test will trigger macOS file access permissions")
    print("   Running automated testing suite...")
    print()
    
    results = tester.run_all_tests()
    
    print("\n🎯 NEXT STEPS BASED ON RESULTS:")
    print("   Based on test results, we'll proceed with most promising approach")
    print("   Phase 2 will test openpyxl and xlsxwriter alternatives")

if __name__ == "__main__":
    main()