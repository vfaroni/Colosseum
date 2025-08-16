#!/usr/bin/env python3
"""
🏆 FINAL INTEGRATED D'Marco Analysis
WINGMAN Agent - All Factors Integrated

INTEGRATION COMPLETE:
✅ Competition Analysis (9% vs 4% credits)
✅ QCT/DDA Analysis (130% basis boost)
✅ Flood Risk Assessment (insurance costs)
✅ Environmental Screening (Phase I ESA costs)
✅ Regional Cost Modifiers (construction costs)
✅ School Amenities Analysis (LIHTC scoring)
✅ COMPREHENSIVE Excel Export with ALL factors
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FinalIntegratedAnalyzer:
    """Complete integrated analysis of all D'Marco factors"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Find latest analysis files
        self.latest_files = {
            'flood': self.find_latest_file("dmarco_sites_FINAL_flood_analysis_*.json"),
            'competition': self.find_latest_file("DMarco_CORRECTED_Competition_Analysis_*.json"),
            'environmental': self.find_latest_file("dmarco_sites_ENVIRONMENTAL_FIXED_*.json"),
            'cost_analysis': self.find_latest_file("DMarco_COMPREHENSIVE_Cost_Analysis_*.xlsx"),
            'school_amenities': self.find_latest_file("DMarco_School_Amenities_Analysis_*.xlsx")
        }
    
    def find_latest_file(self, pattern):
        """Find the most recent file matching pattern"""
        files = list(self.base_dir.glob(pattern))
        if files:
            return max(files, key=lambda x: x.stat().st_mtime)
        return None
    
    def load_all_analyses(self):
        """Load all completed analyses"""
        print("📊 LOADING ALL COMPLETED ANALYSES")
        
        data = {}
        
        # Load base sites
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        with open(sites_file, 'r') as f:
            data['base_sites'] = json.load(f)
        print(f"✅ Base sites: {len(data['base_sites'])} loaded")
        
        # Load flood analysis
        if self.latest_files['flood']:
            with open(self.latest_files['flood'], 'r') as f:
                data['flood'] = json.load(f)
            print(f"✅ Flood analysis: {len(data['flood'])} sites loaded")
        
        # Load competition analysis
        if self.latest_files['competition']:
            with open(self.latest_files['competition'], 'r') as f:
                comp_data = json.load(f)
                data['competition'] = comp_data.get('competition_analysis', [])
            print(f"✅ Competition analysis: {len(data['competition'])} sites loaded")
        
        # Load environmental analysis
        if self.latest_files['environmental']:
            with open(self.latest_files['environmental'], 'r') as f:
                data['environmental'] = json.load(f)
            print(f"✅ Environmental analysis: {len(data['environmental'])} sites loaded")
        
        # Load cost analysis (Excel)
        if self.latest_files['cost_analysis']:
            try:
                cost_df = pd.read_excel(self.latest_files['cost_analysis'], sheet_name='Cost_Analysis')
                data['cost_analysis'] = cost_df.to_dict('records')
                print(f"✅ Cost analysis: {len(data['cost_analysis'])} sites loaded")
            except:
                data['cost_analysis'] = []
        
        # Load school amenities (Excel)
        if self.latest_files['school_amenities']:
            try:
                amenities_df = pd.read_excel(self.latest_files['school_amenities'], sheet_name='School_Amenities')
                data['school_amenities'] = amenities_df.to_dict('records')
                print(f"✅ School amenities: {len(data['school_amenities'])} sites loaded")
            except:
                data['school_amenities'] = []
        
        return data
    
    def create_integrated_dataset(self, data):
        """Create completely integrated dataset"""
        print("🔄 INTEGRATING ALL ANALYSIS DATA")
        
        # Create lookup dictionaries
        flood_lookup = {site['site_index']: site for site in data.get('flood', [])}
        competition_lookup = {comp['site_index']: comp for comp in data.get('competition', [])}
        environmental_lookup = {site['site_index']: site for site in data.get('environmental', [])}
        cost_lookup = {cost['site_index']: cost for cost in data.get('cost_analysis', [])}
        amenities_lookup = {int(amenity['Site_Index']): amenity for amenity in data.get('school_amenities', [])}
        
        integrated_sites = []
        
        for base_site in data['base_sites']:
            site_index = base_site['site_index']
            
            # Get all corresponding analyses
            flood_data = flood_lookup.get(site_index, {})
            competition_data = competition_lookup.get(site_index, {})
            environmental_data = environmental_lookup.get(site_index, {})
            cost_data = cost_lookup.get(site_index, {})
            amenities_data = amenities_lookup.get(site_index, {})
            
            # Create integrated site record
            integrated_site = {
                # Basic Info
                'site_index': site_index,
                'site_name': base_site.get('site_name', ''),
                'address': base_site.get('raw_site_address', ''),
                'acreage': base_site.get('acreage', ''),
                'county': base_site.get('census_county', ''),
                'tdhca_region': base_site.get('tdhca_region', ''),
                'coordinates': [base_site.get('parcel_center_lat'), base_site.get('parcel_center_lng')],
                
                # QCT/DDA Status
                'qct_designation': base_site.get('qct_designation', ''),
                'dda_designation': base_site.get('dda_designation', ''),
                'basis_boost_eligible': base_site.get('basis_boost_eligible', ''),
                
                # Competition Analysis (9% Credits)
                'county_population': competition_data.get('county_population', ''),
                'county_exempt_under_1m': competition_data.get('county_exempt_under_1m', ''),
                'fatal_flaw_9_percent': competition_data.get('fatal_flaw_9_percent', ''),
                'competing_projects_1_mile': len(competition_data.get('nearby_projects_1_mile', [])),
                'competing_projects_2_mile': len(competition_data.get('nearby_projects_2_mile', [])),
                'competition_recommendation': '9% SUITABLE' if not competition_data.get('fatal_flaw_9_percent') else '4% ONLY',
                
                # Flood Analysis
                'flood_zone': flood_data.get('fema_flood_zone', 'Unknown'),
                'flood_risk_level': flood_data.get('flood_risk_level', 'Unknown'),
                'flood_insurance_required': flood_data.get('flood_insurance_required', ''),
                'flood_zone_description': flood_data.get('flood_zone_description', ''),
                
                # Environmental Screening
                'environmental_concerns_found': environmental_data.get('environmental_concerns_found', 0),
                'environmental_risk_level': environmental_data.get('environmental_risk_level', 'Unknown'),
                'environmental_recommendation': environmental_data.get('environmental_recommendation', 'Standard Phase I ESA'),
                
                # Cost Analysis
                'regional_market': cost_data.get('region', 'Unknown'),
                'construction_cost_per_unit': cost_data.get('total_cost_per_unit', 0),
                'cost_variance_percentage': cost_data.get('cost_variance_percentage', 0),
                'total_project_cost_60_units': cost_data.get('total_project_cost', 0),
                
                # School Amenities
                'school_amenity_score': amenities_data.get('Total_Amenity_Score', 0),
                'school_rating': amenities_data.get('Overall_Rating', 'Unknown'),
                'schools_within_3_miles': amenities_data.get('Schools_Within_3_Miles', 0),
                'elementary_schools': amenities_data.get('Elementary_Schools', 0),
                'middle_schools': amenities_data.get('Middle_Schools', 0),
                'high_schools': amenities_data.get('High_Schools', 0),
                'nearest_elementary_distance': amenities_data.get('Nearest_Elementary_Distance', None),
                'nearest_high_school_distance': amenities_data.get('Nearest_High_School_Distance', None),
                
                # Overall Site Assessment
                'data_completeness': self.calculate_data_completeness(flood_data, competition_data, environmental_data, cost_data, amenities_data),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            integrated_sites.append(integrated_site)
        
        return integrated_sites
    
    def calculate_data_completeness(self, flood_data, competition_data, environmental_data, cost_data, amenities_data):
        """Calculate what percentage of analyses are complete for this site"""
        factors = [
            bool(flood_data),
            bool(competition_data),
            bool(environmental_data),
            bool(cost_data),
            bool(amenities_data)
        ]
        
        completeness = sum(factors) / len(factors) * 100
        return f"{completeness:.0f}%"
    
    def calculate_overall_site_rankings(self, integrated_sites):
        """Calculate overall site rankings based on all factors"""
        print("🏆 CALCULATING OVERALL SITE RANKINGS")
        
        # Scoring weights for different factors
        weights = {
            'competition_suitable': 30,  # 30 points for 9% credit eligibility
            'basis_boost': 20,           # 20 points for 130% basis boost
            'low_flood_risk': 15,        # 15 points for minimal flood risk
            'low_environmental_risk': 10, # 10 points for clean environmental screen
            'cost_efficiency': 15,       # 15 points for below-average costs
            'school_amenities': 10       # 10 points for good school access
        }
        
        for site in integrated_sites:
            total_score = 0
            scoring_detail = {}
            
            # Competition scoring (9% vs 4%)
            if site['competition_recommendation'] == '9% SUITABLE':
                comp_score = weights['competition_suitable']
            else:
                comp_score = 10  # Partial credit for 4% eligibility
            
            scoring_detail['competition'] = comp_score
            total_score += comp_score
            
            # Basis boost scoring
            if site['basis_boost_eligible'] == 'YES':
                basis_score = weights['basis_boost']
            else:
                basis_score = 0
            
            scoring_detail['basis_boost'] = basis_score
            total_score += basis_score
            
            # Flood risk scoring
            flood_risk = site['flood_risk_level']
            if flood_risk in ['LOW', 'MINIMAL']:
                flood_score = weights['low_flood_risk']
            elif flood_risk == 'MEDIUM':
                flood_score = 10
            elif flood_risk == 'HIGH':
                flood_score = 5
            else:
                flood_score = 0
            
            scoring_detail['flood_risk'] = flood_score
            total_score += flood_score
            
            # Environmental risk scoring
            env_risk = site['environmental_risk_level']
            if env_risk == 'LOW':
                env_score = weights['low_environmental_risk']
            elif env_risk == 'LOW-MEDIUM':
                env_score = 7
            elif env_risk == 'MEDIUM':
                env_score = 5
            else:
                env_score = 0
            
            scoring_detail['environmental'] = env_score
            total_score += env_score
            
            # Cost efficiency scoring
            cost_variance = site['cost_variance_percentage']
            if cost_variance < 0:  # Below baseline
                cost_score = weights['cost_efficiency']
            elif cost_variance < 10:  # Moderate premium
                cost_score = 10
            elif cost_variance < 20:  # High premium
                cost_score = 5
            else:  # Very high premium
                cost_score = 0
            
            scoring_detail['cost_efficiency'] = cost_score
            total_score += cost_score
            
            # School amenities scoring
            school_score_raw = site['school_amenity_score']
            if school_score_raw >= 60:
                school_score = weights['school_amenities']
            elif school_score_raw >= 40:
                school_score = 7
            elif school_score_raw >= 20:
                school_score = 4
            else:
                school_score = 0
            
            scoring_detail['school_amenities'] = school_score
            total_score += school_score
            
            # Overall assessment
            max_possible_score = sum(weights.values())
            score_percentage = (total_score / max_possible_score) * 100
            
            if score_percentage >= 80:
                overall_rating = 'EXCELLENT'
            elif score_percentage >= 65:
                overall_rating = 'GOOD'
            elif score_percentage >= 50:
                overall_rating = 'FAIR'
            else:
                overall_rating = 'POOR'
            
            # Update site with scoring
            site['overall_score'] = total_score
            site['overall_score_percentage'] = round(score_percentage, 1)
            site['overall_rating'] = overall_rating
            site['scoring_detail'] = scoring_detail
            site['max_possible_score'] = max_possible_score
        
        # Sort by overall score
        integrated_sites.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add rankings
        for rank, site in enumerate(integrated_sites, 1):
            site['overall_rank'] = rank
        
        return integrated_sites
    
    def create_final_integrated_analysis(self):
        """Create the final comprehensive integrated analysis"""
        print("🚀 CREATING FINAL INTEGRATED D'MARCO ANALYSIS")
        
        # Load all data
        data = self.load_all_analyses()
        
        # Create integrated dataset
        integrated_sites = self.create_integrated_dataset(data)
        
        # Calculate overall rankings
        ranked_sites = self.calculate_overall_site_rankings(integrated_sites)
        
        # Create comprehensive Excel export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = self.base_dir / f"DMarco_FINAL_INTEGRATED_Analysis_{timestamp}.xlsx"
        
        df = pd.DataFrame(ranked_sites)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main integrated analysis
            df.to_excel(writer, sheet_name='Integrated_Analysis', index=False)
            
            # Top 10 sites
            top_10 = df.head(10)
            top_10.to_excel(writer, sheet_name='Top_10_Sites', index=False)
            
            # Sites suitable for 9% credits
            nine_percent_sites = df[df['competition_recommendation'] == '9% SUITABLE']
            nine_percent_sites.to_excel(writer, sheet_name='9_Percent_Suitable', index=False)
            
            # Excellent rated sites
            excellent_sites = df[df['overall_rating'] == 'EXCELLENT']
            if not excellent_sites.empty:
                excellent_sites.to_excel(writer, sheet_name='Excellent_Sites', index=False)
            
            # Regional summary
            regional_summary = df.groupby('regional_market').agg({
                'site_index': 'count',
                'overall_score': 'mean',
                'construction_cost_per_unit': 'mean',
                'school_amenity_score': 'mean'
            }).round(1)
            regional_summary.columns = ['Site_Count', 'Avg_Overall_Score', 'Avg_Cost_Per_Unit', 'Avg_School_Score']
            regional_summary.to_excel(writer, sheet_name='Regional_Summary')
            
            # Executive summary
            summary_data = [
                ['D\'MARCO INTEGRATED ANALYSIS SUMMARY', ''],
                ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M CST')],
                ['Total Sites Analyzed', len(ranked_sites)],
                ['Data Completeness', f"{sum(1 for s in ranked_sites if s['data_completeness'] == '100%')}/{len(ranked_sites)} sites complete"],
                ['', ''],
                ['TOP SITE RECOMMENDATIONS', ''],
                ['#1 Ranked Site', f"Site {ranked_sites[0]['site_index']} ({ranked_sites[0]['county']}) - {ranked_sites[0]['overall_score_percentage']:.1f}%"],
                ['#2 Ranked Site', f"Site {ranked_sites[1]['site_index']} ({ranked_sites[1]['county']}) - {ranked_sites[1]['overall_score_percentage']:.1f}%"],
                ['#3 Ranked Site', f"Site {ranked_sites[2]['site_index']} ({ranked_sites[2]['county']}) - {ranked_sites[2]['overall_score_percentage']:.1f}%"],
                ['', ''],
                ['LIHTC CREDIT ANALYSIS', ''],
                ['9% Credit Suitable Sites', len(nine_percent_sites)],
                ['4% Credit Only Sites', len(df[df['competition_recommendation'] == '4% ONLY'])],
                ['130% Basis Boost Eligible', len(df[df['basis_boost_eligible'] == 'YES'])],
                ['', ''],
                ['RISK ASSESSMENT', ''],
                ['Low Flood Risk Sites', len(df[df['flood_risk_level'].isin(['LOW', 'MINIMAL'])])],
                ['High Flood Risk Sites', len(df[df['flood_risk_level'] == 'HIGH'])],
                ['Low Environmental Risk', len(df[df['environmental_risk_level'] == 'LOW'])],
                ['', ''],
                ['COST ANALYSIS', ''],
                ['Average Cost Variance', f"{df['cost_variance_percentage'].mean():.1f}%"],
                ['Most Cost-Efficient Region', df.loc[df['cost_variance_percentage'].idxmin(), 'regional_market']],
                ['Most Expensive Region', df.loc[df['cost_variance_percentage'].idxmax(), 'regional_market']],
                ['', ''],
                ['AMENITIES ANALYSIS', ''],
                ['Average School Score', f"{df['school_amenity_score'].mean():.1f}/75"],
                ['Sites with Excellent School Access', len(df[df['school_rating'] == 'EXCELLENT'])],
                ['Sites with Complete School Levels', len(df[(df['elementary_schools'] > 0) & (df['middle_schools'] > 0) & (df['high_schools'] > 0)])]
            ]
            
            summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # Save detailed JSON
        json_file = self.base_dir / f"DMarco_FINAL_INTEGRATED_Analysis_{timestamp}.json"
        
        comprehensive_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'FINAL_INTEGRATED_DMARCO_ANALYSIS',
            'data_sources_integrated': list(self.latest_files.keys()),
            'methodology': {
                'scoring_weights': {
                    'competition_suitable': 30,
                    'basis_boost': 20,
                    'low_flood_risk': 15,
                    'cost_efficiency': 15,
                    'low_environmental_risk': 10,
                    'school_amenities': 10
                },
                'max_possible_score': 100
            },
            'integrated_sites': ranked_sites
        }
        
        with open(json_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        # Print summary
        print(f"\n🏆 FINAL INTEGRATED ANALYSIS COMPLETE!")
        print(f"✅ Sites analyzed: {len(ranked_sites)}")
        print(f"🥇 Top site: Site {ranked_sites[0]['site_index']} ({ranked_sites[0]['overall_score_percentage']:.1f}%)")
        print(f"📊 Rating distribution: {pd.Series([s['overall_rating'] for s in ranked_sites]).value_counts().to_dict()}")
        print(f"💰 9% credit suitable: {len(nine_percent_sites)}/{len(ranked_sites)} sites")
        print(f"🎯 130% basis boost eligible: {len(df[df['basis_boost_eligible'] == 'YES'])}/{len(ranked_sites)} sites")
        
        print(f"\n💾 Final deliverables:")
        print(f"   • Comprehensive Excel: {excel_file.name}")
        print(f"   • Detailed JSON: {json_file.name}")
        
        return comprehensive_report, excel_file

if __name__ == "__main__":
    analyzer = FinalIntegratedAnalyzer()
    report, excel_file = analyzer.create_final_integrated_analysis()