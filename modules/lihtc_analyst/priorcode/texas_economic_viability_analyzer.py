#!/usr/bin/env python3
"""
Texas LIHTC Economic Viability Analyzer
Combines land analysis with construction costs and AMI rents for comprehensive site evaluation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json

class TexasEconomicViabilityAnalyzer:
    """Analyzes LIHTC site economic viability using construction costs and AMI rents"""
    
    def __init__(self):
        self.base_path = Path('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets')
        
        # Construction cost modifiers by metro area
        self.metro_modifiers = {
            # Major metros
            'Austin-Round Rock-Georgetown': 1.20,
            'Houston-The Woodlands-Sugar Land': 1.18,
            'Dallas-Plano-Irving': 1.17,
            'Fort Worth-Arlington-Grapevine': 1.15,
            'San Antonio-New Braunfels': 1.10,
            # Mid-size cities
            'El Paso': 1.05,
            'Corpus Christi': 1.08,
            'McAllen-Edinburg-Mission': 1.03,
            'Killeen-Temple': 1.05,
            'Beaumont-Port Arthur': 1.06,
            'Lubbock': 1.04,
            'Amarillo': 1.04,
            'Waco': 1.05,
            'Laredo': 1.03,
            'College Station-Bryan': 1.05
        }
        
        # County to metro mapping (expand as needed)
        self.county_metro_map = {
            'Travis': 'Austin-Round Rock-Georgetown',
            'Williamson': 'Austin-Round Rock-Georgetown',
            'Hays': 'Austin-Round Rock-Georgetown',
            'Harris': 'Houston-The Woodlands-Sugar Land',
            'Fort Bend': 'Houston-The Woodlands-Sugar Land',
            'Montgomery': 'Houston-The Woodlands-Sugar Land',
            'Dallas': 'Dallas-Plano-Irving',
            'Collin': 'Dallas-Plano-Irving',
            'Tarrant': 'Fort Worth-Arlington-Grapevine',
            'Bexar': 'San Antonio-New Braunfels',
            'El Paso': 'El Paso',
            'Nueces': 'Corpus Christi',
            'Hidalgo': 'McAllen-Edinburg-Mission',
            'Bell': 'Killeen-Temple',
            'Jefferson': 'Beaumont-Port Arthur',
            'Lubbock': 'Lubbock',
            'Potter': 'Amarillo',
            'McLennan': 'Waco',
            'Webb': 'Laredo',
            'Brazos': 'College Station-Bryan'
        }
        
        # FEMA flood zone construction cost impacts
        self.flood_modifiers = {
            'VE': 0.30,  # 30% increase
            'V': 0.30,
            'AE': 0.20,  # 20% increase
            'A': 0.20,
            'AO': 0.12,  # 12% increase
            'AH': 0.12,
            'X': 0.05,   # 5% increase for 500-year
            'AREA NOT INCLUDED': 0.0,
            'N/A': 0.0
        }
        
        # Density assumptions by location type
        self.density_map = {
            'urban': 30,      # units per acre
            'suburban': 20,
            'rural': 15
        }
        
        self.base_construction_cost = 150  # $/sf
        
    def load_data(self):
        """Load all required data files"""
        print("Loading data files...")
        
        # Load HUD AMI data
        hud_path = self.base_path / 'HUD AMI FMR' / 'HUD2025_AMI_Rent_Data_Static.xlsx'
        self.hud_data = pd.read_excel(hud_path)
        self.texas_hud = self.hud_data[self.hud_data['fips'].astype(str).str.startswith('48')].copy()
        
        # Load land analysis results (from previous analyzer)
        land_files = list(Path('.').glob('CoStar_Land_Analysis_*.xlsx'))
        if land_files:
            latest_land = sorted(land_files)[-1]
            print(f"Loading land analysis from: {latest_land}")
            self.land_data = pd.read_excel(latest_land, sheet_name='All_Land_Analysis')
        else:
            raise FileNotFoundError("No land analysis files found. Run costar_land_specific_analyzer.py first.")
            
        print(f"Loaded {len(self.land_data)} properties from land analysis")
        print(f"Loaded {len(self.texas_hud)} Texas counties from HUD data")
        
    def get_location_type(self, county):
        """Determine if location is urban, suburban, or rural"""
        if county in self.county_metro_map:
            metro = self.county_metro_map[county]
            if metro in ['Austin-Round Rock-Georgetown', 'Houston-The Woodlands-Sugar Land', 
                        'Dallas-Plano-Irving', 'Fort Worth-Arlington-Grapevine', 'San Antonio-New Braunfels']:
                return 'urban'
            else:
                return 'suburban'
        return 'rural'
    
    def get_construction_modifier(self, county):
        """Get construction cost modifier for county"""
        if county in self.county_metro_map:
            metro = self.county_metro_map[county]
            return self.metro_modifiers.get(metro, 1.0)
        return 0.95  # Rural modifier
        
    def calculate_adjusted_construction_cost(self, county, flood_zone):
        """Calculate total construction cost per SF with all modifiers"""
        location_mod = self.get_construction_modifier(county)
        flood_mod = self.flood_modifiers.get(flood_zone, 0.0)
        
        adjusted_cost = self.base_construction_cost * location_mod * (1 + flood_mod)
        return adjusted_cost, location_mod, flood_mod
        
    def calculate_economic_metrics(self, row):
        """Calculate economic viability metrics for a property"""
        try:
            # Get county data
            county = row.get('County', 'Unknown')
            flood_zone = row.get('Flood_Zone', 'X')
            land_price = row.get('Sale Price', 0)
            # Convert land SF to acres (43,560 sf per acre)
            land_sf = row.get('Land SF Gross', 43560)
            acres = land_sf / 43560 if land_sf > 0 else 1
            
            # Get location type and density
            location_type = self.get_location_type(county)
            density = self.density_map[location_type]
            
            # Get construction costs
            construction_psf, location_mod, flood_mod = self.calculate_adjusted_construction_cost(county, flood_zone)
            
            # Get HUD rent data for county
            county_hud = self.texas_hud[self.texas_hud['County_Name'].str.upper() == county.upper()]
            if county_hud.empty:
                return self._empty_metrics()
                
            county_data = county_hud.iloc[0]
            
            # Get 2BR 60% AMI rent
            rent_2br_60 = county_data.get('2BR 60%', 0)
            if pd.isna(rent_2br_60) or rent_2br_60 == 0:
                rent_2br_60 = county_data.get('Rent_2BR_60%', 0)  # Try alternate column name
                
            # Calculate revenue metrics
            annual_rent_per_unit = rent_2br_60 * 12
            total_units = density * acres
            gross_annual_revenue = annual_rent_per_unit * total_units
            
            # Calculate cost metrics
            avg_unit_size = 900  # sf for 2BR
            total_building_sf = total_units * avg_unit_size
            total_construction_cost = construction_psf * total_building_sf
            
            # Calculate per-acre metrics
            revenue_per_acre = gross_annual_revenue / acres if acres > 0 else 0
            construction_cost_per_acre = total_construction_cost / acres if acres > 0 else 0
            land_cost_per_acre = land_price / acres if acres > 0 else 0
            
            # Calculate economic score (higher is better)
            # This represents annual revenue potential adjusted for construction costs
            construction_factor = construction_psf / self.base_construction_cost
            adjusted_revenue_per_acre = revenue_per_acre / construction_factor if construction_factor > 0 else 0
            
            # Calculate ROI metric (simplified)
            total_cost_per_acre = construction_cost_per_acre + land_cost_per_acre
            if total_cost_per_acre > 0:
                simple_roi = (revenue_per_acre / total_cost_per_acre) * 100
            else:
                simple_roi = 0
                
            return {
                'Location_Type': location_type,
                'Density_Units_Acre': density,
                'Construction_PSF': round(construction_psf, 2),
                'Location_Modifier': location_mod,
                'Flood_Modifier': flood_mod,
                'Rent_2BR_60PCT': rent_2br_60,
                'Annual_Rent_Per_Unit': round(annual_rent_per_unit, 0),
                'Total_Units': round(total_units, 0),
                'Gross_Annual_Revenue': round(gross_annual_revenue, 0),
                'Revenue_Per_Acre': round(revenue_per_acre, 0),
                'Construction_Cost_Per_Acre': round(construction_cost_per_acre, 0),
                'Land_Cost_Per_Acre': round(land_cost_per_acre, 0),
                'Total_Cost_Per_Acre': round(total_cost_per_acre, 0),
                'Adjusted_Revenue_Per_Acre': round(adjusted_revenue_per_acre, 0),
                'Simple_ROI_Percent': round(simple_roi, 1),
                'Economic_Score': round(adjusted_revenue_per_acre / 10000, 1)  # Scale to 0-100 range
            }
            
        except Exception as e:
            print(f"Error calculating metrics for {row.get('Address', 'Unknown')}: {e}")
            return self._empty_metrics()
            
    def _empty_metrics(self):
        """Return empty metrics dict"""
        return {col: 0 for col in [
            'Location_Type', 'Density_Units_Acre', 'Construction_PSF', 'Location_Modifier',
            'Flood_Modifier', 'Rent_2BR_60PCT', 'Annual_Rent_Per_Unit', 'Total_Units',
            'Gross_Annual_Revenue', 'Revenue_Per_Acre', 'Construction_Cost_Per_Acre',
            'Land_Cost_Per_Acre', 'Total_Cost_Per_Acre', 'Adjusted_Revenue_Per_Acre',
            'Simple_ROI_Percent', 'Economic_Score'
        ]}
        
    def calculate_combined_score(self, row):
        """Combine land viability with economic score"""
        land_score = row.get('Land_Viability_Score', 0)
        economic_score = row.get('Economic_Score', 0)
        
        # Weight factors (adjust as needed)
        land_weight = 0.4
        economic_weight = 0.6
        
        # Apply penalties
        penalties = 0
        
        # High flood risk penalty
        if row.get('Flood_Modifier', 0) >= 0.20:
            penalties -= 10
            
        # Low rent area penalty
        if row.get('Rent_2BR_60PCT', 0) < 1000:
            penalties -= 5
            
        # Competition penalty (from land analysis)
        if row.get('TDHCA_One_Mile_Fatal', False):
            penalties -= 20
            
        combined = (land_score * land_weight) + (economic_score * economic_weight) + penalties
        return max(0, min(100, combined))  # Clamp to 0-100
        
    def analyze_economic_viability(self):
        """Run economic viability analysis on all properties"""
        print("\nAnalyzing economic viability...")
        
        # Calculate economic metrics for each property
        economic_metrics = []
        for idx, row in self.land_data.iterrows():
            metrics = self.calculate_economic_metrics(row)
            economic_metrics.append(metrics)
            
        # Add metrics to dataframe
        metrics_df = pd.DataFrame(economic_metrics)
        self.results = pd.concat([self.land_data, metrics_df], axis=1)
        
        # Calculate combined score
        self.results['Combined_Viability_Score'] = self.results.apply(self.calculate_combined_score, axis=1)
        
        # Sort by combined score
        self.results = self.results.sort_values('Combined_Viability_Score', ascending=False)
        
        print(f"Completed economic analysis for {len(self.results)} properties")
        
    def generate_report(self):
        """Generate comprehensive Excel report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Texas_Economic_Viability_Analysis_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All properties with full analysis
            self.results.to_excel(writer, sheet_name='Full_Economic_Analysis', index=False)
            
            # High economic potential (top 20%)
            high_econ = self.results.nlargest(int(len(self.results) * 0.2), 'Economic_Score')
            high_econ.to_excel(writer, sheet_name='High_Economic_Potential', index=False)
            
            # Best combined score (balanced land and economics)
            best_combined = self.results.nlargest(30, 'Combined_Viability_Score')
            best_combined.to_excel(writer, sheet_name='Best_Overall_Sites', index=False)
            
            # 4% deals (larger, stable markets)
            # Calculate acres for filtering
            self.results['Acres'] = self.results['Land SF Gross'] / 43560
            
            four_pct = self.results[
                (self.results['Acres'] >= 3) & 
                (self.results['Location_Type'].isin(['urban', 'suburban'])) &
                (self.results['Economic_Score'] > 20)
            ].nlargest(30, 'Combined_Viability_Score')
            four_pct.to_excel(writer, sheet_name='Best_4PCT_Sites', index=False)
            
            # 9% deals (smaller, high-scoring)
            nine_pct = self.results[
                (self.results['Acres'] <= 5) &
                (self.results['TDHCA_One_Mile_Fatal'] == False) &
                (self.results['Economic_Score'] > 15)
            ].nlargest(30, 'Combined_Viability_Score')
            nine_pct.to_excel(writer, sheet_name='Best_9PCT_Sites', index=False)
            
            # Summary statistics
            summary_stats = self._generate_summary_stats()
            summary_df = pd.DataFrame(summary_stats)
            summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
            
        print(f"\nReport saved to: {output_file}")
        self._print_key_findings()
        
    def _generate_summary_stats(self):
        """Generate summary statistics"""
        stats = []
        
        # By location type
        for loc_type in ['urban', 'suburban', 'rural']:
            subset = self.results[self.results['Location_Type'] == loc_type]
            if not subset.empty:
                stats.append({
                    'Category': f'{loc_type.capitalize()} Properties',
                    'Count': len(subset),
                    'Avg_Economic_Score': subset['Economic_Score'].mean(),
                    'Avg_Construction_PSF': subset['Construction_PSF'].mean(),
                    'Avg_Rent_2BR': subset['Rent_2BR_60PCT'].mean(),
                    'Avg_Combined_Score': subset['Combined_Viability_Score'].mean()
                })
                
        # By flood risk
        high_flood = self.results[self.results['Flood_Modifier'] >= 0.15]
        low_flood = self.results[self.results['Flood_Modifier'] < 0.15]
        
        stats.extend([
            {
                'Category': 'High Flood Risk',
                'Count': len(high_flood),
                'Avg_Economic_Score': high_flood['Economic_Score'].mean() if not high_flood.empty else 0,
                'Avg_Construction_PSF': high_flood['Construction_PSF'].mean() if not high_flood.empty else 0,
                'Avg_Rent_2BR': high_flood['Rent_2BR_60PCT'].mean() if not high_flood.empty else 0,
                'Avg_Combined_Score': high_flood['Combined_Viability_Score'].mean() if not high_flood.empty else 0
            },
            {
                'Category': 'Low Flood Risk',
                'Count': len(low_flood),
                'Avg_Economic_Score': low_flood['Economic_Score'].mean() if not low_flood.empty else 0,
                'Avg_Construction_PSF': low_flood['Construction_PSF'].mean() if not low_flood.empty else 0,
                'Avg_Rent_2BR': low_flood['Rent_2BR_60PCT'].mean() if not low_flood.empty else 0,
                'Avg_Combined_Score': low_flood['Combined_Viability_Score'].mean() if not low_flood.empty else 0
            }
        ])
        
        return stats
        
    def _print_key_findings(self):
        """Print key findings to console"""
        print("\n" + "="*50)
        print("KEY ECONOMIC FINDINGS")
        print("="*50)
        
        # Best overall sites
        print("\nTOP 5 SITES BY COMBINED SCORE:")
        top_sites = self.results.nlargest(5, 'Combined_Viability_Score')
        for idx, row in top_sites.iterrows():
            print(f"\n{row['Address']}, {row['City']}")
            print(f"  Combined Score: {row['Combined_Viability_Score']:.1f}")
            print(f"  Economic Score: {row['Economic_Score']:.1f}")
            print(f"  Land Score: {row['Land_Viability_Score']:.1f}")
            print(f"  2BR Rent: ${row['Rent_2BR_60PCT']:,.0f}")
            print(f"  Construction $/SF: ${row['Construction_PSF']:.0f}")
            print(f"  Revenue/Acre: ${row['Revenue_Per_Acre']:,.0f}")
            
        # Economic insights
        print("\n" + "-"*50)
        print("ECONOMIC INSIGHTS:")
        print(f"Average Construction Cost/SF: ${self.results['Construction_PSF'].mean():.0f}")
        print(f"Average 2BR 60% Rent: ${self.results['Rent_2BR_60PCT'].mean():.0f}")
        print(f"Properties with High Flood Costs (>20%): {len(self.results[self.results['Flood_Modifier'] >= 0.20])}")
        print(f"Properties with Strong Economics (>30 score): {len(self.results[self.results['Economic_Score'] > 30])}")
        
        # Best value plays
        high_roi = self.results.nlargest(3, 'Simple_ROI_Percent')
        print("\n" + "-"*50)
        print("HIGHEST ROI PROPERTIES:")
        for idx, row in high_roi.iterrows():
            print(f"\n{row['Address']}, {row['City']}")
            print(f"  Simple ROI: {row['Simple_ROI_Percent']:.1f}%")
            print(f"  Land Price/Acre: ${row['Land_Cost_Per_Acre']:,.0f}")
            print(f"  Revenue/Acre: ${row['Revenue_Per_Acre']:,.0f}")
            
    def run(self):
        """Main execution method"""
        print("Starting Texas Economic Viability Analysis...")
        print("="*50)
        
        self.load_data()
        self.analyze_economic_viability()
        self.generate_report()
        
        print("\nAnalysis complete!")

if __name__ == "__main__":
    analyzer = TexasEconomicViabilityAnalyzer()
    analyzer.run()