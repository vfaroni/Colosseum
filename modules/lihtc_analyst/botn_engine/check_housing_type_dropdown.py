#!/usr/bin/env python3
"""
Check Housing Type Dropdown - Verify the exact options for Housing Type validation
"""

import xlwings as xw
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_housing_type_dropdown():
    """Check what Housing Type options are in the template"""
    
    base_path = Path(__file__).parent
    template_path = base_path / "botntemplate" / "CABOTNTemplate.xlsx"
    
    try:
        logger.info("🔍 Checking Housing Type dropdown options...")
        
        # Open template with xlwings to check actual dropdown
        app = xw.App(visible=True, add_book=False)  # Make visible to see dropdowns
        wb = app.books.open(str(template_path))
        inputs_sheet = wb.sheets['Inputs']
        
        logger.info("📋 Template opened - checking cell H2 (Housing Type)")
        
        # Check what's currently in H2
        current_value = inputs_sheet.range('H2').value
        logger.info(f"Current H2 value: {current_value}")
        
        # Check validation options by looking at B14 (which had housing type validation)
        b14_value = inputs_sheet.range('B14').value
        logger.info(f"Current B14 value: {b14_value}")
        
        logger.info("\n💡 Please manually check the dropdown options in:")
        logger.info("   • Cell H2 (Housing Type for inputs)")
        logger.info("   • Cell B14 (Housing Type validation reference)")
        logger.info("\nTemplate is open - check the dropdowns and close when done.")
        
        input("Press Enter when you've checked the dropdowns...")
        
        wb.close()
        app.quit()
        
    except Exception as e:
        logger.error(f"Error checking template: {str(e)}")
        try:
            if 'wb' in locals():
                wb.close()
            if 'app' in locals():
                app.quit()
        except:
            pass

if __name__ == "__main__":
    check_housing_type_dropdown()