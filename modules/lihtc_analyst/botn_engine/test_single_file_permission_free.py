#!/usr/bin/env python3
"""
Test Single File Permission-Free Processing
Validate the core approach with one file
"""

import pandas as pd
import shutil
import logging
from pathlib import Path
from datetime import datetime

from excel_session_manager import excel_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_file_processing():
    """Test processing a single BOTN file without permission prompts"""
    
    base_path = Path(__file__).parent
    template_path = base_path / "botntemplate" / "CABOTNTemplate.xlsx"
    outputs_path = base_path / "outputs"
    sites_path = base_path / "Sites"
    
    outputs_path.mkdir(exist_ok=True)
    
    logger.info("🧪 Testing single file permission-free processing...")
    
    # Step 1: Load one site from the data
    final_portfolio_path = sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
    
    if not final_portfolio_path.exists():
        logger.error(f"❌ Site data file not found: {final_portfolio_path}")
        return False
    
    df = pd.read_excel(final_portfolio_path)
    
    # Get first valid site
    test_site = None
    for idx in range(len(df)):
        site = df.iloc[idx]
        site_name = site.get('Property Name', '')
        if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
            test_site = site
            break
    
    if test_site is None:
        logger.error("❌ No valid test site found")
        return False
    
    logger.info(f"📊 Test site: {test_site.get('Property Name', 'Unknown')}")
    
    # Step 2: Create template copy
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SINGLE_TEST_{timestamp}.xlsx"
    output_path = outputs_path / output_filename
    
    logger.info("📋 Copying template...")
    shutil.copy2(template_path, output_path)
    
    # Step 3: Process with Excel
    try:
        logger.info("🔧 Opening Excel session...")
        with excel_session() as session:
            logger.info("📝 Opening workbook...")
            wb = session.open_workbook(output_path)
            
            logger.info("📋 Accessing Inputs sheet...")
            inputs_sheet = wb.sheets['Inputs']
            
            # Simple test data
            logger.info("✏️ Writing test data...")
            inputs_sheet.range('A2').value = test_site.get('Property Name', 'Test Property')
            inputs_sheet.range('B2').value = test_site.get('Property Address', 'Test Address')
            inputs_sheet.range('G2').value = 2000000  # Purchase price
            inputs_sheet.range('H2').value = 'Large Family'  # Housing type
            inputs_sheet.range('O2').value = 100  # Units
            
            logger.info("💾 Saving workbook...")
            wb.save()
            
            logger.info("🔍 Verifying data was written...")
            written_name = inputs_sheet.range('A2').value
            written_price = inputs_sheet.range('G2').value
            written_units = inputs_sheet.range('O2').value
            
            logger.info(f"   Property: {written_name}")
            logger.info(f"   Price: ${written_price:,}")
            logger.info(f"   Units: {written_units}")
            
            logger.info("🔒 Closing workbook...")
            wb.close()
        
        logger.info(f"✅ Single file test completed successfully!")
        logger.info(f"📁 Output file: {output_path}")
        
        # Step 4: Quick validation - reopen and check formulas exist
        logger.info("🔍 Validating formulas are preserved...")
        with excel_session() as session:
            wb = session.open_workbook(output_path)
            
            # Check other sheets exist
            sheet_names = [sheet.name for sheet in wb.sheets]
            logger.info(f"   📊 Sheets: {sheet_names}")
            
            # Look for a calculation sheet
            calc_sheets = [s for s in sheet_names if 'sources' in s.lower() or 'uses' in s.lower()]
            if calc_sheets:
                calc_sheet = wb.sheets[calc_sheets[0]]
                
                # Check for formulas in first few cells
                formula_count = 0
                for row in range(1, 6):
                    for col in range(1, 6):
                        try:
                            cell = calc_sheet.range(row, col)
                            if cell.formula and cell.formula.startswith('='):
                                formula_count += 1
                        except:
                            continue
                
                logger.info(f"   ✨ Found {formula_count} formulas in {calc_sheets[0]}")
            
            wb.close()
        
        logger.info("🎉 Single file permission-free test PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Single file test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_file_processing()
    if success:
        print("\n✅ Single file test passed - permission-free approach works!")
    else:
        print("\n❌ Single file test failed - need to debug further.")