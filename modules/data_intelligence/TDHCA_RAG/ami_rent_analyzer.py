#!/usr/bin/env python3
"""
AMI Rent Analysis for 117 Flood-Viable Sites
Integrate HUD 2025 static AMI/rent data with Texas LIHTC sites
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class AMIRentAnalyzer:
    """Integrate HUD AMI rent data with viable LIHTC sites"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        
        # Input files
        self.hud_ami_file = self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.flood_screened_file = self.base_dir / "D'Marco_Sites/Analysis_Results/Phase2_Flood_Screened_Sites_20250731_232355.xlsx"
        
        # Output timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_flood_viable_sites(self):
        """Load 117 flood-viable sites from Phase2 screening"""
        print(f"📊 Loading flood-viable sites from: {self.flood_screened_file.name}")
        
        try:
            # Load the viable sites sheet
            df = pd.read_excel(self.flood_screened_file, sheet_name='Viable_Sites_After_Flood')
            print(f"✅ Loaded {len(df)} flood-viable sites for AMI analysis")
            return df
        except Exception as e:
            print(f"❌ Failed to load flood-viable sites: {e}")
            return None
    
    def load_hud_ami_data(self):
        """Load HUD 2025 AMI rent data (static dataset)"""
        print(f"📊 Loading HUD AMI data from: {self.hud_ami_file.name}")
        
        try:
            # Load AMI data - likely first or main sheet
            ami_df = pd.read_excel(self.hud_ami_file, sheet_name=0)
            print(f"✅ Loaded HUD AMI data: {len(ami_df)} records")
            print(f"🔍 AMI data columns: {list(ami_df.columns)}")
            return ami_df
        except Exception as e:
            print(f"❌ Failed to load HUD AMI data: {e}")
            return None
    
    def match_sites_with_ami_data(self, sites_df, ami_df):
        """Match Texas sites with appropriate AMI area data"""
        print("🔄 Matching sites with AMI data...")
        
        # Look for common geographic identifiers
        site_geo_cols = [col for col in sites_df.columns if any(term in col.lower() for term in ['county', 'msa', 'metro', 'cbsa', 'state'])]
        ami_geo_cols = [col for col in ami_df.columns if any(term in col.lower() for term in ['county', 'msa', 'metro', 'cbsa', 'area', 'name'])]
        
        print(f"🗺️ Site geographic columns: {site_geo_cols}")
        print(f"🗺️ AMI geographic columns: {ami_geo_cols}")
        
        # Strategy: Look for Texas AMI areas and attempt matching
        if 'State' in ami_df.columns or 'state' in ami_df.columns:
            state_col = 'State' if 'State' in ami_df.columns else 'state'
            texas_ami = ami_df[ami_df[state_col].str.contains('TX|Texas', case=False, na=False)]
            print(f"🎯 Found {len(texas_ami)} Texas AMI records")
        else:
            texas_ami = ami_df  # Use all data if no state filter possible
        
        # For now, create a simple join attempt - will need refinement based on actual data structure
        enhanced_sites = sites_df.copy()
        
        # Add placeholder AMI columns for analysis
        enhanced_sites['AMI_Area'] = 'TO_BE_MATCHED'
        enhanced_sites['AMI_50_Studio'] = 0
        enhanced_sites['AMI_50_1BR'] = 0  
        enhanced_sites['AMI_50_2BR'] = 0
        enhanced_sites['AMI_50_3BR'] = 0
        enhanced_sites['AMI_60_Studio'] = 0
        enhanced_sites['AMI_60_1BR'] = 0
        enhanced_sites['AMI_60_2BR'] = 0
        enhanced_sites['AMI_60_3BR'] = 0
        enhanced_sites['AMI_100_4Person'] = 0
        
        print(f"✅ Enhanced {len(enhanced_sites)} sites with AMI structure")
        return enhanced_sites, texas_ami
    
    def analyze_rent_feasibility(self, enhanced_sites):
        """Analyze LIHTC rent feasibility for each site"""
        print("💰 Analyzing LIHTC rent feasibility...")
        
        # Add feasibility analysis columns
        enhanced_sites['Rent_Feasibility_Score'] = 0
        enhanced_sites['Market_Competitiveness'] = 'UNKNOWN'
        enhanced_sites['LIHTC_Rent_Premium'] = 0
        enhanced_sites['Investment_Priority'] = 'MEDIUM'
        
        # Placeholder scoring - will need actual AMI data integration
        for idx, site in enhanced_sites.iterrows():
            # Basic feasibility scoring framework
            feasibility_score = 50  # Base score
            
            # Adjust based on available site data
            if hasattr(site, 'Price_Per_Acre') and pd.notna(site.get('Price_Per_Acre')):
                if site['Price_Per_Acre'] < 50000:  # Lower land cost = higher feasibility
                    feasibility_score += 20
                elif site['Price_Per_Acre'] > 100000:
                    feasibility_score -= 20
            
            enhanced_sites.loc[idx, 'Rent_Feasibility_Score'] = feasibility_score
            
            # Set priority based on feasibility
            if feasibility_score >= 70:
                enhanced_sites.loc[idx, 'Investment_Priority'] = 'HIGH'
            elif feasibility_score <= 40:
                enhanced_sites.loc[idx, 'Investment_Priority'] = 'LOW'
        
        print(f"✅ Completed rent feasibility analysis for {len(enhanced_sites)} sites")
        return enhanced_sites
    
    def generate_ami_analysis_summary(self, enhanced_sites, texas_ami):
        """Generate comprehensive AMI analysis summary"""
        summary = {
            'analysis_date': self.timestamp,
            'total_sites_analyzed': len(enhanced_sites),
            'texas_ami_areas_available': len(texas_ami),
            'feasibility_distribution': {
                'HIGH': len(enhanced_sites[enhanced_sites['Investment_Priority'] == 'HIGH']),
                'MEDIUM': len(enhanced_sites[enhanced_sites['Investment_Priority'] == 'MEDIUM']),
                'LOW': len(enhanced_sites[enhanced_sites['Investment_Priority'] == 'LOW'])
            },
            'average_feasibility_score': enhanced_sites['Rent_Feasibility_Score'].mean(),
            'data_integration_status': 'PLACEHOLDER_ANALYSIS_COMPLETE',
            'next_steps': [
                'Integrate actual HUD AMI matching logic',
                'Add county-based AMI area lookup',
                'Calculate precise LIHTC rent limits',
                'Add market rent comparison analysis'
            ]
        }
        
        return summary
    
    def save_results(self, enhanced_sites, summary, texas_ami):
        """Save AMI analysis results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        results_dir.mkdir(exist_ok=True)
        
        # Save enhanced sites with AMI data
        excel_file = results_dir / f"Phase2_AMI_Enhanced_Sites_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            enhanced_sites.to_excel(writer, sheet_name='Sites_With_AMI_Analysis', index=False)
            texas_ami.to_excel(writer, sheet_name='Texas_AMI_Reference', index=False)
            
            # Create summary sheet
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Analysis_Summary', index=False)
        
        # Save JSON summary
        json_file = results_dir / f"AMI_Analysis_Summary_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"💾 Results saved:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📋 Summary: {json_file.name}")
        
        return excel_file, json_file

def main():
    """Execute AMI rent analysis on flood-viable sites"""
    print("💰 PHASE 2: AMI RENT ANALYSIS")
    print("🎯 OBJECTIVE: Integrate HUD AMI data with viable LIHTC sites")
    print("=" * 80)
    
    analyzer = AMIRentAnalyzer()
    
    # Load flood-viable sites (117 sites from flood screening)
    sites_df = analyzer.load_flood_viable_sites()
    if sites_df is None:
        print("❌ AMI analysis failed - no viable sites loaded")
        return
    
    # Load HUD AMI data
    ami_df = analyzer.load_hud_ami_data()
    if ami_df is None:
        print("❌ AMI analysis failed - no HUD data loaded")
        return
    
    # Match sites with AMI data
    enhanced_sites, texas_ami = analyzer.match_sites_with_ami_data(sites_df, ami_df)
    
    # Analyze rent feasibility
    enhanced_sites = analyzer.analyze_rent_feasibility(enhanced_sites)
    
    # Generate summary
    summary = analyzer.generate_ami_analysis_summary(enhanced_sites, texas_ami)
    
    # Save results
    excel_file, json_file = analyzer.save_results(enhanced_sites, summary, texas_ami)
    
    print("\n🎯 AMI ANALYSIS RESULTS:")
    print(f"   Sites Analyzed: {summary['total_sites_analyzed']}")
    print(f"   High Priority: {summary['feasibility_distribution']['HIGH']}")
    print(f"   Medium Priority: {summary['feasibility_distribution']['MEDIUM']}")  
    print(f"   Low Priority: {summary['feasibility_distribution']['LOW']}")
    print(f"   Avg Feasibility: {summary['average_feasibility_score']:.1f}")
    
    print("\n✅ AMI rent analysis complete")
    print(f"📁 Results: {excel_file}")

if __name__ == "__main__":
    main()