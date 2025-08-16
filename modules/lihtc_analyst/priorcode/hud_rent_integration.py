"""
HUD AMI Rent Data Integration
Loads HUD 2025 AMI rent data and matches to properties by county
"""

import pandas as pd
import numpy as np
from pathlib import Path

class HUDRentIntegrator:
    def __init__(self, hud_file_path: str = None):
        """Initialize with HUD AMI rent data file"""
        
        if hud_file_path is None:
            hud_file_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        self.hud_file_path = hud_file_path
        self.rent_data = None
        self.load_rent_data()
    
    def load_rent_data(self):
        """Load HUD AMI rent data"""
        try:
            if Path(self.hud_file_path).exists():
                # Try different sheet names
                sheet_names = ['Rent_Data', 'AMI_Rents', 'Sheet1', 0]
                
                for sheet in sheet_names:
                    try:
                        self.rent_data = pd.read_excel(self.hud_file_path, sheet_name=sheet)
                        print(f"✅ Loaded HUD rent data from sheet: {sheet}")
                        print(f"   Columns: {list(self.rent_data.columns)}")
                        print(f"   Rows: {len(self.rent_data)}")
                        break
                    except:
                        continue
                
                if self.rent_data is not None:
                    self.clean_rent_data()
                else:
                    print("❌ Could not load HUD rent data from any sheet")
            else:
                print(f"❌ HUD rent file not found: {self.hud_file_path}")
                self.create_sample_rent_data()
                
        except Exception as e:
            print(f"Error loading HUD rent data: {e}")
            self.create_sample_rent_data()
    
    def clean_rent_data(self):
        """Clean and standardize the rent data"""
        if self.rent_data is None:
            return
        
        # Handle the actual HUD file structure
        # Expected columns: 'stusps', 'County_Name', 'Studio 50%', '1BR 50%', etc.
        
        # Standardize column names
        column_mapping = {
            'County_Name': 'County',
            'county_name': 'County',
            'county': 'County',
            'County': 'County',
            'stusps': 'State',
            'state': 'State',
            'State': 'State'
        }
        
        # Rename columns if they exist
        for old_col, new_col in column_mapping.items():
            if old_col in self.rent_data.columns:
                self.rent_data = self.rent_data.rename(columns={old_col: new_col})
        
        # Standardize rent column names
        rent_mapping = {
            'Studio 50%': 'Studio_50AMI',
            '1BR 50%': 'BR1_50AMI',
            '2BR 50%': 'BR2_50AMI', 
            '3BR 50%': 'BR3_50AMI',
            '4BR 50%': 'BR4_50AMI',
            'Studio 60%': 'Studio_60AMI',
            '1BR 60%': 'BR1_60AMI',
            '2BR 60%': 'BR2_60AMI',
            '3BR 60%': 'BR3_60AMI',
            '4BR 60%': 'BR4_60AMI'
        }
        
        for old_col, new_col in rent_mapping.items():
            if old_col in self.rent_data.columns:
                self.rent_data = self.rent_data.rename(columns={old_col: new_col})
        
        # Ensure County column exists
        if 'County' not in self.rent_data.columns:
            # Try to identify county column
            county_candidates = [col for col in self.rent_data.columns if 'county' in col.lower()]
            if county_candidates:
                self.rent_data = self.rent_data.rename(columns={county_candidates[0]: 'County'})
        
        # Clean county names (remove "County" suffix if present)
        if 'County' in self.rent_data.columns:
            self.rent_data['County'] = self.rent_data['County'].astype(str)
            self.rent_data['County'] = self.rent_data['County'].str.replace(' County', '').str.strip()
        
        # Filter for Texas if State column exists
        if 'State' in self.rent_data.columns:
            self.rent_data = self.rent_data[self.rent_data['State'].isin(['TX', 'Texas', 'TEXAS'])]
        elif 'stusps' in self.rent_data.columns:
            self.rent_data = self.rent_data[self.rent_data['stusps'] == 'TX']
        
        print(f"✅ Cleaned rent data: {len(self.rent_data)} Texas counties")
        if len(self.rent_data) > 0:
            print(f"   Sample counties: {list(self.rent_data['County'].head())}")
            print(f"   Available rent columns: {[col for col in self.rent_data.columns if 'AMI' in col]}")
    
    def create_sample_rent_data(self):
        """Create sample rent data for major Texas counties if file not available"""
        print("📝 Creating sample HUD rent data for major Texas counties...")
        
        # Sample data for major Texas counties (2025 estimates)
        sample_data = {
            'County': [
                'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin', 'Denton',
                'Fort Bend', 'Hidalgo', 'Montgomery', 'Williamson', 'Brazoria',
                'Galveston', 'Cameron', 'Nueces', 'Bell', 'Guadalupe', 'Hays'
            ],
            'State': ['TX'] * 18,
            # 50% AMI Rents
            'Studio_50AMI': [920, 850, 830, 710, 980, 890, 850, 950, 580, 880, 920, 890, 820, 580, 720, 680, 750, 920],
            'BR1_50AMI': [985, 910, 890, 760, 1050, 950, 910, 1020, 620, 940, 985, 950, 880, 620, 770, 730, 800, 985],
            'BR2_50AMI': [1180, 1090, 1070, 910, 1260, 1140, 1090, 1220, 745, 1130, 1180, 1140, 1055, 745, 925, 875, 960, 1180],
            'BR3_50AMI': [1365, 1260, 1235, 1055, 1455, 1320, 1260, 1410, 860, 1305, 1365, 1320, 1220, 860, 1070, 1010, 1110, 1365],
            'BR4_50AMI': [1525, 1405, 1380, 1180, 1625, 1475, 1405, 1575, 960, 1455, 1525, 1475, 1360, 960, 1195, 1130, 1240, 1525],
            # 60% AMI Rents
            'Studio_60AMI': [1104, 1020, 996, 852, 1176, 1068, 1020, 1140, 696, 1056, 1104, 1068, 984, 696, 864, 816, 900, 1104],
            'BR1_60AMI': [1182, 1092, 1068, 912, 1260, 1140, 1092, 1224, 744, 1128, 1182, 1140, 1056, 744, 924, 876, 960, 1182],
            'BR2_60AMI': [1416, 1308, 1284, 1092, 1512, 1368, 1308, 1464, 894, 1356, 1416, 1368, 1266, 894, 1110, 1050, 1152, 1416],
            'BR3_60AMI': [1638, 1512, 1482, 1266, 1746, 1584, 1512, 1692, 1032, 1566, 1638, 1584, 1464, 1032, 1284, 1212, 1332, 1638],
            'BR4_60AMI': [1830, 1686, 1656, 1416, 1950, 1770, 1686, 1890, 1152, 1746, 1830, 1770, 1632, 1152, 1434, 1356, 1488, 1830]
        }
        
        self.rent_data = pd.DataFrame(sample_data)
        print(f"✅ Created sample rent data for {len(self.rent_data)} counties")
    
    def get_rent_for_county(self, county: str) -> dict:
        """Get rent data for a specific county"""
        if self.rent_data is None:
            return {}
        
        # Clean county name
        county_clean = str(county).replace(' County', '').strip()
        
        # Find matching county
        county_match = self.rent_data[self.rent_data['County'].str.lower() == county_clean.lower()]
        
        if len(county_match) == 0:
            return {}
        
        county_data = county_match.iloc[0]
        
        rent_info = {}
        
        # Extract 50% AMI rents
        for unit_type in ['Studio', 'BR1', 'BR2', 'BR3', 'BR4']:
            col_50 = f'{unit_type}_50AMI'
            col_60 = f'{unit_type}_60AMI'
            
            if col_50 in county_data:
                rent_info[f'{unit_type}_50AMI_rent'] = county_data[col_50]
            if col_60 in county_data:
                rent_info[f'{unit_type}_60AMI_rent'] = county_data[col_60]
        
        return rent_info
    
    def add_rents_to_dataframe(self, df: pd.DataFrame, county_column: str = 'County') -> pd.DataFrame:
        """Add rent columns to property dataframe"""
        if self.rent_data is None:
            print("❌ No rent data available")
            return df
        
        print(f"📊 Adding HUD rent data to {len(df)} properties...")
        
        # Initialize rent columns
        rent_columns = []
        for ami_level in ['50AMI', '60AMI']:
            for unit_type in ['Studio', 'BR1', 'BR2', 'BR3', 'BR4']:
                col_name = f'{unit_type}_{ami_level}_rent'
                df[col_name] = np.nan
                rent_columns.append(col_name)
        
        # Add rent data for each property
        for idx, row in df.iterrows():
            county = row.get(county_column, '')
            if county:
                rent_info = self.get_rent_for_county(county)
                for rent_col, rent_value in rent_info.items():
                    if rent_col in df.columns:
                        df.loc[idx, rent_col] = rent_value
        
        # Calculate additional metrics
        df = self.calculate_rent_metrics(df)
        
        filled_count = df[rent_columns[0]].notna().sum()
        print(f"✅ Added rent data for {filled_count} properties")
        
        return df
    
    def calculate_rent_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate rent-based financial metrics"""
        
        # Calculate average rent per unit type
        for ami_level in ['50AMI', '60AMI']:
            rent_cols = [f'{unit}_50AMI_rent' if ami_level == '50AMI' else f'{unit}_60AMI_rent' 
                        for unit in ['Studio', 'BR1', 'BR2', 'BR3', 'BR4']]
            
            # Average rent across all unit types
            valid_cols = [col for col in rent_cols if col in df.columns]
            if valid_cols:
                df[f'avg_rent_{ami_level}'] = df[valid_cols].mean(axis=1)
        
        # Calculate potential monthly and annual income
        # Assume typical unit mix: 20% Studio, 30% 1BR, 35% 2BR, 15% 3BR
        if all(col in df.columns for col in ['Studio_50AMI_rent', 'BR1_50AMI_rent', 'BR2_50AMI_rent', 'BR3_50AMI_rent']):
            df['weighted_avg_rent_50AMI'] = (
                df['Studio_50AMI_rent'] * 0.20 +
                df['BR1_50AMI_rent'] * 0.30 +
                df['BR2_50AMI_rent'] * 0.35 +
                df['BR3_50AMI_rent'] * 0.15
            )
            
            df['weighted_avg_rent_60AMI'] = (
                df['Studio_60AMI_rent'] * 0.20 +
                df['BR1_60AMI_rent'] * 0.30 +
                df['BR2_60AMI_rent'] * 0.35 +
                df['BR3_60AMI_rent'] * 0.15
            )
            
            # Calculate annual income per unit
            df['annual_income_per_unit_50AMI'] = df['weighted_avg_rent_50AMI'] * 12
            df['annual_income_per_unit_60AMI'] = df['weighted_avg_rent_60AMI'] * 12
        
        return df
    
    def get_rent_summary(self, county: str) -> pd.DataFrame:
        """Get formatted rent summary for a county"""
        rent_data = self.get_rent_for_county(county)
        
        if not rent_data:
            return pd.DataFrame()
        
        # Format rent data into table
        summary_data = []
        
        unit_types = {
            'Studio': 'Studio',
            'BR1': '1 Bedroom', 
            'BR2': '2 Bedroom',
            'BR3': '3 Bedroom',
            'BR4': '4 Bedroom'
        }
        
        for unit_code, unit_name in unit_types.items():
            rent_50 = rent_data.get(f'{unit_code}_50AMI_rent', 'N/A')
            rent_60 = rent_data.get(f'{unit_code}_60AMI_rent', 'N/A')
            
            summary_data.append({
                'Unit Type': unit_name,
                '50% AMI Rent': f"${rent_50:,.0f}" if rent_50 != 'N/A' else 'N/A',
                '60% AMI Rent': f"${rent_60:,.0f}" if rent_60 != 'N/A' else 'N/A',
                'Monthly Diff': f"${rent_60 - rent_50:,.0f}" if rent_50 != 'N/A' and rent_60 != 'N/A' else 'N/A'
            })
        
        return pd.DataFrame(summary_data)


def test_rent_integration():
    """Test the rent integration with sample data"""
    
    # Create sample property data
    sample_properties = pd.DataFrame({
        'Address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'City': ['Houston', 'Dallas', 'Austin'],
        'County': ['Harris', 'Dallas', 'Travis']
    })
    
    # Initialize rent integrator
    rent_integrator = HUDRentIntegrator()
    
    # Add rent data
    enhanced_properties = rent_integrator.add_rents_to_dataframe(sample_properties)
    
    print("\nSample enhanced property data:")
    print(enhanced_properties.head())
    
    # Test county rent summary
    print("\nHarris County Rent Summary:")
    harris_summary = rent_integrator.get_rent_summary('Harris')
    print(harris_summary)


if __name__ == "__main__":
    test_rent_integration()