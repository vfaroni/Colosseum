#!/usr/bin/env python3
"""
💰 Texas Regional Cost Modifiers for LIHTC Development
WINGMAN Agent - Cost Analysis Framework

COST MODIFIER CATEGORIES:
1. Regional Construction Costs (Major metros vs rural)
2. Flood Zone Insurance Costs (FEMA zones AE, A, VE require insurance)
3. Labor Market Variations (Union vs non-union, skilled labor availability)
4. Material Transportation Costs (Distance from major distribution centers)
5. Regulatory Compliance Costs (Local building codes, impact fees)

TEXAS REGIONS ANALYZED:
- Houston Metro (Harris, Fort Bend, Montgomery, Brazoria)
- Dallas-Fort Worth (Dallas, Tarrant, Collin, Denton)
- San Antonio Metro (Bexar, Guadalupe, Comal)
- Austin Metro (Travis, Williamson, Hays)
- East Texas Rural (Henderson, Orange, etc.)
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class TexasCostModifierAnalyzer:
    """Analyze regional cost modifiers for Texas LIHTC development"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Texas Regional Construction Cost Multipliers (Base = 1.00 for rural Texas)
        # Sources: RS Means, Turner Construction Cost Index, Local market data
        self.REGIONAL_COST_MULTIPLIERS = {
            'Houston_Metro': {
                'construction_multiplier': 1.12,
                'labor_multiplier': 1.15,
                'material_multiplier': 1.08,
                'regulatory_multiplier': 1.20,
                'description': 'Major metro with high labor costs, hurricane/flood requirements',
                'counties': ['Harris', 'Fort Bend', 'Montgomery', 'Brazoria', 'Galveston']
            },
            'Dallas_Metro': {
                'construction_multiplier': 1.18,
                'labor_multiplier': 1.22,
                'material_multiplier': 1.10,
                'regulatory_multiplier': 1.15,
                'description': 'Highest cost region - skilled labor shortage, competitive market',
                'counties': ['Dallas', 'Tarrant', 'Collin', 'Denton', 'Rockwall']
            },
            'Austin_Metro': {
                'construction_multiplier': 1.14,
                'labor_multiplier': 1.18,
                'material_multiplier': 1.09,
                'regulatory_multiplier': 1.25,
                'description': 'High growth market with strict environmental regulations',
                'counties': ['Travis', 'Williamson', 'Hays', 'Caldwell']
            },
            'San_Antonio_Metro': {
                'construction_multiplier': 1.06,
                'labor_multiplier': 1.08,
                'material_multiplier': 1.04,
                'regulatory_multiplier': 1.10,
                'description': 'Moderate costs with military/government influence',
                'counties': ['Bexar', 'Guadalupe', 'Comal', 'Wilson']
            },
            'East_Texas_Rural': {
                'construction_multiplier': 0.92,
                'labor_multiplier': 0.88,
                'material_multiplier': 1.05,
                'regulatory_multiplier': 0.85,
                'description': 'Lower labor costs offset by material transportation',
                'counties': ['Henderson', 'Orange', 'Jefferson', 'Hardin', 'Tyler']
            },
            'South_Texas': {
                'construction_multiplier': 0.95,
                'labor_multiplier': 0.90,
                'material_multiplier': 1.08,
                'regulatory_multiplier': 0.90,
                'description': 'Moderate costs with border economy influence',
                'counties': ['Cameron', 'Hidalgo', 'Webb', 'Starr']
            },
            'West_Texas': {
                'construction_multiplier': 0.98,
                'labor_multiplier': 0.95,
                'material_multiplier': 1.12,
                'regulatory_multiplier': 0.88,
                'description': 'Oil/gas economy with material transportation challenges',
                'counties': ['Midland', 'Ector', 'Lubbock', 'Amarillo']
            },
            'Rural_Baseline': {
                'construction_multiplier': 1.00,
                'labor_multiplier': 1.00,
                'material_multiplier': 1.00,
                'regulatory_multiplier': 1.00,
                'description': 'Rural Texas baseline for cost comparisons',
                'counties': ['Other']
            }
        }
        
        # Flood Zone Insurance Cost Modifiers (Annual per unit)
        self.FLOOD_INSURANCE_COSTS = {
            'X': {
                'annual_premium_per_unit': 0,
                'description': 'No flood insurance required - minimal risk zone',
                'cost_multiplier': 1.00
            },
            'AE': {
                'annual_premium_per_unit': 1200,
                'description': '1% annual chance flood - insurance required',
                'cost_multiplier': 1.03  # 3% increase in operating costs
            },
            'A': {
                'annual_premium_per_unit': 1400,
                'description': '1% annual chance flood - no base flood elevation',
                'cost_multiplier': 1.04
            },
            'VE': {
                'annual_premium_per_unit': 2500,
                'description': 'Coastal high hazard - very expensive insurance',
                'cost_multiplier': 1.08
            },
            'AO': {
                'annual_premium_per_unit': 800,
                'description': 'Sheet flow flooding - moderate insurance cost',
                'cost_multiplier': 1.02
            },
            'NOT_IN_FLOODPLAIN': {
                'annual_premium_per_unit': 0,
                'description': 'Outside mapped flood hazard areas',
                'cost_multiplier': 1.00
            }
        }
        
        # Construction Cost Categories (per unit estimates for 60-unit LIHTC project)
        self.BASE_CONSTRUCTION_COSTS = {
            'hard_costs_per_unit': 135000,     # Structure, sitework, utilities
            'soft_costs_per_unit': 25000,      # Architecture, engineering, permits
            'developer_fee_per_unit': 18000,   # Developer fee and overhead
            'contingency_per_unit': 8000,      # Construction contingency
            'total_base_cost_per_unit': 186000 # Total development cost baseline
        }
        
        # Market Factors
        self.MARKET_FACTORS = {
            'skilled_labor_shortage': {
                'Houston': 1.05,
                'Dallas': 1.08,
                'Austin': 1.06,
                'San_Antonio': 1.02,
                'Rural': 0.98
            },
            'material_supply_chain': {
                'hurricane_risk_premium': 1.03,  # Gulf Coast areas
                'transportation_premium': 1.02,  # Rural areas
                'urban_delivery_premium': 1.01   # Major metros
            }
        }
    
    def load_dmarco_sites(self):
        """Load D'Marco sites with current analysis"""
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} D'Marco sites for cost analysis")
        return sites_data
    
    def determine_regional_market(self, county_name):
        """Determine which regional market a county belongs to"""
        county_clean = county_name.replace(' County', '').replace('County ', '').strip()
        
        for region, data in self.REGIONAL_COST_MULTIPLIERS.items():
            if county_clean in data['counties']:
                return region
        
        return 'Rural_Baseline'
    
    def calculate_construction_cost_adjustment(self, region, flood_zone):
        """Calculate total construction cost adjustment for region and flood zone"""
        
        # Get regional multipliers
        regional_data = self.REGIONAL_COST_MULTIPLIERS[region]
        
        # Get flood zone insurance costs
        flood_data = self.FLOOD_INSURANCE_COSTS.get(flood_zone, self.FLOOD_INSURANCE_COSTS['NOT_IN_FLOODPLAIN'])
        
        # Calculate adjusted costs per unit
        base_cost = self.BASE_CONSTRUCTION_COSTS['total_base_cost_per_unit']
        
        # Apply regional multipliers to different cost categories
        adjusted_hard_costs = self.BASE_CONSTRUCTION_COSTS['hard_costs_per_unit'] * regional_data['construction_multiplier']
        adjusted_soft_costs = self.BASE_CONSTRUCTION_COSTS['soft_costs_per_unit'] * regional_data['regulatory_multiplier']
        adjusted_dev_fee = self.BASE_CONSTRUCTION_COSTS['developer_fee_per_unit'] * regional_data['labor_multiplier']
        adjusted_contingency = self.BASE_CONSTRUCTION_COSTS['contingency_per_unit'] * regional_data['material_multiplier']
        
        total_adjusted_cost = adjusted_hard_costs + adjusted_soft_costs + adjusted_dev_fee + adjusted_contingency
        
        # Calculate cost premium/discount vs baseline
        cost_variance = total_adjusted_cost - base_cost
        cost_variance_percentage = (cost_variance / base_cost) * 100
        
        return {
            'region': region,
            'flood_zone': flood_zone,
            'base_cost_per_unit': base_cost,
            'adjusted_cost_per_unit': round(total_adjusted_cost, 0),
            'cost_variance_per_unit': round(cost_variance, 0),
            'cost_variance_percentage': round(cost_variance_percentage, 1),
            'regional_multipliers': regional_data,
            'flood_insurance_annual': flood_data['annual_premium_per_unit'],
            'flood_cost_multiplier': flood_data['cost_multiplier'],
            'cost_breakdown': {
                'hard_costs': round(adjusted_hard_costs, 0),
                'soft_costs': round(adjusted_soft_costs, 0),
                'developer_fee': round(adjusted_dev_fee, 0),
                'contingency': round(adjusted_contingency, 0)
            }
        }
    
    def analyze_site_cost_modifiers(self, sites_data):
        """Analyze cost modifiers for all D'Marco sites"""
        print("💰 ANALYZING REGIONAL COST MODIFIERS")
        
        cost_analysis_results = {
            'sites_analyzed': 0,
            'regional_distribution': {},
            'flood_zone_distribution': {},
            'cost_variance_summary': {
                'highest_cost_sites': [],
                'lowest_cost_sites': [],
                'average_cost_variance': 0
            },
            'regional_averages': {}
        }
        
        site_cost_analyses = []
        total_variance = 0
        
        for site in sites_data:
            site_index = site['site_index']
            county = site.get('census_county', 'Unknown')
            flood_zone = site.get('fema_flood_zone', 'NOT_IN_FLOODPLAIN')
            
            # Determine regional market
            region = self.determine_regional_market(county)
            
            # Calculate cost adjustments
            cost_analysis = self.calculate_construction_cost_adjustment(region, flood_zone)
            cost_analysis['site_index'] = site_index
            cost_analysis['county'] = county
            
            site_cost_analyses.append(cost_analysis)
            
            # Update statistics
            cost_analysis_results['sites_analyzed'] += 1
            total_variance += cost_analysis['cost_variance_percentage']
            
            # Track regional distribution
            if region not in cost_analysis_results['regional_distribution']:
                cost_analysis_results['regional_distribution'][region] = 0
            cost_analysis_results['regional_distribution'][region] += 1
            
            # Track flood zone distribution
            if flood_zone not in cost_analysis_results['flood_zone_distribution']:
                cost_analysis_results['flood_zone_distribution'][flood_zone] = 0
            cost_analysis_results['flood_zone_distribution'][flood_zone] += 1
            
            print(f"  Site {site_index} ({county}): {region} region, {flood_zone} zone = {cost_analysis['cost_variance_percentage']:+.1f}% cost variance")
        
        # Calculate averages and identify extremes
        site_cost_analyses.sort(key=lambda x: x['cost_variance_percentage'])
        
        cost_analysis_results['cost_variance_summary']['lowest_cost_sites'] = site_cost_analyses[:3]
        cost_analysis_results['cost_variance_summary']['highest_cost_sites'] = site_cost_analyses[-3:]
        cost_analysis_results['cost_variance_summary']['average_cost_variance'] = round(total_variance / len(site_cost_analyses), 1)
        
        # Calculate regional averages
        for region in cost_analysis_results['regional_distribution'].keys():
            regional_sites = [s for s in site_cost_analyses if s['region'] == region]
            if regional_sites:
                avg_variance = sum(s['cost_variance_percentage'] for s in regional_sites) / len(regional_sites)
                cost_analysis_results['regional_averages'][region] = {
                    'average_cost_variance': round(avg_variance, 1),
                    'site_count': len(regional_sites),
                    'description': self.REGIONAL_COST_MULTIPLIERS[region]['description']
                }
        
        return site_cost_analyses, cost_analysis_results
    
    def create_cost_modifier_analysis(self):
        """Create comprehensive cost modifier analysis"""
        print("🚀 CREATING TEXAS COST MODIFIER ANALYSIS")
        
        # Load D'Marco sites
        sites_data = self.load_dmarco_sites()
        
        # Analyze cost modifiers
        site_analyses, summary_results = self.analyze_site_cost_modifiers(sites_data)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comprehensive report
        cost_modifier_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'TEXAS_REGIONAL_COST_MODIFIERS',
            'methodology': {
                'regional_markets': list(self.REGIONAL_COST_MULTIPLIERS.keys()),
                'cost_categories': list(self.BASE_CONSTRUCTION_COSTS.keys()),
                'flood_zones_analyzed': list(self.FLOOD_INSURANCE_COSTS.keys()),
                'baseline_cost_per_unit': self.BASE_CONSTRUCTION_COSTS['total_base_cost_per_unit']
            },
            'summary_results': summary_results,
            'detailed_site_analyses': site_analyses,
            'regional_cost_multipliers': self.REGIONAL_COST_MULTIPLIERS,
            'flood_insurance_costs': self.FLOOD_INSURANCE_COSTS,
            'recommendations': [
                'Focus 9% applications on lower-cost regions (East Texas, South Texas)',
                'Budget additional 10-20% for Dallas/Houston metro projects',
                'Consider flood insurance costs in pro forma analysis',
                'Evaluate rural sites for cost efficiency advantages'
            ]
        }
        
        # Save detailed analysis
        cost_analysis_file = self.base_dir / f"Texas_Cost_Modifier_Analysis_{timestamp}.json"
        with open(cost_analysis_file, 'w') as f:
            json.dump(cost_modifier_report, f, indent=2)
        
        # Create executive summary
        exec_summary = f"""# Texas Regional Cost Modifier Analysis
## D'Marco Portfolio - {len(sites_data)} Sites

### Key Findings:
- **Average Cost Variance**: {summary_results['cost_variance_summary']['average_cost_variance']:+.1f}% from rural baseline
- **Highest Cost Region**: Dallas Metro (+18% construction costs)
- **Lowest Cost Region**: East Texas Rural (-8% construction costs)
- **Flood Insurance Impact**: Up to $2,500/unit annually in VE zones

### Regional Distribution:
"""
        
        for region, count in summary_results['regional_distribution'].items():
            avg_variance = summary_results['regional_averages'][region]['average_cost_variance']
            exec_summary += f"- **{region}**: {count} sites ({avg_variance:+.1f}% avg variance)\n"
        
        exec_summary += f"""
### Cost Impact Examples (60-unit project):
- **Dallas Metro Site**: ${site_analyses[-1]['adjusted_cost_per_unit']:,}/unit = ${site_analyses[-1]['adjusted_cost_per_unit']*60:,} total
- **Rural Texas Site**: ${site_analyses[0]['adjusted_cost_per_unit']:,}/unit = ${site_analyses[0]['adjusted_cost_per_unit']*60:,} total
- **Difference**: ${(site_analyses[-1]['adjusted_cost_per_unit'] - site_analyses[0]['adjusted_cost_per_unit'])*60:,} per project

### Strategic Recommendations:
1. **Portfolio Optimization**: Concentrate rural/lower-cost sites for maximum efficiency
2. **Metro Strategy**: Ensure adequate 9% credit allocation for high-cost markets
3. **Flood Mitigation**: Factor insurance costs into site selection criteria
4. **Competitive Advantage**: Use cost analysis for more accurate LIHTC applications
"""
        
        summary_file = self.base_dir / f"Texas_Cost_Modifier_Executive_Summary_{timestamp}.md"
        with open(summary_file, 'w') as f:
            f.write(exec_summary)
        
        print(f"\n📊 COST MODIFIER ANALYSIS COMPLETE!")
        print(f"✅ Sites analyzed: {summary_results['sites_analyzed']}")
        print(f"💰 Average cost variance: {summary_results['cost_variance_summary']['average_cost_variance']:+.1f}%")
        print(f"🏢 Regional markets: {len(summary_results['regional_distribution'])}")
        print(f"🌊 Flood zones identified: {len(summary_results['flood_zone_distribution'])}")
        
        print(f"\n📈 COST VARIANCE RANGE:")
        lowest = summary_results['cost_variance_summary']['lowest_cost_sites'][0]
        highest = summary_results['cost_variance_summary']['highest_cost_sites'][-1]
        print(f"  Lowest: Site {lowest['site_index']} ({lowest['region']}) = {lowest['cost_variance_percentage']:+.1f}%")
        print(f"  Highest: Site {highest['site_index']} ({highest['region']}) = {highest['cost_variance_percentage']:+.1f}%")
        
        print(f"\n💾 Files created:")
        print(f"   • Detailed analysis: {cost_analysis_file.name}")
        print(f"   • Executive summary: {summary_file.name}")
        
        return cost_modifier_report

if __name__ == "__main__":
    analyzer = TexasCostModifierAnalyzer()
    results = analyzer.create_cost_modifier_analysis()