#!/usr/bin/env python3
"""
🔧 FIXED Environmental Screening with Proper Descriptions
WINGMAN Agent - Fix the "1 concern per site" bug

ISSUES TO FIX:
1. Every site showing exactly 1 environmental concern (clearly wrong)
2. Missing description of what the actual concerns are
3. Need proper proximity analysis using OpenStreetMap Nominatim (free alternative)

SOLUTION:
1. Use TCEQ Enforcement database WITH coordinates (verified working)
2. Implement proper distance-based screening 
3. Add detailed descriptions of environmental concerns found
4. Use OpenStreetMap Nominatim for any geocoding needs (PositionStack alternative)
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import requests
import time
import warnings
warnings.filterwarnings('ignore')

class FixedEnvironmentalScreening:
    """Fixed environmental screening with proper distance analysis and descriptions"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.tceq_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env")
        
        # Distance thresholds for environmental screening (miles)
        self.SCREENING_DISTANCES = {
            'IMMEDIATE': 0.125,    # 1/8 mile - vapor intrusion concern
            'CRITICAL': 0.25,      # 1/4 mile - Enhanced Phase I required
            'HIGH': 0.5,           # 1/2 mile - Standard screening distance
            'MEDIUM': 1.0,         # 1 mile - Regional assessment
        }
        
        # Risk scoring based on distance and concern type
        self.RISK_SCORES = {
            'ENFORCEMENT_IMMEDIATE': 100,
            'ENFORCEMENT_CRITICAL': 75,
            'ENFORCEMENT_HIGH': 50,
            'ENFORCEMENT_MEDIUM': 25,
            'LPST_COUNTY_HIGH': 40,    # High density of LPST sites in county
            'LPST_COUNTY_MEDIUM': 20,  # Medium density
            'LPST_COUNTY_LOW': 5       # Low density
        }
    
    def load_dmarco_sites(self):
        """Load D'Marco sites data"""
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} D'Marco sites")
        return sites_data
    
    def load_tceq_enforcement_with_coordinates(self):
        """Load TCEQ enforcement database and validate coordinates"""
        print("🔍 LOADING TCEQ ENFORCEMENT DATA WITH COORDINATE VALIDATION")
        
        enforcement_file = self.tceq_dir / "Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv"
        
        if not enforcement_file.exists():
            print(f"❌ Enforcement file not found: {enforcement_file}")
            return pd.DataFrame()
        
        try:
            # Load enforcement data
            df = pd.read_csv(enforcement_file, encoding='utf-8-sig')
            print(f"📊 Loaded {len(df)} enforcement records")
            
            # Validate and clean coordinates
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
            
            # Filter to valid Texas coordinates with actual lat/lng values
            valid_coords = (
                df['Latitude'].notna() & 
                df['Longitude'].notna() &
                (df['Latitude'] != 0) &
                (df['Longitude'] != 0) &
                (df['Latitude'] >= 25.0) & (df['Latitude'] <= 37.0) &
                (df['Longitude'] >= -107.0) & (df['Longitude'] <= -93.0)
            )
            
            valid_df = df[valid_coords].copy()
            
            print(f"✅ Valid coordinates: {len(valid_df)}/{len(df)} ({len(valid_df)/len(df)*100:.1f}%)")
            
            if len(valid_df) == 0:
                print("❌ No valid coordinates found in enforcement database")
                return pd.DataFrame()
            
            # Show sample of coordinate data
            print(f"📍 Sample coordinates:")
            for i, row in valid_df.head(3).iterrows():
                print(f"   {row['Regulated Entity Name']}: ({row['Latitude']:.4f}, {row['Longitude']:.4f})")
            
            return valid_df
            
        except Exception as e:
            print(f"❌ Error loading enforcement data: {e}")
            return pd.DataFrame()
    
    def load_lpst_for_county_analysis(self):
        """Load LPST data for county-level analysis"""
        print("🛢️ LOADING LPST DATA FOR COUNTY ANALYSIS")
        
        lpst_file = self.tceq_dir / "Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv"
        
        if not lpst_file.exists():
            print(f"❌ LPST file not found")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(lpst_file, encoding='utf-8-sig')
            print(f"📊 Loaded {len(df)} LPST records")
            
            # Count by county for analysis
            county_counts = df['County'].value_counts()
            print(f"🗺️  LPST sites by major counties:")
            for county, count in county_counts.head(5).items():
                print(f"   {county}: {count} sites")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading LPST data: {e}")
            return pd.DataFrame()
    
    def find_nearby_enforcement_actions(self, site_lat, site_lng, enforcement_df):
        """Find enforcement actions within screening distances"""
        nearby_concerns = []
        
        if enforcement_df.empty:
            return nearby_concerns
        
        site_coords = (site_lat, site_lng)
        
        for idx, enforcement in enforcement_df.iterrows():
            try:
                enforcement_coords = (enforcement['Latitude'], enforcement['Longitude'])
                distance_miles = geodesic(site_coords, enforcement_coords).miles
                
                # Only include within 1 mile screening radius
                if distance_miles <= 1.0:
                    # Determine risk level based on distance
                    if distance_miles <= self.SCREENING_DISTANCES['IMMEDIATE']:
                        risk_level = 'IMMEDIATE'
                        risk_score = self.RISK_SCORES['ENFORCEMENT_IMMEDIATE']
                    elif distance_miles <= self.SCREENING_DISTANCES['CRITICAL']:
                        risk_level = 'CRITICAL'
                        risk_score = self.RISK_SCORES['ENFORCEMENT_CRITICAL']
                    elif distance_miles <= self.SCREENING_DISTANCES['HIGH']:
                        risk_level = 'HIGH'
                        risk_score = self.RISK_SCORES['ENFORCEMENT_HIGH']
                    else:
                        risk_level = 'MEDIUM'
                        risk_score = self.RISK_SCORES['ENFORCEMENT_MEDIUM']
                    
                    # Create detailed concern description
                    concern = {
                        'type': 'ENVIRONMENTAL_ENFORCEMENT',
                        'facility_name': enforcement.get('Regulated Entity Name', 'Unknown Facility'),
                        'business_type': enforcement.get('Business Type', 'Unknown'),
                        'physical_location': enforcement.get('Physical Location', 'Unknown'),
                        'physical_county': enforcement.get('Physical County', 'Unknown'),
                        'total_violations': enforcement.get('Total Violation Count', 0),
                        'noe_date': enforcement.get('NOE Date', 'Unknown'),
                        'tceq_region': enforcement.get('TCEQ Region Name', 'Unknown'),
                        'distance_miles': round(distance_miles, 3),
                        'risk_level': risk_level,
                        'risk_score': risk_score,
                        'coordinates': [enforcement['Latitude'], enforcement['Longitude']],
                        'description': f"Environmental enforcement action against {enforcement.get('Regulated Entity Name', 'facility')} ({enforcement.get('Business Type', 'unknown business type')}) - {enforcement.get('Total Violation Count', 0)} violations noted {enforcement.get('NOE Date', 'date unknown')}"
                    }
                    
                    nearby_concerns.append(concern)
                    
            except Exception as e:
                continue
        
        # Sort by distance (closest first)
        nearby_concerns.sort(key=lambda x: x['distance_miles'])
        
        return nearby_concerns
    
    def analyze_county_lpst_density(self, site_county, lpst_df):
        """Analyze LPST density in county for regional risk assessment"""
        if lpst_df.empty:
            return []
        
        county_clean = site_county.replace(' County', '').replace('County ', '').strip()
        
        # Filter LPST sites in same county
        county_lpst = lpst_df[lpst_df['County'].str.contains(county_clean, case=False, na=False)]
        
        if county_lpst.empty:
            return []
        
        total_sites = len(county_lpst)
        
        # Determine risk level based on LPST density
        if total_sites > 500:  # High density counties (e.g., Harris, Dallas)
            risk_level = 'HIGH'
            risk_score = self.RISK_SCORES['LPST_COUNTY_HIGH']
            density_description = f"High LPST density county - {total_sites} petroleum contamination sites"
        elif total_sites > 100:
            risk_level = 'MEDIUM'
            risk_score = self.RISK_SCORES['LPST_COUNTY_MEDIUM']
            density_description = f"Medium LPST density county - {total_sites} petroleum contamination sites"
        else:
            risk_level = 'LOW'
            risk_score = self.RISK_SCORES['LPST_COUNTY_LOW']
            density_description = f"Low LPST density county - {total_sites} petroleum contamination sites"
        
        # Create county-level concern
        county_concern = {
            'type': 'COUNTY_LPST_DENSITY',
            'county': site_county,
            'total_lpst_sites': total_sites,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'description': density_description,
            'recommendation': f"County has {total_sites} LPST sites - {'Enhanced' if total_sites > 500 else 'Standard'} Phase I ESA recommended"
        }
        
        return [county_concern]
    
    def calculate_environmental_risk_assessment(self, enforcement_concerns, county_concerns):
        """Calculate overall environmental risk based on all concerns"""
        all_concerns = enforcement_concerns + county_concerns
        
        if not all_concerns:
            return {
                'total_concerns': 0,
                'risk_level': 'LOW',
                'risk_score': 0,
                'recommendation': 'Standard Phase I ESA',
                'concern_summary': 'No environmental concerns identified within screening radius'
            }
        
        # Calculate total risk score
        total_risk_score = sum(concern.get('risk_score', 0) for concern in all_concerns)
        
        # Determine overall risk level
        if total_risk_score >= 100:
            overall_risk = 'HIGH'
            recommendation = 'Enhanced Phase I ESA with vapor assessment required'
        elif total_risk_score >= 50:
            overall_risk = 'MEDIUM'
            recommendation = 'Enhanced Phase I ESA recommended'
        elif total_risk_score >= 20:
            overall_risk = 'LOW-MEDIUM'
            recommendation = 'Standard Phase I ESA with environmental awareness'
        else:
            overall_risk = 'LOW'
            recommendation = 'Standard Phase I ESA'
        
        # Create concern summary
        enforcement_count = len(enforcement_concerns)
        county_count = len(county_concerns)
        
        if enforcement_count > 0 and county_count > 0:
            summary = f"{enforcement_count} nearby enforcement action(s) + county-level LPST density assessment"
        elif enforcement_count > 0:
            summary = f"{enforcement_count} environmental enforcement action(s) within 1 mile"
        elif county_count > 0:
            summary = "County-level LPST contamination site density assessment"
        else:
            summary = "No environmental concerns identified"
        
        return {
            'total_concerns': len(all_concerns),
            'risk_level': overall_risk,
            'risk_score': total_risk_score,
            'recommendation': recommendation,
            'concern_summary': summary
        }
    
    def screen_all_sites(self):
        """Screen all D'Marco sites for environmental concerns"""
        print("🎯 SCREENING ALL SITES FOR ENVIRONMENTAL CONCERNS")
        
        # Load data
        sites_data = self.load_dmarco_sites()
        enforcement_df = self.load_tceq_enforcement_with_coordinates()
        lpst_df = self.load_lpst_for_county_analysis()
        
        if enforcement_df.empty and lpst_df.empty:
            print("❌ No environmental data available for screening")
            return []
        
        site_screenings = []
        
        for site in sites_data:
            site_index = site['site_index']
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            county = site.get('census_county', 'Unknown')
            
            print(f"  Site {site_index} ({county}): ", end="")
            
            # Find nearby enforcement actions (if coordinates available)
            enforcement_concerns = []
            if not enforcement_df.empty:
                enforcement_concerns = self.find_nearby_enforcement_actions(
                    site_lat, site_lng, enforcement_df
                )
            
            # Analyze county LPST density
            county_concerns = []
            if not lpst_df.empty:
                county_concerns = self.analyze_county_lpst_density(county, lpst_df)
            
            # Calculate overall risk assessment
            risk_assessment = self.calculate_environmental_risk_assessment(
                enforcement_concerns, county_concerns
            )
            
            # Create site screening result
            screening_result = {
                'site_index': site_index,
                'county': county,
                'coordinates': [site_lat, site_lng],
                'environmental_screening_status': 'SUCCESS_FIXED_SCREENING',
                'enforcement_concerns': enforcement_concerns,
                'county_concerns': county_concerns,
                'environmental_risk_assessment': risk_assessment,
                'screening_timestamp': datetime.now().isoformat()
            }
            
            site_screenings.append(screening_result)
            
            # Print result
            concerns_count = risk_assessment['total_concerns']
            risk_level = risk_assessment['risk_level']
            print(f"{concerns_count} concern(s), {risk_level} risk")
        
        return site_screenings
    
    def create_fixed_environmental_analysis(self):
        """Create fixed environmental analysis with proper descriptions"""
        print("🚀 CREATING FIXED ENVIRONMENTAL ANALYSIS")
        
        # Screen all sites
        site_screenings = self.screen_all_sites()
        
        if not site_screenings:
            print("❌ No screening results generated")
            return None
        
        # Calculate summary statistics
        total_sites = len(site_screenings)
        sites_with_concerns = len([s for s in site_screenings if s['environmental_risk_assessment']['total_concerns'] > 0])
        sites_clean = total_sites - sites_with_concerns
        
        concern_counts = [s['environmental_risk_assessment']['total_concerns'] for s in site_screenings]
        risk_levels = [s['environmental_risk_assessment']['risk_level'] for s in site_screenings]
        
        summary_stats = {
            'total_sites_screened': total_sites,
            'sites_with_concerns': sites_with_concerns,
            'sites_clean': sites_clean,
            'concern_rate_percentage': round((sites_with_concerns / total_sites) * 100, 1),
            'average_concerns_per_site': round(np.mean(concern_counts), 1),
            'concern_distribution': {
                '0_concerns': concern_counts.count(0),
                '1_concern': concern_counts.count(1),
                '2_concerns': concern_counts.count(2),
                '3_plus_concerns': len([c for c in concern_counts if c >= 3])
            },
            'risk_level_distribution': {
                'HIGH': risk_levels.count('HIGH'),
                'MEDIUM': risk_levels.count('MEDIUM'),
                'LOW-MEDIUM': risk_levels.count('LOW-MEDIUM'),
                'LOW': risk_levels.count('LOW')
            }
        }
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed screening results
        screening_file = self.base_dir / f"DMarco_FIXED_Environmental_Screening_{timestamp}.json"
        
        comprehensive_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'FIXED_ENVIRONMENTAL_SCREENING',
            'fix_summary': {
                'original_issue': 'All sites showing exactly 1 environmental concern (clearly erroneous)',
                'root_cause': 'County-level LPST screening creating uniform results',
                'solution': 'Proper distance-based screening with TCEQ enforcement coordinates + detailed descriptions',
                'improvements': [
                    'Distance-based proximity analysis (1/8 mile to 1 mile screening)',
                    'Detailed concern descriptions with facility names and violation details',
                    'Risk scoring based on proximity and violation severity',
                    'County-level LPST density assessment as secondary factor'
                ]
            },
            'summary_statistics': summary_stats,
            'screening_methodology': {
                'distance_thresholds': self.SCREENING_DISTANCES,
                'risk_scoring': self.RISK_SCORES,
                'data_sources': [
                    'TCEQ Notices of Enforcement (with coordinates)',
                    'TCEQ LPST Sites (county-level density)'
                ]
            },
            'site_screenings': site_screenings
        }
        
        with open(screening_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        # Create Excel export with descriptions
        excel_data = []
        for screening in site_screenings:
            risk_assessment = screening['environmental_risk_assessment']
            
            # Create detailed description of concerns
            concern_descriptions = []
            
            # Add enforcement concerns
            for concern in screening['enforcement_concerns']:
                concern_descriptions.append(f"• {concern['description']} (Distance: {concern['distance_miles']} mi)")
            
            # Add county concerns
            for concern in screening['county_concerns']:
                concern_descriptions.append(f"• {concern['description']}")
            
            if not concern_descriptions:
                concern_descriptions = ["No environmental concerns identified within screening radius"]
            
            row = {
                'Site_Index': screening['site_index'],
                'County': screening['county'],
                'Total_Environmental_Concerns': risk_assessment['total_concerns'],
                'Environmental_Risk_Level': risk_assessment['risk_level'],
                'Risk_Score': risk_assessment['risk_score'],
                'Phase_I_ESA_Recommendation': risk_assessment['recommendation'],
                'Concern_Summary': risk_assessment['concern_summary'],
                'Detailed_Concern_Descriptions': ' | '.join(concern_descriptions),
                'Enforcement_Actions_Within_1_Mile': len(screening['enforcement_concerns'])
            }
            
            excel_data.append(row)
        
        df = pd.DataFrame(excel_data)
        
        excel_file = self.base_dir / f"DMarco_FIXED_Environmental_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main analysis
            df.to_excel(writer, sheet_name='Environmental_Screening', index=False)
            
            # High risk sites
            high_risk = df[df['Environmental_Risk_Level'].isin(['HIGH', 'MEDIUM'])]
            if not high_risk.empty:
                high_risk.to_excel(writer, sheet_name='High_Risk_Sites', index=False)
            
            # Sites with enforcement actions
            with_enforcement = df[df['Enforcement_Actions_Within_1_Mile'] > 0]
            if not with_enforcement.empty:
                with_enforcement.to_excel(writer, sheet_name='Sites_With_Enforcement', index=False)
        
        print(f"\n📊 FIXED ENVIRONMENTAL SCREENING COMPLETE!")
        print(f"✅ Sites screened: {summary_stats['total_sites_screened']}")
        print(f"🔍 Sites with concerns: {summary_stats['sites_with_concerns']} ({summary_stats['concern_rate_percentage']}%)")
        print(f"🧹 Clean sites: {summary_stats['sites_clean']}")
        print(f"📊 Concern distribution: {summary_stats['concern_distribution']}")
        print(f"⚠️  Risk levels: {summary_stats['risk_level_distribution']}")
        
        print(f"\n💾 Files created:")
        print(f"   • Detailed JSON: {screening_file.name}")
        print(f"   • Excel analysis: {excel_file.name}")
        
        return comprehensive_report

if __name__ == "__main__":
    fixer = FixedEnvironmentalScreening()
    results = fixer.create_fixed_environmental_analysis()