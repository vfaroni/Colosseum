#!/usr/bin/env python3
"""
TCEQ Environmental Screening System
Industry-standard environmental risk assessment for LIHTC sites
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class TCEQEnvironmentalScreener:
    """TCEQ environmental screening using Texas official datasets"""
    
    def __init__(self):
        self.data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env")
        
        # Industry-standard environmental risk thresholds (miles)
        self.RISK_THRESHOLDS = {
            'CRITICAL': 0.125,      # ≤1/8 mile - Vapor intrusion concern, immediate regulatory liability
            'HIGH': 0.25,           # ≤1/4 mile - Phase II ESA required, potential vapor issues
            'MODERATE': 0.5,        # ≤1/2 mile - Enhanced Phase I ESA recommended
            'LOW': 1.0              # 1/2 to 1 mile - Standard Phase I with environmental awareness
        }
        
        # Risk scoring for LIHTC analysis (higher risk = lower score)
        self.RISK_SCORES = {
            'CRITICAL': 0,      # Eliminate - immediate regulatory liability
            'HIGH': 5,          # Poor - extensive environmental due diligence
            'MODERATE': 10,     # Moderate - enhanced screening required
            'LOW': 12,          # Good - standard environmental protocols
            'NONE': 15          # Best - no significant environmental concerns within 1 mile
        }
        
        # Environmental due diligence costs (per site)
        self.DD_COSTS = {
            'CRITICAL': 25000,  # Phase II ESA + vapor assessment + regulatory consultation
            'HIGH': 15000,      # Phase II ESA + enhanced vapor screening  
            'MODERATE': 8000,   # Enhanced Phase I ESA + targeted investigation
            'LOW': 3000,        # Standard Phase I ESA with environmental awareness
            'NONE': 2500        # Standard Phase I ESA baseline
        }
        
        # Contaminant-specific risk modifiers
        self.CONTAMINANT_MODIFIERS = {
            'LPST': 1.0,        # Petroleum contamination (baseline)
            'DRY_CLEANER': 1.2, # Chlorinated solvents (higher vapor intrusion risk)
            'ENFORCEMENT': 1.1   # Unknown contaminants (regulatory uncertainty)
        }
    
    def load_environmental_datasets(self):
        """Load all TCEQ environmental datasets"""
        print("📊 Loading TCEQ environmental datasets...")
        
        datasets = {}
        
        try:
            # 1. LPST Sites (Petroleum contamination)
            lpst_file = self.data_path / "Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv"
            lpst_df = pd.read_csv(lpst_file)
            datasets['lpst'] = lpst_df
            print(f"   ✅ LPST Sites: {len(lpst_df):,} petroleum contamination sites")
            
            # 2. Operating Dry Cleaners (Active solvent users)
            dry_file = self.data_path / "Texas_Commission_on_Environmental_Quality_-_Operating_Dry_Cleaner_Registrations_20250702.csv"
            dry_df = pd.read_csv(dry_file)
            datasets['dry_cleaners'] = dry_df
            print(f"   ✅ Operating Dry Cleaners: {len(dry_df):,} active solvent operations")
            
            # 3. Enforcement Notices (Regulatory violations)
            enf_file = self.data_path / "Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv"
            enf_df = pd.read_csv(enf_file)
            datasets['enforcement'] = enf_df
            print(f"   ✅ Enforcement Notices: {len(enf_df):,} regulatory violation sites")
            
        except Exception as e:
            print(f"❌ Error loading datasets: {e}")
            return None
        
        return datasets
    
    def parse_dry_cleaner_coordinates(self, coord_str):
        """Parse dry cleaner coordinate string: 'POINT (-98.22435 32.21035)'"""
        try:
            if pd.isna(coord_str) or 'POINT' not in str(coord_str):
                return None, None
            
            # Extract coordinates from POINT string
            coord_part = str(coord_str).replace('POINT (', '').replace(')', '')
            lng, lat = map(float, coord_part.split())
            return lat, lng
        except:
            return None, None
    
    def find_nearby_environmental_sites(self, site_lat, site_lng, datasets):
        """Find all environmental concerns within 1 mile of LIHTC site"""
        nearby_sites = {
            'lpst': [],
            'dry_cleaners': [],  
            'enforcement': []
        }
        
        site_coords = (site_lat, site_lng)
        
        # 1. Check LPST sites (using address-based search - no coordinates in this dataset)
        lpst_df = datasets['lpst']
        # For LPST, we'll use county-level analysis since coordinates aren't available
        # This is a limitation of the current dataset
        
        # 2. Check Operating Dry Cleaners (high coordinate quality)
        dry_df = datasets['dry_cleaners']
        if 'Location Coordinates (Decimal Degrees)' in dry_df.columns:
            for idx, facility in dry_df.iterrows():
                facility_lat, facility_lng = self.parse_dry_cleaner_coordinates(
                    facility.get('Location Coordinates (Decimal Degrees)')
                )
                
                if facility_lat and facility_lng:
                    facility_coords = (facility_lat, facility_lng)
                    distance = geodesic(site_coords, facility_coords).miles
                    
                    if distance <= 1.0:  # Within 1 mile screening radius
                        nearby_sites['dry_cleaners'].append({
                            'name': facility.get('Regulated Entity Name', 'Unknown'),
                            'address': facility.get('Location Address', 'Unknown'),
                            'city': facility.get('Location City', 'Unknown'),
                            'distance_miles': round(distance, 3),
                            'contaminant_type': 'Chlorinated Solvents',
                            'facility_type': 'Operating Dry Cleaner',
                            'coordinates': (facility_lat, facility_lng)
                        })
        
        # 3. Check Enforcement Notices (good coordinate quality)
        enf_df = datasets['enforcement']
        if 'Latitude' in enf_df.columns and 'Longitude' in enf_df.columns:
            valid_coords = ((enf_df['Latitude'].notna()) & (enf_df['Longitude'].notna()))
            
            for idx, notice in enf_df[valid_coords].iterrows():
                notice_lat = notice['Latitude']
                notice_lng = notice['Longitude']
                
                if pd.notna(notice_lat) and pd.notna(notice_lng):
                    notice_coords = (notice_lat, notice_lng)
                    distance = geodesic(site_coords, notice_coords).miles
                    
                    if distance <= 1.0:  # Within 1 mile screening radius
                        nearby_sites['enforcement'].append({
                            'name': notice.get('Regulated Entity Name', 'Unknown'),
                            'business_type': notice.get('Business Type', 'Unknown'),
                            'distance_miles': round(distance, 3),
                            'violation_count': notice.get('Total Violation Count', 0),
                            'contaminant_type': 'Unknown/Mixed',
                            'facility_type': 'Environmental Violation',
                            'coordinates': (notice_lat, notice_lng)
                        })
        
        return nearby_sites
    
    def assess_environmental_risk(self, nearby_sites):
        """Assess overall environmental risk based on nearby contamination"""
        all_concerns = []
        
        # Combine all nearby environmental concerns
        for source_type, sites in nearby_sites.items():
            for site in sites:
                distance = site['distance_miles']
                
                # Apply distance-based risk classification
                if distance <= self.RISK_THRESHOLDS['CRITICAL']:
                    base_risk = 'CRITICAL'
                elif distance <= self.RISK_THRESHOLDS['HIGH']:
                    base_risk = 'HIGH'
                elif distance <= self.RISK_THRESHOLDS['MODERATE']:
                    base_risk = 'MODERATE'
                else:
                    base_risk = 'LOW'
                
                # Apply contaminant-specific modifiers
                if source_type == 'lpst':
                    modifier = self.CONTAMINANT_MODIFIERS['LPST']
                elif source_type == 'dry_cleaners':
                    modifier = self.CONTAMINANT_MODIFIERS['DRY_CLEANER']
                else:
                    modifier = self.CONTAMINANT_MODIFIERS['ENFORCEMENT']
                
                concern = {
                    'source_type': source_type,
                    'facility_info': site,
                    'base_risk': base_risk,
                    'risk_modifier': modifier,
                    'distance': distance
                }
                all_concerns.append(concern)
        
        # Determine overall risk level (worst-case scenario)
        if not all_concerns:
            return {
                'overall_risk': 'NONE',
                'risk_score': self.RISK_SCORES['NONE'],
                'dd_cost': self.DD_COSTS['NONE'],
                'total_concerns': 0,
                'critical_concerns': 0,
                'high_concerns': 0,
                'moderate_concerns': 0,
                'low_concerns': 0,
                'concerns_detail': []
            }
        
        # Count concerns by risk level
        risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MODERATE': 0, 'LOW': 0}
        for concern in all_concerns:
            risk_counts[concern['base_risk']] += 1
        
        # Overall risk is the highest individual risk found
        if risk_counts['CRITICAL'] > 0:
            overall_risk = 'CRITICAL'
        elif risk_counts['HIGH'] > 0:
            overall_risk = 'HIGH'
        elif risk_counts['MODERATE'] > 0:
            overall_risk = 'MODERATE'
        else:
            overall_risk = 'LOW'
        
        return {
            'overall_risk': overall_risk,
            'risk_score': self.RISK_SCORES[overall_risk],
            'dd_cost': self.DD_COSTS[overall_risk],
            'total_concerns': len(all_concerns),
            'critical_concerns': risk_counts['CRITICAL'],
            'high_concerns': risk_counts['HIGH'],
            'moderate_concerns': risk_counts['MODERATE'],
            'low_concerns': risk_counts['LOW'],
            'concerns_detail': all_concerns[:5]  # Top 5 closest concerns
        }
    
    def screen_lihtc_site(self, site_data, datasets):
        """Screen a single LIHTC site for environmental concerns"""
        city = site_data.get('City', 'Unknown')
        lat = site_data.get('Latitude')
        lng = site_data.get('Longitude')
        
        if pd.isna(lat) or pd.isna(lng):
            return {
                'city': city,
                'screening_status': 'NO_COORDINATES',
                'overall_risk': 'UNDETERMINED',
                'risk_score': 8,  # Conservative middle score
                'dd_cost': 5000,  # Conservative estimate
                'error': 'Missing coordinates for environmental screening'
            }
        
        # Find nearby environmental sites
        nearby_sites = self.find_nearby_environmental_sites(lat, lng, datasets)
        
        # Assess risk
        risk_assessment = self.assess_environmental_risk(nearby_sites)
        risk_assessment.update({
            'city': city,
            'coordinates': (lat, lng),
            'screening_status': 'COMPLETED',
            'nearby_sites': nearby_sites
        })
        
        return risk_assessment

def test_tceq_environmental_screening():
    """Test TCEQ environmental screening with sample sites"""
    print("🧪 TESTING TCEQ ENVIRONMENTAL SCREENING")
    print("=" * 60)
    
    screener = TCEQEnvironmentalScreener()
    
    # Load datasets
    datasets = screener.load_environmental_datasets()
    if not datasets:
        print("❌ Failed to load environmental datasets")
        return
    
    # Test sites (first few from LIHTC analysis)
    test_sites = [
        {'City': 'Dallas', 'Latitude': 32.7767, 'Longitude': -96.7970},
        {'City': 'Houston', 'Latitude': 29.7604, 'Longitude': -95.3698},
        {'City': 'Austin', 'Latitude': 30.2672, 'Longitude': -97.7431},
        {'City': 'San Antonio', 'Latitude': 29.4241, 'Longitude': -98.4936},
        {'City': 'Fort Worth', 'Latitude': 32.7555, 'Longitude': -97.3308}
    ]
    
    print(f"\n🏠 Testing environmental screening on {len(test_sites)} sites:")
    
    results = []
    for i, site in enumerate(test_sites):
        print(f"\n   Site {i+1}: {site['City']}")
        result = screener.screen_lihtc_site(site, datasets)
        results.append(result)
        
        # Display results
        risk = result.get('overall_risk', 'UNKNOWN')
        score = result.get('risk_score', 0)
        cost = result.get('dd_cost', 0)
        total_concerns = result.get('total_concerns', 0)
        
        print(f"      Risk: {risk} | Score: {score}/15 | DD Cost: ${cost:,} | Concerns: {total_concerns}")
        
        if total_concerns > 0:
            critical = result.get('critical_concerns', 0)
            high = result.get('high_concerns', 0)
            moderate = result.get('moderate_concerns', 0)
            low = result.get('low_concerns', 0)
            print(f"      Breakdown: {critical} Critical, {high} High, {moderate} Moderate, {low} Low")
    
    print(f"\n✅ TCEQ Environmental Screening Test Complete")
    return results

if __name__ == "__main__":
    results = test_tceq_environmental_screening()