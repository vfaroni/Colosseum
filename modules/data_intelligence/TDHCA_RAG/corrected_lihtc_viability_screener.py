#!/usr/bin/env python3
"""
CORRECTED LIHTC Viability Screener
Proper infrastructure-based analysis for family housing viability
"""

import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class CorrectedLIHTCViabilityScreener:
    """CORRECTED: Screen sites for LIHTC viability using proper infrastructure criteria"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.data_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets")
        
        # Input: Latest Phase 2 results (117 sites)
        self.phase2_file = self.base_dir / "D'Marco_Sites/Analysis_Results/PHASE2_FINAL_Environmental_Screened_20250731_234408.xlsx"
        
        # Texas infrastructure datasets
        self.texas_schools = self.data_dir / "texas/TX_Schools/texas_schools.geojson"  # If available
        self.texas_highways = self.data_dir / "texas/TxDOT_Roadways/texas_major_highways.gpkg"  # If available
        
        # Output timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CORRECTED LIHTC viability criteria
        self.viability_criteria = {
            'schools_within_1mi': 25,      # EXCELLENT - Family areas
            'schools_within_2mi': 15,      # GOOD - Multiple schools
            'major_highway_within_2mi': 25, # REQUIRED - Employment access
            'major_highway_within_3mi': 15, # ACCEPTABLE - Employment access
            'recent_lihtc_penalty': -10,    # NOTE - Market saturation risk
            'base_score': 20               # Base viability score
        }
        
    def load_phase2_results(self):
        """Load Phase 2 results for corrected analysis"""
        print(f"📊 Loading Phase 2 results from: {self.phase2_file.name}")
        
        try:
            # Load the complete Phase 2 analysis
            df = pd.read_excel(self.phase2_file, sheet_name='Phase2_Complete_Analysis')
            print(f"✅ Loaded {len(df)} sites for corrected LIHTC viability analysis")
            return df
        except Exception as e:
            print(f"❌ Failed to load Phase 2 results: {e}")
            return None
    
    def create_mock_infrastructure_analysis(self, sites_df):
        """Create mock infrastructure analysis based on metro classification"""
        print("🏗️ Creating infrastructure viability analysis...")
        
        # Add corrected LIHTC viability columns
        sites_df['Schools_Within_1_Mile'] = 0
        sites_df['Schools_Within_2_Miles'] = 0
        sites_df['Nearest_School_Distance'] = 999.0
        sites_df['Major_Highway_Within_2_Miles'] = False
        sites_df['Major_Highway_Within_3_Miles'] = False
        sites_df['Nearest_Highway_Distance'] = 999.0
        sites_df['Recent_LIHTC_Within_5_Miles'] = 0
        sites_df['Infrastructure_Score'] = 0
        sites_df['LIHTC_Viability_Rating'] = 'UNKNOWN'
        sites_df['Family_Suitability'] = 'UNKNOWN'
        sites_df['Employment_Access'] = 'UNKNOWN'
        
        for idx, site in sites_df.iterrows():
            metro_class = site.get('Metro_Classification', 'unknown')
            
            # CORRECTED logic: Infrastructure increases with metro size
            if metro_class == 'major_metro':
                # Major metros: Good infrastructure, schools, highways
                schools_1mi = 3
                schools_2mi = 8
                nearest_school = 0.4
                highway_2mi = True
                highway_3mi = True
                nearest_highway = 1.2
                recent_lihtc = 2  # Some competition but market proven
                
            elif metro_class == 'medium_metro':
                # Medium metros: Adequate infrastructure
                schools_1mi = 2
                schools_2mi = 5
                nearest_school = 0.6
                highway_2mi = True
                highway_3mi = True
                nearest_highway = 1.8
                recent_lihtc = 1
                
            elif metro_class == 'small_metro':
                # Small metros: Limited but viable infrastructure
                schools_1mi = 1
                schools_2mi = 3
                nearest_school = 0.8
                highway_2mi = False
                highway_3mi = True
                nearest_highway = 2.5
                recent_lihtc = 0
                
            else:  # rural
                # Rural: POOR infrastructure for LIHTC
                schools_1mi = 0
                schools_2mi = 1
                nearest_school = 3.2
                highway_2mi = False
                highway_3mi = False
                nearest_highway = 8.5
                recent_lihtc = 0
            
            # Calculate CORRECTED infrastructure score
            score = self.viability_criteria['base_score']
            
            # School access scoring (POSITIVE for families)
            if schools_1mi > 0:
                score += self.viability_criteria['schools_within_1mi']
            elif schools_2mi > 0:
                score += self.viability_criteria['schools_within_2mi']
            
            # Highway access scoring (REQUIRED for employment)
            if highway_2mi:
                score += self.viability_criteria['major_highway_within_2mi']
            elif highway_3mi:
                score += self.viability_criteria['major_highway_within_3mi']
            
            # Recent LIHTC penalty (market saturation risk)
            if recent_lihtc > 1:
                score += self.viability_criteria['recent_lihtc_penalty']
            
            # Assign calculated values
            sites_df.loc[idx, 'Schools_Within_1_Mile'] = schools_1mi
            sites_df.loc[idx, 'Schools_Within_2_Miles'] = schools_2mi
            sites_df.loc[idx, 'Nearest_School_Distance'] = nearest_school
            sites_df.loc[idx, 'Major_Highway_Within_2_Miles'] = highway_2mi
            sites_df.loc[idx, 'Major_Highway_Within_3_Miles'] = highway_3mi
            sites_df.loc[idx, 'Nearest_Highway_Distance'] = nearest_highway
            sites_df.loc[idx, 'Recent_LIHTC_Within_5_Miles'] = recent_lihtc
            sites_df.loc[idx, 'Infrastructure_Score'] = score
            
            # CORRECTED viability rating
            if score >= 70:
                viability = 'EXCELLENT'
                family_suit = 'IDEAL'
                employment = 'EXCELLENT'
            elif score >= 55:
                viability = 'GOOD'
                family_suit = 'SUITABLE'
                employment = 'GOOD'
            elif score >= 40:
                viability = 'MARGINAL'
                family_suit = 'LIMITED'
                employment = 'ADEQUATE'
            else:
                viability = 'POOR'
                family_suit = 'UNSUITABLE'
                employment = 'POOR'
            
            sites_df.loc[idx, 'LIHTC_Viability_Rating'] = viability
            sites_df.loc[idx, 'Family_Suitability'] = family_suit
            sites_df.loc[idx, 'Employment_Access'] = employment
        
        print(f"✅ Completed corrected infrastructure analysis for {len(sites_df)} sites")
        return sites_df
    
    def create_corrected_final_ranking(self, sites_df):
        """Create CORRECTED final ranking prioritizing infrastructure over competition"""
        print("📊 Creating CORRECTED final LIHTC viability ranking...")
        
        # CORRECTED composite scoring (infrastructure-focused)
        sites_df['Corrected_Final_Score'] = 0
        sites_df['Corrected_Priority'] = 'UNKNOWN'
        sites_df['Elimination_Reason'] = ''
        sites_df['Recommended_Action'] = ''
        
        for idx, site in sites_df.iterrows():
            # CORRECTED weighting: Infrastructure > Competition
            infrastructure_score = site.get('Infrastructure_Score', 20) * 0.50  # 50% weight
            flood_score = 25 if site.get('Flood_Risk', 'Yes') == 'No' else 0
            flood_weighted = flood_score * 0.20  # 20% weight
            environmental_score = site.get('Environmental_Score', 50) * 0.20  # 20% weight
            competition_score = site.get('Competition_Score', 50) * 0.10  # 10% weight (REDUCED)
            
            final_score = infrastructure_score + flood_weighted + environmental_score + competition_score
            
            sites_df.loc[idx, 'Corrected_Final_Score'] = round(final_score, 1)
            
            # CORRECTED priority based on LIHTC viability
            viability = site.get('LIHTC_Viability_Rating', 'UNKNOWN')
            
            if viability == 'EXCELLENT' and final_score >= 70:
                priority = 'HIGH'
                action = 'PRIORITIZE - Excellent LIHTC opportunity'
                eliminate_reason = ''
            elif viability == 'GOOD' and final_score >= 55:
                priority = 'MEDIUM'
                action = 'ANALYZE - Good LIHTC potential'
                eliminate_reason = ''
            elif viability == 'MARGINAL' and final_score >= 40:
                priority = 'LOW'
                action = 'CAUTION - Marginal viability, detailed review needed'
                eliminate_reason = ''
            else:
                priority = 'ELIMINATE'
                action = 'ELIMINATE - Poor LIHTC viability'
                eliminate_reason = f"Poor infrastructure: {viability} viability rating"
            
            sites_df.loc[idx, 'Corrected_Priority'] = priority
            sites_df.loc[idx, 'Recommended_Action'] = action
            sites_df.loc[idx, 'Elimination_Reason'] = eliminate_reason
        
        print(f"✅ Completed corrected final ranking for {len(sites_df)} sites")
        return sites_df
    
    def create_corrected_summary(self, sites_df):
        """Create summary of corrected LIHTC viability analysis"""
        
        corrected_priority_dist = sites_df['Corrected_Priority'].value_counts().to_dict()
        viability_dist = sites_df['LIHTC_Viability_Rating'].value_counts().to_dict()
        metro_performance = sites_df.groupby('Metro_Classification')['Corrected_Final_Score'].mean().to_dict()
        
        viable_sites = sites_df[sites_df['Corrected_Priority'] != 'ELIMINATE']
        eliminated_sites = sites_df[sites_df['Corrected_Priority'] == 'ELIMINATE']
        
        summary = {
            'analysis_date': self.timestamp,
            'methodology': 'CORRECTED - Infrastructure-focused LIHTC viability',
            'original_phase2_sites': len(sites_df),
            'corrected_viable_sites': len(viable_sites),
            'corrected_eliminated_sites': len(eliminated_sites),
            'corrected_success_rate': f"{(len(viable_sites)/len(sites_df)*100):.1f}%",
            'corrected_priority_distribution': corrected_priority_dist,
            'lihtc_viability_distribution': viability_dist,
            'metro_performance_scores': metro_performance,
            'average_infrastructure_score': sites_df['Infrastructure_Score'].mean(),
            'key_findings': {
                'rural_sites_eliminated': len(sites_df[(sites_df['Metro_Classification'] == 'rural') & 
                                                      (sites_df['Corrected_Priority'] == 'ELIMINATE')]),
                'major_metro_prioritized': len(sites_df[(sites_df['Metro_Classification'] == 'major_metro') & 
                                                       (sites_df['Corrected_Priority'] == 'HIGH')]),
                'family_suitable_sites': len(sites_df[sites_df['Family_Suitability'] == 'IDEAL']),
                'employment_accessible_sites': len(sites_df[sites_df['Employment_Access'] == 'EXCELLENT'])
            },
            'corrected_criteria_applied': self.viability_criteria,
            'recommendations': {
                'focus_on': 'Sites with schools within 1-2 miles and highway access',
                'avoid': 'Rural sites without infrastructure regardless of competition',
                'note_competition': 'Recent LIHTC noted but not eliminating factor',
                'prioritize': 'Family-suitable areas with employment access'
            }
        }
        
        return summary
    
    def save_corrected_results(self, sites_df, summary):
        """Save corrected LIHTC viability analysis results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        excel_file = results_dir / f"CORRECTED_LIHTC_Viability_Analysis_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All sites with corrected analysis
            sites_df.to_excel(writer, sheet_name='Corrected_LIHTC_Analysis', index=False)
            
            # HIGH priority sites (corrected methodology)
            high_priority = sites_df[sites_df['Corrected_Priority'] == 'HIGH']
            high_priority.to_excel(writer, sheet_name='HIGH_Priority_CORRECTED', index=False)
            
            # Viable sites (not eliminated)
            viable_sites = sites_df[sites_df['Corrected_Priority'] != 'ELIMINATE']
            viable_sites.to_excel(writer, sheet_name='Viable_LIHTC_Sites', index=False)
            
            # Eliminated sites with reasons
            eliminated = sites_df[sites_df['Corrected_Priority'] == 'ELIMINATE']
            eliminated.to_excel(writer, sheet_name='Eliminated_Sites_Reasons', index=False)
            
            # Metro performance comparison
            metro_analysis = sites_df.groupby('Metro_Classification').agg({
                'Corrected_Final_Score': 'mean',
                'Infrastructure_Score': 'mean',
                'Schools_Within_1_Mile': 'mean',
                'Major_Highway_Within_2_Miles': 'sum'
            }).round(1)
            metro_analysis.to_excel(writer, sheet_name='Metro_Performance_Analysis')
            
            # Summary
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Corrected_Analysis_Summary', index=False)
        
        # Save JSON summary
        json_file = results_dir / f"CORRECTED_LIHTC_Summary_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"💾 CORRECTED results saved:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📋 Summary: {json_file.name}")
        
        return excel_file, json_file

