#!/usr/bin/env python3
"""
CoStar 375 Sites Batch Processor - Handles large dataset with checkpoints
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime

# Add the CTCAC code directory to path for imports
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

class CoStar375BatchProcessor:
    """Process CoStar 375 sites in batches with checkpoint saving"""
    
    def __init__(self):
        self.costar_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx"
        self.output_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/"
        self.checkpoint_file = f"{self.output_path}checkpoint_progress.json"
        self.qct_dda_analyzer = ComprehensiveQCTDDAAnalyzer()
        
    def save_checkpoint(self, df, stage, batch_num=None):
        """Save progress checkpoint"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if batch_num:
            filename = f"checkpoint_{stage}_batch_{batch_num}_{timestamp}.xlsx"
        else:
            filename = f"checkpoint_{stage}_{timestamp}.xlsx"
        
        filepath = f"{self.output_path}{filename}"
        df.to_excel(filepath, index=False)
        print(f"💾 Checkpoint saved: {filename}")
        return filepath
    
    def load_costar_data(self):
        """Load and analyze CoStar structure"""
        print("🔍 LOADING COSTAR DATA...")
        df = pd.read_excel(self.costar_file)
        print(f"✅ Loaded {len(df)} CoStar sites")
        print(f"📊 Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
        return df
    
    def process_density_screening(self, df):
        """Apply density and unit count screening"""
        print("🏗️ APPLYING DENSITY SCREENING...")
        
        # Find the size column - try different possible names
        size_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['size', 'sf', 'acre', 'land']):
                if 'sf' in col.lower() and ('gross' in col.lower() or 'net' in col.lower()):
                    size_col = col
                    break
        
        if not size_col:
            print("⚠️ Could not find size column - using 'Land SF Gross' as default")
            size_col = 'Land SF Gross'
        
        print(f"📏 Using size column: {size_col}")
        
        # Add analysis columns with proper NaN handling
        df['Acres_Calculated'] = pd.to_numeric(df[size_col], errors='coerce') / 43560  # Convert SF to acres
        df['Max_Units_17_Acre'] = (df['Acres_Calculated'] * 17).fillna(0).astype(int)
        df['Max_Units_18_Acre'] = (df['Acres_Calculated'] * 18).fillna(0).astype(int)
        df['Density_Viable'] = df['Max_Units_18_Acre'] >= 250
        df['Unit_Count_Category'] = df['Max_Units_18_Acre'].apply(self.categorize_unit_count)
        
        viable_count = len(df[df['Density_Viable']])
        print(f"✅ Density Analysis Complete: {viable_count}/{len(df)} sites viable (250+ units)")
        
        return df
    
    def categorize_unit_count(self, units):
        """Categorize unit count for LIHTC viability"""
        if units >= 400:
            return "EXCELLENT (400+ units)"
        elif units >= 300:
            return "STRONG (300+ units)"
        elif units >= 250:
            return "VIABLE (250+ units)"
        else:
            return f"UNDERSIZED ({units} units)"
    
    def quick_qct_dda_analysis(self, df):
        """Quick QCT/DDA analysis without full geographic lookup"""
        print("🎯 RUNNING QUICK QCT/DDA CHECK...")
        
        df['QCT_DDA_Status'] = 'Pending Full Analysis'
        df['Basis_Boost_Eligible'] = 'TBD'
        df['QCT_DDA_Notes'] = 'Phase 2 M4 Beast Analysis Required'
        
        # For now, mark as pending - M4 Beast will do full analysis
        print("✅ QCT/DDA Quick Check Complete - Full analysis queued for M4 Beast")
        return df
    
    def export_phase1_results(self, df):
        """Export Phase 1 screening results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export full analysis
        full_file = f"{self.output_path}CoStar_375_Phase1_Screening_{timestamp}.xlsx"
        df.to_excel(full_file, index=False)
        print(f"💾 Phase 1 complete analysis: {full_file}")
        
        # Export density viable sites
        viable_df = df[df['Density_Viable']].copy()
        viable_file = f"{self.output_path}CoStar_375_Density_Viable_Sites_{timestamp}.xlsx"
        viable_df.to_excel(viable_file, index=False)
        print(f"🎯 Density viable sites: {viable_file}")
        
        # Export top sites for M4 Beast analysis
        top_df = df[df['Max_Units_18_Acre'] >= 300].copy().sort_values('Max_Units_18_Acre', ascending=False)
        top_file = f"{self.output_path}CoStar_375_TOP_Sites_M4_Analysis_{timestamp}.xlsx"
        top_df.to_excel(top_file, index=False)
        print(f"🏆 Top sites for M4 Beast: {top_file}")
        
        return full_file, viable_file, top_file
    
    def generate_summary_report(self, df):
        """Generate summary statistics"""
        print("\\n📊 PHASE 1 SUMMARY REPORT")
        print("=" * 50)
        print(f"📋 Total Sites Analyzed: {len(df)}")
        print(f"🏗️ Density Viable (250+ units): {len(df[df['Density_Viable']])}")
        print(f"💪 Strong Sites (300+ units): {len(df[df['Max_Units_18_Acre'] >= 300])}")
        print(f"🏆 Excellent Sites (400+ units): {len(df[df['Max_Units_18_Acre'] >= 400])}")
        
        # Unit count distribution
        print("\\n📈 UNIT COUNT DISTRIBUTION:")
        unit_ranges = [
            (250, 299, "Viable"),
            (300, 399, "Strong"), 
            (400, 499, "Excellent"),
            (500, float('inf'), "Premium")
        ]
        
        for min_units, max_units, category in unit_ranges:
            if max_units == float('inf'):
                count = len(df[df['Max_Units_18_Acre'] >= min_units])
                print(f"  {category} ({min_units}+ units): {count}")
            else:
                count = len(df[(df['Max_Units_18_Acre'] >= min_units) & (df['Max_Units_18_Acre'] < max_units)])
                print(f"  {category} ({min_units}-{max_units} units): {count}")
        
        # Geographic distribution
        print("\\n🗺️ GEOGRAPHIC DISTRIBUTION (Top 10):")
        city_counts = df['City'].value_counts().head(10)
        for city, count in city_counts.items():
            print(f"  {city}: {count} sites")
        
        print("\\n🎯 READY FOR M4 BEAST PHASE 2 COMPREHENSIVE ANALYSIS")
    
    def run_phase1_batch_analysis(self):
        """Execute Phase 1 batch analysis"""
        print("🚀 STARTING PHASE 1 BATCH ANALYSIS")
        print("=" * 60)
        
        try:
            # Step 1: Load data
            df = self.load_costar_data()
            self.save_checkpoint(df, "01_loaded")
            
            # Step 2: Density screening
            df = self.process_density_screening(df)
            self.save_checkpoint(df, "02_density")
            
            # Step 3: Quick QCT/DDA check (full analysis for M4 Beast)
            df = self.quick_qct_dda_analysis(df)
            self.save_checkpoint(df, "03_qct_dda_quick")
            
            # Step 4: Export results
            files = self.export_phase1_results(df)
            
            # Step 5: Generate summary
            self.generate_summary_report(df)
            
            print("\\n✅ PHASE 1 BATCH ANALYSIS COMPLETE!")
            print("🚀 Ready to hand off to M4 Beast for Phase 2 comprehensive analysis")
            
            return df, files
            
        except Exception as e:
            print(f"❌ Error in batch analysis: {e}")
            import traceback
            traceback.print_exc()
            return None, None

if __name__ == "__main__":
    processor = CoStar375BatchProcessor()
    results = processor.run_phase1_batch_analysis()