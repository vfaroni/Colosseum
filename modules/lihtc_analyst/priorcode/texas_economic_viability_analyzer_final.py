#!/usr/bin/env python3
"""
Texas LIHTC Economic Viability Analyzer - FINAL VERSION
Uses county-enhanced land data with direct AMI integration
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class TexasEconomicViabilityAnalyzer:
    """Final version with proper county-AMI integration"""
    
    def __init__(self):
        # Construction cost modifiers by metro area
        self.metro_modifiers = {
            'Austin-Round Rock-Georgetown': 1.20,
            'Houston-The Woodlands-Sugar Land': 1.18,
            'Dallas-Plano-Irving': 1.17,
            'Fort Worth-Arlington-Grapevine': 1.15,
            'San Antonio-New Braunfels': 1.10,
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
        
        # County to metro mapping
        self.county_metro_map = {
            'Travis County': 'Austin-Round Rock-Georgetown',
            'Williamson County': 'Austin-Round Rock-Georgetown', 
            'Hays County': 'Austin-Round Rock-Georgetown',
            'Harris County': 'Houston-The Woodlands-Sugar Land',
            'Fort Bend County': 'Houston-The Woodlands-Sugar Land',
            'Montgomery County': 'Houston-The Woodlands-Sugar Land',
            'Dallas County': 'Dallas-Plano-Irving',
            'Collin County': 'Dallas-Plano-Irving',
            'Tarrant County': 'Fort Worth-Arlington-Grapevine',
            'Bexar County': 'San Antonio-New Braunfels',
            'El Paso County': 'El Paso',
            'Nueces County': 'Corpus Christi',
            'Hidalgo County': 'McAllen-Edinburg-Mission',
            'Bell County': 'Killeen-Temple',
            'Jefferson County': 'Beaumont-Port Arthur',
            'Lubbock County': 'Lubbock',
            'Potter County': 'Amarillo',
            'McLennan County': 'Waco',
            'Webb County': 'Laredo',
            'Brazos County': 'College Station-Bryan'
        }
        
        # FEMA flood zone construction cost impacts
        self.flood_modifiers = {
            'VE': 0.30, 'V': 0.30,
            'AE': 0.20, 'A': 0.20,
            'AO': 0.12, 'AH': 0.12,
            'X': 0.05,
            'AREA NOT INCLUDED': 0.0,
            'N/A': 0.0
        }
        
        # Density by location type
        self.density_map = {'urban': 30, 'suburban': 20, 'rural': 15}
        self.base_construction_cost = 150
        
    def load_data(self):
        """Load enhanced land data with counties"""
        print("Loading county-enhanced land analysis data...")
        
        # Find the latest county-enhanced file
        county_files = list(Path('.').glob('CoStar_Land_Analysis_With_Counties_*.xlsx'))
        if not county_files:
            raise FileNotFoundError("County-enhanced land analysis file not found. Run add_county_to_land_data.py first.")
            
        latest_file = sorted(county_files)[-1]
        print(f"Loading from: {latest_file}")
        
        self.land_data = pd.read_excel(latest_file, sheet_name='Land_Analysis_With_Counties')
        print(f"Loaded {len(self.land_data)} properties with county data")
        
        # Check for AMI data columns
        has_ami = 'rent_2br_60pct' in self.land_data.columns
        print(f"Direct AMI data available: {has_ami}")
        
    def get_location_type(self, county):
        """Determine location type from county"""
        if county in self.county_metro_map:
            metro = self.county_metro_map[county]
            if metro in ['Austin-Round Rock-Georgetown', 'Houston-The Woodlands-Sugar Land', 
                        'Dallas-Plano-Irving', 'Fort Worth-Arlington-Grapevine', 'San Antonio-New Braunfels']:
                return 'urban'
            else:
                return 'suburban'
        return 'rural'
    
    def get_construction_modifier(self, county):
        """Get construction cost modifier"""
        if county in self.county_metro_map:
            metro = self.county_metro_map[county]
            return self.metro_modifiers.get(metro, 1.0)
        return 0.95  # Rural modifier
        
    def calculate_economic_metrics(self, row):
        """Calculate economic viability metrics"""
        try:
            # Basic data
            county = row.get('county_name', 'Unknown')
            flood_zone = row.get('FEMA_Zone', 'X')
            land_price = row.get('Sale Price', 0)
            land_sf = row.get('Land SF Gross', 43560)
            acres = land_sf / 43560 if land_sf > 0 else 1
            
            # Get AMI rent data (directly from the joined data)
            rent_2br_60 = row.get('rent_2br_60pct', 0)
            
            if pd.isna(rent_2br_60) or rent_2br_60 == 0:
                print(f"Warning: No rent data for {county}")
                return self._empty_metrics()
                
            # Location and construction costs
            location_type = self.get_location_type(county)
            density = self.density_map[location_type]
            location_mod = self.get_construction_modifier(county)
            flood_mod = self.flood_modifiers.get(flood_zone, 0.0)
            construction_psf = self.base_construction_cost * location_mod * (1 + flood_mod)
            
            # Revenue calculations
            annual_rent_per_unit = rent_2br_60 * 12
            total_units = density * acres
            gross_annual_revenue = annual_rent_per_unit * total_units
            
            # Cost calculations
            avg_unit_size = 900  # sf for 2BR
            total_building_sf = total_units * avg_unit_size
            total_construction_cost = construction_psf * total_building_sf
            
            # Per-acre metrics
            revenue_per_acre = gross_annual_revenue / acres if acres > 0 else 0
            construction_cost_per_acre = total_construction_cost / acres if acres > 0 else 0
            land_cost_per_acre = land_price / acres if acres > 0 else 0
            total_cost_per_acre = construction_cost_per_acre + land_cost_per_acre
            
            # Economic scoring
            construction_factor = construction_psf / self.base_construction_cost
            adjusted_revenue_per_acre = revenue_per_acre / construction_factor if construction_factor > 0 else 0
            
            # ROI calculation
            simple_roi = (revenue_per_acre / total_cost_per_acre) * 100 if total_cost_per_acre > 0 else 0
            
            return {
                'County': county,
                'Location_Type': location_type,
                'Density_Units_Acre': density,
                'Construction_PSF': round(construction_psf, 2),
                'Location_Modifier': location_mod,
                'Flood_Modifier': flood_mod,
                'Rent_2BR_60PCT': rent_2br_60,
                'Annual_Rent_Per_Unit': round(annual_rent_per_unit, 0),
                'Total_Units': round(total_units, 0),
                'Acres': round(acres, 2),
                'Gross_Annual_Revenue': round(gross_annual_revenue, 0),
                'Revenue_Per_Acre': round(revenue_per_acre, 0),
                'Construction_Cost_Per_Acre': round(construction_cost_per_acre, 0),
                'Land_Cost_Per_Acre': round(land_cost_per_acre, 0),
                'Total_Cost_Per_Acre': round(total_cost_per_acre, 0),
                'Adjusted_Revenue_Per_Acre': round(adjusted_revenue_per_acre, 0),
                'Simple_ROI_Percent': round(simple_roi, 1),
                'Economic_Score': round(adjusted_revenue_per_acre / 10000, 1)
            }
            
        except Exception as e:
            print(f"Error processing {row.get('Address', 'Unknown')}: {e}")
            return self._empty_metrics()
            
    def _empty_metrics(self):
        """Return empty metrics"""
        return {col: 0 for col in [
            'County', 'Location_Type', 'Density_Units_Acre', 'Construction_PSF', 
            'Location_Modifier', 'Flood_Modifier', 'Rent_2BR_60PCT', 
            'Annual_Rent_Per_Unit', 'Total_Units', 'Acres', 'Gross_Annual_Revenue',
            'Revenue_Per_Acre', 'Construction_Cost_Per_Acre', 'Land_Cost_Per_Acre',
            'Total_Cost_Per_Acre', 'Adjusted_Revenue_Per_Acre', 'Simple_ROI_Percent',
            'Economic_Score'
        ]}
        
    def calculate_combined_score(self, row):
        """Calculate combined land + economic score"""
        land_score = row.get('Land_Viability_Score', 0)
        economic_score = row.get('Economic_Score', 0)
        
        # Weights
        land_weight = 0.4
        economic_weight = 0.6
        
        # Penalties
        penalties = 0
        if row.get('Flood_Modifier', 0) >= 0.20:
            penalties -= 10
        if row.get('Rent_2BR_60PCT', 0) < 1000:
            penalties -= 5
        if row.get('TDHCA_One_Mile_Fatal', False):
            penalties -= 20
            
        combined = (land_score * land_weight) + (economic_score * economic_weight) + penalties
        return max(0, min(100, combined))
        
    def run_analysis(self):
        """Run the complete economic analysis"""
        print("\nRunning economic viability analysis...")
        
        # Calculate metrics
        economic_metrics = []
        for idx, row in self.land_data.iterrows():
            metrics = self.calculate_economic_metrics(row)
            economic_metrics.append(metrics)
            
        # Combine with original data
        metrics_df = pd.DataFrame(economic_metrics)
        self.results = pd.concat([self.land_data, metrics_df], axis=1)
        
        # Calculate combined score
        self.results['Combined_Viability_Score'] = self.results.apply(self.calculate_combined_score, axis=1)
        
        # Sort by combined score
        self.results = self.results.sort_values('Combined_Viability_Score', ascending=False)
        
        print(f"Analysis complete for {len(self.results)} properties")
        
    def generate_report(self):
        """Generate comprehensive Excel report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Texas_Economic_Viability_Analysis_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Full analysis
            self.results.to_excel(writer, sheet_name='Full_Economic_Analysis', index=False)
            
            # Best overall sites
            best_overall = self.results.nlargest(30, 'Combined_Viability_Score')
            best_overall.to_excel(writer, sheet_name='Best_Overall_Sites', index=False)
            
            # High economic potential
            high_econ = self.results.nlargest(30, 'Economic_Score')
            high_econ.to_excel(writer, sheet_name='High_Economic_Potential', index=False)
            
            # 4% credit sites (larger properties)
            four_pct = self.results[
                (self.results['Acres'] >= 3) &
                (self.results['Location_Type'].isin(['urban', 'suburban'])) &
                (self.results['Economic_Score'] > 20)
            ].nlargest(25, 'Combined_Viability_Score')
            four_pct.to_excel(writer, sheet_name='Best_4PCT_Sites', index=False)
            
            # 9% credit sites (competitive)
            nine_pct = self.results[
                (self.results['Acres'] <= 5) &
                (self.results['TDHCA_One_Mile_Fatal'] == False) &
                (self.results['Economic_Score'] > 15)
            ].nlargest(25, 'Combined_Viability_Score')
            nine_pct.to_excel(writer, sheet_name='Best_9PCT_Sites', index=False)
            
            # County summary
            county_summary = self.results.groupby('County').agg({
                'Address': 'count',
                'Economic_Score': 'mean',
                'Combined_Viability_Score': 'mean',
                'Rent_2BR_60PCT': 'first',
                'Construction_PSF': 'mean'
            }).rename(columns={'Address': 'Property_Count'}).round(1).reset_index()
            county_summary.to_excel(writer, sheet_name='County_Summary', index=False)
            
        print(f"\nReport saved: {output_file}")
        self._print_findings()
        
    def _print_findings(self):
        """Print key findings"""
        print("\n" + "="*60)
        print("TEXAS ECONOMIC VIABILITY ANALYSIS - KEY FINDINGS")
        print("="*60)
        
        # Top properties
        print("\nTOP 5 PROPERTIES BY COMBINED SCORE:")
        top_5 = self.results.nlargest(5, 'Combined_Viability_Score')
        for idx, row in top_5.iterrows():
            print(f"\n{row['Address']}, {row['City']} ({row['County']})")
            print(f"  Combined Score: {row['Combined_Viability_Score']:.1f}")
            print(f"  Economic Score: {row['Economic_Score']:.1f}")
            print(f"  2BR Rent: ${row['Rent_2BR_60PCT']:,.0f}")
            print(f"  Construction $/SF: ${row['Construction_PSF']:.0f}")
            print(f"  Acres: {row['Acres']:.1f}")
            
        # Market insights
        print(f"\n" + "-"*50)
        print("MARKET INSIGHTS:")
        print(f"Properties analyzed: {len(self.results)}")
        print(f"Counties covered: {self.results['County'].nunique()}")
        print(f"Average construction cost: ${self.results['Construction_PSF'].mean():.0f}/SF")
        print(f"Average 2BR 60% rent: ${self.results['Rent_2BR_60PCT'].mean():.0f}")
        print(f"Properties with strong economics (>30): {len(self.results[self.results['Economic_Score'] > 30])}")
        
        # Best counties
        print(f"\n" + "-"*50)
        print("TOP COUNTIES BY ECONOMIC PERFORMANCE:")
        county_perf = self.results.groupby('County').agg({
            'Economic_Score': 'mean',
            'Address': 'count'
        }).rename(columns={'Address': 'Count'}).sort_values('Economic_Score', ascending=False).head(5)
        
        for county, data in county_perf.iterrows():
            print(f"  {county}: {data['Economic_Score']:.1f} avg score ({data['Count']} properties)")
            
    def run(self):
        """Main execution"""
        print("TEXAS LIHTC ECONOMIC VIABILITY ANALYZER - FINAL VERSION")
        print("="*60)
        
        self.load_data()
        self.run_analysis() 
        self.generate_report()
        
        print("\n🎯 Analysis complete! Check the Excel report for detailed results.")

if __name__ == "__main__":
    analyzer = TexasEconomicViabilityAnalyzer()
    analyzer.run()