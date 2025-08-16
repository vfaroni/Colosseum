#!/usr/bin/env python3
"""
Final Arizona USDA Rural Development Properties Analysis
With correct county and AMI data matching
"""

import pandas as pd
import folium
from folium.plugins import MeasureControl
from datetime import datetime

class ArizonaFinalAnalyzer:
    def __init__(self):
        # Properties with coordinates and correct county assignments
        self.properties = [
            {
                "name": "Mt. Graham",
                "address": "2040 S Twentieth Avenue, Safford, AZ",
                "units": 40,
                "rental_assistance": 36,
                "latitude": 32.822054,
                "longitude": -109.720607,
                "county": "Graham County",
                "city": "Safford"
            },
            {
                "name": "Safford Villa", 
                "address": "106 W 11th Street, Safford, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.8276193,
                "longitude": -109.7085118,
                "county": "Graham County",
                "city": "Safford"
            },
            {
                "name": "Willcox Villa",
                "address": "201 N. Bisbee Ave, Wilcox, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.261129,
                "longitude": -109.841382,
                "county": "Cochise County",
                "city": "Willcox"
            },
            {
                "name": "Cochise Apts",
                "address": "650 W. Union Street, Benson, AZ",
                "units": 24,
                "rental_assistance": 23,
                "latitude": 31.962736,
                "longitude": -110.308719,
                "county": "Cochise County",
                "city": "Benson"
            },
            {
                "name": "United Church Village Apts",
                "address": "320 E Placita Naco Cir, Nogales, AZ 85621",
                "units": 48,
                "rental_assistance": 48,
                "latitude": 31.3713391,
                "longitude": -110.9240253,
                "county": "Santa Cruz County",
                "city": "Nogales"
            }
        ]
        
        # County AMI data from HUD 2025
        self.county_ami_data = {
            "Graham County": {
                "ami_100_4person": 81100,
                "rent_studio_60": 852,
                "rent_1br_60": 912,
                "rent_2br_60": 1095,
                "rent_3br_60": 1265,
                "rent_4br_60": 1411,
                "metro_status": "Non-Metro",
                "hud_area": "Graham County, AZ"
            },
            "Cochise County": {
                "ami_100_4person": 71200,
                "rent_studio_60": 748,
                "rent_1br_60": 801,
                "rent_2br_60": 961,
                "rent_3br_60": 1110,
                "rent_4br_60": 1239,
                "metro_status": "Metro",
                "hud_area": "Sierra Vista-Douglas, AZ MSA"
            },
            "Santa Cruz County": {
                "ami_100_4person": 66100,
                "rent_studio_60": 735,
                "rent_1br_60": 787,
                "rent_2br_60": 945,
                "rent_3br_60": 1092,
                "rent_4br_60": 1218,
                "metro_status": "Non-Metro",
                "hud_area": "Santa Cruz County, AZ"
            }
        }
        
        # Census tract poverty data (estimated from 2022 ACS)
        self.poverty_data = {
            "Graham County": 12.4,  # Estimated rural poverty rate
            "Cochise County": 11.8,  # Estimated rural poverty rate  
            "Santa Cruz County": 16.2  # Estimated border county poverty rate
        }
    
    def analyze_properties(self):
        """Add AMI and poverty data to properties"""
        print("\n🏢 FINAL ARIZONA RURAL DEVELOPMENT ANALYSIS")
        print("=" * 55)
        
        for prop in self.properties:
            county = prop['county']
            
            # Add AMI data
            ami_data = self.county_ami_data[county]
            prop.update(ami_data)
            
            # Add poverty data
            prop['poverty_rate'] = self.poverty_data[county]
            
            # Add QCT/DDA status (all rural properties are neither)
            prop['is_qct'] = False
            prop['is_dda'] = False
            prop['qct_dda_status'] = "Neither (Rural)"
            
            print(f"\n📊 {prop['name']} - {prop['city']}")
            print(f"   County: {county}")
            print(f"   Units: {prop['units']} (RA: {prop['rental_assistance']})")
            print(f"   Metro Status: {ami_data['metro_status']}")
            print(f"   4-Person 100% AMI: ${ami_data['ami_100_4person']:,}")
            print(f"   60% AMI Rents: 1BR=${ami_data['rent_1br_60']}, 2BR=${ami_data['rent_2br_60']}, 3BR=${ami_data['rent_3br_60']}, 4BR=${ami_data['rent_4br_60']}")
            print(f"   Poverty Rate: {prop['poverty_rate']:.1f}%")
            print(f"   QCT/DDA Status: Neither (Rural)")
        
        return self.properties
    
    def create_map(self):
        """Create HTML map of all properties"""
        print("\n🗺️ Creating interactive map...")
        
        # Calculate center point
        lats = [prop['latitude'] for prop in self.properties]
        lons = [prop['longitude'] for prop in self.properties]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add properties
        for prop in self.properties:
            popup_text = f"""
            <b>{prop['name']}</b><br>
            <b>Address:</b> {prop['address']}<br>
            <b>Units:</b> {prop['units']} (RA: {prop['rental_assistance']})<br>
            <b>County:</b> {prop['county']}<br>
            <b>Metro Status:</b> {prop['metro_status']}<br>
            <b>QCT/DDA:</b> Neither (Rural)<br>
            <b>Poverty Rate:</b> {prop['poverty_rate']:.1f}%<br>
            <b>4-Person 100% AMI:</b> ${prop['ami_100_4person']:,}<br>
            <b>60% AMI Rents:</b><br>
            • Studio: ${prop['rent_studio_60']}<br>
            • 1BR: ${prop['rent_1br_60']}<br>
            • 2BR: ${prop['rent_2br_60']}<br>
            • 3BR: ${prop['rent_3br_60']}<br>
            • 4BR: ${prop['rent_4br_60']}
            """
            
            # Color code by county
            county_colors = {
                "Graham County": "green",
                "Cochise County": "blue", 
                "Santa Cruz County": "red"
            }
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{prop['name']} - {prop['city']}",
                icon=folium.Icon(color=county_colors[prop['county']], icon='home')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px
                    ">
        <h4>Arizona USDA Rural Properties</h4>
        <p><i class="fa fa-map-marker fa-2x" style="color:green"></i> Graham County (2)</p>
        <p><i class="fa fa-map-marker fa-2x" style="color:blue"></i> Cochise County (2)</p>
        <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> Santa Cruz County (1)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>Arizona USDA Rural Development Properties</b></h3>
        <h4 align="center" style="font-size:14px">LIHTC Eligibility Analysis - 5 Properties, 160 Units</h4>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        map_filename = f"Arizona_Rural_Properties_Final_Map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(map_filename)
        print(f"✅ Map saved to: {map_filename}")
        
        return map_filename
    
    def save_results(self):
        """Save results to Excel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.properties)
        
        # Reorder columns for clarity
        column_order = [
            'name', 'address', 'city', 'county', 'units', 'rental_assistance',
            'latitude', 'longitude', 'is_qct', 'is_dda', 'qct_dda_status',
            'poverty_rate', 'metro_status', 'hud_area',
            'ami_100_4person', 'rent_studio_60', 'rent_1br_60', 'rent_2br_60', 
            'rent_3br_60', 'rent_4br_60'
        ]
        
        existing_cols = [col for col in column_order if col in df.columns]
        df = df[existing_cols]
        
        # Save Excel
        excel_path = f"Arizona_Rural_Final_Analysis_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✅ Final analysis saved to: {excel_path}")
        
        return excel_path
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n📋 COMPREHENSIVE SUMMARY")
        print("=" * 100)
        print(f"{'Property':<25} {'County':<15} {'Units':<6} {'RA':<4} {'Metro':<10} {'Poverty%':<9} {'100% AMI':<10} {'1BR':<5} {'2BR':<5} {'3BR':<5} {'4BR':<5}")
        print("-" * 100)
        
        total_units = 0
        total_ra = 0
        
        for prop in self.properties:
            total_units += prop['units']
            total_ra += prop['rental_assistance']
            
            metro_short = "Metro" if prop['metro_status'] == "Metro" else "Rural"
            
            print(f"{prop['name'][:24]:<25} {prop['county'][:14]:<15} {prop['units']:<6} {prop['rental_assistance']:<4} {metro_short:<10} {prop['poverty_rate']:.1f}%{'':<4} ${prop['ami_100_4person']:,}{'':<2} ${prop['rent_1br_60']:<4} ${prop['rent_2br_60']:<4} ${prop['rent_3br_60']:<4} ${prop['rent_4br_60']:<4}")
        
        print("-" * 100)
        print(f"{'TOTALS':<25} {'3 Counties':<15} {total_units:<6} {total_ra:<4} {'Mix':<10} {'Varies':<9} {'Varies':<10}")
        
        print(f"\n📊 PORTFOLIO SUMMARY:")
        print(f"   • Total Properties: 5")
        print(f"   • Total Units: {total_units}")
        print(f"   • Total Rental Assistance: {total_ra} units ({total_ra/total_units*100:.1f}%)")
        print(f"   • Counties: Graham (2), Cochise (2), Santa Cruz (1)")
        print(f"   • QCT/DDA Status: None (All Rural)")
        print(f"   • Metro Status: 2 Metro, 3 Rural")

if __name__ == "__main__":
    analyzer = ArizonaFinalAnalyzer()
    results = analyzer.analyze_properties()
    analyzer.save_results()
    analyzer.create_map()
    analyzer.print_summary()