#!/usr/bin/env python3
"""
Enhanced 6-Factor Anchor Scoring System
Combines existing anchor analysis with highway proximity data

Scoring Factors:
1. Schools (2.5 mi) - 30% (reduced from 40%)
2. City Incorporation - 15% (reduced from 20%) 
3. LIHTC Market Validation - 25% (reduced from 30%)
4. Community Scale - 10% (unchanged)
5. Highway Access - 15% (NEW)
6. Utility Service - 5% (NEW - simplified approach)

Author: Claude Code
Date: July 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAnchorScoring:
    """Enhanced 6-factor anchor scoring system"""
    
    def __init__(self):
        # Enhanced scoring weights
        self.scoring_weights = {
            'schools_2_5_miles': 0.30,      # Reduced from 0.40
            'city_incorporation': 0.15,     # Reduced from 0.20
            'lihtc_market_validation': 0.25, # Reduced from 0.30
            'community_scale': 0.10,        # Unchanged
            'highway_access': 0.15,         # NEW
            'utility_service': 0.05         # NEW
        }
        
        # Score thresholds for classification
        self.classification_thresholds = {
            'Exceptional': 4.5,    # 90%+ of max score
            'Excellent': 4.0,      # 80%+ of max score  
            'Good': 3.0,           # 60%+ of max score
            'Fair': 2.0,           # 40%+ of max score
            'Poor': 1.0,           # 20%+ of max score
            'Isolated': 0.0        # Below 20%
        }
    
    def load_data(self):
        """Load existing anchor analysis and highway proximity data"""
        
        # Load original anchor analysis
        anchor_file = "Complete_Anchor_Analysis_All_195_Sites_20250702_151312.xlsx"
        if not Path(anchor_file).exists():
            raise FileNotFoundError(f"Anchor analysis file not found: {anchor_file}")
        
        self.anchor_df = pd.read_excel(anchor_file, sheet_name='All_195_Sites_Ranked')
        logger.info(f"✅ Loaded {len(self.anchor_df)} sites from anchor analysis")
        
        # Load highway proximity analysis
        highway_files = list(Path('.').glob('Highway_Proximity_Analysis_*.xlsx'))
        if not highway_files:
            raise FileNotFoundError("Highway proximity analysis file not found")
        
        highway_file = max(highway_files)  # Get most recent
        self.highway_df = pd.read_excel(highway_file, sheet_name='Highway_Proximity_Analysis')
        logger.info(f"✅ Loaded {len(self.highway_df)} sites from highway analysis")
        
        # Merge datasets
        self._merge_datasets()
    
    def _merge_datasets(self):
        """Merge anchor and highway datasets"""
        
        # Merge on coordinates (most reliable)
        self.combined_df = pd.merge(
            self.anchor_df,
            self.highway_df[['Latitude', 'Longitude', 'Highway_Access_Score', 'Highway_Access_Rating',
                           'Interstate_Distance_Miles', 'US_Highway_Distance_Miles', 'State_Highway_Distance_Miles']],
            on=['Latitude', 'Longitude'],
            how='left'
        )
        
        logger.info(f"✅ Merged datasets: {len(self.combined_df)} sites total")
        
        # Check for missing highway data
        missing_highway = self.combined_df['Highway_Access_Score'].isna().sum()
        if missing_highway > 0:
            logger.warning(f"⚠️  {missing_highway} sites missing highway data - will use 0 score")
            self.combined_df['Highway_Access_Score'].fillna(0, inplace=True)
            self.combined_df['Highway_Access_Rating'].fillna('Isolated - No highway access', inplace=True)
    
    def calculate_utility_service_score(self):
        """Calculate simplified utility service score"""
        
        logger.info("🔧 Calculating utility service scores...")
        
        utility_scores = []
        
        for _, row in self.combined_df.iterrows():
            score = 0.0
            notes = []
            
            # Base scoring on city incorporation and population
            within_city = row.get('Within_City_Limits', False)
            city_name = row.get('City_Name', '')
            schools_count = row.get('Schools_Within_2_5mi', 0)
            
            if within_city and city_name:
                # Within incorporated city limits
                if schools_count >= 5:
                    # Large city - likely full utilities
                    score = 1.0
                    notes.append("Large incorporated city")
                elif schools_count >= 2:
                    # Medium city - likely has utilities
                    score = 0.8
                    notes.append("Medium incorporated city")
                else:
                    # Small city - utilities possible but uncertain
                    score = 0.6
                    notes.append("Small incorporated city")
            else:
                # Unincorporated area
                highway_score = row.get('Highway_Access_Score', 0)
                if highway_score >= 0.8:
                    # Good highway access - likely near development/utilities
                    score = 0.4
                    notes.append("Unincorporated, good highway access")
                elif highway_score >= 0.4:
                    # Some highway access
                    score = 0.2
                    notes.append("Unincorporated, limited highway access")
                else:
                    # Poor access - utilities unlikely
                    score = 0.0
                    notes.append("Unincorporated, poor access")
            
            utility_scores.append({
                'score': score,
                'notes': '; '.join(notes)
            })
        
        # Add to dataframe
        self.combined_df['Utility_Service_Score'] = [item['score'] for item in utility_scores]
        self.combined_df['Utility_Service_Notes'] = [item['notes'] for item in utility_scores]
        
        logger.info("✅ Utility service scores calculated")
    
    def calculate_enhanced_anchor_scores(self):
        """Calculate enhanced 6-factor anchor scores"""
        
        logger.info("📊 Calculating enhanced anchor scores...")
        
        enhanced_scores = []
        
        for _, row in self.combined_df.iterrows():
            # Extract original anchor components (normalized to 0-1)
            schools_score = min(row.get('Schools_Within_2_5mi', 0) / 2.0, 1.0)  # 2+ schools = max
            city_score = 1.0 if row.get('Within_City_Limits', False) else 0.0
            lihtc_score = min(row.get('LIHTC_Within_2mi', 0) / 2.0, 1.0)  # 2+ projects = max
            scale_score = min(row.get('Schools_Within_2_5mi', 0) / 5.0, 1.0)  # 5+ schools = max
            
            # New components (already 0-1 normalized)
            highway_score = row.get('Highway_Access_Score', 0)
            utility_score = row.get('Utility_Service_Score', 0)
            
            # Calculate weighted score
            total_score = (
                schools_score * self.scoring_weights['schools_2_5_miles'] +
                city_score * self.scoring_weights['city_incorporation'] +
                lihtc_score * self.scoring_weights['lihtc_market_validation'] +
                scale_score * self.scoring_weights['community_scale'] +
                highway_score * self.scoring_weights['highway_access'] +
                utility_score * self.scoring_weights['utility_service']
            ) * 5.0  # Scale to 0-5
            
            # Determine classification
            classification = self._classify_score(total_score)
            
            enhanced_scores.append({
                'Enhanced_Anchor_Score': round(total_score, 3),
                'Enhanced_Classification': classification,
                'Schools_Component': round(schools_score * self.scoring_weights['schools_2_5_miles'] * 5, 3),
                'City_Component': round(city_score * self.scoring_weights['city_incorporation'] * 5, 3),
                'LIHTC_Component': round(lihtc_score * self.scoring_weights['lihtc_market_validation'] * 5, 3),
                'Scale_Component': round(scale_score * self.scoring_weights['community_scale'] * 5, 3),
                'Highway_Component': round(highway_score * self.scoring_weights['highway_access'] * 5, 3),
                'Utility_Component': round(utility_score * self.scoring_weights['utility_service'] * 5, 3)
            })
        
        # Add to dataframe
        for key in enhanced_scores[0].keys():
            self.combined_df[key] = [item[key] for item in enhanced_scores]
        
        logger.info("✅ Enhanced anchor scores calculated")
    
    def _classify_score(self, score):
        """Classify score into categories"""
        for classification, threshold in self.classification_thresholds.items():
            if score >= threshold:
                return classification
        return 'Isolated'
    
    def generate_comparison_analysis(self):
        """Generate comparison between old and new scoring"""
        
        logger.info("📊 Generating comparison analysis...")
        
        # Compare classifications
        old_classification = self.combined_df['Priority_Classification']
        new_classification = self.combined_df['Enhanced_Classification']
        
        comparison_data = []
        
        for old_class in old_classification.unique():
            old_sites = self.combined_df[old_classification == old_class]
            
            for new_class in new_classification.unique():
                count = sum((old_classification == old_class) & (new_classification == new_class))
                if count > 0:
                    comparison_data.append({
                        'Original_Classification': old_class,
                        'Enhanced_Classification': new_class,
                        'Site_Count': count,
                        'Percentage': round(count / len(old_sites) * 100, 1)
                    })
        
        self.comparison_df = pd.DataFrame(comparison_data)
        
        # Summary statistics
        self.summary_stats = {
            'Total_Sites': len(self.combined_df),
            'Original_High_Priority': sum(old_classification == 'High Priority'),
            'Enhanced_Excellent_Plus': sum(new_classification.isin(['Exceptional', 'Excellent'])),
            'Improvement_Rate': round(
                sum(self.combined_df['Enhanced_Anchor_Score'] > self.combined_df['Anchor_Score']) / 
                len(self.combined_df) * 100, 1
            ),
            'Average_Score_Change': round(
                (self.combined_df['Enhanced_Anchor_Score'] - self.combined_df['Anchor_Score']).mean(), 3
            ),
            'Highway_Impact': round(self.combined_df['Highway_Component'].mean(), 3),
            'Utility_Impact': round(self.combined_df['Utility_Component'].mean(), 3)
        }
        
        logger.info("✅ Comparison analysis complete")
    
    def save_results(self, output_file):
        """Save enhanced analysis results"""
        
        logger.info(f"💾 Saving enhanced analysis to: {output_file}")
        
        with pd.ExcelWriter(output_file) as writer:
            # Main results
            self.combined_df.to_excel(writer, sheet_name='Enhanced_Analysis_All_Sites', index=False)
            
            # Classification summaries
            for classification in self.combined_df['Enhanced_Classification'].unique():
                if pd.notna(classification):
                    sites = self.combined_df[self.combined_df['Enhanced_Classification'] == classification]
                    sheet_name = classification.replace(' ', '_')[:31]
                    sites.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Comparison analysis
            self.comparison_df.to_excel(writer, sheet_name='Classification_Comparison', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([self.summary_stats]).T
            summary_df.columns = ['Value']
            summary_df.to_excel(writer, sheet_name='Summary_Statistics')
            
            # Methodology documentation
            methodology_data = [
                ['Enhanced Anchor Scoring Methodology', '', ''],
                ['', '', ''],
                ['Scoring Components:', 'Weight', 'Description'],
                ['Schools (2.5 miles)', '30%', 'Number of schools within 2.5 miles'],
                ['City Incorporation', '15%', 'Within incorporated city limits'],
                ['LIHTC Market Validation', '25%', 'LIHTC projects within 2 miles'],
                ['Community Scale', '10%', 'School count as proxy for population'],
                ['Highway Access', '15%', 'Distance to Interstate/US/State highways'],
                ['Utility Service', '5%', 'Estimated utility service availability'],
                ['', '', ''],
                ['Classification Thresholds:', 'Score Range', 'Description'],
                ['Exceptional', '4.5 - 5.0', 'Outstanding infrastructure (90%+)'],
                ['Excellent', '4.0 - 4.5', 'Strong infrastructure (80%+)'],
                ['Good', '3.0 - 4.0', 'Adequate infrastructure (60%+)'],
                ['Fair', '2.0 - 3.0', 'Limited infrastructure (40%+)'],
                ['Poor', '1.0 - 2.0', 'Minimal infrastructure (20%+)'],
                ['Isolated', '0.0 - 1.0', 'Insufficient infrastructure (<20%)']
            ]
            
            methodology_df = pd.DataFrame(methodology_data, columns=['Component', 'Value', 'Description'])
            methodology_df.to_excel(writer, sheet_name='Enhanced_Methodology', index=False)
        
        logger.info("✅ Results saved successfully")

def main():
    """Run enhanced anchor scoring analysis"""
    
    scorer = EnhancedAnchorScoring()
    
    # Load and merge data
    scorer.load_data()
    
    # Calculate utility scores
    scorer.calculate_utility_service_score()
    
    # Calculate enhanced anchor scores
    scorer.calculate_enhanced_anchor_scores()
    
    # Generate comparison analysis
    scorer.generate_comparison_analysis()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Enhanced_Anchor_Analysis_{timestamp}.xlsx"
    scorer.save_results(output_file)
    
    # Print summary
    print("\n🎯 ENHANCED ANCHOR SCORING ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total Sites Analyzed: {scorer.summary_stats['Total_Sites']}")
    print(f"\nClassification Changes:")
    print(f"  Original High Priority: {scorer.summary_stats['Original_High_Priority']} sites")
    print(f"  Enhanced Excellent+:   {scorer.summary_stats['Enhanced_Excellent_Plus']} sites")
    print(f"\nScoring Impact:")
    print(f"  Sites with improved scores: {scorer.summary_stats['Improvement_Rate']}%")
    print(f"  Average score change: {scorer.summary_stats['Average_Score_Change']:+.3f}")
    print(f"  Highway component avg: {scorer.summary_stats['Highway_Impact']:.3f}")
    print(f"  Utility component avg: {scorer.summary_stats['Utility_Impact']:.3f}")
    print(f"\n✅ Analysis saved to: {output_file}")

if __name__ == "__main__":
    main()