#!/usr/bin/env python3
"""
Manual Test - Check if the issue is with the specific template file
"""

import xlwings as xw
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_excel_access():
    """Test direct Excel access with minimal code"""
    
    base_path = Path(__file__).parent
    template_path = base_path / "botntemplate" / "CABOTNTemplate.xlsx"
    
    logger.info(f"🧪 Testing direct Excel access to: {template_path}")
    logger.info(f"📁 Template exists: {template_path.exists()}")
    
    if not template_path.exists():
        logger.error("❌ Template file not found")
        return False
    
    try:
        logger.info("🔧 Creating Excel app...")
        
        # Start with minimal settings
        app = xw.App(visible=True, add_book=False)  # Make visible to see what's happening
        app.display_alerts = False
        
        logger.info("✅ Excel app created")
        logger.info(f"   Version: {app.version}")
        
        logger.info("📂 Opening template file...")
        
        # Try with a timeout approach
        wb = None
        try:
            wb = app.books.open(str(template_path), update_links=False)
            logger.info("✅ Template opened successfully!")
            
            # Quick test
            sheets = [sheet.name for sheet in wb.sheets]
            logger.info(f"📊 Found sheets: {sheets}")
            
            if 'Inputs' in sheets:
                inputs_sheet = wb.sheets['Inputs']
                a1_value = inputs_sheet.range('A1').value
                logger.info(f"📋 A1 value: {a1_value}")
                
                # Try a simple write
                inputs_sheet.range('A2').value = "TEST_WRITE"
                written_value = inputs_sheet.range('A2').value
                logger.info(f"✅ Write test: {written_value}")
            
            wb.close()
            logger.info("✅ Workbook closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error with workbook: {str(e)}")
            if wb:
                try:
                    wb.close()
                except:
                    pass
        
        app.quit()
        logger.info("🔧 Excel app closed")
        
        logger.info("🎉 Direct Excel test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct Excel test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running direct Excel access test...")
    print("   This will open Excel visibly to see any prompts")
    print("   Close any dialog boxes that appear and watch the console")
    
    success = test_direct_excel_access()
    
    if success:
        print("\n✅ Direct Excel test passed!")
    else:
        print("\n❌ Direct Excel test failed!")