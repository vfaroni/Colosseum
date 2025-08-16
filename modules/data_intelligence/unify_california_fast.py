#!/usr/bin/env python3
"""
California Environmental Database Unification - FAST VERSION
Optimized for speed: aggregates compliance data first, then joins
WINGMAN Execution - Mission CA-ENV-UNIFIED-2025-003
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import sqlite3
import logging
import gc

class FastCaliforniaUnifier:
    """Fast unification using aggregation-first approach"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "california" / "CA_Environmental_Data" / "CalEPA_Compliance"
        self.output_path = self.base_path / "data_sets" / "california" / "CA_Environmental_Unified"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        
    def run_fast(self):
        """Fast execution with aggregation first"""
        
        self.logger.info("="*80)
        self.logger.info("FAST CALIFORNIA ENVIRONMENTAL DATABASE UNIFICATION")
        self.logger.info("="*80)
        
        # 1. Load master sites
        self.logger.info("\n1. Loading master sites...")
        df_sites = pd.read_csv(self.data_path / "Site.csv", dtype=str)
        df_sites['SiteID'] = df_sites['SiteID'].astype(str)
        self.logger.info(f"   Loaded {len(df_sites):,} sites")
        
        # 2. Load and merge coordinates
        self.logger.info("\n2. Adding coordinates...")
        
        # Check if Latitude column already exists in sites
        if 'Latitude' in df_sites.columns:
            # Rename existing columns to avoid conflict
            df_sites.rename(columns={'Latitude': 'Site_Lat', 'Longitude': 'Site_Lng'}, inplace=True)
        
        df_coords = pd.read_csv(self.data_path / "Coordinates.csv", dtype=str)
        df_coords['SiteID'] = df_coords['SiteID'].astype(str)
        df_coords['LATITUDE'] = pd.to_numeric(df_coords['LATITUDE'], errors='coerce')
        df_coords['LONGITUDE'] = pd.to_numeric(df_coords['LONGITUDE'], errors='coerce')
        
        # Keep first valid coordinate per site
        coords_dedup = df_coords.groupby('SiteID').first().reset_index()
        df_sites = df_sites.merge(coords_dedup[['SiteID', 'LATITUDE', 'LONGITUDE']], 
                                  on='SiteID', how='left', suffixes=('', '_coord'))
        
        df_sites['HasCoordinates'] = df_sites['LATITUDE'].notna()
        self.logger.info(f"   Added coordinates to {df_sites['HasCoordinates'].sum():,} sites")
        
        # 3. Aggregate violations (don't store details, just counts)
        self.logger.info("\n3. Aggregating violations...")
        viol_counts = pd.read_csv(
            self.data_path / "Violations.csv",
            usecols=['SiteID'],
            dtype=str
        )['SiteID'].value_counts().to_dict()
        
        df_sites['ViolationCount'] = df_sites['SiteID'].map(viol_counts).fillna(0).astype(int)
        self.logger.info(f"   Found violations for {(df_sites['ViolationCount'] > 0).sum():,} sites")
        
        # 4. Aggregate evaluations
        self.logger.info("\n4. Aggregating evaluations...")
        eval_data = pd.read_csv(
            self.data_path / "Evaluations.csv",
            usecols=['SiteID', 'ViolationsFound'],
            dtype=str
        )
        
        eval_counts = eval_data.groupby('SiteID').agg({
            'ViolationsFound': [
                'count',
                lambda x: (x == 'Yes').sum()
            ]
        }).reset_index()
        
        eval_counts.columns = ['SiteID', 'EvaluationCount', 'EvaluationsWithViolations']
        eval_counts['SiteID'] = eval_counts['SiteID'].astype(str)
        
        df_sites = df_sites.merge(eval_counts, on='SiteID', how='left')
        df_sites['EvaluationCount'] = df_sites['EvaluationCount'].fillna(0).astype(int)
        df_sites['EvaluationsWithViolations'] = df_sites['EvaluationsWithViolations'].fillna(0).astype(int)
        
        self.logger.info(f"   Found evaluations for {(df_sites['EvaluationCount'] > 0).sum():,} sites")
        
        # 5. Aggregate enforcements
        self.logger.info("\n5. Aggregating enforcements...")
        enf_counts = pd.read_csv(
            self.data_path / "EA.csv",
            usecols=['SiteID'],
            dtype=str
        )['SiteID'].value_counts().to_dict()
        
        df_sites['EnforcementCount'] = df_sites['SiteID'].map(enf_counts).fillna(0).astype(int)
        self.logger.info(f"   Found enforcements for {(df_sites['EnforcementCount'] > 0).sum():,} sites")
        
        # 6. Check for chemicals
        self.logger.info("\n6. Checking chemical data...")
        chem_sites = pd.read_csv(
            self.data_path / "Chems.csv",
            usecols=['SiteID'],
            dtype=str
        )['SiteID'].unique()
        
        df_sites['HasChemicals'] = df_sites['SiteID'].isin(chem_sites)
        self.logger.info(f"   Found chemicals at {df_sites['HasChemicals'].sum():,} sites")
        
        # 7. Count regulated programs
        self.logger.info("\n7. Counting regulated programs...")
        prog_counts = pd.read_csv(
            self.data_path / "SiteEI.csv",
            usecols=['SiteID'],
            dtype=str
        )['SiteID'].value_counts().to_dict()
        
        df_sites['RegulatedProgramCount'] = df_sites['SiteID'].map(prog_counts).fillna(0).astype(int)
        self.logger.info(f"   Found programs for {(df_sites['RegulatedProgramCount'] > 0).sum():,} sites")
        
        # 8. Clean up data types
        df_sites['City'] = df_sites.get('City', '')
        df_sites['County'] = df_sites.get('County', '')
        
        # Add County from City if missing (basic mapping for major cities)
        city_to_county = {
            'LOS ANGELES': 'LOS ANGELES',
            'SAN DIEGO': 'SAN DIEGO',
            'SAN JOSE': 'SANTA CLARA',
            'SAN FRANCISCO': 'SAN FRANCISCO',
            'SACRAMENTO': 'SACRAMENTO',
            'OAKLAND': 'ALAMEDA',
            'FRESNO': 'FRESNO',
            'LONG BEACH': 'LOS ANGELES',
            'ANAHEIM': 'ORANGE',
            'SANTA ANA': 'ORANGE'
        }
        
        if 'County' not in df_sites.columns or df_sites['County'].isna().all():
            df_sites['County'] = df_sites['City'].str.upper().map(city_to_county)
        
        # 9. Save outputs
        self.logger.info("\n" + "="*80)
        self.logger.info("CREATING OUTPUTS")
        self.logger.info("="*80)
        
        # Parquet (S3 optimized)
        self.logger.info("\nSaving Parquet file...")
        parquet_file = self.output_path / "california_environmental_unified.parquet"
        df_sites.to_parquet(parquet_file, engine='pyarrow', compression='snappy', index=False)
        self.logger.info(f"   ✓ Saved {len(df_sites):,} sites to Parquet")
        
        # CSV for compatibility
        self.logger.info("\nSaving CSV file...")
        csv_file = self.output_path / "california_environmental_unified.csv"
        df_sites.to_csv(csv_file, index=False)
        self.logger.info(f"   ✓ Saved to CSV")
        
        # SQLite database
        self.logger.info("\nCreating SQLite database...")
        db_file = self.output_path / "california_environmental.db"
        conn = sqlite3.connect(db_file)
        df_sites.to_sql('sites', conn, if_exists='replace', index=False)
        
        # Create indexes
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_siteid ON sites(SiteID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON sites(City)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations ON sites(ViolationCount)")
        conn.commit()
        conn.close()
        self.logger.info(f"   ✓ Created SQLite database with indexes")
        
        # Summary statistics
        summary = {
            'processing_date': datetime.now().isoformat(),
            'processing_time_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'total_sites': len(df_sites),
            'sites_with_coordinates': int(df_sites['HasCoordinates'].sum()),
            'sites_with_violations': int((df_sites['ViolationCount'] > 0).sum()),
            'sites_with_evaluations': int((df_sites['EvaluationCount'] > 0).sum()),
            'sites_with_enforcements': int((df_sites['EnforcementCount'] > 0).sum()),
            'sites_with_chemicals': int(df_sites['HasChemicals'].sum()),
            'total_violations': int(df_sites['ViolationCount'].sum()),
            'total_evaluations': int(df_sites['EvaluationCount'].sum()),
            'total_enforcements': int(df_sites['EnforcementCount'].sum())
        }
        
        with open(self.output_path / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create README
        self.create_readme(summary)
        
        # Final report
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        self.logger.info("\n" + "="*80)
        self.logger.info("UNIFICATION COMPLETE")
        self.logger.info("="*80)
        self.logger.info(f"Processing Time: {duration:.1f} minutes")
        self.logger.info(f"Total Sites: {len(df_sites):,}")
        self.logger.info(f"Sites with Violations: {summary['sites_with_violations']:,}")
        self.logger.info(f"Sites with Coordinates: {summary['sites_with_coordinates']:,}")
        self.logger.info("="*80)
        
        return df_sites
    
    def create_readme(self, summary):
        """Create README documentation"""
        readme = f"""CALIFORNIA UNIFIED ENVIRONMENTAL DATABASE
==========================================
Source: CalEPA Site Portal
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Processing Time: {summary['processing_time_minutes']:.1f} minutes

STATISTICS:
- Total Sites: {summary['total_sites']:,}
- Sites with Coordinates: {summary['sites_with_coordinates']:,}
- Sites with Violations: {summary['sites_with_violations']:,}
- Sites with Evaluations: {summary['sites_with_evaluations']:,}
- Sites with Enforcements: {summary['sites_with_enforcements']:,}
- Sites with Chemicals: {summary['sites_with_chemicals']:,}

AGGREGATE COUNTS:
- Total Violations: {summary['total_violations']:,}
- Total Evaluations: {summary['total_evaluations']:,}
- Total Enforcements: {summary['total_enforcements']:,}

FILES CREATED:
1. california_environmental_unified.parquet - S3 optimized format
2. california_environmental_unified.csv - Excel compatible
3. california_environmental.db - SQLite database with indexes
4. summary.json - Processing statistics

FIELDS:
- SiteID: Unique identifier
- SiteName, Address, City, ZIP: Location info
- LATITUDE, LONGITUDE: Coordinates (where available)
- HasCoordinates: Boolean flag
- ViolationCount: Number of violations
- EvaluationCount: Number of evaluations
- EvaluationsWithViolations: Evaluations that found violations
- EnforcementCount: Number of enforcement actions
- HasChemicals: Boolean flag for chemical presence
- RegulatedProgramCount: Number of regulatory programs

NOTE: This contains aggregated counts only. For detailed violation
descriptions, refer to original source files.

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
"""
        
        with open(self.output_path / "README.txt", 'w') as f:
            f.write(readme)

def main():
    print("\nFAST CALIFORNIA ENVIRONMENTAL UNIFICATION")
    print("="*60)
    
    unifier = FastCaliforniaUnifier()
    df = unifier.run_fast()
    
    print(f"\n✅ SUCCESS!")
    print(f"📁 Output: data_sets/california/CA_Environmental_Unified/")
    print(f"🚀 Ready for S3 deployment")

if __name__ == "__main__":
    main()