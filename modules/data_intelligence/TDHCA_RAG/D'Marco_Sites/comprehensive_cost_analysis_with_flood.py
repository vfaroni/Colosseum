#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE Cost Analysis with Flood Integration
WINGMAN Agent - Complete Cost Framework Integration

INTEGRATION POINTS:
1. Regional cost modifiers (construction costs)
2. Flood zone insurance costs (operational impact)  
3. Environmental screening costs (Phase I ESA requirements)
4. Competition analysis impact (9% vs 4% financing costs)

FINAL DELIVERABLE: Excel with complete cost analysis for all 38 D'Marco sites
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveCostAnalyzer:
    """Complete cost analysis integrating all factors"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Find latest flood analysis file
        flood_files = list(self.base_dir.glob("dmarco_sites_FINAL_flood_analysis_*.json"))
        if flood_files:
            self.flood_data_file = max(flood_files, key=lambda x: x.stat().st_mtime)
        else:
            # Fallback to complete final analysis
            self.flood_data_file = self.base_dir / "complete_final_analysis.py"
        
        # Find latest competition analysis
        competition_files = list(self.base_dir.glob("DMarco_CORRECTED_Competition_Analysis_*.json"))
        if competition_files:
            self.competition_file = max(competition_files, key=lambda x: x.stat().st_mtime)
        
        # Regional cost multipliers (from previous analysis)
        self.REGIONAL_COST_MULTIPLIERS = {
            'Houston_Metro': {'construction_multiplier': 1.12, 'regulatory_multiplier': 1.20},
            'Dallas_Metro': {'construction_multiplier': 1.18, 'regulatory_multiplier': 1.15},
            'Austin_Metro': {'construction_multiplier': 1.14, 'regulatory_multiplier': 1.25},
            'San_Antonio_Metro': {'construction_multiplier': 1.06, 'regulatory_multiplier': 1.10},
            'East_Texas_Rural': {'construction_multiplier': 0.92, 'regulatory_multiplier': 0.85},
            'Rural_Baseline': {'construction_multiplier': 1.00, 'regulatory_multiplier': 1.00}
        }
        
        # Flood insurance annual costs per unit
        self.FLOOD_INSURANCE_COSTS = {
            'X': 0,
            'AE': 1200,
            'A': 1400,
            'VE': 2500,
            'AO': 800,
            'NOT_IN_FLOODPLAIN': 0
        }
        
        # Environmental screening costs
        self.ENVIRONMENTAL_COSTS = {
            'LOW': 5000,          # Standard Phase I ESA
            'LOW-MEDIUM': 8000,   # Phase I with additional review
            'MEDIUM': 12000,      # Enhanced Phase I ESA
            'HIGH': 20000,        # Phase I + vapor assessment
            'VERY_HIGH': 35000    # Phase I + II + remediation planning
        }
        
        # Financing cost differences (9% vs 4% credits)
        self.FINANCING_IMPACT = {
            '9_PERCENT_SUITABLE': {
                'financing_cost_per_unit': 8000,
                'description': 'Competitive 9% credits - lower debt burden'
            },
            '4_PERCENT_ONLY': {
                'financing_cost_per_unit': 15000,
                'description': '4% credits with bonds - higher debt service'
            }
        }
        
        # Base development costs (per unit for 60-unit project)
        self.BASE_COSTS = {
            'construction_base': 135000,
            'soft_costs_base': 25000,
            'developer_fee': 18000,
            'contingency': 8000
        }
    
    def load_comprehensive_data(self):
        """Load all analysis data sources"""
        print("📊 LOADING COMPREHENSIVE ANALYSIS DATA")
        
        # Load flood analysis (with correct zones)
        try:
            with open(self.flood_data_file, 'r') as f:
                flood_data = json.load(f)
            print(f"✅ Loaded flood data from {self.flood_data_file.name}")
        except:
            print("❌ Could not load flood data - using fallback")
            flood_data = []
        
        # Load competition analysis
        try:
            with open(self.competition_file, 'r') as f:
                competition_data = json.load(f)
            print(f"✅ Loaded competition data from {self.competition_file.name}")
        except:
            print("❌ Could not load competition data")
            competition_data = {'competition_analysis': []}
        
        # Load environmental analysis
        env_files = list(self.base_dir.glob("dmarco_sites_ENVIRONMENTAL_FIXED_*.json"))
        if env_files:
            env_file = max(env_files, key=lambda x: x.stat().st_mtime)
            with open(env_file, 'r') as f:
                environmental_data = json.load(f)
            print(f"✅ Loaded environmental data from {env_file.name}")
        else:
            environmental_data = []
        
        return flood_data, competition_data, environmental_data
    
    def determine_regional_market(self, county_name):
        """Determine regional market from county"""
        county_clean = county_name.replace(' County', '').replace('County ', '').strip()
        
        region_mapping = {
            'Harris': 'Houston_Metro',
            'Dallas': 'Dallas_Metro', 
            'Collin': 'Dallas_Metro',
            'Bexar': 'San_Antonio_Metro',
            'Guadalupe': 'San_Antonio_Metro',
            'Orange': 'East_Texas_Rural',
            'Henderson': 'East_Texas_Rural',
            'Kaufman': 'Rural_Baseline'
        }
        
        return region_mapping.get(county_clean, 'Rural_Baseline')
    
    def calculate_comprehensive_costs(self, site, flood_site, competition_site, environmental_site):
        """Calculate all cost factors for a site"""
        
        # Basic site info
        site_index = site['site_index']
        county = site.get('census_county', 'Unknown')
        region = self.determine_regional_market(county)
        
        # Get flood zone (from flood analysis or fallback)
        flood_zone = 'X'  # Default
        if flood_site:
            flood_zone = flood_site.get('fema_flood_zone', 'X')
        elif 'fema_flood_zone' in site:
            flood_zone = site['fema_flood_zone']
        
        # Get competition status
        competition_suitable = True
        if competition_site:
            competition_suitable = not competition_site.get('fatal_flaw_9_percent', True)
        
        # Get environmental risk
        environmental_risk = 'LOW'
        if environmental_site:
            environmental_risk = environmental_site.get('environmental_risk_level', 'LOW')
        
        # Calculate cost components
        
        # 1. Construction costs (regional adjustment)
        regional_multiplier = self.REGIONAL_COST_MULTIPLIERS[region]['construction_multiplier']
        base_construction = sum(self.BASE_COSTS.values())
        adjusted_construction = base_construction * regional_multiplier
        
        # 2. Flood insurance (annual operating cost)
        flood_insurance_annual = self.FLOOD_INSURANCE_COSTS.get(flood_zone, 0)
        flood_insurance_present_value = flood_insurance_annual * 15  # 15-year present value
        
        # 3. Environmental screening costs (one-time)
        environmental_cost = self.ENVIRONMENTAL_COSTS.get(environmental_risk, 5000)
        
        # 4. Financing costs (9% vs 4% impact)
        financing_type = '9_PERCENT_SUITABLE' if competition_suitable else '4_PERCENT_ONLY'
        financing_cost = self.FINANCING_IMPACT[financing_type]['financing_cost_per_unit']
        
        # Total adjusted cost per unit
        total_cost_per_unit = (
            adjusted_construction +
            flood_insurance_present_value +
            (environmental_cost / 60) +  # Spread over 60 units
            financing_cost
        )
        
        # Cost variance from baseline
        baseline_cost = sum(self.BASE_COSTS.values()) + self.FINANCING_IMPACT['9_PERCENT_SUITABLE']['financing_cost_per_unit']
        cost_variance = total_cost_per_unit - baseline_cost
        cost_variance_percentage = (cost_variance / baseline_cost) * 100
        
        return {
            'site_index': site_index,
            'county': county,
            'region': region,
            'flood_zone': flood_zone,
            'environmental_risk': environmental_risk,
            'competition_suitable_9_percent': competition_suitable,
            'financing_type': financing_type,
            
            # Cost breakdown
            'base_construction_cost': base_construction,
            'adjusted_construction_cost': round(adjusted_construction, 0),
            'flood_insurance_pv': round(flood_insurance_present_value, 0),
            'environmental_screening_cost': environmental_cost,
            'financing_cost_per_unit': financing_cost,
            'total_cost_per_unit': round(total_cost_per_unit, 0),
            
            # Cost analysis
            'cost_variance_per_unit': round(cost_variance, 0),
            'cost_variance_percentage': round(cost_variance_percentage, 1),
            'regional_multiplier': regional_multiplier,
            
            # 60-unit project totals
            'total_project_cost': round(total_cost_per_unit * 60, 0),
            'cost_variance_total_project': round(cost_variance * 60, 0)
        }
    
    def create_comprehensive_cost_analysis(self):
        """Create complete comprehensive cost analysis"""
        print("🚀 CREATING COMPREHENSIVE COST ANALYSIS")
        
        # Load all data sources
        flood_data, competition_data, environmental_data = self.load_comprehensive_data()
        
        # Create lookup dictionaries
        flood_lookup = {site['site_index']: site for site in flood_data} if flood_data else {}
        competition_lookup = {analysis['site_index']: analysis for analysis in competition_data.get('competition_analysis', [])}
        environmental_lookup = {site['site_index']: site for site in environmental_data} if environmental_data else {}
        
        # Load base site data
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Analyzing costs for {len(sites_data)} sites...")
        
        # Analyze each site
        comprehensive_analyses = []
        
        for site in sites_data:
            site_index = site['site_index']
            
            # Get corresponding analyses
            flood_site = flood_lookup.get(site_index)
            competition_site = competition_lookup.get(site_index)
            environmental_site = environmental_lookup.get(site_index)
            
            # Calculate comprehensive costs
            cost_analysis = self.calculate_comprehensive_costs(
                site, flood_site, competition_site, environmental_site
            )
            
            comprehensive_analyses.append(cost_analysis)
            
            print(f"  Site {site_index}: {cost_analysis['region']} region, {cost_analysis['total_cost_per_unit']:,}/unit ({cost_analysis['cost_variance_percentage']:+.1f}%)")
        
        # Create Excel export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        df = pd.DataFrame(comprehensive_analyses)
        
        excel_path = self.base_dir / f"DMarco_COMPREHENSIVE_Cost_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main cost analysis
            df.to_excel(writer, sheet_name='Cost_Analysis', index=False)
            
            # Summary by region
            regional_summary = df.groupby('region').agg({
                'site_index': 'count',
                'cost_variance_percentage': 'mean',
                'total_cost_per_unit': 'mean',
                'flood_insurance_pv': 'mean'
            }).round(1)
            regional_summary.columns = ['Site_Count', 'Avg_Cost_Variance_%', 'Avg_Cost_Per_Unit', 'Avg_Flood_Insurance']
            regional_summary.to_excel(writer, sheet_name='Regional_Summary')
            
            # High-cost sites (>+15% variance)
            high_cost = df[df['cost_variance_percentage'] > 15]
            if not high_cost.empty:
                high_cost.to_excel(writer, sheet_name='High_Cost_Sites', index=False)
            
            # Low-cost opportunities (<0% variance)
            low_cost = df[df['cost_variance_percentage'] < 0]
            if not low_cost.empty:
                low_cost.to_excel(writer, sheet_name='Low_Cost_Opportunities', index=False)
        
        # Create summary statistics
        stats = {
            'total_sites': len(comprehensive_analyses),
            'average_cost_variance': round(df['cost_variance_percentage'].mean(), 1),
            'cost_range': {
                'lowest': {
                    'site_index': df.loc[df['cost_variance_percentage'].idxmin(), 'site_index'],
                    'variance': df['cost_variance_percentage'].min()
                },
                'highest': {
                    'site_index': df.loc[df['cost_variance_percentage'].idxmax(), 'site_index'],
                    'variance': df['cost_variance_percentage'].max()
                }
            },
            'regional_distribution': df['region'].value_counts().to_dict(),
            'financing_split': {
                '9_percent_suitable': len(df[df['competition_suitable_9_percent'] == True]),
                '4_percent_only': len(df[df['competition_suitable_9_percent'] == False])
            }
        }
        
        print(f"\n📊 COMPREHENSIVE COST ANALYSIS COMPLETE!")
        print(f"✅ Sites analyzed: {stats['total_sites']}")
        print(f"💰 Average cost variance: {stats['average_cost_variance']:+.1f}%")
        print(f"📈 Cost range: {stats['cost_range']['lowest']['variance']:+.1f}% to {stats['cost_range']['highest']['variance']:+.1f}%")
        print(f"🏢 Regional distribution: {stats['regional_distribution']}")
        print(f"💳 Financing split: {stats['financing_split']['9_percent_suitable']} sites 9%, {stats['financing_split']['4_percent_only']} sites 4%")
        
        print(f"\n💾 Excel created: {excel_path.name}")
        
        return stats, excel_path

if __name__ == "__main__":
    analyzer = ComprehensiveCostAnalyzer()
    results, excel_file = analyzer.create_comprehensive_cost_analysis()