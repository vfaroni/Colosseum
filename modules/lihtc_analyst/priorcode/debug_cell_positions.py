#!/usr/bin/env python3
"""
Debug cell positions to find exact locations of unit data
"""

import xlwings as xw
from pathlib import Path

def debug_cell_positions():
    """Debug exact cell positions for unit data"""
    
    print("🔍 DEBUGGING CELL POSITIONS")
    print("=" * 50)
    
    test_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx")
    
    app = None
    wb = None
    
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.open(str(test_file), read_only=True, update_links=False)
        app_sheet = wb.sheets['Application']
        
        # Check rows 717-718 with full column range
        print("📊 Row 717 (all columns A-Z):")
        row717 = app_sheet.range("A717:Z717").value
        for i, cell in enumerate(row717):
            if cell is not None and str(cell).strip():
                col_letter = chr(65 + i)  # A=65, B=66, etc.
                print(f"   {col_letter}{i:2d}: {cell}")
        
        print("\n📊 Row 718 (all columns A-Z):")
        row718 = app_sheet.range("A718:Z718").value
        for i, cell in enumerate(row718):
            if cell is not None and str(cell).strip():
                col_letter = chr(65 + i)
                print(f"   {col_letter}{i:2d}: {cell}")
        
        # Check row 752 for total units
        print("\n📊 Row 752 (columns A-J):")
        row752 = app_sheet.range("A752:J752").value
        for i, cell in enumerate(row752):
            if cell is not None and str(cell).strip():
                col_letter = chr(65 + i)
                print(f"   {col_letter}{i:2d}: {cell}")
        
        # Also check the header row 713
        print("\n📊 Row 713 - Header (columns A-Z):")
        row713 = app_sheet.range("A713:Z713").value
        for i, cell in enumerate(row713):
            if cell is not None and str(cell).strip():
                col_letter = chr(65 + i)
                print(f"   {col_letter}{i:2d}: {cell}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if wb: wb.close()
        if app: app.quit()

if __name__ == "__main__":
    debug_cell_positions()