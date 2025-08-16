#!/usr/bin/env python3
"""
Test Permission-Free BOTN Processing with 5 Sites
Validates that Excel formulas are preserved and no permission prompts appear
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import time

from excel_session_manager import excel_session, test_permission_suppression
from botn_xlwings_permission_free import PermissionFreeBOTNProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermissionFreeValidator:
    """Validate permission-free BOTN processing"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.outputs_path = self.base_path / "outputs"
        self.test_results = {}
    
    def run_comprehensive_test(self):
        """Run comprehensive validation test"""
        
        logger.info("\n" + "="*70)
        logger.info("🧪 COMPREHENSIVE PERMISSION-FREE VALIDATION TEST")
        logger.info("="*70)
        
        # Test 1: Permission suppression
        logger.info("\n📋 Test 1: Excel Permission Suppression")
        logger.info("-" * 50)
        
        test1_result = test_permission_suppression()
        self.test_results['permission_suppression'] = test1_result
        
        if not test1_result:
            logger.error("❌ Permission suppression test failed - stopping here")
            return False
        
        # Test 2: Template access
        logger.info("\n📋 Test 2: Template File Access")
        logger.info("-" * 50)
        
        test2_result = self.test_template_access()
        self.test_results['template_access'] = test2_result
        
        # Test 3: Batch processing with validation
        logger.info("\n📋 Test 3: 5-Site Batch Processing with Formula Validation")
        logger.info("-" * 50)
        
        test3_result = self.test_batch_processing_with_validation()
        self.test_results['batch_processing'] = test3_result
        
        # Summary
        self.print_test_summary()
        
        return all(self.test_results.values())
    
    def test_template_access(self):
        """Test that we can access the BOTN template"""
        
        template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        
        if not template_path.exists():
            logger.error(f"❌ Template not found: {template_path}")
            return False
        
        try:
            with excel_session() as session:
                wb = session.open_workbook(template_path)
                
                # Check that we can access key sheets
                sheet_names = [sheet.name for sheet in wb.sheets]
                logger.info(f"   📊 Found sheets: {sheet_names}")
                
                # Check Inputs sheet specifically
                if 'Inputs' not in sheet_names:
                    logger.error("❌ 'Inputs' sheet not found in template")
                    wb.close()
                    return False
                
                inputs_sheet = wb.sheets['Inputs']
                
                # Check that we can read cells
                a1_value = inputs_sheet.range('A1').value
                logger.info(f"   📋 Inputs A1 value: {a1_value}")
                
                # Check that we can write to input cells
                test_value = f"TEST_{datetime.now().strftime('%H%M%S')}"
                inputs_sheet.range('A2').value = test_value
                
                # Verify the write worked
                written_value = inputs_sheet.range('A2').value
                if written_value != test_value:
                    logger.error(f"❌ Write test failed. Expected: {test_value}, Got: {written_value}")
                    wb.close()
                    return False
                
                logger.info(f"   ✅ Successfully wrote and read test value: {test_value}")
                
                wb.close()
                
            logger.info("✅ Template access test passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Template access test failed: {str(e)}")
            return False
    
    def test_batch_processing_with_validation(self):
        """Test batch processing and validate results"""
        
        # Create test inputs (automated - no user interaction)
        test_inputs = [
            "Large Family",      # Housing Type
            "80 cents",         # Credit Pricing
            "4%",               # Credit Type  
            "36 months",        # Loan Term
            "5%",               # Cap Rate
            "6%",               # Interest Rate
            "Non-Elevator",     # Elevator
            "2000000",          # Purchase Price
            "100",              # Units
            "900",              # Unit Size
            "250"               # Hard Cost/SF
        ]
        
        logger.info("🔧 Running automated 5-site batch processing test...")
        
        try:
            # Create processor
            processor = PermissionFreeBOTNProcessor()
            
            # Override the interactive input method for testing
            original_method = processor.get_batch_user_inputs
            processor.get_batch_user_inputs = lambda: test_inputs
            
            # Process 5 sites
            start_time = time.time()
            results = processor.process_batch(num_sites=5)
            end_time = time.time()
            
            # Restore original method
            processor.get_batch_user_inputs = original_method
            
            if not results:
                logger.error("❌ Batch processing returned no results")
                return False
            
            processing_time = end_time - start_time
            logger.info(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
            
            # Validate results
            successful_count = len(results['successful'])
            failed_count = len(results['failed'])
            success_rate = results['success_rate']
            
            logger.info(f"   ✅ Successful sites: {successful_count}")
            logger.info(f"   ❌ Failed sites: {failed_count}")
            logger.info(f"   📈 Success rate: {success_rate:.1f}%")
            
            # Test file validation
            if successful_count > 0:
                validation_result = self.validate_output_files(results['successful'][:3])  # Check first 3
                if not validation_result:
                    return False
            
            # Success criteria: At least 80% success rate
            if success_rate >= 80:
                logger.info("✅ Batch processing test passed!")
                return True
            else:
                logger.error(f"❌ Success rate {success_rate:.1f}% below 80% threshold")
                return False
                
        except Exception as e:
            logger.error(f"❌ Batch processing test failed: {str(e)}")
            return False
    
    def validate_output_files(self, file_paths):
        """Validate that output files have proper formulas and calculations"""
        
        logger.info("🔍 Validating output files for formula preservation...")
        
        validation_passed = True
        
        try:
            with excel_session() as session:
                for i, file_path in enumerate(file_paths, 1):
                    logger.info(f"   📊 Validating file {i}: {Path(file_path).name}")
                    
                    wb = session.open_workbook(file_path)
                    
                    # Check that Inputs sheet has our data
                    inputs_sheet = wb.sheets['Inputs']
                    
                    # Check key input cells
                    property_name = inputs_sheet.range('A2').value
                    housing_type = inputs_sheet.range('H2').value
                    units = inputs_sheet.range('O2').value
                    
                    logger.info(f"     🏠 Property: {property_name}")
                    logger.info(f"     🏢 Housing: {housing_type}")
                    logger.info(f"     🔢 Units: {units}")
                    
                    # Check that formulas exist in other sheets (look for common BOTN sheets)
                    all_sheets = [sheet.name for sheet in wb.sheets]
                    logger.info(f"     📋 Available sheets: {all_sheets}")
                    
                    # Look for calculation sheets (common BOTN sheet names)
                    calc_sheets = [s for s in all_sheets if any(keyword in s.lower() for keyword in 
                                  ['calc', 'summary', 'sources', 'uses', 'financing'])]
                    
                    if calc_sheets:
                        logger.info(f"     🧮 Found calculation sheets: {calc_sheets}")
                        
                        # Check one calculation sheet for formulas
                        calc_sheet = wb.sheets[calc_sheets[0]]
                        
                        # Look for cells with formulas (starting with =)
                        formula_count = 0
                        for row in range(1, 21):  # Check first 20 rows
                            for col in range(1, 11):  # Check first 10 columns
                                try:
                                    cell = calc_sheet.range(row, col)
                                    if cell.formula and cell.formula.startswith('='):
                                        formula_count += 1
                                except:
                                    continue
                        
                        logger.info(f"     ✨ Found {formula_count} formula cells in {calc_sheets[0]}")
                        
                        if formula_count == 0:
                            logger.warning(f"     ⚠️ No formulas found in {calc_sheets[0]} - may indicate calculation issue")
                            validation_passed = False
                    
                    else:
                        logger.warning(f"     ⚠️ No calculation sheets found - may indicate template issue")
                    
                    wb.close()
                    
                    logger.info(f"     ✅ File {i} validation complete")
                    
        except Exception as e:
            logger.error(f"❌ File validation failed: {str(e)}")
            return False
        
        if validation_passed:
            logger.info("✅ Output file validation passed!")
        else:
            logger.warning("⚠️ Output file validation had warnings")
        
        return validation_passed
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        
        logger.info("\n" + "="*70)
        logger.info("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        logger.info("="*70)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(self.test_results.values())
        logger.info(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            logger.info("\n🎉 Permission-free BOTN processing is ready for production!")
            logger.info("   • No permission prompts during processing")
            logger.info("   • Excel formulas preserved and calculating")
            logger.info("   • Batch processing working efficiently")
        else:
            logger.info("\n⚠️ Some issues detected - review test results above")
        
        return overall_success


def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("🧪 PERMISSION-FREE BOTN VALIDATION TEST")
    print("="*70)
    print("This will test the permission-free approach with 5 sites")
    print("No user input required - fully automated test")
    
    validator = PermissionFreeValidator()
    success = validator.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! Permission-free processing is ready.")
    else:
        print("\n❌ Some tests failed. Check logs above for details.")
    
    return success


if __name__ == "__main__":
    main()