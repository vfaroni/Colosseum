#!/usr/bin/env python3
"""
🔧 CORRECTED Environmental Risk Classification
WINGMAN Agent - Fix Risk Hierarchy + Single Excel Export

CORRECTED RISK CLASSIFICATION:
- CRITICAL: ≤1/8 mile (0.125 mi) - Vapor intrusion concern
- HIGH: ≤1/4 mile (0.25 mi) - Enhanced Phase I ESA required  
- MEDIUM: ≤1/2 mile (0.5 mi) - Standard screening distance
- LOW: 1/2 to 1 mile (0.5-1.0 mi) - Regional assessment

DELIVERABLE: Single integrated Excel file with corrected environmental data
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class CorrectedEnvironmentalAnalysis:
    """Corrected environmental analysis with proper risk hierarchy"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # CORRECTED distance thresholds and risk classification
        self.CORRECTED_RISK_THRESHOLDS = {
            'CRITICAL': 0.125,    # ≤1/8 mile - Vapor intrusion concern
            'HIGH': 0.25,         # ≤1/4 mile - Enhanced Phase I ESA required
            'MEDIUM': 0.5,        # ≤1/2 mile - Standard screening distance  
            'LOW': 1.0            # 1/2 to 1 mile - Regional assessment
        }
        
        # Risk scoring (higher scores for closer distances)
        self.CORRECTED_RISK_SCORES = {
            'CRITICAL': 100,      # Immediate vapor intrusion concern
            'HIGH': 75,           # Enhanced Phase I required
            'MEDIUM': 50,         # Standard Phase I
            'LOW': 25             # Regional awareness
        }
        
        # Phase I ESA recommendations
        self.ESA_RECOMMENDATIONS = {
            'CRITICAL': 'Enhanced Phase I ESA with vapor assessment and indoor air quality testing required',
            'HIGH': 'Enhanced Phase I ESA required - detailed investigation needed',
            'MEDIUM': 'Standard Phase I ESA with environmental awareness',
            'LOW': 'Standard Phase I ESA - regional environmental context'
        }
    
    def load_environmental_screening_data(self):
        """Load the latest environmental screening data"""
        print("📊 LOADING ENVIRONMENTAL SCREENING DATA")
        
        screening_file = self.base_dir / "DMarco_FIXED_Environmental_Screening_20250730_173621.json"
        
        if not screening_file.exists():
            print(f"❌ Environmental screening file not found")
            return []
        
        with open(screening_file, 'r') as f:
            data = json.load(f)
        
        site_screenings = data.get('site_screenings', [])
        print(f"✅ Loaded environmental data for {len(site_screenings)} sites")
        
        return site_screenings
    
    def reclassify_environmental_concerns(self, site_screenings):
        """Reclassify environmental concerns with corrected risk hierarchy"""
        print("🔄 RECLASSIFYING ENVIRONMENTAL RISKS WITH CORRECTED HIERARCHY")
        
        corrected_screenings = []
        
        for site_screening in site_screenings:
            site_index = site_screening['site_index']
            enforcement_concerns = site_screening.get('enforcement_concerns', [])
            county_concerns = site_screening.get('county_concerns', [])
            
            # Reclassify enforcement concerns based on corrected distances
            corrected_enforcement = []
            highest_risk_level = 'LOW'
            total_risk_score = 0
            
            for concern in enforcement_concerns:
                distance = concern['distance_miles']
                
                # Apply corrected risk classification
                if distance <= self.CORRECTED_RISK_THRESHOLDS['CRITICAL']:
                    risk_level = 'CRITICAL'
                    risk_score = self.CORRECTED_RISK_SCORES['CRITICAL']
                    if highest_risk_level != 'CRITICAL':
                        highest_risk_level = 'CRITICAL'
                elif distance <= self.CORRECTED_RISK_THRESHOLDS['HIGH']:
                    risk_level = 'HIGH'
                    risk_score = self.CORRECTED_RISK_SCORES['HIGH']
                    if highest_risk_level not in ['CRITICAL']:
                        highest_risk_level = 'HIGH'
                elif distance <= self.CORRECTED_RISK_THRESHOLDS['MEDIUM']:
                    risk_level = 'MEDIUM'
                    risk_score = self.CORRECTED_RISK_SCORES['MEDIUM']
                    if highest_risk_level not in ['CRITICAL', 'HIGH']:
                        highest_risk_level = 'MEDIUM'
                else:  # distance <= 1.0 mile
                    risk_level = 'LOW'
                    risk_score = self.CORRECTED_RISK_SCORES['LOW']
                
                # Update concern with corrected classification
                corrected_concern = concern.copy()
                corrected_concern['risk_level'] = risk_level
                corrected_concern['risk_score'] = risk_score
                corrected_concern['corrected_classification'] = True
                
                corrected_enforcement.append(corrected_concern)
                total_risk_score += risk_score
            
            # Add county-level risk (if any)
            for county_concern in county_concerns:
                total_risk_score += county_concern.get('risk_score', 0)
            
            # Calculate overall risk assessment with corrected hierarchy
            critical_concerns = [c for c in corrected_enforcement if c['risk_level'] == 'CRITICAL']
            high_concerns = [c for c in corrected_enforcement if c['risk_level'] == 'HIGH'] 
            medium_concerns = [c for c in corrected_enforcement if c['risk_level'] == 'MEDIUM']
            low_concerns = [c for c in corrected_enforcement if c['risk_level'] == 'LOW']
            
            # Overall risk is highest individual risk level found
            if critical_concerns:
                overall_risk = 'CRITICAL'
            elif high_concerns:
                overall_risk = 'HIGH'  
            elif medium_concerns:
                overall_risk = 'MEDIUM'
            elif low_concerns or county_concerns:
                overall_risk = 'LOW'
            else:
                overall_risk = 'NONE'
            
            # Create corrected risk assessment
            corrected_risk_assessment = {
                'total_concerns': len(corrected_enforcement) + len(county_concerns),
                'critical_concerns': len(critical_concerns),
                'high_concerns': len(high_concerns),
                'medium_concerns': len(medium_concerns),
                'low_concerns': len(low_concerns),
                'county_concerns': len(county_concerns),
                'overall_risk_level': overall_risk,
                'risk_score': total_risk_score,
                'phase_i_recommendation': self.ESA_RECOMMENDATIONS.get(overall_risk, 'Standard Phase I ESA'),
                'corrected_classification': True
            }
            
            # Create corrected screening result
            corrected_screening = {
                'site_index': site_index,
                'county': site_screening['county'],
                'coordinates': site_screening['coordinates'],
                'corrected_enforcement_concerns': corrected_enforcement,
                'county_concerns': county_concerns,
                'corrected_risk_assessment': corrected_risk_assessment,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            corrected_screenings.append(corrected_screening)
            
            # Print correction summary
            if critical_concerns:
                print(f"  Site {site_index}: 🚨 CRITICAL - {len(critical_concerns)} vapor intrusion concern(s)")
            elif high_concerns:
                print(f"  Site {site_index}: ⚠️  HIGH - {len(high_concerns)} enhanced ESA required")
            elif medium_concerns:
                print(f"  Site {site_index}: 📊 MEDIUM - {len(medium_concerns)} standard screening")
            else:
                print(f"  Site {site_index}: ✅ LOW - regional assessment only")
        
        return corrected_screenings
    
    def load_all_analysis_data(self):
        """Load all analysis components for integration"""
        print("📊 LOADING ALL ANALYSIS DATA FOR INTEGRATION")
        
        data = {}
        
        # Load base sites
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        with open(sites_file, 'r') as f:
            data['base_sites'] = json.load(f)
        print(f"✅ Base sites: {len(data['base_sites'])}")
        
        # Load latest integrated analysis
        integrated_files = list(self.base_dir.glob("DMarco_FINAL_INTEGRATED_Analysis_*.xlsx"))
        if integrated_files:
            latest_integrated = max(integrated_files, key=lambda x: x.stat().st_mtime)
            try:
                integrated_df = pd.read_excel(latest_integrated, sheet_name='Integrated_Analysis')
                data['integrated_analysis'] = integrated_df.to_dict('records')
                print(f"✅ Integrated analysis: {len(data['integrated_analysis'])} sites")
            except:
                data['integrated_analysis'] = []
        
        return data
    
    def create_single_comprehensive_excel(self):
        """Create single comprehensive Excel file with corrected environmental data"""
        print("🚀 CREATING SINGLE COMPREHENSIVE EXCEL WITH CORRECTED ENVIRONMENTAL DATA")
        
        # Load and correct environmental data
        site_screenings = self.load_environmental_screening_data()
        corrected_screenings = self.reclassify_environmental_concerns(site_screenings)
        
        # Load other analysis data
        analysis_data = self.load_all_analysis_data()
        
        # Create lookup for corrected environmental data
        env_lookup = {screening['site_index']: screening for screening in corrected_screenings}
        
        # Create comprehensive dataset
        comprehensive_data = []
        
        if analysis_data.get('integrated_analysis'):
            # Use existing integrated analysis as base
            for record in analysis_data['integrated_analysis']:
                site_index = record.get('site_index')
                env_data = env_lookup.get(site_index, {})
                risk_assessment = env_data.get('corrected_risk_assessment', {})
                enforcement_concerns = env_data.get('corrected_enforcement_concerns', [])
                
                # Create environmental summary
                critical_facilities = [c for c in enforcement_concerns if c.get('risk_level') == 'CRITICAL']
                high_facilities = [c for c in enforcement_concerns if c.get('risk_level') == 'HIGH']
                
                environmental_summary = []
                if critical_facilities:
                    for facility in critical_facilities:
                        environmental_summary.append(f"CRITICAL: {facility['facility_name']} at {facility['distance_miles']} mi")
                if high_facilities:
                    for facility in high_facilities:
                        environmental_summary.append(f"HIGH: {facility['facility_name']} at {facility['distance_miles']} mi")
                
                if not environmental_summary and risk_assessment.get('county_concerns', 0) > 0:
                    environmental_summary.append("County-level LPST density assessment only")
                
                # Update record with corrected environmental data
                record.update({
                    'environmental_risk_level_corrected': risk_assessment.get('overall_risk_level', 'UNKNOWN'),
                    'critical_concerns_count': risk_assessment.get('critical_concerns', 0),
                    'high_concerns_count': risk_assessment.get('high_concerns', 0),
                    'medium_concerns_count': risk_assessment.get('medium_concerns', 0),
                    'total_environmental_concerns': risk_assessment.get('total_concerns', 0),
                    'phase_i_esa_recommendation': risk_assessment.get('phase_i_recommendation', 'Standard Phase I ESA'),
                    'environmental_concerns_detail': ' | '.join(environmental_summary) if environmental_summary else 'No significant concerns within screening radius',
                    'vapor_intrusion_concern': 'YES' if risk_assessment.get('critical_concerns', 0) > 0 else 'NO'
                })
                
                comprehensive_data.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(comprehensive_data)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = self.base_dir / f"DMarco_FINAL_COMPREHENSIVE_Analysis_CORRECTED_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main comprehensive analysis
            df.to_excel(writer, sheet_name='Comprehensive_Analysis', index=False)
            
            # Critical environmental sites (vapor intrusion concerns)
            critical_sites = df[df['critical_concerns_count'] > 0]
            if not critical_sites.empty:
                critical_sites.to_excel(writer, sheet_name='CRITICAL_Environmental', index=False)
            
            # High environmental risk sites
            high_risk_sites = df[df['high_concerns_count'] > 0]
            if not high_risk_sites.empty:
                high_risk_sites.to_excel(writer, sheet_name='HIGH_Environmental_Risk', index=False)
            
            # Top 10 overall sites
            top_sites = df.nlargest(10, 'overall_score') if 'overall_score' in df.columns else df.head(10)
            top_sites.to_excel(writer, sheet_name='Top_10_Sites', index=False)
            
            # Environmental risk summary
            env_summary_data = [
                ['ENVIRONMENTAL RISK SUMMARY', ''],
                ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M CST')],
                ['Total Sites Analyzed', len(df)],
                ['', ''],
                ['CRITICAL RISK (≤1/8 mile)', ''],
                ['Sites with Vapor Intrusion Concerns', len(df[df['critical_concerns_count'] > 0])],
                ['', ''],
                ['HIGH RISK (≤1/4 mile)', ''],
                ['Sites Requiring Enhanced Phase I ESA', len(df[df['high_concerns_count'] > 0])],
                ['', ''],
                ['RISK LEVEL DISTRIBUTION', ''],
                ['CRITICAL Risk Sites', len(df[df['environmental_risk_level_corrected'] == 'CRITICAL'])],
                ['HIGH Risk Sites', len(df[df['environmental_risk_level_corrected'] == 'HIGH'])],
                ['MEDIUM Risk Sites', len(df[df['environmental_risk_level_corrected'] == 'MEDIUM'])],
                ['LOW Risk Sites', len(df[df['environmental_risk_level_corrected'] == 'LOW'])],
                ['', ''],
                ['PHASE I ESA REQUIREMENTS', ''],
                ['Enhanced Phase I + Vapor Assessment', len(df[df['environmental_risk_level_corrected'] == 'CRITICAL'])],
                ['Enhanced Phase I ESA', len(df[df['environmental_risk_level_corrected'] == 'HIGH'])],
                ['Standard Phase I ESA', len(df[df['environmental_risk_level_corrected'].isin(['MEDIUM', 'LOW'])])]
            ]
            
            env_summary_df = pd.DataFrame(env_summary_data, columns=['Category', 'Count'])
            env_summary_df.to_excel(writer, sheet_name='Environmental_Summary', index=False)
        
        # Print summary
        print(f"\n🏆 SINGLE COMPREHENSIVE EXCEL CREATED!")
        print(f"✅ Total sites: {len(df)}")
        
        if len(df) > 0:
            critical_count = len(df[df['critical_concerns_count'] > 0])
            high_count = len(df[df['high_concerns_count'] > 0])
            
            print(f"🚨 CRITICAL sites (vapor intrusion): {critical_count}")
            if critical_count > 0:
                critical_sites_list = df[df['critical_concerns_count'] > 0]['site_index'].tolist()
                print(f"   Sites: {critical_sites_list}")
            
            print(f"⚠️  HIGH risk sites (enhanced ESA): {high_count}")
            if high_count > 0:
                high_sites_list = df[df['high_concerns_count'] > 0]['site_index'].tolist()
                print(f"   Sites: {high_sites_list}")
        
        print(f"\n💾 Final Excel: {excel_file.name}")
        
        return excel_file, df

if __name__ == "__main__":
    analyzer = CorrectedEnvironmentalAnalysis()
    excel_file, df = analyzer.create_single_comprehensive_excel()