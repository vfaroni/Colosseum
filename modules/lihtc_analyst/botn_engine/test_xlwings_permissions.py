#!/usr/bin/env python3
"""
Test XLWings Permissions - Check if xlwings can access files without prompting
"""

import xlwings as xw
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_xlwings_access():
    """Test xlwings file access"""
    
    base_path = Path(__file__).parent
    template_path = base_path / "botntemplate" / "CABOTNTemplate.xlsx"
    
    logger.info("🧪 Testing xlwings access without user prompts...")
    
    try:
        # Try to open Excel without prompting
        logger.info("Opening Excel application...")
        app = xw.App(visible=False, add_book=False)
        
        logger.info(f"Opening template: {template_path}")
        wb = app.books.open(str(template_path))
        
        logger.info("✅ File opened successfully!")
        logger.info("Checking sheet access...")
        
        inputs_sheet = wb.sheets['Inputs']
        logger.info("✅ Can access Inputs sheet!")
        
        # Try to read a cell
        cell_value = inputs_sheet.range('A1').value
        logger.info(f"✅ Can read cell A1: {cell_value}")
        
        # Close without saving
        wb.close()
        app.quit()
        
        logger.info("🎉 SUCCESS: xlwings works without permission prompts!")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        try:
            if 'wb' in locals():
                wb.close()
            if 'app' in locals():
                app.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    test_xlwings_access()