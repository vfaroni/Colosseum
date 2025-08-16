#!/usr/bin/env python3
"""
CTCAC Excel Structure Analyzer
Analyze the structure of CTCAC applications to identify actual data locations
"""

import xlwings as xw
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

def analyze_ctcac_structure(file_path: Path, max_sheets: int = 10) -> Dict[str, Any]:
    """Analyze the structure of a CTCAC Excel file"""
    
    print(f"🔍 Analyzing structure of: {file_path.name}")
    
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.open(str(file_path), read_only=True, update_links=False)
        
        analysis = {
            "filename": file_path.name,
            "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            "total_sheets": len(wb.sheets),
            "sheets_analyzed": [],
            "potential_data_locations": {},
            "template_patterns": [],
            "numeric_data_cells": [],
            "text_data_cells": []
        }
        
        # Analyze each sheet
        for i, sheet in enumerate(wb.sheets[:max_sheets]):
            print(f"   📋 Analyzing sheet: {sheet.name}")
            
            sheet_analysis = analyze_sheet_structure(sheet)
            sheet_analysis["sheet_name"] = sheet.name
            sheet_analysis["sheet_index"] = i
            
            analysis["sheets_analyzed"].append(sheet_analysis)
            
            # Look for potential project data
            data_locations = find_data_locations(sheet)
            if data_locations:
                analysis["potential_data_locations"][sheet.name] = data_locations
        
        wb.close()
        app.quit()
        
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {"error": str(e)}

def analyze_sheet_structure(sheet: xw.Sheet) -> Dict[str, Any]:
    """Analyze the structure of a single sheet"""
    
    try:
        used_range = sheet.used_range
        if not used_range:
            return {"empty_sheet": True}
        
        rows, cols = used_range.shape
        
        # Sample key areas of the sheet
        areas_to_check = [
            ("header", "A1:Z20"),
            ("left_column", "A1:A100"),
            ("financial_section", "A1:Z200"),
            ("middle_section", f"A{min(50, rows//2)}:Z{min(100, rows//2 + 50)}"),
            ("bottom_section", f"A{max(1, rows-50)}:Z{rows}")
        ]
        
        sheet_data = {
            "dimensions": {"rows": rows, "cols": cols},
            "areas": {},
            "data_summary": {
                "non_empty_cells": 0,
                "numeric_cells": 0,
                "formula_cells": 0,
                "text_cells": 0
            }
        }
        
        for area_name, range_str in areas_to_check:
            try:
                # Adjust range to not exceed sheet bounds
                area_range = adjust_range_to_bounds(range_str, rows, cols)
                area_data = sheet.range(area_range).value
                
                area_analysis = analyze_area_data(area_data, area_name)
                sheet_data["areas"][area_name] = area_analysis
                
                # Update summary
                for key in ["non_empty_cells", "numeric_cells", "text_cells"]:
                    sheet_data["data_summary"][key] += area_analysis.get(key, 0)
                    
            except Exception as e:
                sheet_data["areas"][area_name] = {"error": str(e)}
        
        return sheet_data
        
    except Exception as e:
        return {"error": str(e)}

def adjust_range_to_bounds(range_str: str, max_rows: int, max_cols: int) -> str:
    """Adjust range string to not exceed sheet bounds"""
    try:
        start, end = range_str.split(":")
        
        # Parse start cell
        start_col, start_row = parse_cell_reference(start)
        end_col, end_row = parse_cell_reference(end)
        
        # Adjust to bounds
        end_row = min(end_row, max_rows)
        end_col = min(end_col, max_cols)
        
        # Convert back to range string
        end_col_letter = chr(ord('A') + end_col - 1) if end_col <= 26 else f"A{chr(ord('A') + end_col - 27)}"
        return f"{start}:{end_col_letter}{end_row}"
        
    except Exception:
        return "A1:Z100"  # Fallback

def parse_cell_reference(cell_ref: str) -> Tuple[int, int]:
    """Parse cell reference like 'A1' into (col, row) numbers"""
    col_part = ""
    row_part = ""
    
    for char in cell_ref:
        if char.isalpha():
            col_part += char
        elif char.isdigit():
            row_part += char
    
    # Convert column letters to number
    col_num = 0
    for char in col_part:
        col_num = col_num * 26 + (ord(char.upper()) - ord('A') + 1)
    
    row_num = int(row_part) if row_part else 1
    
    return col_num, row_num

