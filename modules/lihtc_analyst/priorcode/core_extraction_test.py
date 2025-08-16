#!/usr/bin/env python3
"""
Focused test of core unit mix + financial extraction for 2025 4% applications
Goal: Perfect the essentials before expanding
"""

import pandas as pd
import xlwings as xw
from pathlib import Path
import time

def test_core_extraction():
    """Test core unit mix and financial extraction"""
    
    print("🎯 CORE EXTRACTION TEST - 2025 4% APPLICATIONS")
    print("Focus: Unit mix, rents, AMI levels, Sources & Uses")
    print("=" * 70)
    
    # Find 2025 4% files
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    files_2025_4pct = list(raw_data_path.glob("*2025*4pct*.xlsx"))
    
    print(f"📁 Found {len(files_2025_4pct)} 2025 4% files")
    
    if not files_2025_4pct:
        print("❌ No 2025 4% files found")
        return
    
    # Test first file only
    test_file = files_2025_4pct[0]
    print(f"🧪 Testing: {test_file.name}")
    
    # Core extraction test
    app = None
    wb = None
    
    try:
        # Open Excel efficiently
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.open(str(test_file), read_only=True, update_links=False)
        
        print(f"\n📋 Available sheets: {[sheet.name for sheet in wb.sheets]}")
        
        # 1. UNIT MIX EXTRACTION
        print(f"\n🏠 UNIT MIX EXTRACTION:")
        unit_data = extract_unit_mix_data(wb)
        
        # 2. SOURCES & USES EXTRACTION  
        print(f"\n💰 SOURCES & USES EXTRACTION:")
        financial_data = extract_sources_uses_data(wb)
        
        # 3. BASIC PROJECT INFO
        print(f"\n📊 PROJECT INFO EXTRACTION:")
        project_info = extract_basic_project_info(wb)
        
        # Summary
        print(f"\n✅ CORE EXTRACTION SUMMARY:")
        print(f"   🏠 Unit types found: {len(unit_data) if unit_data else 0}")
        print(f"   💰 Sources & Uses: {'✅' if financial_data else '❌'}")
        print(f"   📊 Project info: {'✅' if project_info else '❌'}")
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
    
    finally:
        # Proper cleanup
        if wb:
            wb.close()
        if app:
            app.quit()
        print(f"🔄 Excel cleaned up")

def extract_unit_mix_data(workbook):
    """Extract unit mix data from Application tab"""
    
    try:
        # Find Application sheet
        app_sheet = None
        for sheet in workbook.sheets:
            if 'application' in sheet.name.lower() and 'checklist' not in sheet.name.lower():
                app_sheet = sheet
                break
        
        if not app_sheet:
            print("   ❌ Application sheet not found")
            return None
        
        print(f"   📋 Using sheet: {app_sheet.name}")
        
        # Get data range (we know unit table is around row 713-720)
        data_range = app_sheet.range("A710:T725").value
        
        unit_data = []
        
        # Look for unit table rows
        for i, row in enumerate(data_range):
            if row and len(row) > 5:
                # Check if this looks like unit data
                if str(row[0]) and 'bedroom' in str(row[0]).lower():
                    unit_type = str(row[0])
                    unit_count = row[1] if row[1] else 0
                    avg_sqft = row[2] if row[2] else 0
                    gross_rent = row[3] if row[3] else 0
                    utility_allowance = row[4] if row[4] else 0
                    
                    unit_info = {
                        'unit_type': unit_type,
                        'unit_count': int(unit_count) if isinstance(unit_count, (int, float)) else 0,
                        'avg_sqft': int(avg_sqft) if isinstance(avg_sqft, (int, float)) else 0,
                        'gross_rent': int(gross_rent) if isinstance(gross_rent, (int, float)) else 0,
                        'utility_allowance': int(utility_allowance) if isinstance(utility_allowance, (int, float)) else 0
                    }
                    
                    if unit_info['unit_count'] > 0:
                        unit_data.append(unit_info)
                        print(f"   ✅ {unit_type}: {unit_count} units @ ${gross_rent}")
        
        return unit_data
        
    except Exception as e:
        print(f"   ❌ Unit mix extraction failed: {e}")
        return None

def extract_sources_uses_data(workbook):
    """Extract Sources & Uses budget data"""
    
    try:
        # Find Sources & Uses sheet
        su_sheet = None
        for sheet in workbook.sheets:
            if 'sources' in sheet.name.lower() and 'uses' in sheet.name.lower():
                su_sheet = sheet
                break
        
        if not su_sheet:
            print("   ❌ Sources & Uses sheet not found")
            return None
        
        print(f"   📋 Using sheet: {su_sheet.name}")
        
        # Extract line items (A4:A150)
        line_items = su_sheet.range("A4:A150").value
        line_items = [str(item) for item in line_items if item and str(item).strip() and str(item) != 'nan']
        
        # Extract total costs (B4:B150) 
        total_costs = su_sheet.range("B4:B150").value
        total_costs = [float(cost) for cost in total_costs if cost and isinstance(cost, (int, float))]
        
        print(f"   ✅ Line items: {len(line_items)}")
        print(f"   ✅ Cost entries: {len(total_costs)}")
        print(f"   💰 Total project cost: ${sum(total_costs):,.0f}")
        
        return {
            'line_items': line_items[:10],  # First 10 for testing
            'total_costs': total_costs[:10],
            'total_project_cost': sum(total_costs)
        }
        
    except Exception as e:
        print(f"   ❌ Sources & Uses extraction failed: {e}")
        return None

def extract_basic_project_info(workbook):
    """Extract basic project information"""
    
    try:
        # Find Application sheet
        app_sheet = None
        for sheet in workbook.sheets:
            if 'application' in sheet.name.lower() and 'checklist' not in sheet.name.lower():
                app_sheet = sheet
                break
        
        if not app_sheet:
            return None
        
        # Look for project name and address (typically in upper area)
        project_data = app_sheet.range("A1:T100").value
        
        project_info = {
            'project_name': 'TBD',
            'total_units': 0,
            'project_type': 'TBD'
        }
        
        # Scan for project info
        for row in project_data:
            if row and len(row) > 1:
                row_text = ' '.join([str(x) for x in row[:5] if x]).lower()
                
                # Look for total units
                if 'total # units' in row_text or 'total units' in row_text:
                    for cell in row:
                        if isinstance(cell, (int, float)) and 50 <= cell <= 200:
                            project_info['total_units'] = int(cell)
                            break
        
        print(f"   📊 Total units: {project_info['total_units']}")
        
        return project_info
        
    except Exception as e:
        print(f"   ❌ Project info extraction failed: {e}")
        return None

if __name__ == "__main__":
    test_core_extraction()