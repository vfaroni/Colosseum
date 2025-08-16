#!/usr/bin/env python3
"""
CoStar Market Analysis for 9481 Marbach Rd Site
Analyzes land costs per acre in 1.8 mile radius market area
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from pathlib import Path
import json
from datetime import datetime

class MarbachMarketAnalyzer:
    """Analyze CoStar land data for Marbach Rd market area"""
    
    def __init__(self):
        # Target site coordinates - 9481 Marbach Rd, San Antonio, TX
        self.target_site = {
            "address": "9481 Marbach Rd, San Antonio, TX",
            "latitude": 29.4289,
            "longitude": -98.6156,
            "size_acres": 10.0,
            "description": "Richland Hills Tract target site"
        }
        
        # Market analysis parameters
        self.market_radius_miles = 1.8
        
    def load_costar_data(self):
        """Load CoStar export data"""
        costar_file = Path("/Users/williamrice/Downloads/CostarExport-11.xlsx")
        
        try:
            # Try to read the Excel file
            df = pd.read_excel(costar_file)
            print(f"✅ Loaded CoStar data: {len(df)} records")
            print(f"📋 Columns available: {list(df.columns)}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading CoStar file: {e}")
            return None
    
    def analyze_market_data(self, df):
        """Analyze land costs in market area"""
        if df is None:
            print("❌ No data to analyze")
            return None
        
        print(f"\n🔍 ANALYZING MARKET AREA AROUND 9481 MARBACH RD")
        print(f"📍 Target coordinates: {self.target_site['latitude']}, {self.target_site['longitude']}")
        print(f"📏 Market radius: {self.market_radius_miles} miles")
        print("=" * 60)
        
        # Look for common CoStar column names
        potential_columns = {
            "address": ["Address", "Property Address", "Street Address", "address", "Address 1"],
            "latitude": ["Latitude", "Lat", "latitude", "lat"],
            "longitude": ["Longitude", "Lng", "Long", "longitude", "lng", "lon"],
            "price": ["Sale Price", "Asking Price", "List Price", "Price", "price", "Total Price"],
            "acres": ["Acres", "Land Size", "Size (Acres)", "acres", "Acreage", "Land Acres"],
            "price_per_acre": ["Price per Acre", "Price/Acre", "Per Acre", "price_per_acre"],
            "property_type": ["Property Type", "Type", "Use Type", "property_type"],
            "status": ["Status", "Listing Status", "status"]
        }
        
        # Map actual columns to our analysis
        column_mapping = {}
        available_columns = [col.lower() for col in df.columns]
        
        for key, possible_names in potential_columns.items():
            for name in possible_names:
                if name.lower() in available_columns:
                    column_mapping[key] = df.columns[available_columns.index(name.lower())]
                    break
        
        print(f"📊 COLUMN MAPPING DETECTED:")
        for key, col in column_mapping.items():
            print(f"   • {key}: {col}")
        
        # Filter data for analysis
        market_data = self.filter_market_area(df, column_mapping)
        
        if market_data is None or len(market_data) == 0:
            print("❌ No market data found in radius")
            return None
        
        # Analyze land costs
        cost_analysis = self.analyze_land_costs(market_data, column_mapping)
        
        return cost_analysis
    
    def filter_market_area(self, df, column_mapping):
        """Filter properties within market radius"""
        if "latitude" not in column_mapping or "longitude" not in column_mapping:
            print("⚠️ No coordinate data found - analyzing all properties")
            return df
        
        lat_col = column_mapping["latitude"]
        lng_col = column_mapping["longitude"]
        
        # Calculate distances
        market_properties = []
        target_coords = (self.target_site["latitude"], self.target_site["longitude"])
        
        for idx, row in df.iterrows():
            try:
                prop_lat = float(row[lat_col])
                prop_lng = float(row[lng_col])
                prop_coords = (prop_lat, prop_lng)
                
                distance_miles = geodesic(target_coords, prop_coords).miles
                
                if distance_miles <= self.market_radius_miles:
                    row_dict = row.to_dict()
                    row_dict["distance_from_target"] = distance_miles
                    market_properties.append(row_dict)
                    
            except (ValueError, TypeError):
                # Skip rows with invalid coordinates
                continue
        
        if market_properties:
            market_df = pd.DataFrame(market_properties)
            print(f"🎯 Found {len(market_df)} properties within {self.market_radius_miles} miles")
            return market_df
        else:
            print(f"❌ No properties found within {self.market_radius_miles} miles")
            return None
    
    def analyze_land_costs(self, df, column_mapping):
        """Analyze land cost per acre statistics"""
        print(f"\n💰 LAND COST ANALYSIS")
        print("=" * 40)
        
        # Get price and acreage data
        price_col = column_mapping.get("price")
        acres_col = column_mapping.get("acres")
        price_per_acre_col = column_mapping.get("price_per_acre")
        address_col = column_mapping.get("address", df.columns[0])
        
        land_costs = []
        
        for idx, row in df.iterrows():
            cost_per_acre = None
            price = None
            acres = None
            
            try:
                # Method 1: Direct price per acre
                if price_per_acre_col and pd.notna(row[price_per_acre_col]):
                    cost_per_acre = float(row[price_per_acre_col])
                
                # Method 2: Calculate from price and acres
                elif price_col and acres_col:
                    if pd.notna(row[price_col]) and pd.notna(row[acres_col]):
                        price = float(row[price_col])
                        acres = float(row[acres_col])
                        if acres > 0:
                            cost_per_acre = price / acres
                
                if cost_per_acre and cost_per_acre > 1000:  # Reasonable minimum
                    land_costs.append({
                        "address": str(row[address_col])[:50],
                        "price": price,
                        "acres": acres,
                        "cost_per_acre": cost_per_acre,
                        "distance": row.get("distance_from_target", "Unknown")
                    })
                    
            except (ValueError, TypeError):
                continue
        
        if not land_costs:
            print("❌ No valid land cost data found")
            return None
        
        # Statistical analysis
        costs_only = [item["cost_per_acre"] for item in land_costs]
        
        analysis = {
            "sample_size": len(land_costs),
            "mean_cost_per_acre": np.mean(costs_only),
            "median_cost_per_acre": np.median(costs_only),
            "min_cost_per_acre": np.min(costs_only),
            "max_cost_per_acre": np.max(costs_only),
            "std_deviation": np.std(costs_only),
            "properties": land_costs
        }
        
        # Display results
        print(f"📊 MARKET STATISTICS ({len(land_costs)} properties):")
        print(f"   • Mean Cost/Acre: ${analysis['mean_cost_per_acre']:,.0f}")
        print(f"   • Median Cost/Acre: ${analysis['median_cost_per_acre']:,.0f}")
        print(f"   • Range: ${analysis['min_cost_per_acre']:,.0f} - ${analysis['max_cost_per_acre']:,.0f}")
        print(f"   • Standard Deviation: ${analysis['std_deviation']:,.0f}")
        
        # Show individual properties
        print(f"\n🏠 COMPARABLE PROPERTIES:")
        sorted_properties = sorted(land_costs, key=lambda x: x["cost_per_acre"])
        
        for i, prop in enumerate(sorted_properties[:10]):  # Show top 10
            distance_str = f"{prop['distance']:.1f}mi" if isinstance(prop['distance'], (int, float)) else prop['distance']
            print(f"   {i+1:2d}. {prop['address']:<35} ${prop['cost_per_acre']:>8,.0f}/acre ({distance_str})")
            
        if len(sorted_properties) > 10:
            print(f"   ... and {len(sorted_properties) - 10} more properties")
        
        # Target site valuation
        target_valuation = analysis['median_cost_per_acre'] * self.target_site['size_acres']
        print(f"\n🎯 TARGET SITE VALUATION (9481 Marbach Rd):")
        print(f"   • Size: {self.target_site['size_acres']} acres")
        print(f"   • Market Rate: ${analysis['median_cost_per_acre']:,.0f}/acre (median)")
        print(f"   • Estimated Value: ${target_valuation:,.0f}")
        
        return analysis
    
    def export_analysis(self, analysis):
        """Export analysis to JSON and Excel"""
        if not analysis:
            return
        
        output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # JSON export
        json_file = output_dir / "Marbach_Market_Analysis.json"
        analysis_export = analysis.copy()
        analysis_export["target_site"] = self.target_site
        analysis_export["analysis_date"] = datetime.now().isoformat()
        
        with open(json_file, 'w') as f:
            json.dump(analysis_export, f, indent=2, default=str)
        
        # Excel export
        excel_file = output_dir / "Marbach_Market_Comparables.xlsx"
        
        if analysis["properties"]:
            df = pd.DataFrame(analysis["properties"])
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Market_Comparables", index=False)
                
                # Summary stats
                summary_data = [
                    {"Metric": "Sample Size", "Value": analysis["sample_size"]},
                    {"Metric": "Mean Cost/Acre", "Value": f"${analysis['mean_cost_per_acre']:,.0f}"},
                    {"Metric": "Median Cost/Acre", "Value": f"${analysis['median_cost_per_acre']:,.0f}"},
                    {"Metric": "Min Cost/Acre", "Value": f"${analysis['min_cost_per_acre']:,.0f}"},
                    {"Metric": "Max Cost/Acre", "Value": f"${analysis['max_cost_per_acre']:,.0f}"},
                    {"Metric": "Target Site Value", "Value": f"${analysis['median_cost_per_acre'] * self.target_site['size_acres']:,.0f}"}
                ]
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Market_Summary", index=False)
        
        print(f"\n✅ ANALYSIS EXPORTED:")
        print(f"   📁 JSON: {json_file}")
        print(f"   📊 Excel: {excel_file}")

def main():
    print("🏢 COSTAR MARKET ANALYSIS - 9481 MARBACH RD")
    print("=" * 55)
    print("🎯 Analyzing land costs in 1.8 mile market radius")
    print("📍 Target: Richland Hills Tract (10 acres)")
    print()
    
    analyzer = MarbachMarketAnalyzer()
    
    # Load CoStar data
    df = analyzer.load_costar_data()
    
    if df is not None:
        # Analyze market
        analysis = analyzer.analyze_market_data(df)
        
        # Export results
        analyzer.export_analysis(analysis)
        
        if analysis:
            print(f"\n🏁 MARKET ANALYSIS COMPLETE")
            print(f"💰 Median Market Rate: ${analysis['median_cost_per_acre']:,.0f}/acre")
            print(f"🎯 10-Acre Site Value: ${analysis['median_cost_per_acre'] * 10:,.0f}")
    else:
        print("❌ Could not load CoStar data")

if __name__ == "__main__":
    main()