def analyze_area_data(area_data: Any, area_name: str) -> Dict[str, Any]:
    """Analyze data from a specific area of the sheet"""
    
    analysis = {
        "area_name": area_name,
        "non_empty_cells": 0,
        "numeric_cells": 0,
        "text_cells": 0,
        "interesting_values": [],
        "potential_labels": [],
        "potential_data": []
    }
    
    if not area_data:
        return analysis
    
    # Handle different data structures
    if isinstance(area_data, list):
        for row_idx, row in enumerate(area_data):
            if isinstance(row, list):
                for col_idx, cell in enumerate(row):
                    analyze_cell_value(cell, analysis, f"{area_name}_{row_idx}_{col_idx}")
            else:
                analyze_cell_value(row, analysis, f"{area_name}_{row_idx}")
    else:
        analyze_cell_value(area_data, analysis, area_name)
    
    return analysis

def analyze_cell_value(cell_value: Any, analysis: Dict, cell_id: str):
    """Analyze a single cell value"""
    
    if cell_value is None or str(cell_value).strip() == "":
        return
    
    analysis["non_empty_cells"] += 1
    cell_str = str(cell_value).strip()
    
    # Check if numeric
    if isinstance(cell_value, (int, float)):
        analysis["numeric_cells"] += 1
        if cell_value > 1000:  # Potentially interesting numbers
            analysis["potential_data"].append({
                "cell_id": cell_id,
                "value": cell_value,
                "type": "numeric"
            })
    else:
        analysis["text_cells"] += 1
        
        # Look for interesting text patterns
        lower_str = cell_str.lower()
        
        # Template indicators
        if any(pattern in lower_str for pattern in ["...", "xxx", "enter", "fill", "insert"]):
            analysis["potential_labels"].append({
                "cell_id": cell_id,
                "value": cell_str[:50],
                "type": "template"
            })
        
        # Potential labels for data entry
        elif any(keyword in lower_str for keyword in [
            "project", "name", "address", "city", "developer", "cost", "units", 
            "loan", "lender", "contact", "phone", "email", "total", "amount"
        ]):
            analysis["potential_labels"].append({
                "cell_id": cell_id,
                "value": cell_str[:50],
                "type": "label"
            })
        
        # Actual data (non-template text)
        elif len(cell_str) > 3 and not any(pattern in lower_str for pattern in ["...", "xxx", "enter", "fill"]):
            analysis["potential_data"].append({
                "cell_id": cell_id,
                "value": cell_str[:100],
                "type": "text_data"
            })

def find_data_locations(sheet: xw.Sheet) -> Dict[str, Any]:
    """Find specific data locations in the sheet"""
    
    data_locations = {}
    
    # Common CTCAC field patterns and where to look for their values
    field_patterns = {
        "project_name": ["project name", "development name", "property name"],
        "project_address": ["project address", "site address", "property address"],
        "total_units": ["total units", "number of units", "unit count"],
        "total_cost": ["total development cost", "total project cost", "tdc"],
        "developer": ["developer", "sponsor", "development company"],
        "construction_loan": ["construction loan", "construction financing"],
        "permanent_loan": ["permanent loan", "permanent financing"]
    }
    
    try:
        # Search in common areas where CTCAC data is typically found
        search_ranges = [
            "A1:Z50",   # Header area
            "A1:C200",  # Left side labels
            "A50:Z150", # Middle section
        ]
        
        for field_name, search_terms in field_patterns.items():
            locations = find_field_data_location(sheet, search_terms, search_ranges)
            if locations:
                data_locations[field_name] = locations
    
    except Exception as e:
        data_locations["error"] = str(e)
    
    return data_locations

def find_field_data_location(sheet: xw.Sheet, search_terms: List[str], search_ranges: List[str]) -> List[Dict]:
    """Find where actual data for a field might be located"""
    
    locations = []
    
    for range_str in search_ranges:
        try:
            range_data = sheet.range(range_str).value
            if not range_data:
                continue
            
            # Search through the range for labels and adjacent data
            if isinstance(range_data, list):
                for row_idx, row in enumerate(range_data):
                    if isinstance(row, list):
                        for col_idx, cell in enumerate(row):
                            if cell and isinstance(cell, str):
                                cell_lower = cell.lower().strip()
                                
                                # Check if this cell contains one of our search terms
                                for term in search_terms:
                                    if term.lower() in cell_lower:
                                        # Look for data in adjacent cells
                                        adjacent_data = find_adjacent_data(
                                            range_data, row_idx, col_idx, len(range_data), len(row)
                                        )
                                        
                                        if adjacent_data:
                                            locations.append({
                                                "label_cell": f"Row{row_idx}_Col{col_idx}",
                                                "label_text": cell[:50],
                                                "data_locations": adjacent_data,
                                                "search_term": term,
                                                "range": range_str
                                            })
        except Exception:
            continue
    
    return locations