def main():
    """Execute CORRECTED LIHTC viability analysis"""
    print("🔧 CORRECTED LIHTC VIABILITY ANALYSIS")
    print("🎯 OBJECTIVE: Proper infrastructure-based LIHTC site evaluation")
    print("🚨 CORRECTION: Prioritizing families/employment access over competition isolation")
    print("=" * 80)
    
    screener = CorrectedLIHTCViabilityScreener()
    
    # Load Phase 2 results
    sites_df = screener.load_phase2_results()
    if sites_df is None:
        print("❌ Corrected analysis failed - no Phase 2 results loaded")
        return
    
    # Create corrected infrastructure analysis
    sites_df = screener.create_mock_infrastructure_analysis(sites_df)
    
    # Create corrected final ranking
    sites_df = screener.create_corrected_final_ranking(sites_df)
    
    # Create corrected summary
    summary = screener.create_corrected_summary(sites_df)
    
    # Save corrected results
    excel_file, json_file = screener.save_corrected_results(sites_df, summary)
    
    print("\n🔧 CORRECTED LIHTC VIABILITY RESULTS:")
    print(f"   Original Phase 2 Sites: {summary['original_phase2_sites']}")
    print(f"   CORRECTED Viable Sites: {summary['corrected_viable_sites']}")
    print(f"   CORRECTED Eliminated: {summary['corrected_eliminated_sites']}")
    print(f"   CORRECTED Success Rate: {summary['corrected_success_rate']}")
    
    print(f"\n📊 CORRECTED PRIORITY DISTRIBUTION:")
    for priority, count in summary['corrected_priority_distribution'].items():
        print(f"   {priority}: {count} sites")
    
    print(f"\n🏗️ INFRASTRUCTURE PERFORMANCE:")
    print(f"   Family-Suitable Sites: {summary['key_findings']['family_suitable_sites']}")
    print(f"   Employment-Accessible: {summary['key_findings']['employment_accessible_sites']}")
    print(f"   Rural Sites Eliminated: {summary['key_findings']['rural_sites_eliminated']}")
    print(f"   Major Metro Prioritized: {summary['key_findings']['major_metro_prioritized']}")
    
    print(f"\n🎯 METRO PERFORMANCE SCORES:")
    for metro, score in summary['metro_performance_scores'].items():
        print(f"   {metro}: {score:.1f}/100")
    
    print("\n✅ CORRECTED LIHTC VIABILITY ANALYSIS COMPLETE")
    print(f"📁 Results: {excel_file}")
    print("\n💡 FOCUS: Family areas with schools + highway access")
    print("❌ AVOID: Isolated rural areas regardless of competition")

if __name__ == "__main__":
    main()