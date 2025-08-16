#!/usr/bin/env python3
"""
Site Data Reader - Batch Processing Module

This module provides functionality for reading and validating CSV and Excel files containing
multiple LIHTC site locations for batch analysis.

Features:
- CSV and Excel file support (.csv, .xlsx, .xls)
- Automatic file format detection
- Required column validation (site_id, latitude, longitude)
- Data type validation with coordinate range checking
- Duplicate site ID detection
- Row-level error reporting with line numbers
- Support for optional columns (address, notes)
- Column name mapping and normalization
"""

import csv
import logging
from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
import pandas as pd


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass


# Keep backward compatibility
CSVValidationError = FileValidationError


class SiteDataReader:
    """
    Site data reader for LIHTC sites with support for CSV and Excel files
    
    Validates file structure, data types, and coordinate ranges before
    returning clean site data for batch processing. Supports automatic
    file format detection and column name mapping.
    """
    
    # Required columns for site analysis
    REQUIRED_COLUMNS = {'site_id', 'latitude', 'longitude'}
    
    # Optional columns that will be preserved if present
    OPTIONAL_COLUMNS = {'address', 'notes', 'description', 'project_type', 'name', 'city', 'state'}
    
    # Column name mapping for common variations
    COLUMN_MAPPING = {
        # Site ID variations
        'id': 'site_id',
        'site_id': 'site_id',
        'property_id': 'site_id',
        'parcel_id': 'site_id',
        'record_id': 'site_id',
        
        # Latitude variations
        'lat': 'latitude',
        'latitude': 'latitude',
        'y': 'latitude',
        'y_coordinate': 'latitude',
        
        # Longitude variations
        'lon': 'longitude',
        'lng': 'longitude',
        'long': 'longitude',
        'longitude': 'longitude',
        'x': 'longitude',
        'x_coordinate': 'longitude',
        
        # Address variations
        'address': 'address',
        'property_address': 'address',
        'full_address': 'address',
        'street_address': 'address',
        
        # Name variations
        'name': 'name',
        'property_name': 'name',
        'site_name': 'name',
        'project_name': 'name',
        
        # City variations
        'city': 'city',
        'municipality': 'city',
        
        # State variations
        'state': 'state',
        'state_code': 'state',
        
        # Notes variations
        'notes': 'notes',
        'comments': 'notes',
        'description': 'description',
        'remarks': 'notes'
    }
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    
    # Coordinate validation ranges
    LATITUDE_RANGE = (-90.0, 90.0)
    LONGITUDE_RANGE = (-180.0, 180.0)
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize site data reader
        
        Args:
            logger: Optional logger for error reporting
        """
        self.logger = logger or logging.getLogger(__name__)
        self._sites_data = []
        self._validation_errors = []
    
    def load_file(self, file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load and validate CSV or Excel file containing site data
        
        Args:
            file_path: Path to CSV or Excel file
            sheet_name: Optional sheet name for Excel files (uses first sheet if None)
            
        Returns:
            List of validated site dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            FileValidationError: If file validation fails
        """
        file_obj = Path(file_path)
        
        # Check file exists
        if not file_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file is not empty
        if file_obj.stat().st_size == 0:
            raise ValueError("File is empty")
        
        # Check file extension
        file_extension = file_obj.suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            raise FileValidationError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        try:
            # Read file based on extension
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
                self.logger.debug(f"Reading CSV file: {file_path}")
            else:  # Excel files (.xlsx, .xls)
                if sheet_name is None:
                    # Default to first sheet (sheet_name=0) to get DataFrame
                    df = pd.read_excel(file_path, sheet_name=0)
                    self.logger.debug(f"Reading Excel file: {file_path}, sheet: first sheet (0)")
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    self.logger.debug(f"Reading Excel file: {file_path}, sheet: {sheet_name}")
            
            if len(df) == 0:
                raise ValueError("File contains no data rows")
            
            # Apply column mapping to normalize column names
            df = self._apply_column_mapping(df)
            
            # Validate file structure
            self._validate_file_structure(df, file_path)
            
            # Convert to list of dictionaries and validate each row
            sites_data = []
            for index, row in df.iterrows():
                try:
                    site_data = self._validate_and_process_row(row, index + 2)  # +2 for header + 0-based index
                    sites_data.append(site_data)
                except FileValidationError as e:
                    raise FileValidationError(f"Error in row {index + 2}: {e}")
            
            # Check for duplicate site IDs
            self._validate_unique_site_ids(sites_data)
            
            self.logger.info(f"Successfully loaded {len(sites_data)} sites from {file_path}")
            return sites_data
            
        except pd.errors.EmptyDataError:
            raise ValueError("File is empty or contains no data")
        except pd.errors.ParserError as e:
            raise ValueError(f"Malformed file: {e}")
        except Exception as e:
            if isinstance(e, (FileValidationError, ValueError, FileNotFoundError)):
                raise
            else:
                raise FileValidationError(f"Unexpected error reading file: {e}")
    
    def _apply_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply column name mapping to normalize column names
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with normalized column names
        """
        # Ensure we have a DataFrame
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(df)}")
        
        # Create mapping for columns that exist in the DataFrame
        column_mapping = {}
        df_columns_lower = {col: col.lower().strip() for col in df.columns}
        
        for original_col, lower_col in df_columns_lower.items():
            if lower_col in self.COLUMN_MAPPING:
                mapped_name = self.COLUMN_MAPPING[lower_col]
                column_mapping[original_col] = mapped_name
                self.logger.debug(f"Mapping column '{original_col}' -> '{mapped_name}'")
        
        # Apply the mapping
        if column_mapping:
            df = df.rename(columns=column_mapping)
            self.logger.info(f"Applied column mappings: {list(column_mapping.values())}")
        
        return df
    
    def _validate_file_structure(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Validate file has required columns and proper structure
        
        Args:
            df: DataFrame to validate
            file_path: Path for error reporting
        """
        # Check for required columns (now that column mapping has been applied)
        df_columns = set(df.columns)
        missing_columns = self.REQUIRED_COLUMNS - df_columns
        
        if missing_columns:
            raise FileValidationError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Required: {', '.join(self.REQUIRED_COLUMNS)}"
            )
    
    def _validate_and_process_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """
        Validate and process a single file row
        
        Args:
            row: Pandas Series representing a file row
            row_number: Row number for error reporting (1-based)
            
        Returns:
            Validated site data dictionary
        """
        site_data = {}
        
        # Validate site_id
        site_id = str(row['site_id']).strip()
        if not site_id or site_id.lower() == 'nan':
            raise FileValidationError("Empty site_id not allowed")
        site_data['site_id'] = site_id
        
        # Validate and convert latitude
        try:
            latitude = float(row['latitude'])
            if not (self.LATITUDE_RANGE[0] <= latitude <= self.LATITUDE_RANGE[1]):
                raise FileValidationError(
                    f"Latitude out of range: {latitude}. "
                    f"Must be between {self.LATITUDE_RANGE[0]} and {self.LATITUDE_RANGE[1]}"
                )
            site_data['latitude'] = latitude
        except (ValueError, TypeError):
            raise FileValidationError(f"Invalid latitude: {row['latitude']}")
        
        # Validate and convert longitude
        try:
            longitude = float(row['longitude'])
            if not (self.LONGITUDE_RANGE[0] <= longitude <= self.LONGITUDE_RANGE[1]):
                raise FileValidationError(
                    f"Longitude out of range: {longitude}. "
                    f"Must be between {self.LONGITUDE_RANGE[0]} and {self.LONGITUDE_RANGE[1]}"
                )
            site_data['longitude'] = longitude
        except (ValueError, TypeError):
            raise FileValidationError(f"Invalid longitude: {row['longitude']}")
        
        # Add optional columns if present
        for col in row.index:
            if col not in self.REQUIRED_COLUMNS and col in row:
                value = row[col]
                # Only add non-null optional values
                if pd.notna(value) and str(value).strip():
                    site_data[col] = str(value).strip()
        
        return site_data
    
    def _validate_unique_site_ids(self, sites_data: List[Dict[str, Any]]) -> None:
        """
        Validate that all site IDs are unique
        
        Args:
            sites_data: List of site dictionaries to check
        """
        site_ids = [site['site_id'] for site in sites_data]
        duplicates = []
        seen = set()
        
        for site_id in site_ids:
            if site_id in seen:
                duplicates.append(site_id)
            else:
                seen.add(site_id)
        
        if duplicates:
            raise FileValidationError(f"Duplicate site_id values found: {', '.join(set(duplicates))}")
    
    def validate_file(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate file without loading data (for quick validation)
        
        Args:
            file_path: Path to CSV or Excel file
            sheet_name: Optional sheet name for Excel files
            
        Returns:
            Validation summary dictionary
        """
        validation_result = {
            'valid': False,
            'row_count': 0,
            'column_count': 0,
            'required_columns_present': False,
            'file_type': None,
            'errors': []
        }
        
        try:
            file_obj = Path(file_path)
            if not file_obj.exists():
                validation_result['errors'].append(f"File not found: {file_path}")
                return validation_result
            
            # Check file extension
            file_extension = file_obj.suffix.lower()
            if file_extension not in self.SUPPORTED_EXTENSIONS:
                validation_result['errors'].append(f"Unsupported file format: {file_extension}")
                return validation_result
            
            validation_result['file_type'] = file_extension
            
            # Read file based on extension
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                if sheet_name is None:
                    # Default to first sheet (sheet_name=0) to get DataFrame
                    df = pd.read_excel(file_path, sheet_name=0)
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Check if we got a DataFrame
            if not isinstance(df, pd.DataFrame):
                validation_result['errors'].append(f"Failed to read file as DataFrame, got {type(df)}")
                return validation_result
            
            validation_result['row_count'] = len(df)
            validation_result['column_count'] = len(df.columns)
            
            # Apply column mapping
            df = self._apply_column_mapping(df)
            
            # Check required columns
            df_columns = set(df.columns)
            missing_columns = self.REQUIRED_COLUMNS - df_columns
            
            if not missing_columns:
                validation_result['required_columns_present'] = True
                validation_result['valid'] = True
            else:
                validation_result['errors'].append(f"Missing columns: {', '.join(missing_columns)}")
        
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result
    
    def validate_csv_file(self, csv_path: str) -> Dict[str, Any]:
        """
        Validate CSV file without loading data (for quick validation)
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Validation summary dictionary
        """
        # Use the generic file validation method
        return self.validate_file(csv_path)
    
    def load_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Load CSV file (backward compatibility method)
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of validated site dictionaries
        """
        return self.load_file(csv_path)
    
    def get_sample_csv_format(self) -> str:
        """
        Return sample CSV format string for documentation
        
        Returns:
            Sample CSV format as string
        """
        return """site_id,latitude,longitude,address,notes
SITE001,37.3897,-121.9927,"1205 Oakmead Parkway, Sunnyvale CA","DDA qualified site"
SITE002,32.7157,-117.1611,"Downtown San Diego, CA","High amenity density"
SITE003,34.0522,-118.2437,"Central Los Angeles, CA","Major metropolitan area" """


def main():
    """Command-line interface for testing CSV reader"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate LIHTC sites CSV file')
    parser.add_argument('csv_file', help='Path to CSV file to validate')
    parser.add_argument('--sample', action='store_true', help='Show sample CSV format')
    
    args = parser.parse_args()
    
    if args.sample:
        reader = CSVSiteReader()
        print("Sample CSV format:")
        print(reader.get_sample_csv_format())
        return
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        reader = CSVSiteReader()
        
        # Quick validation first
        validation_result = reader.validate_csv_file(args.csv_file)
        print(f"CSV Validation Results for: {args.csv_file}")
        print(f"Valid: {validation_result['valid']}")
        print(f"Rows: {validation_result['row_count']}")
        print(f"Columns: {validation_result['column_count']}")
        print(f"Required columns present: {validation_result['required_columns_present']}")
        
        if validation_result['errors']:
            print("Errors:")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        if validation_result['valid']:
            # Full load and validation
            sites_data = reader.load_csv(args.csv_file)
            print(f"\n✅ Successfully loaded {len(sites_data)} sites")
            
            # Show first few sites
            for i, site in enumerate(sites_data[:3]):
                print(f"  Site {i+1}: {site['site_id']} at ({site['latitude']}, {site['longitude']})")
            
            if len(sites_data) > 3:
                print(f"  ... and {len(sites_data) - 3} more sites")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()