def find_adjacent_data(range_data: List, label_row: int, label_col: int, max_rows: int, max_cols: int) -> List[Dict]:
    """Find data in cells adjacent to a label"""
    
    adjacent_data = []
    
    # Check common adjacent positions
    positions_to_check = [
        (label_row, label_col + 1),      # Right
        (label_row, label_col + 2),      # Two right
        (label_row + 1, label_col),      # Below
        (label_row + 1, label_col + 1),  # Diagonal
    ]
    
    for check_row, check_col in positions_to_check:
        if 0 <= check_row < max_rows and 0 <= check_col < max_cols:
            try:
                if isinstance(range_data[check_row], list) and check_col < len(range_data[check_row]):
                    cell_value = range_data[check_row][check_col]
                    
                    if cell_value and str(cell_value).strip():
                        # Skip template placeholders
                        cell_str = str(cell_value).strip()
                        if not any(pattern in cell_str.lower() for pattern in ["...", "xxx", "enter", "fill"]):
                            adjacent_data.append({
                                "position": f"Row{check_row}_Col{check_col}",
                                "value": cell_value,
                                "relative_position": f"({check_row - label_row}, {check_col - label_col})",
                                "type": "numeric" if isinstance(cell_value, (int, float)) else "text"
                            })
            except (IndexError, TypeError):
                continue
    
    return adjacent_data

def analyze_multiple_files(sample_size: int = 3) -> Dict[str, Any]:
    """Analyze structure of multiple CTCAC files"""
    
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    excel_files = list(raw_data_path.glob("*.xlsx"))[:sample_size]
    
    print(f"🔍 CTCAC STRUCTURE ANALYSIS: {len(excel_files)} files")
    print("=" * 60)
    
    all_analyses = []
    
    for file_path in excel_files:
        analysis = analyze_ctcac_structure(file_path, max_sheets=5)
        all_analyses.append(analysis)
    
    # Generate comprehensive analysis
    comprehensive_analysis = {
        "total_files_analyzed": len(all_analyses),
        "individual_analyses": all_analyses,
        "common_patterns": identify_common_patterns(all_analyses),
        "recommended_extraction_strategy": generate_extraction_strategy(all_analyses)
    }
    
    return comprehensive_analysis

def identify_common_patterns(analyses: List[Dict]) -> Dict[str, Any]:
    """Identify common patterns across multiple files"""
    
    common_patterns = {
        "sheet_names": {},
        "data_location_patterns": {},
        "template_indicators": [],
        "numeric_data_patterns": []
    }
    
    for analysis in analyses:
        if "sheets_analyzed" in analysis:
            for sheet in analysis["sheets_analyzed"]:
                sheet_name = sheet.get("sheet_name", "unknown")
                common_patterns["sheet_names"][sheet_name] = common_patterns["sheet_names"].get(sheet_name, 0) + 1
    
    return common_patterns

def generate_extraction_strategy(analyses: List[Dict]) -> Dict[str, Any]:
    """Generate recommended extraction strategy based on analysis"""
    
    strategy = {
        "priority_sheets": [],
        "recommended_search_areas": [],
        "field_extraction_hints": {},
        "template_detection_rules": []
    }
    
    # Analyze most common sheet types
    sheet_frequency = {}
    for analysis in analyses:
        if "sheets_analyzed" in analysis:
            for sheet in analysis["sheets_analyzed"]:
                sheet_name = sheet.get("sheet_name", "").lower()
                sheet_frequency[sheet_name] = sheet_frequency.get(sheet_name, 0) + 1
    
    # Sort by frequency and recommend top sheets
    sorted_sheets = sorted(sheet_frequency.items(), key=lambda x: x[1], reverse=True)
    strategy["priority_sheets"] = [sheet[0] for sheet in sorted_sheets[:5]]
    
    # Common search areas based on analysis
    strategy["recommended_search_areas"] = [
        "A1:Z30",    # Header section
        "A1:E200",   # Left side labels
        "A30:Z100",  # Main data section
    ]
    
    return strategy

def main():
    """Run CTCAC structure analysis"""
    
    print("🔍 CTCAC EXCEL STRUCTURE ANALYZER")
    print("=" * 50)
    
    # Analyze multiple files
    analysis = analyze_multiple_files(sample_size=3)
    
    # Save results
    output_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/structure_analysis")
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "ctcac_structure_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n📊 Analysis complete - {analysis['total_files_analyzed']} files analyzed")
    print(f"💾 Results saved to: {output_path}")
    
    # Display key findings
    print(f"\n🔍 KEY FINDINGS:")
    common = analysis["common_patterns"]
    strategy = analysis["recommended_extraction_strategy"]
    
    print(f"📋 Common sheet names: {list(common['sheet_names'].keys())[:5]}")
    print(f"🎯 Priority extraction sheets: {strategy['priority_sheets'][:3]}")
    print(f"📍 Recommended search areas: {len(strategy['recommended_search_areas'])}")
    
    print(f"\n✅ Use this analysis to improve extraction patterns!")

if __name__ == "__main__":
    main()