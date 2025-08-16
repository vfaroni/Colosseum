#!/usr/bin/env python3
"""
CoStar Land Use Filter - Phase 6 Simplified Implementation
Mission: VITOR-WINGMAN-LANDUSE-004

Uses CoStar's own Secondary Type classifications to eliminate prohibited sites.
Much faster and more reliable than API lookups since CoStar has already done the analysis.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

class CoStarLandUseFilter:
    """
    Filter sites based on CoStar Secondary Type classifications
    
    Eliminates sites that CoStar has already identified as:
    - Agricultural
    - Industrial 
    - Other prohibited uses for LIHTC development
    """
    
    # Prohibited secondary types from CoStar
    PROHIBITED_SECONDARY_TYPES = {
        'Agricultural': 'Agricultural land unsuitable for LIHTC residential development',
        'Industrial': 'Industrial zoning/use incompatible with affordable housing',
        # Add more as needed based on CoStar classifications
    }
    
    # Suitable secondary types
    SUITABLE_SECONDARY_TYPES = {
        'Residential': 'Suitable for residential LIHTC development',
        'Commercial': 'Suitable for mixed-use or adaptive reuse LIHTC development',
        'Land': 'Vacant/undeveloped land suitable for new construction'
    }
    
    def __init__(self):
        print("🏛️ COSTAR LAND USE FILTER - PHASE 6")
        print("Mission: VITOR-WINGMAN-LANDUSE-004")
        print("Using CoStar Secondary Type Classifications")
        print("=" * 50)
    
    def analyze_dataset(self, dataset_path: str):
        """
        Analyze dataset using CoStar Secondary Type classifications
        
        Args:
            dataset_path: Path to Excel file with CoStar data
        """
        
        # Load dataset
        df = pd.read_excel(dataset_path)
        total_sites = len(df)
        
        print(f"📊 Dataset loaded: {total_sites} sites")
        print()
        print("Secondary Type distribution:")
        secondary_counts = df['Secondary Type'].value_counts()
        print(secondary_counts)
        print()
        
        # Analyze each site
        df['Land_Use_Status'] = df['Secondary Type'].apply(self._classify_land_use)
        df['Elimination_Reason'] = df['Secondary Type'].apply(self._get_elimination_reason)
        df['Is_Suitable'] = df['Land_Use_Status'] == 'SUITABLE'
        
        # Count results
        eliminated = df[df['Land_Use_Status'] == 'ELIMINATED']
        flagged = df[df['Land_Use_Status'] == 'FLAGGED']
        suitable = df[df['Land_Use_Status'] == 'SUITABLE']
        
        print("🚫 LAND USE FILTERING RESULTS")
        print("=" * 35)
        print(f"Total Sites Analyzed: {total_sites}")
        print(f"Sites Eliminated: {len(eliminated)}")
        print(f"Sites Flagged for Review: {len(flagged)}")
        print(f"Sites Suitable: {len(suitable)}")
        print(f"Elimination Rate: {len(eliminated)/total_sites*100:.1f}%")
        print()
        
        # Show eliminated sites
        if len(eliminated) > 0:
            print("❌ ELIMINATED SITES")
            print("-" * 25)
            for idx, row in eliminated.iterrows():
                print(f"• {row['Property Address']}")
                print(f"  City: {row['City']}, County: {row.get('County Name', 'N/A')}")
                print(f"  Secondary Type: {row['Secondary Type']}")
                print(f"  Reason: {row['Elimination_Reason']}")
                print()
        
        # Show flagged sites
        if len(flagged) > 0:
            print("⚠️  FLAGGED SITES (Manual Review Required)")
            print("-" * 45)
            for idx, row in flagged.iterrows():
                print(f"• {row['Property Address']}")
                print(f"  City: {row['City']}")
                print(f"  Secondary Type: {row['Secondary Type']}")
                print()
        
        # Generate output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Full results
        results_file = f"CoStar_LandUse_Analysis_{timestamp}.csv"
        df.to_csv(results_file, index=False)
        
        # Eliminated sites only
        eliminated_file = f"CoStar_LandUse_Eliminated_{timestamp}.csv"
        eliminated.to_csv(eliminated_file, index=False)
        
        # Create filtered dataset (suitable sites only)
        suitable_file = f"CoStar_LandUse_Filtered_Dataset_{timestamp}.xlsx"
        suitable.to_excel(suitable_file, index=False)
        
        print("💾 OUTPUT FILES CREATED:")
        print(f"  📊 Full Analysis: {results_file}")
        print(f"  ❌ Eliminated Sites: {eliminated_file}")
        print(f"  ✅ Filtered Dataset: {suitable_file}")
        print()
        
        # Summary statistics
        print("📈 ELIMINATION BY SECONDARY TYPE")
        print("-" * 35)
        type_summary = df.groupby(['Secondary Type', 'Land_Use_Status']).size().unstack(fill_value=0)
        print(type_summary)
        
        return df, eliminated, suitable
    
    def _classify_land_use(self, secondary_type):
        """Classify land use based on CoStar Secondary Type"""
        if pd.isna(secondary_type):
            return 'FLAGGED'  # Unknown requires manual review
        
        if secondary_type in self.PROHIBITED_SECONDARY_TYPES:
            return 'ELIMINATED'
        elif secondary_type in self.SUITABLE_SECONDARY_TYPES:
            return 'SUITABLE'
        else:
            return 'FLAGGED'  # Unknown secondary type
    
    def _get_elimination_reason(self, secondary_type):
        """Get explanation for elimination/retention decision"""
        if pd.isna(secondary_type):
            return 'Unknown secondary type - manual review required'
        
        if secondary_type in self.PROHIBITED_SECONDARY_TYPES:
            return self.PROHIBITED_SECONDARY_TYPES[secondary_type]
        elif secondary_type in self.SUITABLE_SECONDARY_TYPES:
            return self.SUITABLE_SECONDARY_TYPES[secondary_type]
        else:
            return f'Unknown secondary type "{secondary_type}" - manual review required'

def analyze_costar_export(dataset_path: str):
    """Analyze a CoStar export file for land use filtering"""
    
    if not Path(dataset_path).exists():
        print(f"❌ Dataset not found: {dataset_path}")
        return None
    
    filter_engine = CoStarLandUseFilter()
    return filter_engine.analyze_dataset(dataset_path)

if __name__ == "__main__":
    # Test with CoStar export file
    dataset_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-15.xlsx"
    
    results = analyze_costar_export(dataset_path)
    
    if results:
        print("\n✅ COSTAR LAND USE FILTERING COMPLETE")
        print("CoStar's classifications used for fast, accurate filtering")