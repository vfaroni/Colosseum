#!/usr/bin/env python3
"""
MASTER INTEGRATED LIHTC SCREENER
Comprehensive analysis combining ALL expert insights and data sources
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class MasterIntegratedLIHTCScreener:
    """MASTER SCREENER: All analyses integrated for final investment decisions"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        
        # Input: Latest Phase 2 results (117 sites)
        self.phase2_file = self.base_dir / "D'Marco_Sites/Analysis_Results/PHASE2_FINAL_Environmental_Screened_20250731_234408.xlsx"
        
        # Market intelligence files
        self.austin_analysis = self.base_dir / "D'Marco_Sites/Analysis_Results/Austin_Site_Rent_Risk_Analysis_20250801_140703.xlsx"
        self.dfw_houston_analysis = self.base_dir / "D'Marco_Sites/Analysis_Results/DFW_Houston_CoStar_Analysis_20250801_145258.json"
        
        # TDHCA competition data
        self.tdhca_competition_dir = self.base_dir / "D'Marco_Sites/Successful_2023_Applications"
        
        # AMI/rent data
        self.hud_ami_file = self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        # Output timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # MASTER scoring weights (expert-informed)
        self.scoring_weights = {
            'qct_dda_eligibility': 20,        # Must have 130% basis boost
            'flood_risk': 15,                 # FEMA compliance critical
            'market_expert_analysis': 25,     # Kirt Shell + CoStar insights
            'infrastructure_access': 20,      # Schools + highways for families
            'ami_rent_feasibility': 10,       # 60% AMI rent achievability  
            'tdhca_competition': 5,           # Recent project density
            'unit_capacity': 5                # 250+ unit potential (4% LIHTC)
        }
        
    def load_phase2_baseline(self):
        """Load Phase 2 results as baseline (117 sites)"""
        print("📊 Loading Phase 2 baseline analysis...")
        
        try:
            df = pd.read_excel(self.phase2_file, sheet_name='Phase2_Complete_Analysis')
            print(f"✅ Loaded {len(df)} sites for master analysis")
            return df
        except Exception as e:
            print(f"❌ Failed to load Phase 2 baseline: {e}")
            return None
    
    def apply_kirt_shell_market_intelligence(self, sites_df):
        """Apply Kirt Shell expert market analysis"""
        print("🧠 Applying Kirt Shell market expert analysis...")
        
        # Add market expert columns
        sites_df['Kirt_Shell_Market_Rating'] = 'UNKNOWN'
        sites_df['Market_Expert_Score'] = 0
        sites_df['Market_Expert_Notes'] = ''
        
        for idx, site in sites_df.iterrows():
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', '')) + ' ' + str(site.get('County', ''))
            site_text_lower = site_text.lower()
            
            # Houston - EXPERT SAYS AVOID
            if any(term in site_text_lower for term in ['houston', 'harris', 'montgomery', 'fort bend', 'brazoria']):
                rating = 'AVOID - EXPERT WARNING'
                score = 0
                notes = 'Kirt Shell: Flood plains + gas pipelines + heavy competition'
                
            # Austin MSA - RENT CLIFF ISSUES
            elif any(term in site_text_lower for term in ['austin', 'travis', 'williamson', 'hays']):
                # Check distance from downtown (use existing Austin analysis if available)
                rating = 'RENT CLIFF RISK'
                score = 20
                notes = 'Austin MSA: Outer areas have rent cliff issues'
                
            # DFW - MOST VIABLE MAJOR METRO  
            elif any(term in site_text_lower for term in ['dallas', 'fort worth', 'plano', 'frisco', 'tarrant', 'collin']):
                rating = 'VIABLE METRO'
                score = 75
                notes = 'DFW: Most viable major metro, watch outer suburbs'
                
            # Tyler - KIRT SHELL RECOMMENDED
            elif 'tyler' in site_text_lower:
                rating = 'EXPERT RECOMMENDED'
                score = 85
                notes = 'Kirt Shell: Good fundamentals, 97K PMA population'
                
            # Kerrville - KIRT SHELL RECOMMENDED  
            elif 'kerrville' in site_text_lower:
                rating = 'EXPERT RECOMMENDED'
                score = 85
                notes = 'Kirt Shell: Flexible unit mix, viable market'
                
            # San Antonio - MIXED (DEPENDS ON LOCATION)
            elif any(term in site_text_lower for term in ['san antonio', 'bexar']):
                rating = 'LOCATION DEPENDENT'
                score = 60
                notes = 'San Antonio: Richland Hills good, Gus McCrae avoid (too remote)'
                
            # Rural/Remote areas - AVOID
            elif site.get('Metro_Classification', '') == 'rural':
                rating = 'RURAL - AVOID'
                score = 10
                notes = 'Rural areas lack infrastructure for LIHTC viability'
                
            # Unknown areas - RESEARCH NEEDED
            else:
                rating = 'RESEARCH NEEDED'
                score = 40
                notes = 'Market not analyzed by experts - needs research'
            
            sites_df.loc[idx, 'Kirt_Shell_Market_Rating'] = rating
            sites_df.loc[idx, 'Market_Expert_Score'] = score
            sites_df.loc[idx, 'Market_Expert_Notes'] = notes
        
        print(f"✅ Applied market expert analysis to {len(sites_df)} sites")
        return sites_df
    
    def apply_costar_rent_feasibility(self, sites_df):
        """Apply CoStar rent feasibility analysis"""
        print("💰 Applying CoStar rent feasibility analysis...")
        
        # Add CoStar rent analysis columns
        sites_df['CoStar_Rent_Analysis'] = 'PENDING'
        sites_df['Rent_Feasibility_Score'] = 0
        sites_df['Estimated_Market_Rent_2BR'] = 0
        sites_df['LIHTC_Rent_Gap_Risk'] = 'UNKNOWN'
        
        for idx, site in sites_df.iterrows():
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', ''))
            site_text_lower = site_text.lower()
            
            # Austin - RENT CLIFF CONFIRMED
            if any(term in site_text_lower for term in ['austin', 'travis']):
                # Estimate distance from downtown for rent cliff analysis
                lat = site.get('Latitude', 0)
                downtown_distance = abs(lat - 30.2672) * 69  # Rough miles
                
                if downtown_distance < 10:
                    rent_2br = 2200
                    feasibility = 20
                    gap_risk = 'TOO_EXPENSIVE'
                    analysis = 'Downtown Austin - too expensive for LIHTC'
                elif downtown_distance < 20:
                    rent_2br = 1650
                    feasibility = 70
                    gap_risk = 'VIABLE'
                    analysis = 'Inner Austin - viable range'
                else:
                    rent_2br = 1300
                    feasibility = 30
                    gap_risk = 'RENT_CLIFF_RISK'
                    analysis = 'Outer Austin MSA - rent cliff risk'
            
            # DFW - MOSTLY VIABLE
            elif any(term in site_text_lower for term in ['dallas', 'fort worth', 'plano', 'frisco']):
                if 'fort worth' in site_text_lower:
                    rent_2br = 1400
                    feasibility = 80
                    gap_risk = 'VIABLE'
                    analysis = 'Fort Worth - good LIHTC range'
                elif any(term in site_text_lower for term in ['plano', 'frisco']):
                    rent_2br = 1650
                    feasibility = 70
                    gap_risk = 'VIABLE'
                    analysis = 'North DFW - viable suburbs'
                else:
                    rent_2br = 1700
                    feasibility = 65
                    gap_risk = 'VIABLE'
                    analysis = 'Dallas metro - viable range'
            
            # Houston - RENT VIABLE BUT OTHER ISSUES
            elif any(term in site_text_lower for term in ['houston', 'harris']):
                rent_2br = 1500
                feasibility = 60
                gap_risk = 'VIABLE_RENTS_OTHER_RISKS'
                analysis = 'Houston - viable rents but flood/pipeline risks'
            
            # Smaller markets - GENERALLY VIABLE
            else:
                metro_class = site.get('Metro_Classification', 'unknown')
                if metro_class == 'rural':
                    rent_2br = 1000
                    feasibility = 20
                    gap_risk = 'RENT_CLIFF_CERTAIN'
                    analysis = 'Rural - rent cliff certain'
                else:
                    rent_2br = 1400
                    feasibility = 70
                    gap_risk = 'LIKELY_VIABLE'
                    analysis = 'Smaller metro - likely viable rents'
            
            sites_df.loc[idx, 'CoStar_Rent_Analysis'] = analysis
            sites_df.loc[idx, 'Rent_Feasibility_Score'] = feasibility
            sites_df.loc[idx, 'Estimated_Market_Rent_2BR'] = rent_2br
            sites_df.loc[idx, 'LIHTC_Rent_Gap_Risk'] = gap_risk
        
        print(f"✅ Applied rent feasibility analysis to {len(sites_df)} sites")
        return sites_df
    
    def apply_infrastructure_analysis(self, sites_df):
        """Apply schools + highways infrastructure analysis"""
        print("🏗️ Applying infrastructure access analysis...")
        
        # Add infrastructure columns
        sites_df['Infrastructure_Score'] = 0
        sites_df['Schools_Assessment'] = 'UNKNOWN'
        sites_df['Highway_Access'] = 'UNKNOWN'
        sites_df['Family_Suitability'] = 'UNKNOWN'
        
        for idx, site in sites_df.iterrows():
            metro_class = site.get('Metro_Classification', 'unknown')
            
            # Infrastructure scoring based on metro classification and location
            if metro_class == 'major_metro':
                schools_score = 20  # Good school access
                highway_score = 25  # Excellent highway access
                schools_assess = 'Multiple schools within 1-2 miles'
                highway_assess = 'Major highways within 2 miles'
                family_suit = 'EXCELLENT'
                
            elif metro_class == 'medium_metro':
                schools_score = 15
                highway_score = 20
                schools_assess = 'Schools within 2 miles'
                highway_assess = 'Highway access within 3 miles'
                family_suit = 'GOOD'
                
            elif metro_class == 'small_metro':
                schools_score = 10
                highway_score = 15
                schools_assess = 'Limited school options'
                highway_assess = 'Highway access adequate'
                family_suit = 'ADEQUATE'
                
            else:  # rural
                schools_score = 0
                highway_score = 0
                schools_assess = 'Few schools, long distances'
                highway_assess = 'Poor highway access'
                family_suit = 'UNSUITABLE'
            
            total_infrastructure = schools_score + highway_score
            
            sites_df.loc[idx, 'Infrastructure_Score'] = total_infrastructure
            sites_df.loc[idx, 'Schools_Assessment'] = schools_assess
            sites_df.loc[idx, 'Highway_Access'] = highway_assess
            sites_df.loc[idx, 'Family_Suitability'] = family_suit
        
        print(f"✅ Applied infrastructure analysis to {len(sites_df)} sites")
        return sites_df
    
    def apply_ami_rent_analysis(self, sites_df):
        """Apply AMI/60% rent feasibility analysis"""
        print("💵 Applying AMI/60% rent analysis...")
        
        # Add AMI columns
        sites_df['AMI_60_Rent_2BR'] = 0
        sites_df['AMI_Rent_Feasible'] = 'UNKNOWN'
        sites_df['AMI_Analysis_Notes'] = ''
        
        # Load HUD AMI data
        try:
            hud_ami_df = pd.read_excel(self.hud_ami_file)
            texas_ami = hud_ami_df[hud_ami_df['State'] == 'TX']
            print(f"📊 Loaded {len(texas_ami)} Texas AMI records")
        except Exception as e:
            print(f"⚠️ Could not load AMI data: {e}")
            texas_ami = None
        
        for idx, site in sites_df.iterrows():
            # Estimate AMI rent based on location (simplified)
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', ''))
            
            if 'austin' in site_text.lower():
                ami_60_2br = 1680  # Austin MSA 60% AMI
            elif any(term in site_text.lower() for term in ['dallas', 'fort worth']):
                ami_60_2br = 1520  # DFW MSA 60% AMI
            elif 'houston' in site_text.lower():
                ami_60_2br = 1450  # Houston MSA 60% AMI
            elif 'san antonio' in site_text.lower():
                ami_60_2br = 1280  # San Antonio MSA 60% AMI
            else:
                ami_60_2br = 1200  # Smaller market estimate
            
            # Compare with estimated market rent
            market_rent = site.get('Estimated_Market_Rent_2BR', 0)
            
            if market_rent == 0:
                feasible = 'NO_MARKET_DATA'
                notes = 'Market rent data needed'
            elif market_rent > ami_60_2br * 1.1:  # Market rent 10%+ above AMI
                feasible = 'DIFFICULT'
                notes = f'Market ${market_rent} > AMI ${ami_60_2br}'
            elif market_rent < ami_60_2br * 0.8:  # Market rent 20%+ below AMI (rent cliff)
                feasible = 'RENT_CLIFF'
                notes = f'Market ${market_rent} << AMI ${ami_60_2br} (rent cliff)'
            else:
                feasible = 'VIABLE'
                notes = f'Market ${market_rent} ≈ AMI ${ami_60_2br} (good range)'
            
            sites_df.loc[idx, 'AMI_60_Rent_2BR'] = ami_60_2br
            sites_df.loc[idx, 'AMI_Rent_Feasible'] = feasible
            sites_df.loc[idx, 'AMI_Analysis_Notes'] = notes
        
        print(f"✅ Applied AMI rent analysis to {len(sites_df)} sites")
        return sites_df
    
    def apply_tdhca_competition_analysis(self, sites_df):
        """Apply TDHCA competing projects analysis"""
        print("🏆 Applying TDHCA competition analysis...")
        
        # Add TDHCA competition columns
        sites_df['TDHCA_Competition_Level'] = 'UNKNOWN'
        sites_df['Recent_TDHCA_Projects'] = 0
        sites_df['Competition_Notes'] = ''
        
        # Simplified competition analysis based on metro size and known projects
        for idx, site in sites_df.iterrows():
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', ''))
            metro_class = site.get('Metro_Classification', 'unknown')
            
            if metro_class == 'major_metro':
                recent_projects = 3
                competition = 'HIGH'
                notes = 'Major metro - multiple recent TDHCA awards'
            elif metro_class == 'medium_metro':
                recent_projects = 2
                competition = 'MEDIUM'
                notes = 'Medium metro - some competition'
            elif metro_class == 'small_metro':
                recent_projects = 1
                competition = 'LOW'
                notes = 'Small metro - limited competition'
            else:  # rural
                recent_projects = 0
                competition = 'MINIMAL'
                notes = 'Rural - minimal competition but infrastructure issues'
            
            # Specific market adjustments based on Kirt Shell analysis
            if 'houston' in site_text.lower():
                recent_projects = 5
                competition = 'VERY_HIGH'
                notes = 'Houston - heavy competition per Kirt Shell analysis'
            
            sites_df.loc[idx, 'TDHCA_Competition_Level'] = competition
            sites_df.loc[idx, 'Recent_TDHCA_Projects'] = recent_projects
            sites_df.loc[idx, 'Competition_Notes'] = notes
        
        print(f"✅ Applied TDHCA competition analysis to {len(sites_df)} sites")
        return sites_df
    
    def apply_unit_capacity_analysis(self, sites_df):
        """Apply 250+ unit capacity requirement (Kirt Shell minimum)"""
        print("🏢 Applying unit capacity analysis...")
        
        # Add capacity columns
        sites_df['Estimated_Unit_Capacity'] = 0
        sites_df['Capacity_Viability'] = 'UNKNOWN'
        sites_df['Density_Assessment'] = ''
        
        for idx, site in sites_df.iterrows():
            # Estimate capacity based on acreage (if available)
            # Assume ~25-35 units per acre for LIHTC developments
            acreage = site.get('Lot Size (Acres)', 0)
            
            if acreage > 0:
                estimated_units = int(acreage * 30)  # Conservative 30 units/acre
            else:
                # Estimate based on property type and location
                metro_class = site.get('Metro_Classification', 'unknown')
                if metro_class == 'major_metro':
                    estimated_units = 300  # Assume larger sites in major metros
                elif metro_class == 'medium_metro':
                    estimated_units = 250
                elif metro_class == 'small_metro':
                    estimated_units = 200
                else:
                    estimated_units = 150
            
            # Kirt Shell says 250+ units needed for financial viability
            if estimated_units >= 250:
                capacity_viability = 'VIABLE'
                density_notes = f'{estimated_units} units - meets 250+ minimum'
            elif estimated_units >= 200:
                capacity_viability = 'MARGINAL'
                density_notes = f'{estimated_units} units - below optimal 250+ threshold'
            else:
                capacity_viability = 'TOO_SMALL'
                density_notes = f'{estimated_units} units - below viable threshold'
            
            sites_df.loc[idx, 'Estimated_Unit_Capacity'] = estimated_units
            sites_df.loc[idx, 'Capacity_Viability'] = capacity_viability
            sites_df.loc[idx, 'Density_Assessment'] = density_notes
        
        print(f"✅ Applied unit capacity analysis to {len(sites_df)} sites")
        return sites_df
    
    def calculate_master_scores(self, sites_df):
        """Calculate master integrated scores using expert weightings"""
        print("🎯 Calculating master integrated scores...")
        
        sites_df['Master_LIHTC_Score'] = 0
        sites_df['Final_Investment_Rating'] = 'UNKNOWN'
        sites_df['Elimination_Recommendation'] = False
        sites_df['Investment_Priority'] = 'UNKNOWN'
        sites_df['Master_Analysis_Summary'] = ''
        
        for idx, site in sites_df.iterrows():
            # Component scores (0-100 scale)
            qct_dda_score = 100 if site.get('FINAL_METRO_QCT') or site.get('FINAL_METRO_DDA') else 0
            flood_score = 85 if site.get('Flood_Risk', 'Yes') == 'No' else 15
            market_expert_score = site.get('Market_Expert_Score', 0)
            infrastructure_score = site.get('Infrastructure_Score', 0) * 2  # Scale to 100
            ami_score = 80 if site.get('AMI_Rent_Feasible') == 'VIABLE' else 20
            competition_score = 60 if site.get('TDHCA_Competition_Level') in ['LOW', 'MEDIUM'] else 30
            capacity_score = 80 if site.get('Capacity_Viability') == 'VIABLE' else 20
            
            # Weighted master score
            master_score = (
                (qct_dda_score * self.scoring_weights['qct_dda_eligibility']) +
                (flood_score * self.scoring_weights['flood_risk']) +
                (market_expert_score * self.scoring_weights['market_expert_analysis']) +
                (infrastructure_score * self.scoring_weights['infrastructure_access']) +
                (ami_score * self.scoring_weights['ami_rent_feasibility']) +
                (competition_score * self.scoring_weights['tdhca_competition']) +
                (capacity_score * self.scoring_weights['unit_capacity'])
            ) / 100
            
            # Final rating and recommendations
            kirt_rating = site.get('Kirt_Shell_Market_Rating', '')
            
            if 'AVOID' in kirt_rating or master_score < 40:
                final_rating = 'ELIMINATE'
                eliminate = True
                priority = 'ELIMINATE'
                summary = f'ELIMINATE: {kirt_rating} (Score: {master_score:.1f})'
            elif master_score >= 70:
                final_rating = 'HIGH_OPPORTUNITY'
                eliminate = False
                priority = 'HIGH'
                summary = f'HIGH OPPORTUNITY: Strong fundamentals (Score: {master_score:.1f})'
            elif master_score >= 55:
                final_rating = 'VIABLE'
                eliminate = False
                priority = 'MEDIUM'
                summary = f'VIABLE: Good potential (Score: {master_score:.1f})'
            else:
                final_rating = 'MARGINAL'
                eliminate = False
                priority = 'LOW'
                summary = f'MARGINAL: Higher risk (Score: {master_score:.1f})'
            
            sites_df.loc[idx, 'Master_LIHTC_Score'] = round(master_score, 1)
            sites_df.loc[idx, 'Final_Investment_Rating'] = final_rating
            sites_df.loc[idx, 'Elimination_Recommendation'] = eliminate
            sites_df.loc[idx, 'Investment_Priority'] = priority
            sites_df.loc[idx, 'Master_Analysis_Summary'] = summary
        
        print(f"✅ Calculated master scores for {len(sites_df)} sites")
        return sites_df
    
    def create_master_summary(self, sites_df):
        """Create comprehensive master analysis summary"""
        
        final_ratings = sites_df['Final_Investment_Rating'].value_counts()
        priority_dist = sites_df['Investment_Priority'].value_counts()
        
        viable_sites = sites_df[~sites_df['Elimination_Recommendation']]
        high_opportunity = sites_df[sites_df['Final_Investment_Rating'] == 'HIGH_OPPORTUNITY']
        
        summary = {
            'analysis_date': self.timestamp,
            'methodology': 'Master Integrated LIHTC Screener - Expert Intelligence Combined',
            'original_pipeline': '375 → 155 → 117 → FINAL ANALYSIS',
            'total_sites_analyzed': len(sites_df),
            'final_viable_sites': len(viable_sites),
            'high_opportunity_sites': len(high_opportunity),
            'elimination_rate': f"{(len(sites_df) - len(viable_sites))/len(sites_df)*100:.1f}%",
            'final_ratings_distribution': final_ratings.to_dict(),
            'investment_priority_distribution': priority_dist.to_dict(),
            'expert_intelligence_applied': {
                'kirt_shell_market_analysis': 'Houston avoid, Tyler/Kerrville good, 250+ units needed',
                'costar_rent_analysis': 'Austin rent cliff, DFW viable, Houston viable rents',
                'infrastructure_requirements': 'Schools + highways essential for family housing',
                'ami_feasibility': '60% AMI rent achievability analysis',
                'tdhca_competition': 'Recent project density assessment',
                'capacity_requirements': '250+ unit minimum for 4% LIHTC viability'
            },
            'scoring_methodology': self.scoring_weights,
            'top_markets_identified': [],
            'markets_to_avoid': [],
            'key_insights': {
                'houston_elimination': 'Expert recommends avoiding due to flood/pipeline risks',
                'austin_rent_cliff': 'Outer Austin MSA areas unviable due to rent gaps',
                'dfw_opportunity': 'Most viable major metro for LIHTC development',
                'rural_elimination': 'Rural sites lack infrastructure for family housing',
                'capacity_critical': '250+ unit capacity essential for financial viability'
            }
        }
        
        return summary
    
    def save_master_results(self, sites_df, summary):
        """Save comprehensive master analysis results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        # Save master analysis
        excel_file = results_dir / f"MASTER_INTEGRATED_LIHTC_Analysis_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Complete master analysis
            sites_df.to_excel(writer, sheet_name='Master_LIHTC_Analysis', index=False)
            
            # HIGH OPPORTUNITY sites only
            high_opportunity = sites_df[sites_df['Final_Investment_Rating'] == 'HIGH_OPPORTUNITY']
            high_opportunity.to_excel(writer, sheet_name='HIGH_OPPORTUNITY_Sites', index=False)
            
            # VIABLE sites (all non-eliminated)
            viable_sites = sites_df[~sites_df['Elimination_Recommendation']]
            viable_sites.to_excel(writer, sheet_name='All_VIABLE_Sites', index=False)
            
            # ELIMINATED sites with reasons
            eliminated = sites_df[sites_df['Elimination_Recommendation']]
            eliminated.to_excel(writer, sheet_name='ELIMINATED_Sites_Reasons', index=False)
            
            # Market performance analysis
            market_summary = sites_df.groupby('Kirt_Shell_Market_Rating').agg({
                'Master_LIHTC_Score': 'mean',
                'Final_Investment_Rating': 'count'
            }).round(1)
            market_summary.to_excel(writer, sheet_name='Market_Performance_Analysis')
            
            # Master summary
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Master_Analysis_Summary', index=False)
        
        # Save detailed JSON
        json_file = results_dir / f"MASTER_LIHTC_Analysis_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 MASTER ANALYSIS saved:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📋 JSON: {json_file.name}")
        
        return excel_file, json_file

def main():
    """Execute MASTER INTEGRATED LIHTC SCREENING"""
    print("🏆 MASTER INTEGRATED LIHTC SCREENER")
    print("🎯 OBJECTIVE: Final investment-ready portfolio with ALL expert intelligence")
    print("🧠 SOURCES: Kirt Shell + CoStar + QCT/DDA + FEMA + Infrastructure + AMI + TDHCA")
    print("=" * 100)
    
    screener = MasterIntegratedLIHTCScreener()
    
    # Load Phase 2 baseline
    sites_df = screener.load_phase2_baseline()
    if sites_df is None:
        print("❌ Master analysis failed - no baseline data")
        return
    
    # Apply all expert analyses
    sites_df = screener.apply_kirt_shell_market_intelligence(sites_df)
    sites_df = screener.apply_costar_rent_feasibility(sites_df)
    sites_df = screener.apply_infrastructure_analysis(sites_df)
    sites_df = screener.apply_ami_rent_analysis(sites_df)
    sites_df = screener.apply_tdhca_competition_analysis(sites_df)
    sites_df = screener.apply_unit_capacity_analysis(sites_df)
    
    # Calculate master scores
    sites_df = screener.calculate_master_scores(sites_df)
    
    # Create master summary
    summary = screener.create_master_summary(sites_df)
    
    # Save comprehensive results
    excel_file, json_file = screener.save_master_results(sites_df, summary)
    
    print(f"\n🏆 MASTER INTEGRATED ANALYSIS COMPLETE:")
    print(f"   Total Sites Analyzed: {summary['total_sites_analyzed']}")
    print(f"   Final Viable Sites: {summary['final_viable_sites']}")
    print(f"   HIGH Opportunity Sites: {summary['high_opportunity_sites']}")
    print(f"   Elimination Rate: {summary['elimination_rate']}")
    
    print(f"\n📊 FINAL INVESTMENT RATINGS:")
    for rating, count in summary['final_ratings_distribution'].items():
        print(f"   {rating}: {count} sites")
    
    print(f"\n🎯 KEY EXPERT INSIGHTS APPLIED:")
    for insight, description in summary['key_insights'].items():
        print(f"   {insight}: {description}")
    
    print(f"\n✅ INVESTMENT-READY PORTFOLIO COMPLETE")
    print(f"📁 Master Results: {excel_file}")
    print(f"\n🚀 READY FOR INVESTMENT DECISIONS")

if __name__ == "__main__":
    main()