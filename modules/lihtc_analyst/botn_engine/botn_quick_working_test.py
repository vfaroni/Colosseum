#!/usr/bin/env python3
"""
Quick Working Test - Use visible Excel like our successful test
"""

import pandas as pd
import shutil
import xlwings as xw
from pathlib import Path
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_working_test():
    """Quick test that works - based on successful manual test"""
    
    base_path = Path(__file__).parent
    template_path = base_path / "botntemplate" / "CABOTNTemplate.xlsx"
    outputs_path = base_path / "outputs"
    sites_path = base_path / "Sites"
    
    outputs_path.mkdir(exist_ok=True)
    
    # Load one site
    portfolio_path = sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
    df = pd.read_excel(portfolio_path)
    
    test_site = None
    for idx in range(len(df)):
        site = df.iloc[idx]
        site_name = site.get('Property Name', '')
        if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
            test_site = site
            break
    
    logger.info(f"🧪 Quick test with: {test_site.get('Property Name')}")
    
    # Create one file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = outputs_path / f"QUICK_TEST_{timestamp}.xlsx"
    shutil.copy2(template_path, output_path)
    
    logger.info("📋 Template copied, opening Excel...")
    
    try:
        # Use visible Excel like our successful test
        app = xw.App(visible=True, add_book=False)
        app.display_alerts = False
        
        logger.info("📂 Opening file...")
        wb = app.books.open(str(output_path), update_links=False)
        
        logger.info("✏️ Writing data...")
        inputs_sheet = wb.sheets['Inputs']
        
        # Write minimal test data
        inputs_sheet.range('A2').value = test_site.get('Property Name', 'Test')
        inputs_sheet.range('B2').value = test_site.get('Property Address', 'Test Address')
        inputs_sheet.range('G2').value = 2000000  # Purchase price
        inputs_sheet.range('H2').value = 'Large Family'
        inputs_sheet.range('O2').value = 100  # Units
        
        logger.info("💾 Saving...")
        wb.save()
        
        logger.info("🔍 Verifying...")
        written_name = inputs_sheet.range('A2').value
        written_price = inputs_sheet.range('G2').value
        logger.info(f"   Name: {written_name}")
        logger.info(f"   Price: ${written_price:,}")
        
        wb.close()
        app.quit()
        
        logger.info(f"✅ Success! File: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Running quick working test with visible Excel...")
    print("   Excel will briefly appear - this is normal")
    
    success = quick_working_test()
    
    if success:
        print("\n✅ Quick test PASSED!")
        print("   The approach works - we can now optimize for batch processing")
    else:
        print("\n❌ Quick test failed")