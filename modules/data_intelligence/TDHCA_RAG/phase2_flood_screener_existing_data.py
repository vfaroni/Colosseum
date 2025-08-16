#!/usr/bin/env python3
"""
Phase 2: Flood Zone Screening Using Existing CoStar Data
Priority 1 - Eliminate high-risk flood sites using data already in MASTER file
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class Phase2FloodScreenerExistingData:
    """Screen 155 qualified sites using existing CoStar flood data"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        
        # Input: MASTER file with 155 qualified sites
        self.master_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        
        # Flood zone risk classification (based on FEMA standards)
        self.flood_zone_risk = {
            # High Risk Zones (eliminate or flag)
            'A': 'HIGH_RISK',           # 1% annual chance flood zone
            'AE': 'HIGH_RISK',          # 1% annual chance with Base Flood Elevation
            'AH': 'HIGH_RISK',          # 1% annual chance shallow flooding
            'AO': 'HIGH_RISK',          # 1% annual chance sheet flow
            'AR': 'HIGH_RISK',          # 1% annual chance with restored studies
            'V': 'VERY_HIGH_RISK',      # 1% annual chance coastal
            'VE': 'VERY_HIGH_RISK',     # 1% annual chance coastal with BFE
            
            # Low/Moderate Risk Zones (keep)
            'B and X': 'LOW_RISK',      # Outside 1% and 0.2% flood zones
            'C and X': 'LOW_RISK',      # Outside 1% and 0.2% flood zones  
            'X': 'LOW_RISK',            # Outside 1% and 0.2% flood zones
            'X500': 'MODERATE_RISK',    # 0.2% annual chance (500-year flood)
            
            # Unknown
            'D': 'UNDETERMINED'         # Undetermined flood hazard
        }
        
        # Sites in these risk categories get flagged for elimination
        self.elimination_risks = ['HIGH_RISK', 'VERY_HIGH_RISK']
        
        # Insurance cost implications
        self.insurance_costs = {
            'HIGH_RISK': {'min': 1500, 'max': 3000, 'required': True},
            'VERY_HIGH_RISK': {'min': 2000, 'max': 4000, 'required': True},
            'MODERATE_RISK': {'min': 800, 'max': 1200, 'required': False},
            'LOW_RISK': {'min': 400, 'max': 800, 'required': False},
            'UNDETERMINED': {'min': 1000, 'max': 2000, 'required': True}
        }
    
    def load_and_analyze_flood_data(self):
        """Load MASTER file and analyze existing flood data"""
        print(f"📊 Loading MASTER file: {self.master_file}")
        
        df = pd.read_excel(self.master_file)
        print(f"✅ Loaded {len(df)} qualified sites")
        
        # Check flood data coverage
        has_flood_risk = df['Flood Risk'].notna().sum()
        has_flood_zone = df['Flood Zone'].notna().sum()
        
        print(f"📊 Existing flood data coverage:")
        print(f"   Flood Risk: {has_flood_risk}/{len(df)} sites ({has_flood_risk/len(df)*100:.1f}%)")
        print(f"   Flood Zone: {has_flood_zone}/{len(df)} sites ({has_flood_zone/len(df)*100:.1f}%)")
        
        return df
    
    def classify_flood_risk(self, df):
        """Classify flood risk for all sites"""
        print("\n🌊 CLASSIFYING FLOOD RISK FOR ALL 155 SITES")
        print("=" * 60)
        
        # Initialize risk classification columns
        df['flood_risk_level'] = 'UNKNOWN'
        df['eliminate_flag'] = False
        df['insurance_required'] = False
        df['annual_insurance_cost_min'] = 0
        df['annual_insurance_cost_max'] = 0
        df['flood_analysis_method'] = 'COSTAR_EXISTING_DATA'
        
        elimination_count = 0
        viable_count = 0
        
        for idx, row in df.iterrows():
            flood_zone = str(row.get('Flood Zone', 'UNKNOWN')).strip()
            flood_risk_text = str(row.get('Flood Risk', 'UNKNOWN')).strip()
            address = row.get('Address', 'Unknown')
            
            # Classify risk level
            risk_level = self.flood_zone_risk.get(flood_zone, 'UNKNOWN')
            
            # Special handling for missing data
            if pd.isna(row.get('Flood Zone')) or flood_zone in ['nan', 'UNKNOWN', '']:
                if flood_risk_text.lower() == 'yes':
                    risk_level = 'MODERATE_RISK'  # Conservative estimate
                elif flood_risk_text.lower() == 'no':
                    risk_level = 'LOW_RISK'
                else:
                    risk_level = 'UNKNOWN'
            
            # Determine elimination flag
            eliminate = risk_level in self.elimination_risks
            
            # Get insurance costs
            insurance_info = self.insurance_costs.get(risk_level, self.insurance_costs['UNDETERMINED'])
            
            # Update DataFrame
            df.at[idx, 'flood_risk_level'] = risk_level
            df.at[idx, 'eliminate_flag'] = eliminate
            df.at[idx, 'insurance_required'] = insurance_info['required']
            df.at[idx, 'annual_insurance_cost_min'] = insurance_info['min']
            df.at[idx, 'annual_insurance_cost_max'] = insurance_info['max']
            
            # Count results
            if eliminate:
                elimination_count += 1
                print(f"🚫 Site {idx:3d}: {address[:45]:45} | Zone: {flood_zone:8} | {risk_level:15} | ELIMINATE")
            else:
                viable_count += 1
                print(f"✅ Site {idx:3d}: {address[:45]:45} | Zone: {flood_zone:8} | {risk_level:15} | VIABLE")
        
        print(f"\n📊 FLOOD RISK CLASSIFICATION COMPLETE:")
        print(f"   🚫 Sites flagged for elimination: {elimination_count} ({elimination_count/len(df)*100:.1f}%)")
        print(f"   ✅ Viable sites after flood screening: {viable_count} ({viable_count/len(df)*100:.1f}%)")
        
        return df, elimination_count, viable_count
    
    def create_detailed_analysis(self, df):
        """Create detailed flood risk analysis"""
        
        # Risk level distribution
        risk_distribution = df['flood_risk_level'].value_counts().to_dict()
        zone_distribution = df['Flood Zone'].value_counts().to_dict()
        
        # Insurance cost analysis
        total_min_cost = df['annual_insurance_cost_min'].sum()
        total_max_cost = df['annual_insurance_cost_max'].sum()
        insurance_required_sites = len(df[df['insurance_required'] == True])
        
        # Elimination analysis
        eliminated_sites = df[df['eliminate_flag'] == True]
        viable_sites = df[df['eliminate_flag'] == False]
        
        # Geographic distribution of eliminations
        eliminated_by_city = eliminated_sites['City'].value_counts().to_dict() if len(eliminated_sites) > 0 else {}
        viable_by_city = viable_sites['City'].value_counts().to_dict()
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_sites_analyzed': len(df),
            'data_source': 'CoStar existing flood data in MASTER file',
            'coverage_stats': {
                'sites_with_flood_zone': len(df[df['Flood Zone'].notna()]),
                'sites_with_flood_risk': len(df[df['Flood Risk'].notna()]),
                'coverage_percentage': round(len(df[df['Flood Zone'].notna()])/len(df)*100, 1)
            },
            'elimination_results': {
                'sites_flagged_for_elimination': len(eliminated_sites),
                'viable_sites_remaining': len(viable_sites),
                'elimination_rate_percent': round(len(eliminated_sites)/len(df)*100, 1)
            },
            'risk_distribution': risk_distribution,
            'flood_zone_distribution': zone_distribution,
            'insurance_analysis': {
                'sites_requiring_insurance': insurance_required_sites,
                'estimated_total_annual_cost_range': f'${total_min_cost:,} - ${total_max_cost:,}',
                'average_cost_per_site_requiring_insurance': f'${total_min_cost/insurance_required_sites:,.0f} - ${total_max_cost/insurance_required_sites:,.0f}' if insurance_required_sites > 0 else 'N/A'
            },
            'geographic_distribution': {
                'eliminated_sites_by_city': eliminated_by_city,
                'viable_sites_by_city': viable_by_city
            },
            'methodology': {
                'high_risk_zones': ['A', 'AE', 'AH', 'AO', 'AR'],
                'very_high_risk_zones': ['V', 'VE'],
                'low_risk_zones': ['B and X', 'C and X', 'X'],
                'elimination_criteria': 'Sites in HIGH_RISK or VERY_HIGH_RISK zones flagged for elimination due to flood insurance costs $1,500-4,000/unit annually'
            }
        }
        
        return summary
    
    def save_screening_results(self, df, summary):
        """Save flood screening results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save enhanced Excel with flood screening
        excel_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Flood_Screened_Sites_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All sites with flood analysis
            df.to_excel(writer, sheet_name='All_Sites_Flood_Analysis', index=False)
            
            # Viable sites (recommended to keep) - this is our filtered dataset
            viable_sites = df[df['eliminate_flag'] == False]
            viable_sites.to_excel(writer, sheet_name='Viable_Sites_After_Flood', index=False)
            print(f"✅ Viable sites sheet: {len(viable_sites)} sites")
            
            # Eliminated sites (high flood risk)
            eliminated_sites = df[df['eliminate_flag'] == True]
            if len(eliminated_sites) > 0:
                eliminated_sites.to_excel(writer, sheet_name='Eliminated_High_Flood_Risk', index=False)
                print(f"🚫 Eliminated sites sheet: {len(eliminated_sites)} sites")
            
            # Risk level summary
            risk_summary = df['flood_risk_level'].value_counts().reset_index()
            risk_summary.columns = ['Risk_Level', 'Site_Count']
            risk_summary.to_excel(writer, sheet_name='Risk_Level_Summary', index=False)
            
            # Insurance cost analysis
            insurance_df = df[df['insurance_required'] == True][['Address', 'City', 'Flood Zone', 'flood_risk_level', 
                                                               'annual_insurance_cost_min', 'annual_insurance_cost_max']]
            if len(insurance_df) > 0:
                insurance_df.to_excel(writer, sheet_name='Insurance_Required_Sites', index=False)
        
        # Save summary JSON
        summary_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Flood_Screening_Summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 FLOOD SCREENING RESULTS SAVED:")
        print(f"   📊 Excel analysis: {excel_file.name}")
        print(f"   📋 Summary report: {summary_file.name}")
        
        return excel_file, summary_file, viable_sites
    
    def run_flood_screening(self):
        """Run complete flood screening using existing CoStar data"""
        print("🌊 PHASE 2: FLOOD SCREENING - 155 QUALIFIED SITES")
        print("🎯 OBJECTIVE: Use existing CoStar flood data to eliminate high-risk sites")
        print("=" * 80)
        
        # Load sites with existing flood data
        df = self.load_and_analyze_flood_data()
        
        # Classify flood risk and elimination flags
        enhanced_df, elimination_count, viable_count = self.classify_flood_risk(df)
        
        # Create detailed analysis
        summary = self.create_detailed_analysis(enhanced_df)
        
        # Save results
        excel_file, summary_file, viable_sites = self.save_screening_results(enhanced_df, summary)
        
        print("\n" + "=" * 80)
        print("🌊 FLOOD SCREENING PHASE COMPLETE!")
        print("=" * 80)
        print(f"📊 Total sites analyzed: {summary['total_sites_analyzed']}")
        print(f"🚫 High flood risk (flagged): {summary['elimination_results']['sites_flagged_for_elimination']}")
        print(f"✅ Viable sites remaining: {summary['elimination_results']['viable_sites_remaining']}")
        print(f"📈 Success rate: {100-summary['elimination_results']['elimination_rate_percent']:.1f}% sites remain viable")
        print(f"💰 Insurance impact: {summary['insurance_analysis']['sites_requiring_insurance']} sites need flood insurance")
        
        return {
            'success': True,
            'excel_file': str(excel_file),
            'summary_file': str(summary_file), 
            'viable_sites_count': summary['elimination_results']['viable_sites_remaining'],
            'elimination_count': summary['elimination_results']['sites_flagged_for_elimination'],
            'viable_sites_df': viable_sites,
            'summary': summary
        }

if __name__ == "__main__":
    screener = Phase2FloodScreenerExistingData()
    results = screener.run_flood_screening()
    
    if results and results['success']:
        print(f"\n🎯 READY FOR NEXT PHASE: Highway access screening on {results['viable_sites_count']} flood-viable sites")
        print(f"💾 Results: {results['excel_file']}")
    else:
        print("\n❌ Flood screening failed")