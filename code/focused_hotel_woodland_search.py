#!/usr/bin/env python3
"""
Focused Hotel Woodland Search
Search specifically for "Hotel Woodland", "Woodland Hotel" and exclude generic HUD Metro area references
"""

import pandas as pd
import openpyxl
import os
import re
from typing import List, Dict, Any
import traceback
from datetime import datetime

class FocusedHotelWoodlandSearcher:
    def __init__(self):
        # More specific search terms
        self.specific_search_terms = [
            'hotel woodland',
            'woodland hotel',
            'hotel in woodland',
            'woodland inn',
            'woodland resort',
            'woodland development',
            'woodland property'
        ]
        
        # Exclude these generic terms that are likely just geographic references
        self.exclude_terms = [
            'houston-the woodlands-sugar land',
            'hud metro fmr area',
            'metro area'
        ]
        
        self.results = []
        
    def search_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Search through all Excel files for specific Hotel Woodland references"""
        
        print(f"Starting focused Hotel Woodland search at {datetime.now()}")
        print(f"Searching {len(file_paths)} Excel files for specific Hotel Woodland references...")
        print("Excluding generic HUD Metro area references")
        print("=" * 80)
        
        overall_results = {
            'files_processed': 0,
            'files_with_matches': 0,
            'total_matches': 0,
            'detailed_results': [],
            'errors': []
        }
        
        for file_path in file_paths:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            
            try:
                file_results = self._search_excel_file(file_path)
                overall_results['files_processed'] += 1
                
                if file_results['matches']:
                    overall_results['files_with_matches'] += 1
                    overall_results['total_matches'] += len(file_results['matches'])
                    overall_results['detailed_results'].append(file_results)
                    
                    print(f"  ✅ Found {len(file_results['matches'])} specific matches")
                else:
                    print(f"  ❌ No specific hotel/woodland matches found")
                    
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                overall_results['errors'].append(error_msg)
                print(f"  ⚠️  {error_msg}")
                
        return overall_results
    
    def _search_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Search a single Excel file across all worksheets"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_results = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'worksheets_searched': 0,
            'matches': []
        }
        
        # Try to get worksheet names using openpyxl first
        try:
            workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            worksheet_names = workbook.sheetnames
            workbook.close()
        except Exception as e:
            # Fallback to pandas
            try:
                excel_file = pd.ExcelFile(file_path)
                worksheet_names = excel_file.sheet_names
                excel_file.close()
            except Exception as e2:
                raise Exception(f"Could not read Excel file structure: {str(e)} / {str(e2)}")
        
        # Search each worksheet
        for sheet_name in worksheet_names:
            print(f"    Searching worksheet: {sheet_name}")
            
            try:
                sheet_matches = self._search_worksheet(file_path, sheet_name)
                file_results['matches'].extend(sheet_matches)
                file_results['worksheets_searched'] += 1
                
            except Exception as e:
                print(f"      Warning: Could not search worksheet '{sheet_name}': {str(e)}")
                continue
                
        return file_results
    
    def _search_worksheet(self, file_path: str, sheet_name: str) -> List[Dict[str, Any]]:
        """Search a single worksheet for specific Hotel Woodland references"""
        
        matches = []
        
        try:
            # Read the worksheet
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            # Convert all cells to string for searching
            df_str = df.astype(str)
            
            # Search through each cell
            for row_idx in range(len(df_str)):
                for col_idx in range(len(df_str.columns)):
                    cell_value = df_str.iloc[row_idx, col_idx]
                    
                    if pd.isna(cell_value) or cell_value.strip() == '' or cell_value == 'nan':
                        continue
                    
                    cell_value_lower = cell_value.lower()
                    
                    # Skip if this is just a generic HUD Metro area reference
                    if any(exclude_term.lower() in cell_value_lower for exclude_term in self.exclude_terms):
                        continue
                    
                    # Check if cell contains any specific search terms
                    contains_woodland = 'woodland' in cell_value_lower
                    contains_hotel_terms = any(term in cell_value_lower for term in ['hotel', 'inn', 'resort', 'development', 'property'])
                    
                    if contains_woodland and (contains_hotel_terms or any(term.lower() in cell_value_lower for term in self.specific_search_terms)):
                        
                        # Create match record
                        match = self._create_match_record(
                            file_path, sheet_name, row_idx, col_idx, 
                            cell_value, df_str
                        )
                        matches.append(match)
                        
        except Exception as e:
            raise Exception(f"Error searching worksheet '{sheet_name}': {str(e)}")
            
        return matches
    
    def _create_match_record(self, file_path: str, sheet_name: str, row_idx: int, 
                           col_idx: int, cell_value: str, df_str: pd.DataFrame) -> Dict[str, Any]:
        """Create detailed match record with context"""
        
        # Convert to Excel cell reference (A1, B5, etc.)
        cell_ref = self._to_excel_cell_ref(row_idx, col_idx)
        
        # Get surrounding context
        context = self._get_cell_context(df_str, row_idx, col_idx)
        
        # Analyze the type of match
        match_type = self._analyze_match_type(cell_value)
        
        match_record = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'worksheet': sheet_name,
            'cell_reference': cell_ref,
            'cell_content': cell_value.strip(),
            'row_index': row_idx + 1,  # 1-based for Excel
            'column_index': col_idx + 1,  # 1-based for Excel
            'match_type': match_type,
            'surrounding_context': context
        }
        
        return match_record
    
    def _to_excel_cell_ref(self, row_idx: int, col_idx: int) -> str:
        """Convert row/column indices to Excel cell reference (A1, B5, etc.)"""
        
        # Convert column index to Excel column letters
        col_letters = ""
        col_num = col_idx + 1  # Convert to 1-based
        
        while col_num > 0:
            col_num -= 1
            col_letters = chr(col_num % 26 + ord('A')) + col_letters
            col_num //= 26
            
        return f"{col_letters}{row_idx + 1}"
    
    def _get_cell_context(self, df_str: pd.DataFrame, row_idx: int, col_idx: int, 
                         context_range: int = 3) -> Dict[str, Any]:
        """Get enhanced surrounding cell context"""
        
        context = {
            'same_row': [],
            'same_column': [],
            'nearby_cells': [],
            'full_row_data': [],
            'column_headers': []
        }
        
        try:
            # Get entire row data
            for c in range(len(df_str.columns)):
                val = df_str.iloc[row_idx, c]
                if not pd.isna(val) and str(val).strip() != '' and str(val) != 'nan':
                    context['full_row_data'].append({
                        'cell_ref': self._to_excel_cell_ref(row_idx, c),
                        'content': str(val).strip()
                    })
            
            # Get potential column headers (first few rows)
            for header_row in range(min(3, len(df_str))):
                val = df_str.iloc[header_row, col_idx]
                if not pd.isna(val) and str(val).strip() != '' and str(val) != 'nan':
                    context['column_headers'].append({
                        'row': header_row + 1,
                        'content': str(val).strip()
                    })
            
            # Get cells in same row (extended range)
            row_start = max(0, col_idx - context_range)
            row_end = min(len(df_str.columns), col_idx + context_range + 1)
            
            for c in range(row_start, row_end):
                if c != col_idx:
                    val = df_str.iloc[row_idx, c]
                    if not pd.isna(val) and str(val).strip() != '' and str(val) != 'nan':
                        context['same_row'].append({
                            'cell_ref': self._to_excel_cell_ref(row_idx, c),
                            'content': str(val).strip()
                        })
            
            # Get cells in same column (extended range)
            col_start = max(0, row_idx - context_range)
            col_end = min(len(df_str), row_idx + context_range + 1)
            
            for r in range(col_start, col_end):
                if r != row_idx:
                    val = df_str.iloc[r, col_idx]
                    if not pd.isna(val) and str(val).strip() != '' and str(val) != 'nan':
                        context['same_column'].append({
                            'cell_ref': self._to_excel_cell_ref(r, col_idx),
                            'content': str(val).strip()
                        })
                        
        except Exception as e:
            context['error'] = f"Error getting context: {str(e)}"
            
        return context
    
    def _analyze_match_type(self, cell_value: str) -> str:
        """Analyze what type of Woodland/Hotel match this is"""
        
        cell_value_lower = cell_value.lower()
        
        if 'hotel woodland' in cell_value_lower or 'woodland hotel' in cell_value_lower:
            return "Direct Hotel-Woodland Match"
        elif 'woodland' in cell_value_lower and any(term in cell_value_lower for term in ['hotel', 'inn', 'resort']):
            return "Woodland + Hospitality Term"
        elif 'woodland' in cell_value_lower and any(term in cell_value_lower for term in ['development', 'property', 'project']):
            return "Woodland Development/Property"
        elif 'woodland' in cell_value_lower:
            return "General Woodland Reference"
        else:
            return "Other Match"
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate focused search report"""
        
        report = []
        report.append("=" * 80)
        report.append("FOCUSED HOTEL WOODLAND SEARCH REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now()}")
        report.append("")
        report.append("SEARCH CRITERIA:")
        report.append("- Looking for: Hotel Woodland, Woodland Hotel, Woodland Inn, etc.")
        report.append("- Excluding: Generic HUD Metro area references")
        report.append("")
        
        # Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Files Processed: {results['files_processed']}")
        report.append(f"Files with Specific Matches: {results['files_with_matches']}")
        report.append(f"Total Specific Matches Found: {results['total_matches']}")
        report.append("")
        
        if results['errors']:
            report.append("PROCESSING ERRORS")
            report.append("-" * 40)
            for error in results['errors']:
                report.append(f"⚠️  {error}")
            report.append("")
        
        # Detailed results
        if results['detailed_results']:
            report.append("DETAILED FINDINGS")
            report.append("-" * 40)
            
            for file_result in results['detailed_results']:
                report.append(f"\n📁 FILE: {file_result['file_name']}")
                report.append(f"Path: {file_result['file_path']}")
                report.append(f"Worksheets Searched: {file_result['worksheets_searched']}")
                report.append(f"Specific Matches Found: {len(file_result['matches'])}")
                report.append("")
                
                for i, match in enumerate(file_result['matches'], 1):
                    report.append(f"  🎯 SPECIFIC MATCH #{i}")
                    report.append(f"     Worksheet: {match['worksheet']}")
                    report.append(f"     Cell: {match['cell_reference']}")
                    report.append(f"     Content: {match['cell_content']}")
                    report.append(f"     Match Type: {match['match_type']}")
                    
                    # Show enhanced context
                    context = match['surrounding_context']
                    
                    if context.get('column_headers'):
                        report.append(f"     Possible Column Headers:")
                        for header in context['column_headers']:
                            report.append(f"       Row {header['row']}: {header['content']}")
                    
                    if context.get('full_row_data'):
                        report.append(f"     Complete Row Data:")
                        for item in context['full_row_data'][:10]:  # Limit to 10 items
                            report.append(f"       {item['cell_ref']}: {item['content']}")
                        if len(context['full_row_data']) > 10:
                            report.append(f"       ... and {len(context['full_row_data']) - 10} more items")
                    
                    report.append("")
        
        else:
            report.append("NO SPECIFIC MATCHES FOUND")
            report.append("No specific references to 'Hotel Woodland', 'Woodland Hotel', or similar")
            report.append("hospitality-related Woodland references were found in any of the processed files.")
            report.append("")
            report.append("Note: Generic HUD Metro area references like 'Houston-The Woodlands-Sugar Land'")
            report.append("were excluded from this focused search.")
        
        report.append("=" * 80)
        report.append("END OF FOCUSED SEARCH REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main execution function"""
    
    # Define the Excel files to search
    excel_files = [
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_LIHTC_Investment_Opportunities_20250703_172130_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_LIHTC_Investment_Opportunities_20250703_172422_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250703_173814_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_095500_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_102112_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_112036_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/Enhanced_Anchor_Analysis_With_Priority_Sheets_20250703_001634.xlsx"
    ]
    
    # Create focused searcher and run analysis
    searcher = FocusedHotelWoodlandSearcher()
    results = searcher.search_files(excel_files)
    
    # Generate and display report
    report = searcher.generate_report(results)
    print(report)
    
    # Save report to file
    report_filename = f"focused_hotel_woodland_search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Focused report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    main()