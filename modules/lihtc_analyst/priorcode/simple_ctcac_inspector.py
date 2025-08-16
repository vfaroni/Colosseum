#!/usr/bin/env python3
"""
Simple CTCAC Inspector
Quick inspection of CTCAC Excel files to understand structure
"""

import xlwings as xw
import json
from pathlib import Path

def inspect_ctcac_file(file_path: Path):
    """Inspect a single CTCAC file"""
    
    print(f"🔍 Inspecting: {file_path.name}")
    
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        
        wb = app.books.open(str(file_path), read_only=True, update_links=False)
        
        print(f"   📊 Total sheets: {len(wb.sheets)}")
        
        # Inspect each sheet
        for i, sheet in enumerate(wb.sheets):
            if i >= 5:  # Limit to first 5 sheets
                break
                
            print(f"\n   📋 Sheet {i+1}: '{sheet.name}'")
            
            try:
                used_range = sheet.used_range
                if used_range:
                    rows, cols = used_range.shape
                    print(f"      📐 Size: {rows} rows × {cols} columns")
                    
                    # Sample the first few rows and columns
                    print(f"      🔍 Sample data (A1:E10):")
                    sample_data = sheet.range("A1:E10").value
                    
                    if sample_data:
                        for row_idx, row in enumerate(sample_data[:5]):
                            if isinstance(row, list):
                                row_preview = []
                                for cell in row[:5]:
                                    if cell:
                                        cell_str = str(cell)[:20]
                                        row_preview.append(cell_str)
                                    else:
                                        row_preview.append("--")
                                print(f"         Row {row_idx+1}: {' | '.join(row_preview)}")
                            elif row:
                                print(f"         Row {row_idx+1}: {str(row)[:50]}")
                    
                    # Look for specific patterns
                    print(f"      🎯 Looking for key data...")
                    
                    # Check larger area for project info
                    project_area = sheet.range("A1:Z50").value
                    if project_area:
                        found_patterns = []
                        
                        for row_idx, row in enumerate(project_area[:50]):
                            if isinstance(row, list):
                                for col_idx, cell in enumerate(row[:26]):  # A-Z columns
                                    if cell and isinstance(cell, str):
                                        cell_lower = cell.lower()
                                        
                                        # Look for key indicators
                                        if any(term in cell_lower for term in [
                                            "project name", "development name", "property name"
                                        ]):
                                            # Look for data in adjacent cells
                                            adjacent_cells = []
                                            for offset in [1, 2]:
                                                if col_idx + offset < len(row):
                                                    adj_cell = row[col_idx + offset]
                                                    if adj_cell and str(adj_cell).strip():
                                                        adjacent_cells.append(str(adj_cell)[:30])
                                            
                                            if adjacent_cells:
                                                found_patterns.append(f"Project name area: Row {row_idx+1}, adjacent: {adjacent_cells}")
                                        
                                        elif any(term in cell_lower for term in [
                                            "total development cost", "total project cost", "total cost"
                                        ]):
                                            adjacent_cells = []
                                            for offset in [1, 2]:
                                                if col_idx + offset < len(row):
                                                    adj_cell = row[col_idx + offset]
                                                    if adj_cell and (isinstance(adj_cell, (int, float)) or 
                                                                   (isinstance(adj_cell, str) and any(c.isdigit() for c in adj_cell))):
                                                        adjacent_cells.append(str(adj_cell)[:30])
                                            
                                            if adjacent_cells:
                                                found_patterns.append(f"Total cost area: Row {row_idx+1}, adjacent: {adjacent_cells}")
                                        
                                        elif "developer" in cell_lower and len(cell_lower) < 50:
                                            adjacent_cells = []
                                            for offset in [1, 2]:
                                                if col_idx + offset < len(row):
                                                    adj_cell = row[col_idx + offset]
                                                    if adj_cell and str(adj_cell).strip() and "..." not in str(adj_cell):
                                                        adjacent_cells.append(str(adj_cell)[:30])
                                            
                                            if adjacent_cells:
                                                found_patterns.append(f"Developer area: Row {row_idx+1}, adjacent: {adjacent_cells}")
                        
                        if found_patterns:
                            for pattern in found_patterns[:5]:  # Show first 5 findings
                                print(f"         ✅ {pattern}")
                        else:
                            print(f"         ⚠️  No clear data patterns found")
                
                else:
                    print(f"      📭 Sheet appears empty")
                    
            except Exception as e:
                print(f"      ❌ Error analyzing sheet: {e}")
        
        wb.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to inspect file: {e}")
        return False

def main():
    """Inspect sample CTCAC files"""
    
    print("🔍 SIMPLE CTCAC INSPECTOR")
    print("=" * 40)
    
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    excel_files = list(raw_data_path.glob("*.xlsx"))[:3]
    
    print(f"📁 Found {len(excel_files)} files to inspect")
    
    successful_inspections = 0
    
    for file_path in excel_files:
        print(f"\n{'='*60}")
        if inspect_ctcac_file(file_path):
            successful_inspections += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully inspected {successful_inspections}/{len(excel_files)} files")
    print(f"🎯 Use findings to improve extraction patterns")

if __name__ == "__main__":
    main()