#!/usr/bin/env python3
"""
📊 D'Marco Master Excel Export
WINGMAN Agent - Complete 38-site analysis for client delivery

Creates comprehensive Excel file with all D'Marco site analysis data:
- Site details with corrected county names
- QCT/DDA status and basis boost eligibility
- Competition analysis with proper TDHCA rules
- Environmental screening results
- Economic viability data
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class DMarcoMasterExcelCreator:
    """Create comprehensive Excel export of all D'Marco analysis"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Input files
        self.corrected_sites_path = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        # Find the most recent corrected competition analysis
        competition_files = list(self.base_dir.glob("DMarco_CORRECTED_Competition_Analysis_*.json"))
        if competition_files:
            self.competition_path = max(competition_files, key=lambda x: x.stat().st_mtime)
        else:
            self.competition_path = None
            
    def load_site_data(self):
        """Load corrected site data from TOWER"""
        print("📊 Loading corrected D'Marco site data...")
        
        with open(self.corrected_sites_path, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} sites")
        return sites_data
    
    def load_competition_data(self):
        """Load corrected competition analysis"""
        if not self.competition_path:
            print("⚠️  No corrected competition analysis found")
            return {}
        
        print(f"📊 Loading competition analysis: {self.competition_path.name}")
        
        with open(self.competition_path, 'r') as f:
            competition_data = json.load(f)
        
        # Create lookup dictionary by site index
        competition_lookup = {}
        for analysis in competition_data.get('competition_analysis', []):
            site_index = analysis['site_index']
            competition_lookup[site_index] = analysis
            
        print(f"✅ Loaded competition data for {len(competition_lookup)} sites")
        return competition_lookup
    
    def create_master_dataframe(self, sites_data, competition_lookup):
        """Create comprehensive DataFrame with all site information"""
        print("📊 Creating master DataFrame...")
        
        master_data = []
        
        for site in sites_data:
            site_index = site['site_index']
            competition = competition_lookup.get(site_index, {})
            
            # Basic site information
            row = {
                'Site_Index': site_index,
                'Site_Name': site.get('site_name', ''),
                'Address': site.get('raw_site_address', ''),
                'Acreage': site.get('acreage', ''),
                'TDHCA_Region': site.get('tdhca_region', ''),
                
                # Coordinates
                'Latitude': site.get('parcel_center_lat', ''),
                'Longitude': site.get('parcel_center_lng', ''),
                'Coordinate_Quality': site.get('coordinate_quality', ''),
                
                # County (corrected)
                'County': site.get('census_county', ''),
                'Census_Tract': site.get('census_tract', ''),
                'State': site.get('census_state', ''),
                
                # QCT/DDA Status
                'QCT_Designation': site.get('qct_designation', ''),
                'DDA_Designation': site.get('dda_designation', ''),
                'Basis_Boost_Eligible': site.get('basis_boost_eligible', ''),
                'AMI_Source_Type': site.get('ami_source_type', ''),
                
                # Environmental Analysis
                'Environmental_Risk_Level': site.get('environmental_risk_level', ''),
                'Environmental_Sites_1_Mile': site.get('environmental_sites_1_mile', ''),
                'Phase_I_ESA_Recommendation': site.get('phase_i_esa_recommendation', ''),
                
                # FEMA Flood Analysis
                'FEMA_Flood_Zone': site.get('fema_flood_zone', ''),
                'Flood_Risk_Level': site.get('flood_risk_level', ''),
                
                # Viability Assessment
                'Acreage_Assessment': site.get('acreage_assessment', ''),
                'Unit_Development_Potential': site.get('unit_development_potential', ''),
                'Regional_Market_Strength': site.get('regional_market_strength', ''),
                
                # Competition Analysis
                'County_Population': competition.get('county_population', ''),
                'County_Exempt_Under_1M': competition.get('county_exempt_under_1m', ''),
                'Fatal_Flaw_9_Percent': competition.get('fatal_flaw_9_percent', ''),
                'Risk_Assessment_4_Percent': competition.get('risk_assessment_4_percent', ''),
                'Nearby_Projects_1_Mile': len(competition.get('nearby_projects_1_mile', [])),
                'Nearby_Projects_2_Mile': len(competition.get('nearby_projects_2_mile', [])),
                'Exemption_Reason': competition.get('exemption_reason', ''),
                
                # Analysis Status
                'Analysis_Timestamp': site.get('analysis_timestamp', ''),
                'QCT_Analysis_Status': site.get('qct_analysis_status', ''),
                'Environmental_Analysis_Status': site.get('environmental_analysis_status', ''),
                'FEMA_Analysis_Status': site.get('fema_analysis_status', ''),
                'AMI_Analysis_Status': site.get('ami_analysis_status', ''),
                'Viability_Analysis_Status': site.get('viability_analysis_status', '')
            }
            
            master_data.append(row)
        
        df = pd.DataFrame(master_data)
        df = df.sort_values('Site_Index')
        
        print(f"✅ Created master DataFrame with {len(df)} sites and {len(df.columns)} columns")
        return df
    
    def create_competition_details_sheet(self, competition_lookup):
        """Create detailed competition analysis sheet"""
        print("📊 Creating competition details sheet...")
        
        details_data = []
        
        for site_index, competition in competition_lookup.items():
            # Add nearby projects within 1 mile
            for project in competition.get('nearby_projects_1_mile', []):
                details_data.append({
                    'Site_Index': site_index,
                    'Site_Name': competition.get('site_name', ''),
                    'Distance_Type': '1_Mile_Fatal_Flaw',
                    'Distance_Miles': project['distance_miles'],
                    'Competing_Project': project['development_name'],
                    'TDHCA_Number': project['tdhca_number'],
                    'Project_County': project['project_county'],
                    'Program_Type': project['program_type'],
                    'Award_Year': project['award_year'],
                    'LIHTC_Units': project['lihtc_units']
                })
            
            # Add nearby projects within 2 miles (excluding 1-mile projects)
            for project in competition.get('nearby_projects_2_mile', []):
                if project['distance_miles'] > 1.0:
                    details_data.append({
                        'Site_Index': site_index,
                        'Site_Name': competition.get('site_name', ''),
                        'Distance_Type': '2_Mile_Risk_Assessment',
                        'Distance_Miles': project['distance_miles'],
                        'Competing_Project': project['development_name'],
                        'TDHCA_Number': project['tdhca_number'],
                        'Project_County': project['project_county'],
                        'Program_Type': project['program_type'],
                        'Award_Year': project['award_year'],
                        'LIHTC_Units': project['lihtc_units']
                    })
        
        if details_data:
            details_df = pd.DataFrame(details_data)
            details_df = details_df.sort_values(['Site_Index', 'Distance_Miles'])
            print(f"✅ Created competition details with {len(details_df)} competing projects")
            return details_df
        else:
            print("ℹ️  No competing projects found")
            return pd.DataFrame()
    
    def create_summary_sheet(self, master_df, competition_lookup):
        """Create executive summary sheet"""
        print("📊 Creating executive summary sheet...")
        
        # Site counts by status
        total_sites = len(master_df)
        qct_dda_eligible = len(master_df[master_df['Basis_Boost_Eligible'] == 'YES'])
        county_exempt = len(master_df[master_df['County_Exempt_Under_1M'] == True])
        fatal_flaw_sites = len(master_df[master_df['Fatal_Flaw_9_Percent'] == True])
        clean_sites_9pct = total_sites - fatal_flaw_sites
        
        # County distribution
        county_counts = master_df['County'].value_counts()
        
        # Environmental risk distribution
        env_risk_counts = master_df['Environmental_Risk_Level'].value_counts()
        
        summary_data = [
            ['EXECUTIVE SUMMARY', ''],
            ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Total Sites Analyzed', total_sites],
            ['', ''],
            ['QCT/DDA ANALYSIS', ''],
            ['Sites Eligible for 130% Basis Boost', qct_dda_eligible],
            ['Sites Not Eligible for Basis Boost', total_sites - qct_dda_eligible],
            ['', ''],
            ['COMPETITION ANALYSIS (9% CREDITS)', ''],
            ['Sites Exempt (County Population <1M)', county_exempt],
            ['Fatal Flaw Sites (Cannot Use 9% Credits)', fatal_flaw_sites],
            ['Clean Sites (Suitable for 9% Credits)', clean_sites_9pct],
            ['Fatal Flaw Rate', f"{(fatal_flaw_sites/total_sites)*100:.1f}%"],
            ['', ''],
            ['COUNTY DISTRIBUTION', ''],
        ]
        
        # Add county counts
        for county, count in county_counts.items():
            summary_data.append([county, count])
        
        summary_data.extend([
            ['', ''],
            ['ENVIRONMENTAL RISK LEVELS', ''],
        ])
        
        # Add environmental risk counts
        for risk_level, count in env_risk_counts.items():
            summary_data.append([risk_level, count])
        
        summary_df = pd.DataFrame(summary_data, columns=['Category', 'Value'])
        print("✅ Created executive summary")
        return summary_df
    
    def export_to_excel(self):
        """Create comprehensive Excel export"""
        print("🚀 Creating D'Marco Master Excel Export...")
        
        # Load data
        sites_data = self.load_site_data()
        competition_lookup = self.load_competition_data()
        
        # Create DataFrames
        master_df = self.create_master_dataframe(sites_data, competition_lookup)
        competition_details_df = self.create_competition_details_sheet(competition_lookup)
        summary_df = self.create_summary_sheet(master_df, competition_lookup)
        
        # Create Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = self.base_dir / f"DMarco_Master_Analysis_{timestamp}.xlsx"
        
        print(f"📊 Writing Excel file: {excel_path.name}")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Executive Summary
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # Master site data
            master_df.to_excel(writer, sheet_name='Master_Site_Analysis', index=False)
            
            # Competition details
            if not competition_details_df.empty:
                competition_details_df.to_excel(writer, sheet_name='Competition_Details', index=False)
            
            # Filter sheets for easier analysis
            # Clean sites (suitable for 9%)
            clean_sites = master_df[master_df['Fatal_Flaw_9_Percent'] != True]
            clean_sites.to_excel(writer, sheet_name='Clean_Sites_9_Percent', index=False)
            
            # Fatal flaw sites
            fatal_flaw_sites = master_df[master_df['Fatal_Flaw_9_Percent'] == True]
            if not fatal_flaw_sites.empty:
                fatal_flaw_sites.to_excel(writer, sheet_name='Fatal_Flaw_Sites', index=False)
            
            # QCT/DDA eligible sites
            qct_dda_sites = master_df[master_df['Basis_Boost_Eligible'] == 'YES']
            qct_dda_sites.to_excel(writer, sheet_name='QCT_DDA_Eligible', index=False)
        
        print(f"✅ Excel export complete: {excel_path}")
        print(f"📋 Sheets created:")
        print(f"   • Executive_Summary")
        print(f"   • Master_Site_Analysis ({len(master_df)} sites)")
        print(f"   • Competition_Details ({len(competition_details_df)} competing projects)")
        print(f"   • Clean_Sites_9_Percent ({len(clean_sites)} sites)")
        if not fatal_flaw_sites.empty:
            print(f"   • Fatal_Flaw_Sites ({len(fatal_flaw_sites)} sites)")
        print(f"   • QCT_DDA_Eligible ({len(qct_dda_sites)} sites)")
        
        return excel_path

if __name__ == "__main__":
    creator = DMarcoMasterExcelCreator()
    excel_file = creator.export_to_excel()