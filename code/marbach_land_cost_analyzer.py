#!/usr/bin/env python3
"""
Marbach Market Land Cost Analyzer
Extracts acreage from property names and calculates cost per acre
"""

import pandas as pd
import re
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class MarbachLandCostAnalyzer:
    """Analyze land costs from CoStar data with embedded acreage"""
    
    def __init__(self):
        self.target_site = {
            "address": "9481 Marbach Rd (Richland Hills Tract)",
            "size_acres": 10.0,
            "market_area": "Far West San Antonio (Marbach Corridor)"
        }
    
    def load_and_analyze_costar_data(self):
        """Load CoStar data and analyze land costs"""
        costar_file = Path("/Users/williamrice/Downloads/CostarExport-11.xlsx")
        
        try:
            df = pd.read_excel(costar_file)
            print(f"✅ Loaded {len(df)} CoStar properties")
            
            # Extract acreage and calculate costs
            analyzed_properties = self.extract_acreage_and_costs(df)
            
            # Market analysis
            market_analysis = self.analyze_market_rates(analyzed_properties)
            
            return analyzed_properties, market_analysis
            
        except Exception as e:
            print(f"❌ Error loading CoStar data: {e}")
            return None, None
    
    def extract_acreage_and_costs(self, df):
        """Extract acreage from property names and calculate cost per acre"""
        print(f"\n🔍 EXTRACTING ACREAGE AND CALCULATING COSTS")
        print("=" * 50)
        
        analyzed_properties = []
        
        for idx, row in df.iterrows():
            prop_data = {
                "address": row.get("Property Address", "Unknown"),
                "property_name": row.get("Property Name", "Unknown"),
                "price": row.get("For Sale Price"),
                "zoning": row.get("Zoning", "Unknown"),
                "submarket": row.get("Submarket Name", "Unknown"),
                "zip": row.get("Zip", "Unknown")
            }
            
            # Extract acreage from property name
            acreage = self.extract_acreage_from_name(prop_data["property_name"])
            
            if acreage and prop_data["price"] and pd.notna(prop_data["price"]):
                cost_per_acre = prop_data["price"] / acreage
                
                prop_data.update({
                    "acres": acreage,
                    "cost_per_acre": cost_per_acre,
                    "total_price": prop_data["price"]
                })
                
                analyzed_properties.append(prop_data)
                
                print(f"✅ {prop_data['address'][:30]:<30} | {acreage:>5.1f} ac | ${cost_per_acre:>8,.0f}/ac | ${prop_data['price']:>10,.0f}")
            else:
                missing = []
                if not acreage:
                    missing.append("acreage")
                if not prop_data["price"] or pd.isna(prop_data["price"]):
                    missing.append("price")
                print(f"⚠️  {prop_data['address'][:30]:<30} | Missing: {', '.join(missing)}")
        
        print(f"\n📊 Successfully analyzed {len(analyzed_properties)} properties with complete data")
        return analyzed_properties
    
    def extract_acreage_from_name(self, property_name):
        """Extract acreage from property name using regex"""
        if pd.isna(property_name) or property_name == "Unknown":
            return None
        
        # Common patterns for acreage in property names
        patterns = [
            r'(\d+\.?\d*)\s*acres?',  # "10.6 acres", "5 acre"
            r'(\d+\.?\d*)\s*ac\b',    # "10.6 ac", "5 ac"
            r'(\d+\.?\d*)\s*Acres?',  # "10.6 Acres"
        ]
        
        property_name_str = str(property_name).lower()
        
        for pattern in patterns:
            match = re.search(pattern, property_name_str, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def analyze_market_rates(self, analyzed_properties):
        """Analyze market rates and provide statistics"""
        if not analyzed_properties:
            print("❌ No properties to analyze")
            return None
        
        print(f"\n💰 MARBACH CORRIDOR LAND MARKET ANALYSIS")
        print("=" * 55)
        
        costs_per_acre = [prop["cost_per_acre"] for prop in analyzed_properties]
        acres = [prop["acres"] for prop in analyzed_properties]
        prices = [prop["total_price"] for prop in analyzed_properties]
        
        analysis = {
            "sample_size": len(analyzed_properties),
            "total_acres_analyzed": sum(acres),
            "total_value_analyzed": sum(prices),
            
            # Cost per acre statistics
            "mean_cost_per_acre": np.mean(costs_per_acre),
            "median_cost_per_acre": np.median(costs_per_acre),
            "min_cost_per_acre": np.min(costs_per_acre),
            "max_cost_per_acre": np.max(costs_per_acre),
            "std_dev_cost_per_acre": np.std(costs_per_acre),
            
            # Size distribution
            "mean_property_size": np.mean(acres),
            "median_property_size": np.median(acres),
            "min_property_size": np.min(acres),
            "max_property_size": np.max(acres),
            
            "properties": analyzed_properties
        }
        
        print(f"📊 MARKET STATISTICS:")
        print(f"   • Sample Size: {analysis['sample_size']} properties")
        print(f"   • Total Acres: {analysis['total_acres_analyzed']:.1f} acres")
        print(f"   • Total Value: ${analysis['total_value_analyzed']:,.0f}")
        print(f"")
        print(f"💵 COST PER ACRE:")
        print(f"   • Mean: ${analysis['mean_cost_per_acre']:,.0f}/acre")
        print(f"   • Median: ${analysis['median_cost_per_acre']:,.0f}/acre")
        print(f"   • Range: ${analysis['min_cost_per_acre']:,.0f} - ${analysis['max_cost_per_acre']:,.0f}/acre")
        print(f"   • Std Dev: ${analysis['std_dev_cost_per_acre']:,.0f}")
        print(f"")
        print(f"📏 PROPERTY SIZES:")
        print(f"   • Average Size: {analysis['mean_property_size']:.1f} acres")
        print(f"   • Median Size: {analysis['median_property_size']:.1f} acres")
        print(f"   • Size Range: {analysis['min_property_size']:.1f} - {analysis['max_property_size']:.1f} acres")
        
        # Market positioning analysis
        target_valuation_median = analysis['median_cost_per_acre'] * self.target_site['size_acres']
        target_valuation_mean = analysis['mean_cost_per_acre'] * self.target_site['size_acres']
        
        print(f"\n🎯 RICHLAND HILLS TRACT VALUATION (10 acres):")
        print(f"   • At Median Rate (${analysis['median_cost_per_acre']:,.0f}/ac): ${target_valuation_median:,.0f}")
        print(f"   • At Mean Rate (${analysis['mean_cost_per_acre']:,.0f}/ac): ${target_valuation_mean:,.0f}")
        
        # Comparable properties analysis
        print(f"\n🏘️  COMPARABLE PROPERTIES (Sorted by $/acre):")
        sorted_props = sorted(analyzed_properties, key=lambda x: x['cost_per_acre'])
        
        for i, prop in enumerate(sorted_props):
            size_comparable = "🎯" if 8 <= prop['acres'] <= 12 else "  "
            print(f"   {i+1:2d}. {size_comparable} {prop['address'][:25]:<25} | {prop['acres']:>5.1f}ac | ${prop['cost_per_acre']:>8,.0f}/ac | {prop['zoning']:>5}")
        
        # Size-similar properties
        size_similar = [p for p in analyzed_properties if 8 <= p['acres'] <= 12]
        if size_similar:
            similar_costs = [p['cost_per_acre'] for p in size_similar]
            print(f"\n🔍 SIZE-SIMILAR PROPERTIES (8-12 acres, {len(size_similar)} properties):")
            print(f"   • Mean: ${np.mean(similar_costs):,.0f}/acre")
            print(f"   • Median: ${np.median(similar_costs):,.0f}/acre")
            print(f"   • Range: ${np.min(similar_costs):,.0f} - ${np.max(similar_costs):,.0f}/acre")
        
        return analysis
    
    def export_analysis(self, properties, analysis):
        """Export analysis results"""
        if not analysis:
            return
        
        output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # JSON export
        json_file = output_dir / "Marbach_Land_Market_Analysis.json"
        export_data = {
            "target_site": self.target_site,
            "analysis_date": datetime.now().isoformat(),
            "market_analysis": analysis,
            "methodology": "Acreage extracted from property names, cost per acre calculated from sale prices"
        }
        
        with open(json_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        # Excel export
        excel_file = output_dir / "Marbach_Land_Comparables.xlsx"
        
        if properties:
            df = pd.DataFrame(properties)
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Comparable properties
                df_export = df[['address', 'acres', 'total_price', 'cost_per_acre', 'zoning', 'submarket']].copy()
                df_export = df_export.sort_values('cost_per_acre')
                df_export.to_excel(writer, sheet_name="Land_Comparables", index=False)
                
                # Market summary
                summary_data = [
                    {"Metric": "Sample Size", "Value": analysis["sample_size"]},
                    {"Metric": "Mean Cost/Acre", "Value": f"${analysis['mean_cost_per_acre']:,.0f}"},
                    {"Metric": "Median Cost/Acre", "Value": f"${analysis['median_cost_per_acre']:,.0f}"},
                    {"Metric": "Min Cost/Acre", "Value": f"${analysis['min_cost_per_acre']:,.0f}"},
                    {"Metric": "Max Cost/Acre", "Value": f"${analysis['max_cost_per_acre']:,.0f}"},
                    {"Metric": "10-Acre Site Value (Median)", "Value": f"${analysis['median_cost_per_acre'] * 10:,.0f}"},
                    {"Metric": "10-Acre Site Value (Mean)", "Value": f"${analysis['mean_cost_per_acre'] * 10:,.0f}"}
                ]
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Market_Summary", index=False)
        
        print(f"\n✅ ANALYSIS EXPORTED:")
        print(f"   📁 JSON: {json_file}")
        print(f"   📊 Excel: {excel_file}")
        
        return json_file, excel_file

def main():
    print("🏢 MARBACH CORRIDOR LAND MARKET ANALYSIS")
    print("=" * 55)
    print("📍 Target: 9481 Marbach Rd (Richland Hills Tract)")
    print("📏 Market: Far West San Antonio Land Corridor")
    print("🎯 Analysis: Cost per acre from CoStar comparable sales")
    print()
    
    analyzer = MarbachLandCostAnalyzer()
    
    # Analyze CoStar data
    properties, analysis = analyzer.load_and_analyze_costar_data()
    
    if analysis:
        # Export results
        analyzer.export_analysis(properties, analysis)
        
        print(f"\n🏁 MARKET ANALYSIS COMPLETE")
        print(f"💰 Market Rate: ${analysis['median_cost_per_acre']:,.0f}/acre (median)")
        print(f"🎯 10-Acre Value: ${analysis['median_cost_per_acre'] * 10:,.0f}")
        print(f"📊 Based on {analysis['sample_size']} comparable sales")
    else:
        print("❌ Analysis failed - check CoStar data format")

if __name__ == "__main__":
    main()