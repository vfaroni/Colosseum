#!/usr/bin/env python3
"""
Comprehensive Excel Search for Woodland Hotel References
Search through 8 Excel files for any mentions of "Hotel Woodland", "Woodland Hotel", "Woodland" 
in the context of hotels/development projects, owner/developer entities, legal structures, 
property addresses, or financial data.
"""

import pandas as pd
import openpyxl
import os
import re
from typing import List, Dict, Any, Tuple
import traceback
from datetime import datetime

class WoodlandHotelSearcher:
    def __init__(self):
        self.search_terms = [
            'woodland',
            'hotel woodland', 
            'woodland hotel'
        ]
        
        # Legal entity patterns to look for
        self.legal_patterns = [
            r'\b\w*LLC\b',
            r'\b\w*LP\b', 
            r'\b\w*Corporation\b',
            r'\b\w*Corp\b',
            r'\b\w*Partnership\b',
            r'\b\w*Limited\b',
            r'\b\w*Inc\b'
        ]
        
        # Hotel/development context keywords
        self.development_keywords = [
            'hotel', 'development', 'project', 'property', 'site', 'construction',
            'investment', 'opportunity', 'apartment', 'housing', 'residential',
            'commercial', 'real estate', 'lihtc', 'tax credit'
        ]
        
        # Financial context keywords
        self.financial_keywords = [
            'investment', 'equity', 'debt', 'financing', 'loan', 'credit',
            'capital', 'fund', 'revenue', 'income', 'cost', 'expense',
            'budget', 'financial', 'tax', 'lihtc'
        ]
        
        self.results = []
        
    def search_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Search through all Excel files for Woodland references"""
        
        print(f"Starting comprehensive search at {datetime.now()}")
        print(f"Searching {len(file_paths)} Excel files for Woodland references...")
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
                    
                    print(f"  ✅ Found {len(file_results['matches'])} matches")
                else:
                    print(f"  ❌ No matches found")
                    
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
        """Search a single worksheet for Woodland references"""
        
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
                        
                    # Check if cell contains any search terms (case insensitive)
                    if any(term.lower() in cell_value.lower() for term in self.search_terms):
                        
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
        
        # Analyze content for legal entities, development context, financial context
        analysis = self._analyze_content(cell_value, context)
        
        match_record = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'worksheet': sheet_name,
            'cell_reference': cell_ref,
            'cell_content': cell_value.strip(),
            'row_index': row_idx + 1,  # 1-based for Excel
            'column_index': col_idx + 1,  # 1-based for Excel
            'surrounding_context': context,
            'legal_entities_found': analysis['legal_entities'],
            'development_context': analysis['development_context'],
            'financial_context': analysis['financial_context'],
            'context_score': analysis['context_score']
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
                         context_range: int = 2) -> Dict[str, Any]:
        """Get surrounding cell context for better understanding"""
        
        context = {
            'same_row': [],
            'same_column': [],
            'nearby_cells': []
        }
        
        try:
            # Get cells in same row (left and right)
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
            
            # Get cells in same column (above and below)
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
            
            # Get nearby cells in a small grid
            for r in range(max(0, row_idx - 1), min(len(df_str), row_idx + 2)):
                for c in range(max(0, col_idx - 1), min(len(df_str.columns), col_idx + 2)):
                    if r != row_idx or c != col_idx:
                        val = df_str.iloc[r, c]
                        if not pd.isna(val) and str(val).strip() != '' and str(val) != 'nan':
                            context['nearby_cells'].append({
                                'cell_ref': self._to_excel_cell_ref(r, c),
                                'content': str(val).strip()
                            })
                            
        except Exception as e:
            context['error'] = f"Error getting context: {str(e)}"
            
        return context
    
    def _analyze_content(self, cell_value: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cell content and context for legal entities, development, financial info"""
        
        analysis = {
            'legal_entities': [],
            'development_context': [],
            'financial_context': [],
            'context_score': 0
        }
        
        # Combine cell value with context for analysis
        all_text = cell_value.lower()
        
        # Add context text
        for context_type in ['same_row', 'same_column', 'nearby_cells']:
            if context_type in context:
                for item in context[context_type]:
                    all_text += " " + item['content'].lower()
        
        # Check for legal entity patterns
        for pattern in self.legal_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            analysis['legal_entities'].extend(matches)
        
        # Check for development context
        for keyword in self.development_keywords:
            if keyword.lower() in all_text:
                analysis['development_context'].append(keyword)
                analysis['context_score'] += 1
        
        # Check for financial context
        for keyword in self.financial_keywords:
            if keyword.lower() in all_text:
                analysis['financial_context'].append(keyword)
                analysis['context_score'] += 1
        
        # Remove duplicates
        analysis['legal_entities'] = list(set(analysis['legal_entities']))
        analysis['development_context'] = list(set(analysis['development_context']))
        analysis['financial_context'] = list(set(analysis['financial_context']))
        
        return analysis
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive search report"""
        
        report = []
        report.append("=" * 80)
        report.append("WOODLAND HOTEL COMPREHENSIVE SEARCH REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now()}")
        report.append("")
        
        # Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Files Processed: {results['files_processed']}")
        report.append(f"Files with Matches: {results['files_with_matches']}")
        report.append(f"Total Matches Found: {results['total_matches']}")
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
                report.append(f"Matches Found: {len(file_result['matches'])}")
                report.append("")
                
                # Sort matches by context score (most relevant first)
                matches = sorted(file_result['matches'], 
                               key=lambda x: x['context_score'], reverse=True)
                
                for i, match in enumerate(matches, 1):
                    report.append(f"  🎯 MATCH #{i}")
                    report.append(f"     Worksheet: {match['worksheet']}")
                    report.append(f"     Cell: {match['cell_reference']}")
                    report.append(f"     Content: {match['cell_content']}")
                    report.append(f"     Context Score: {match['context_score']}")
                    
                    if match['legal_entities_found']:
                        report.append(f"     Legal Entities: {', '.join(match['legal_entities_found'])}")
                    
                    if match['development_context']:
                        report.append(f"     Development Context: {', '.join(match['development_context'])}")
                    
                    if match['financial_context']:
                        report.append(f"     Financial Context: {', '.join(match['financial_context'])}")
                    
                    # Show surrounding context
                    context = match['surrounding_context']
                    if context.get('same_row'):
                        report.append(f"     Same Row Context:")
                        for ctx in context['same_row'][:3]:  # Limit to 3 items
                            report.append(f"       {ctx['cell_ref']}: {ctx['content'][:100]}...")
                    
                    if context.get('same_column'):
                        report.append(f"     Same Column Context:")
                        for ctx in context['same_column'][:3]:  # Limit to 3 items
                            report.append(f"       {ctx['cell_ref']}: {ctx['content'][:100]}...")
                    
                    report.append("")
        
        else:
            report.append("NO MATCHES FOUND")
            report.append("No references to 'Woodland' were found in any of the processed files.")
        
        report.append("=" * 80)
        report.append("END OF REPORT")
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
    
    # Create searcher and run analysis
    searcher = WoodlandHotelSearcher()
    results = searcher.search_files(excel_files)
    
    # Generate and display report
    report = searcher.generate_report(results)
    print(report)
    
    # Save report to file
    report_filename = f"woodland_hotel_search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    main()