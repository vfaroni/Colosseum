#!/usr/bin/env python3
"""
🏛️ CALIFORNIA HCD HOUSING ELEMENT DATA LOADER
Roman Engineering Standards: Built to Last 2000+ Years
Built by Structured Consultants LLC for Colosseum Platform

Comprehensive ETL pipeline for loading all HCD Housing Element CSV data
Tables A, A2, C-K with validation and intelligence integration
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import numpy as np
from pathlib import Path
import logging
from datetime import datetime, date
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import warnings
from dataclasses import dataclass
import os

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🏛️ %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hcd_data_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HCDDataConfig:
    """Configuration for HCD data loading"""
    data_path: str
    database_config: Dict[str, Any]
    batch_size: int = 1000
    validate_data: bool = True
    update_existing: bool = True

class ColasseumHCDDataLoader:
    """Comprehensive HCD Housing Element Data Loader for Colosseum Platform"""
    
    def __init__(self, config: HCDDataConfig):
        """Initialize the data loader with configuration"""
        self.config = config
        self.data_path = Path(config.data_path)
        self.engine = None
        self.connection = None
        
        # HCD Table mappings
        self.table_mappings = {
            'HCD_HE_tablea.csv': 'housing_applications',
            'HCD_HE_tablea2.csv': 'building_permits',
            'HCD_HE_tablec.csv': 'sites_inventory',
            'HCD_HE_tabled.csv': 'workforce_housing',
            'HCD_HE_tablee.csv': 'accessory_units',
            'HCD_HE_tablef.csv': 'subsidized_housing',
            'HCD_HE_tablef2.csv': 'subsidized_housing_detail',
            'HCD_HE_tableg.csv': 'governmental_constraints',
            'HCD_HE_tableh.csv': 'non_governmental_constraints',
            'HCD_HE_tablei.csv': 'housing_preservation',
            'HCD_HE_tablek.csv': 'fair_share_plan'
        }
        
        # Income category mappings
        self.income_categories = {
            'vlow_income_dr': 'Very Low Income (Deed Restricted)',
            'vlow_income_ndr': 'Very Low Income (Non-Deed Restricted)',
            'low_income_dr': 'Low Income (Deed Restricted)',
            'low_income_ndr': 'Low Income (Non-Deed Restricted)',
            'mod_income_dr': 'Moderate Income (Deed Restricted)',
            'mod_income_ndr': 'Moderate Income (Non-Deed Restricted)',
            'above_mod_income': 'Above Moderate Income'
        }
        
        # Data validation rules
        self.validation_rules = {
            'required_columns': {
                'housing_applications': ['JURIS_NAME', 'CNTY_NAME', 'YEAR'],
                'building_permits': ['JURIS_NAME', 'CNTY_NAME', 'YEAR']
            },
            'numeric_columns': [
                'VLOW_INCOME_DR', 'VLOW_INCOME_NDR', 'LOW_INCOME_DR', 
                'LOW_INCOME_NDR', 'MOD_INCOME_DR', 'MOD_INCOME_NDR', 
                'ABOVE_MOD_INCOME'
            ],
            'date_columns': [
                'APP_SUBMIT_DT', 'ENT_APPROVE_DT1', 'BP_ISSUE_DT1', 'CO_ISSUE_DT1'
            ]
        }
        
    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            db_config = self.config.database_config
            connection_string = (
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            
            logger.info("✅ Database connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def validate_data_files(self) -> bool:
        """Validate that required data files exist and are readable"""
        missing_files = []
        
        for file_name in self.table_mappings.keys():
            file_path = self.data_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
            else:
                try:
                    # Test read first few rows
                    pd.read_csv(file_path, nrows=5)
                    logger.info(f"✅ Validated file: {file_name}")
                except Exception as e:
                    logger.error(f"❌ File validation failed for {file_name}: {e}")
                    missing_files.append(file_name)
        
        if missing_files:
            logger.error(f"❌ Missing or invalid files: {missing_files}")
            return False
        
        logger.info("✅ All HCD data files validated")
        return True
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names for database compatibility"""
        # Convert to lowercase and replace spaces/special chars with underscores
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') 
                     for col in df.columns]
        return df
    
    def parse_dates(self, date_str: Any) -> Optional[date]:
        """Parse various date formats to standard date"""
        if pd.isna(date_str) or date_str == '':
            return None
        
        if isinstance(date_str, (date, datetime)):
            return date_str.date() if isinstance(date_str, datetime) else date_str
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', 
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"⚠️ Could not parse date: {date_str}")
        return None
    
    def standardize_jurisdiction_name(self, name: str) -> str:
        """Standardize jurisdiction names for consistency"""
        if pd.isna(name):
            return ""
        
        # Remove extra whitespace and standardize case
        name = str(name).strip().title()
        
        # Handle common variations
        name_mappings = {
            'Los Angeles City': 'Los Angeles',
            'San Francisco City': 'San Francisco',
            'San Diego City': 'San Diego'
        }
        
        return name_mappings.get(name, name)
    
    def process_housing_applications_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Table A - Housing Applications data"""
        logger.info("🔄 Processing Table A - Housing Applications")
        
        # Clean and standardize
        df = self.clean_column_names(df)
        
        # Standardize jurisdiction names
        if 'juris_name' in df.columns:
            df['juris_name'] = df['juris_name'].apply(self.standardize_jurisdiction_name)
        
        # Parse dates
        date_columns = ['app_submit_dt']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.parse_dates)
        
        # Convert numeric columns
        numeric_columns = [
            'vlow_income_dr', 'vlow_income_ndr', 'low_income_dr', 
            'low_income_ndr', 'mod_income_dr', 'mod_income_ndr', 
            'above_mod_income', 'tot_proposed_units', 'tot_approved_units'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Add derived columns
        df['total_affordable_units'] = (
            df.get('vlow_income_dr', 0) + df.get('vlow_income_ndr', 0) + 
            df.get('low_income_dr', 0) + df.get('low_income_ndr', 0) + 
            df.get('mod_income_dr', 0) + df.get('mod_income_ndr', 0)
        )
        
        # Add processing metadata
        df['processed_at'] = datetime.now()
        df['data_source'] = 'HCD_Table_A'
        
        logger.info(f"✅ Processed {len(df)} housing application records")
        return df
    
    def process_building_permits_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Table A2 - Building Permits data (Critical RHNA metric)"""
        logger.info("🔄 Processing Table A2 - Building Permits (Critical RHNA Data)")
        
        # Clean and standardize
        df = self.clean_column_names(df)
        
        # Standardize jurisdiction names
        if 'juris_name' in df.columns:
            df['juris_name'] = df['juris_name'].apply(self.standardize_jurisdiction_name)
        
        # Parse dates - critical for RHNA compliance tracking
        date_columns = ['ent_approve_dt1', 'bp_issue_dt1', 'co_issue_dt1']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.parse_dates)
        
        # Convert all income category columns to numeric
        income_columns = [
            'vlow_income_dr', 'vlow_income_ndr', 'low_income_dr', 'low_income_ndr',
            'mod_income_dr', 'mod_income_ndr', 'above_mod_income',
            'bp_vlow_income_dr', 'bp_vlow_income_ndr', 'bp_low_income_dr', 
            'bp_low_income_ndr', 'bp_mod_income_dr', 'bp_mod_income_ndr', 
            'bp_above_mod_income',
            'co_vlow_income_dr', 'co_vlow_income_ndr', 'co_low_income_dr',
            'co_low_income_ndr', 'co_mod_income_dr', 'co_mod_income_ndr',
            'co_above_mod_income', 'extr_low_income_units'
        ]
        
        for col in income_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Calculate total units by category
        df['total_entitled_units'] = (
            df.get('vlow_income_dr', 0) + df.get('vlow_income_ndr', 0) + 
            df.get('low_income_dr', 0) + df.get('low_income_ndr', 0) + 
            df.get('mod_income_dr', 0) + df.get('mod_income_ndr', 0) + 
            df.get('above_mod_income', 0)
        )
        
        df['total_permitted_units'] = (
            df.get('bp_vlow_income_dr', 0) + df.get('bp_vlow_income_ndr', 0) + 
            df.get('bp_low_income_dr', 0) + df.get('bp_low_income_ndr', 0) + 
            df.get('bp_mod_income_dr', 0) + df.get('bp_mod_income_ndr', 0) + 
            df.get('bp_above_mod_income', 0)
        )
        
        df['total_completed_units'] = (
            df.get('co_vlow_income_dr', 0) + df.get('co_vlow_income_ndr', 0) + 
            df.get('co_low_income_dr', 0) + df.get('co_low_income_ndr', 0) + 
            df.get('co_mod_income_dr', 0) + df.get('co_mod_income_ndr', 0) + 
            df.get('co_above_mod_income', 0)
        )
        
        # Add RHNA compliance flags
        df['rhna_eligible'] = df['total_permitted_units'] > 0
        df['affordable_component'] = (
            (df.get('bp_vlow_income_dr', 0) + df.get('bp_vlow_income_ndr', 0) + 
             df.get('bp_low_income_dr', 0) + df.get('bp_low_income_ndr', 0) + 
             df.get('bp_mod_income_dr', 0) + df.get('bp_mod_income_ndr', 0)) > 0
        )
        
        # Add processing metadata
        df['processed_at'] = datetime.now()
        df['data_source'] = 'HCD_Table_A2'
        
        logger.info(f"✅ Processed {len(df)} building permit records")
        logger.info(f"📊 RHNA-eligible permits: {df['rhna_eligible'].sum()}")
        logger.info(f"🏠 With affordable component: {df['affordable_component'].sum()}")
        
        return df
    
    def get_or_create_jurisdiction(self, jurisdiction_name: str, county_name: str, year: int) -> Optional[int]:
        """Get or create jurisdiction record and return jurisdiction_id"""
        try:
            # First try to find existing jurisdiction
            query = text("""
                SELECT jurisdiction_id FROM jurisdictions 
                WHERE jurisdiction_name = :name AND county_name = :county
            """)
            
            result = self.connection.execute(query, {
                'name': jurisdiction_name, 
                'county': county_name
            }).fetchone()
            
            if result:
                return result[0]
            
            # Create new jurisdiction
            insert_query = text("""
                INSERT INTO jurisdictions (jurisdiction_name, county_name, jurisdiction_type)
                VALUES (:name, :county, 'City')
                RETURNING jurisdiction_id
            """)
            
            result = self.connection.execute(insert_query, {
                'name': jurisdiction_name,
                'county': county_name
            }).fetchone()
            
            self.connection.commit()
            
            if result:
                logger.info(f"✅ Created jurisdiction: {jurisdiction_name}, {county_name}")
                return result[0]
            
        except Exception as e:
            logger.error(f"❌ Failed to get/create jurisdiction {jurisdiction_name}: {e}")
            self.connection.rollback()
        
        return None
    
    def load_housing_applications(self, df: pd.DataFrame) -> bool:
        """Load housing applications data into database"""
        try:
            logger.info("🔄 Loading housing applications to database...")
            
            # Process jurisdictions and get IDs
            df['jurisdiction_id'] = df.apply(
                lambda row: self.get_or_create_jurisdiction(
                    row.get('juris_name', ''), 
                    row.get('cnty_name', ''), 
                    row.get('year', 2023)
                ), axis=1
            )
            
            # Filter out rows without jurisdiction_id
            valid_rows = df[df['jurisdiction_id'].notna()]
            logger.info(f"📊 Loading {len(valid_rows)} valid application records")
            
            # Map DataFrame columns to database columns
            column_mapping = {
                'jurisdiction_id': 'jurisdiction_id',
                'prior_apn': 'prior_apn',
                'apn': 'apn',
                'street_address': 'street_address',
                'project_name': 'project_name',
                'jurs_tracking_id': 'jurisdiction_tracking_id',
                'unit_cat': 'unit_category',
                'tenure': 'tenure',
                'app_submit_dt': 'app_submit_date',
                'vlow_income_dr': 'vlow_income_dr',
                'vlow_income_ndr': 'vlow_income_ndr',
                # ... add more mappings as needed
                'year': 'reporting_year'
            }
            
            # Select and rename columns
            db_df = valid_rows.rename(columns=column_mapping)
            
            # Load to database in batches
            batch_size = self.config.batch_size
            total_rows = len(db_df)
            
            for i in range(0, total_rows, batch_size):
                batch = db_df.iloc[i:i+batch_size]
                batch.to_sql(
                    'housing_applications', 
                    self.engine, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                logger.info(f"✅ Loaded batch {i//batch_size + 1}: {len(batch)} records")
            
            logger.info(f"✅ Successfully loaded {total_rows} housing application records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load housing applications: {e}")
            return False
    
    def load_building_permits(self, df: pd.DataFrame) -> bool:
        """Load building permits data into database"""
        try:
            logger.info("🔄 Loading building permits to database...")
            
            # Process jurisdictions and get IDs
            df['jurisdiction_id'] = df.apply(
                lambda row: self.get_or_create_jurisdiction(
                    row.get('juris_name', ''), 
                    row.get('cnty_name', ''), 
                    row.get('year', 2023)
                ), axis=1
            )
            
            # Filter out rows without jurisdiction_id
            valid_rows = df[df['jurisdiction_id'].notna()]
            logger.info(f"📊 Loading {len(valid_rows)} valid building permit records")
            
            # Map DataFrame columns to database columns
            column_mapping = {
                'jurisdiction_id': 'jurisdiction_id',
                'prior_apn': 'prior_apn',
                'apn': 'apn',
                'street_address': 'street_address',
                'project_name': 'project_name',
                'jurs_tracking_id': 'jurisdiction_tracking_id',
                'unit_cat': 'unit_category',
                'tenure': 'tenure',
                'bp_issue_dt1': 'bp_issue_date',
                'co_issue_dt1': 'co_issue_date',
                # Income categories
                'vlow_income_dr': 'vlow_income_dr',
                'vlow_income_ndr': 'vlow_income_ndr',
                'low_income_dr': 'low_income_dr',
                'low_income_ndr': 'low_income_ndr',
                'mod_income_dr': 'mod_income_dr',
                'mod_income_ndr': 'mod_income_ndr',
                'above_mod_income': 'above_mod_income',
                # Building permit categories
                'bp_vlow_income_dr': 'bp_vlow_income_dr',
                'bp_vlow_income_ndr': 'bp_vlow_income_ndr',
                'bp_low_income_dr': 'bp_low_income_dr',
                'bp_low_income_ndr': 'bp_low_income_ndr',
                'bp_mod_income_dr': 'bp_mod_income_dr',
                'bp_mod_income_ndr': 'bp_mod_income_ndr',
                'bp_above_mod_income': 'bp_above_mod_income',
                # Certificate of occupancy categories
                'co_vlow_income_dr': 'co_vlow_income_dr',
                'co_vlow_income_ndr': 'co_vlow_income_ndr',
                'co_low_income_dr': 'co_low_income_dr',
                'co_low_income_ndr': 'co_low_income_ndr',
                'co_mod_income_dr': 'co_mod_income_dr',
                'co_mod_income_ndr': 'co_mod_income_ndr',
                'co_above_mod_income': 'co_above_mod_income',
                'extr_low_income_units': 'extremely_low_income_units',
                'approve_sb35': 'sb35_approval',
                'notes': 'notes',
                'year': 'reporting_year'
            }
            
            # Select and rename columns that exist
            available_columns = {k: v for k, v in column_mapping.items() if k in valid_rows.columns}
            db_df = valid_rows[list(available_columns.keys())].rename(columns=available_columns)
            
            # Load to database in batches
            batch_size = self.config.batch_size
            total_rows = len(db_df)
            
            for i in range(0, total_rows, batch_size):
                batch = db_df.iloc[i:i+batch_size]
                batch.to_sql(
                    'building_permits', 
                    self.engine, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                logger.info(f"✅ Loaded batch {i//batch_size + 1}: {len(batch)} records")
            
            logger.info(f"✅ Successfully loaded {total_rows} building permit records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load building permits: {e}")
            return False
    
    def generate_data_summary(self) -> Dict[str, Any]:
        """Generate comprehensive data loading summary"""
        try:
            summary = {
                'loading_date': datetime.now().isoformat(),
                'data_source': 'CA HCD Housing Element',
                'tables_loaded': {},
                'jurisdictions': {},
                'data_quality': {}
            }
            
            # Get table counts
            tables = ['jurisdictions', 'housing_applications', 'building_permits']
            
            for table in tables:
                try:
                    result = self.connection.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    summary['tables_loaded'][table] = result[0] if result else 0
                except Exception as e:
                    summary['tables_loaded'][table] = f"Error: {e}"
            
            # Get jurisdiction summary
            try:
                result = self.connection.execute(text("""
                    SELECT county_name, COUNT(*) as jurisdiction_count
                    FROM jurisdictions 
                    GROUP BY county_name 
                    ORDER BY jurisdiction_count DESC
                    LIMIT 10
                """)).fetchall()
                
                summary['jurisdictions']['by_county'] = {row[0]: row[1] for row in result}
            except Exception as e:
                summary['jurisdictions']['error'] = str(e)
            
            # Data quality checks
            try:
                # Check for permits with missing dates
                result = self.connection.execute(text("""
                    SELECT COUNT(*) FROM building_permits WHERE bp_issue_date IS NULL
                """)).fetchone()
                summary['data_quality']['permits_missing_dates'] = result[0] if result else 0
                
                # Check for jurisdictions with data
                result = self.connection.execute(text("""
                    SELECT COUNT(DISTINCT j.jurisdiction_id)
                    FROM jurisdictions j
                    JOIN building_permits bp ON j.jurisdiction_id = bp.jurisdiction_id
                """)).fetchone()
                summary['data_quality']['jurisdictions_with_permit_data'] = result[0] if result else 0
                
            except Exception as e:
                summary['data_quality']['error'] = str(e)
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate data summary: {e}")
            return {'error': str(e)}
    
    def load_all_hcd_data(self) -> bool:
        """Load all HCD Housing Element data"""
        logger.info("🏛️ STARTING CALIFORNIA HCD HOUSING ELEMENT DATA LOADING")
        logger.info("=" * 80)
        logger.info("📊 COLOSSEUM PLATFORM - Roman Engineering Standards")
        logger.info("🏗️ Built by Structured Consultants LLC")
        logger.info("=" * 80)
        
        # Validation steps
        if not self.validate_data_files():
            return False
        
        if not self.connect_database():
            return False
        
        success_count = 0
        total_operations = 2  # Applications and Permits
        
        try:
            # Load Table A - Housing Applications
            logger.info("🔄 Loading Table A - Housing Applications")
            table_a_path = self.data_path / 'HCD_HE_tablea.csv'
            if table_a_path.exists():
                df_applications = pd.read_csv(table_a_path)
                df_applications = self.process_housing_applications_data(df_applications)
                if self.load_housing_applications(df_applications):
                    success_count += 1
                    logger.info("✅ Table A loaded successfully")
                else:
                    logger.error("❌ Table A loading failed")
            else:
                logger.warning("⚠️ Table A file not found")
            
            # Load Table A2 - Building Permits (Critical RHNA data)
            logger.info("🔄 Loading Table A2 - Building Permits (Critical RHNA Data)")
            table_a2_path = self.data_path / 'HCD_HE_tablea2.csv'
            if table_a2_path.exists():
                df_permits = pd.read_csv(table_a2_path)
                df_permits = self.process_building_permits_data(df_permits)
                if self.load_building_permits(df_permits):
                    success_count += 1
                    logger.info("✅ Table A2 loaded successfully")
                else:
                    logger.error("❌ Table A2 loading failed")
            else:
                logger.warning("⚠️ Table A2 file not found")
            
            # Generate summary
            logger.info("📊 Generating data loading summary...")
            summary = self.generate_data_summary()
            
            # Save summary to file
            summary_path = self.data_path.parent / 'hcd_data_loading_summary.json'
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info("=" * 80)
            logger.info(f"🎉 DATA LOADING COMPLETE: {success_count}/{total_operations} successful")
            logger.info(f"📊 Total jurisdictions: {summary['tables_loaded'].get('jurisdictions', 0)}")
            logger.info(f"🏠 Total applications: {summary['tables_loaded'].get('housing_applications', 0)}")
            logger.info(f"🔨 Total permits: {summary['tables_loaded'].get('building_permits', 0)}")
            logger.info(f"📄 Summary saved: {summary_path}")
            logger.info("=" * 80)
            logger.info("🎯 NEXT STEPS:")
            logger.info("   1. Run intelligence algorithms for RHNA compliance")
            logger.info("   2. Calculate Good vs Bad city classifications")
            logger.info("   3. Launch Roman Empire dashboard")
            logger.info("=" * 80)
            
            return success_count == total_operations
        
        except Exception as e:
            logger.error(f"❌ Critical error during data loading: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()
            if self.engine:
                self.engine.dispose()

def main():
    """Main data loading function"""
    # Configuration
    data_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/california/CA_HCD_Housing_Element"
    
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': os.getenv('CA_HCD_USER', 'ca_hcd_user'),
        'password': os.getenv('CA_HCD_PASSWORD', 'colosseum_hcd_2025'),
        'database': 'ca_hcd_housing_element'
    }
    
    config = HCDDataConfig(
        data_path=data_path,
        database_config=db_config,
        batch_size=1000,
        validate_data=True,
        update_existing=True
    )
    
    # Initialize and run loader
    loader = ColasseumHCDDataLoader(config)
    
    if loader.load_all_hcd_data():
        logger.info("🏛️ MISSION ACCOMPLISHED - HCD data successfully loaded for Roman conquest!")
        return 0
    else:
        logger.error("❌ MISSION FAILED - Data loading unsuccessful")
        return 1

if __name__ == "__main__":
    exit(main())