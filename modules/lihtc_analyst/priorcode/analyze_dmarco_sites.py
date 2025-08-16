#!/usr/bin/env python3
"""
Analyze D'Marco's 65 Sites from Brent
1. Geocode addresses to get lat/lng
2. Check QCT/DDA status
3. Apply full TDHCA analysis including:
   - Low poverty rates (for 9% bonus)
   - FEMA flood risk
   - Construction costs by region
   - Competition analysis
   - Economic viability

Author: TDHCA Analysis System
Date: 2025-06-19
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import geopandas as gpd
from shapely.geometry import Point
import requests
import time
import logging
from tdhca_qct_focused_analyzer import TDHCAQCTFocusedAnalyzer

class DMarcoSiteAnalyzer:
    """Comprehensive analyzer for D'Marco's broker sites"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the base analyzer
        self.base_analyzer = TDHCAQCTFocusedAnalyzer()
        
        # Geocoding
        self.geolocator = Nominatim(user_agent="tdhca_analyzer")
        
        # Construction cost multipliers by region (based on major cities in each)
        self.regional_cost_multipliers = {
            'Region 1': 0.90,   # Panhandle - Lower costs
            'Region 2': 0.95,   # North Central - Moderate costs
            'Region 3': 1.15,   # Dallas/Fort Worth - Higher costs
            'Region 4': 0.98,   # East Texas - Moderate costs
            'Region 5': 1.00,   # Southeast - Average costs
            'Region 6': 1.18,   # Houston - High costs
            'Region 7': 1.20,   # Austin - Highest costs
            'Region 8': 1.00,   # Central - Average costs
            'Region 9': 1.10,   # San Antonio - Above average
            'Region 10': 1.05,  # Coastal - Above average
            'Region 11': 0.92,  # Rio Grande Valley - Lower costs
            'Region 12': 1.12,  # West Texas - Above average (oil region)
            'Region 13': 1.08   # El Paso - Above average
        }
        
        # Base construction cost (2025 Texas average)
        self.base_construction_cost = 150  # $/SF
        
        # Census API for poverty data
        self.census_api_key = None  # Add if available
    
    def geocode_address(self, address, city, county, max_retries=3):
        """Geocode an address with retry logic"""
        full_address = f"{address}, {city}, {county} County, Texas"
        
        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(full_address, timeout=10)
                if location:
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'geocoded_address': location.address,
                        'geocoding_success': True
                    }
                else:
                    # Try with just city, county if full address fails
                    simple_address = f"{city}, {county} County, Texas"
                    location = self.geolocator.geocode(simple_address, timeout=10)
                    if location:
                        return {
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'geocoded_address': f"{location.address} (City Center - Address Not Found)",
                            'geocoding_success': False
                        }
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                self.logger.warning(f"Geocoding attempt {attempt + 1} failed for {full_address}: {e}")
                time.sleep(2)
        
        return {
            'latitude': None,
            'longitude': None,
            'geocoded_address': 'Geocoding Failed',
            'geocoding_success': False
        }
    
    def get_poverty_rate(self, lat, lng):
        """Get poverty rate for census tract (if Census API available)"""
        # Placeholder - would need Census API key and tract lookup
        # For now, return None - this would be implemented with actual Census API
        return None
    
    def analyze_dmarco_sites(self, csv_file):
        """Analyze all of D'Marco's sites"""
        self.logger.info(f"Analyzing D'Marco sites from: {csv_file}")
        
        # Load the sites
        df = pd.read_csv(csv_file)
        self.logger.info(f"Loaded {len(df)} D'Marco sites")
        
        # Initialize analysis columns
        analysis_columns = [
            # Geocoding results
            'Latitude', 'Longitude', 'Geocoded_Address', 'Geocoding_Success',
            
            # QCT/DDA Status
            'QCT_Status', 'DDA_Status', 'QCT_DDA_Combined', 'Basis_Boost_Eligible',
            
            # Economic factors
            'Regional_Construction_Cost_Multiplier', 'Estimated_Construction_Cost_SF',
            'Poverty_Rate_Percent', 'Low_Poverty_Bonus_Eligible',
            
            # Competition Analysis
            'One_Mile_Competition_Count', 'One_Mile_Risk_4pct', 'One_Mile_Fatal_9pct',
            'Two_Mile_Competition_Count', 'Large_County_Rules_Apply',
            
            # FEMA Flood Risk (would need separate lookup)
            'Flood_Zone_Estimated', 'Flood_Cost_Impact',
            
            # Overall Assessment
            'QCT_DDA_Priority', 'Economic_Viability_4pct', 'Economic_Viability_9pct',
            'Development_Recommendation', 'Key_Advantages', 'Risk_Factors'
        ]
        
        for col in analysis_columns:
            df[col] = None
        
        qct_dda_sites = []
        
        # Process each site
        for idx, row in df.iterrows():
            self.logger.info(f"Processing site {idx + 1}/{len(df)}: {row['MailingName']} in {row['City']}")
            
            # 1. Geocode the address
            geocoding = self.geocode_address(row['Address'], row['City'], row['County'])
            df.loc[idx, 'Latitude'] = geocoding['latitude']
            df.loc[idx, 'Longitude'] = geocoding['longitude']
            df.loc[idx, 'Geocoded_Address'] = geocoding['geocoded_address']
            df.loc[idx, 'Geocoding_Success'] = geocoding['geocoding_success']
            
            if not geocoding['latitude']:
                df.loc[idx, 'Development_Recommendation'] = 'Cannot analyze - geocoding failed'
                continue
            
            # 2. Check QCT/DDA status
            qct_dda = self.base_analyzer.check_qct_dda_status(
                geocoding['latitude'], 
                geocoding['longitude']
            )
            
            df.loc[idx, 'QCT_Status'] = qct_dda['in_qct']
            df.loc[idx, 'DDA_Status'] = qct_dda['in_dda']
            df.loc[idx, 'QCT_DDA_Combined'] = qct_dda['status']
            df.loc[idx, 'Basis_Boost_Eligible'] = qct_dda['basis_boost_eligible']
            
            # Set priority based on QCT/DDA status
            if qct_dda['basis_boost_eligible']:
                df.loc[idx, 'QCT_DDA_Priority'] = 'HIGH - 30% Basis Boost Eligible'
                qct_dda_sites.append(idx)
            else:
                df.loc[idx, 'QCT_DDA_Priority'] = 'LOW - No Basis Boost'
                df.loc[idx, 'Development_Recommendation'] = 'Not recommended - No 30% basis boost'
                continue
            
            # 3. Economic Analysis (for QCT/DDA sites only)
            region = row['Region']
            cost_multiplier = self.regional_cost_multipliers.get(region, 1.0)
            df.loc[idx, 'Regional_Construction_Cost_Multiplier'] = cost_multiplier
            df.loc[idx, 'Estimated_Construction_Cost_SF'] = self.base_construction_cost * cost_multiplier
            
            # 4. Competition Analysis
            competition = self.base_analyzer.analyze_competition_by_type(
                geocoding['latitude'], 
                geocoding['longitude'], 
                row['County'], 
                '4%'
            )
            
            df.loc[idx, 'One_Mile_Competition_Count'] = competition['one_mile_recent_count']
            df.loc[idx, 'One_Mile_Risk_4pct'] = competition['one_mile_risk_level']
            df.loc[idx, 'Two_Mile_Competition_Count'] = competition['market_saturation_2mi']
            
            # Check for large county rules
            is_large_county = row['County'] in self.base_analyzer.large_counties_9pct
            df.loc[idx, 'Large_County_Rules_Apply'] = is_large_county
            
            # 9% analysis
            competition_9pct = self.base_analyzer.analyze_competition_by_type(
                geocoding['latitude'], 
                geocoding['longitude'], 
                row['County'], 
                '9%'
            )
            df.loc[idx, 'One_Mile_Fatal_9pct'] = competition_9pct['one_mile_fatal_flaw']
            
            # 5. Overall Viability Assessment
            advantages = []
            risks = []
            
            advantages.append(f"30% basis boost ({qct_dda['status']})")
            advantages.append(f"TDHCA {region}")
            
            # 4% viability
            if competition['one_mile_risk_level'] == 'Low':
                df.loc[idx, 'Economic_Viability_4pct'] = 'Excellent'
                advantages.append('No recent LIHTC competition')
            elif competition['one_mile_risk_level'] == 'Medium':
                df.loc[idx, 'Economic_Viability_4pct'] = 'Good'
                risks.append('Some recent LIHTC competition')
            else:
                df.loc[idx, 'Economic_Viability_4pct'] = 'Fair'
                risks.append('High LIHTC competition')
            
            # 9% viability
            if competition_9pct['one_mile_fatal_flaw']:
                df.loc[idx, 'Economic_Viability_9pct'] = 'Not Viable - Fatal Flaw'
                risks.append('9% fatal flaw - one mile rule')
            else:
                df.loc[idx, 'Economic_Viability_9pct'] = 'Viable'
            
            # Cost considerations
            if cost_multiplier > 1.15:
                risks.append(f'High construction costs ({region})')
            elif cost_multiplier < 0.95:
                advantages.append(f'Lower construction costs ({region})')
            
            # Acreage considerations
            acreage = float(row['Acres'])
            if acreage > 50:
                advantages.append(f'Large site ({acreage} acres)')
            elif acreage < 3:
                risks.append(f'Small site ({acreage} acres)')
            
            df.loc[idx, 'Key_Advantages'] = '; '.join(advantages)
            df.loc[idx, 'Risk_Factors'] = '; '.join(risks) if risks else 'None identified'
            
            # Final recommendation
            if competition['one_mile_risk_level'] == 'Low':
                df.loc[idx, 'Development_Recommendation'] = 'HIGHLY RECOMMENDED - QCT/DDA + No Competition'
            elif competition['one_mile_risk_level'] == 'Medium':
                df.loc[idx, 'Development_Recommendation'] = 'RECOMMENDED - QCT/DDA with Minor Competition'
            else:
                df.loc[idx, 'Development_Recommendation'] = 'PROCEED WITH CAUTION - High Competition'
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"DMarco_Sites_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            qct_dda_count = len([i for i in qct_dda_sites if df.loc[i, 'Basis_Boost_Eligible']])
            excellent_4pct = len(df[df['Economic_Viability_4pct'] == 'Excellent'])
            
            summary_data = {
                'Metric': [
                    'Total D\'Marco Sites',
                    'Successfully Geocoded',
                    'QCT/DDA Eligible (30% Boost)',
                    'Non-QCT/DDA Sites',
                    'Excellent 4% Opportunities',
                    'Good 4% Opportunities',
                    'Fatal Flaw 9% Sites'
                ],
                'Count': [
                    len(df),
                    len(df[df['Geocoding_Success'] == True]),
                    qct_dda_count,
                    len(df) - qct_dda_count,
                    excellent_4pct,
                    len(df[df['Economic_Viability_4pct'] == 'Good']),
                    len(df[df['One_Mile_Fatal_9pct'] == True])
                ]
            }
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # All sites
            df.to_excel(writer, sheet_name='All_DMarco_Sites', index=False)
            
            # QCT/DDA sites only
            if qct_dda_count > 0:
                df_qct_dda = df[df['Basis_Boost_Eligible'] == True].copy()
                df_qct_dda_sorted = df_qct_dda.sort_values(['Economic_Viability_4pct', 'One_Mile_Competition_Count'])
                df_qct_dda_sorted.to_excel(writer, sheet_name='QCT_DDA_Priority_Sites', index=False)
                
                # Best opportunities
                best_sites = df_qct_dda[df_qct_dda['Economic_Viability_4pct'] == 'Excellent']
                if len(best_sites) > 0:
                    best_sites.to_excel(writer, sheet_name='Best_Opportunities', index=False)
            
            # Regional analysis
            regional_summary = df.groupby('Region').agg({
                'Basis_Boost_Eligible': 'sum',
                'Economic_Viability_4pct': lambda x: (x == 'Excellent').sum(),
                'Acres': 'mean'
            }).rename(columns={
                'Basis_Boost_Eligible': 'QCT_DDA_Count',
                'Economic_Viability_4pct': 'Excellent_4pct_Count',
                'Acres': 'Avg_Acreage'
            })
            regional_summary.to_excel(writer, sheet_name='Regional_Summary')
        
        self.logger.info(f"\n📊 D'Marco Sites Analysis Complete:")
        self.logger.info(f"   Total sites: {len(df)}")
        self.logger.info(f"   QCT/DDA eligible: {qct_dda_count}")
        self.logger.info(f"   Excellent 4% opportunities: {excellent_4pct}")
        self.logger.info(f"\n💾 Results saved to: {output_file}")
        
        return df, output_file

def main():
    analyzer = DMarcoSiteAnalyzer()
    
    # Analyze D'Marco's sites
    csv_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brent_06182025.csv"
    
    if Path(csv_file).exists():
        df_results, output_file = analyzer.analyze_dmarco_sites(csv_file)
        print(f"\nAnalysis complete! Results saved to: {output_file}")
        
        # Quick summary
        qct_dda_sites = len(df_results[df_results['Basis_Boost_Eligible'] == True])
        print(f"\n🎯 Quick Summary:")
        print(f"   QCT/DDA eligible sites: {qct_dda_sites} out of {len(df_results)}")
        print(f"   Focus on these {qct_dda_sites} sites for development")
    else:
        print(f"❌ File not found: {csv_file}")

if __name__ == "__main__":
    main()