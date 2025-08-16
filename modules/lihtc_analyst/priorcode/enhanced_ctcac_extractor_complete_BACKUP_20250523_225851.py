#!/usr/bin/env python3
"""
Enhanced CTCAC LIHTC Application Data Extractor - Complete Production Version
Extracts comprehensive data from CTCAC applications for RAG system

This enhanced version captures:
- Complete project information & unit mix details
- All financing sources and detailed cost breakdowns  
- Full competitive scoring breakdown with all point categories
- Comprehensive basis & credit calculations
- Complete tie breaker responses
- 15-year pro forma data
- Sources and basis breakdown details
- SCE/FCE basis calculations

Based on detailed analysis of 2023-2025 CTCAC applications (4% and 9%)
"""

import pandas as pd
import json
import os
import logging
from pathlib import Path
from datetime import datetime
import openpyxl
from typing import Dict, List, Any, Optional
import re
import sys

class CTCACComprehensiveExtractor:
    """
    Comprehensive extractor that captures ALL valuable data from CTCAC applications
    """
    
    def __init__(self, input_path: str, output_path_4p: str, output_path_9p: str, log_path: str):
        """Initialize the extractor with file paths"""
        self.input_path = Path(input_path)
        self.output_path_4p = Path(output_path_4p)
        self.output_path_9p = Path(output_path_9p)
        self.log_path = Path(log_path)
        
        # Create directories if they don't exist
        self.output_path_4p.mkdir(parents=True, exist_ok=True)
        self.output_path_9p.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.setup_logging()
        
        # Define comprehensive sheet mapping
        self.target_sheets = {
            'application': 'Application',
            'sources_uses': 'Sources and Uses Budget',
            'sources_basis_breakdown': 'Sources and Basis Breakdown',
            'points_system': 'Points System',
            'basis_credits': 'Basis & Credits',
            'tie_breaker': 'Tie Breaker',
            'final_tie_breaker': 'Final Tie Breaker ',
            'disaster_tie_breaker': 'Disaster Credit Tie Breaker',
            'pro_forma': '15 Year Pro Forma',
            'sce_basis': 'SCE Basis and Credits',
            'fce_basis': 'FCE Basis and Credits',
            'calHFA_addendum': 'CalHFA Addendum',
            'subsidy_contract': 'Subsidy Contract Calculation'
        }
    
    def setup_logging(self):
        """Set up logging configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_path / f"ctcac_comprehensive_extraction_{timestamp}.log"
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
        
        self.logger.info(f"Comprehensive extraction logging initialized. Log file: {log_file}")
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """Parse filename to extract metadata"""
        base_name = Path(filename).stem
        
        parsed = {
            'year': 'unknown',
            'credit_type': 'unknown',
            'round': 'unknown',
            'project_id': 'unknown',
            'original_filename': filename
        }
        
        try:
            # Pattern for both formats: YYYY_XpctXX_RX_YY-XXX and YYYY_XpctXX_RX_CAYYXXX
            pattern = r'(\d{4})_(\d+pct)_([rR]\d+)_(?:CA)?(.+)'
            match = re.match(pattern, base_name)
            
            if match:
                parsed['year'] = match.group(1)
                parsed['credit_type'] = match.group(2)
                parsed['round'] = match.group(3).upper()
                parsed['project_id'] = match.group(4)
        
        except Exception as e:
            self.logger.warning(f"Error parsing filename {filename}: {e}")
        
        return parsed
    
    def determine_output_path(self, parsed_info: Dict[str, str]) -> Path:
        """Determine correct output path based on credit type"""
        if '4' in parsed_info['credit_type']:
            return self.output_path_4p
        else:
            return self.output_path_9p
    
    def create_output_filename(self, parsed_info: Dict[str, str]) -> str:
        """Create standardized output filename"""
        return f"{parsed_info['year']}_{parsed_info['credit_type']}_{parsed_info['round']}_CA-{parsed_info['project_id']}.json"
    
    def get_cell_value(self, sheet, cell_ref: str):
        """Safely get cell value from sheet, handling merged cells"""
        try:
            cell = sheet[cell_ref]
            
            # If cell is part of a merged range, get the value from the top-left cell
            if hasattr(sheet, 'merged_cells'):
                for merged_range in sheet.merged_cells.ranges:
                    if cell_ref in merged_range:
                        # Get the top-left cell of the merged range
                        top_left_cell = sheet.cell(merged_range.min_row, merged_range.min_col)
                        return top_left_cell.value if top_left_cell and top_left_cell.value is not None else None
            
            return cell.value if cell and cell.value is not None else None
        except:
            return None
    
    def scan_merged_cell_area(self, sheet, start_row: int, end_row: int, start_col: int = 0, end_col: int = 15):
        """Scan an area and return all non-None values, handling merged cells properly"""
        values = {}
        
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                col_letter = chr(65 + col)
                cell_ref = f'{col_letter}{row}'
                value = self.get_cell_value(sheet, cell_ref)
                
                if value is not None:
                    values[cell_ref] = value
        
        return values
    
    def find_sheet_name(self, workbook, target_name: str) -> Optional[str]:
        """Find the actual shee