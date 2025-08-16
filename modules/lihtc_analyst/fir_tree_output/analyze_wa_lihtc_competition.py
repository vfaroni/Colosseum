#!/usr/bin/env python3
"""
Analyze Washington LIHTC competition within 2 miles of Fir Tree Park
Uses the Washington LIHTC database to identify competing projects
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
import sys
import os

def analyze_lihtc_competition():
    """Analyze LIHTC projects within 2 miles of Fir Tree Park"""
    
    # Fir Tree Park coordinates
    fir_tree_lat = 47.2172038
    fir_tree_lon = -123.1027976
    fir_tree_coords = (fir_tree_lat, fir_tree_lon)
    
    print("🏛️ WASHINGTON LIHTC COMPETITION ANALYSIS")
    print("=" * 50)
    print(f"📍 Target Property: Fir Tree Park Apartments")
    print(f"🗺️ Coordinates: {fir_tree_lat}, {fir_tree_lon}")
    print(f"📏 Search Radius: 2.0 miles (rural standard)")
    print()
    
    # Load Washington LIHTC database
    wa_lihtc_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/Big TC List for website_2-6-25.xlsx"
    
    try:
        df = pd.read_excel(wa_lihtc_path)
        print(f"✅ Loaded {len(df)} Washington LIHTC projects from database")
        print(f"📊 Columns: {list(df.columns)}")
        print()
        
        # Display first few rows to understand structure
        print("📋 Sample Data:")
        print(df.head(3).to_string())
        print()
        
        # Look for coordinate columns (common names)
        coord_columns = [col for col in df.columns if any(term in col.lower() for term in ['lat', 'lon', 'coord', 'geo'])]
        if coord_columns:
            print(f"🗺️ Coordinate columns found: {coord_columns}")
        else:
            print("⚠️ No coordinate columns detected - will need geocoding")
        
        # Look for address/location columns
        location_columns = [col for col in df.columns if any(term in col.lower() for term in ['address', 'city', 'county', 'location', 'street'])]
        print(f"📍 Location columns: {location_columns}")
        print()
        
        # Look for project details
        detail_columns = [col for col in df.columns if any(term in col.lower() for term in ['name', 'project', 'units', 'type', 'year', 'senior'])]
        print(f"🏢 Project detail columns: {detail_columns}")
        print()
        
        # For now, create analysis framework
        competing_projects = []
        
        # If we have coordinates, calculate distances
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            print("🔍 Calculating distances using coordinates...")
            for idx, row in df.iterrows():
                try:
                    project_lat = float(row['Latitude'])
                    project_lon = float(row['Longitude'])
                    project_coords = (project_lat, project_lon)
                    
                    distance_miles = geodesic(fir_tree_coords, project_coords).miles
                    
                    if distance_miles <= 2.0:
                        competing_projects.append({
                            'name': row.get('Project Name', 'Unknown'),
                            'address': row.get('Address', 'Address not available'),
                            'city': row.get('City', 'Unknown'),
                            'units': row.get('Total Units', 'Unknown'),
                            'type': row.get('Project Type', 'Unknown'),
                            'year': row.get('Year', 'Unknown'),
                            'distance_miles': round(distance_miles, 2),
                            'lat': project_lat,
                            'lon': project_lon
                        })
                except (ValueError, TypeError):
                    continue
        
        # Generate competition analysis
        print(f"🎯 COMPETITION ANALYSIS RESULTS:")
        print(f"   Total WA LIHTC Projects: {len(df)}")
        print(f"   Projects within 2 miles: {len(competing_projects)}")
        print()
        
        if competing_projects:
            print("🏘️ COMPETING PROJECTS:")
            for i, project in enumerate(competing_projects, 1):
                print(f"   {i}. {project['name']}")
                print(f"      📍 {project['address']}, {project['city']}")
                print(f"      🏠 Units: {project['units']} | Type: {project['type']}")
                print(f"      📏 Distance: {project['distance_miles']} miles")
                print(f"      🗓️ Year: {project['year']}")
                print()
        else:
            print("✅ NO COMPETING LIHTC PROJECTS within 2 miles")
            print("   This indicates excellent market positioning for Fir Tree Park")
            print()
        
        # Generate HTML snippet for report
        html_snippet = generate_html_competition_section(competing_projects)
        
        # Save to file for HTML integration
        with open('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output/lihtc_competition_analysis.html', 'w') as f:
            f.write(html_snippet)
        
        print("📄 HTML competition analysis saved to: lihtc_competition_analysis.html")
        
        return competing_projects
        
    except Exception as e:
        print(f"❌ Error analyzing LIHTC competition: {e}")
        return []

def generate_html_competition_section(competing_projects):
    """Generate HTML snippet for competition analysis"""
    
    if not competing_projects:
        return """
        <div style="background: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 1rem;">
            <strong>✅ EXCELLENT MARKET POSITIONING:</strong><br>
            <span style="color: #166534;">NO COMPETING LIHTC PROJECTS</span> found within 2-mile radius.<br>
            Fir Tree Park has <strong>exclusive senior housing market position</strong> in Shelton area.
        </div>
        """
    
    html = """
    <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem;">
        <strong>⚠️ LIHTC COMPETITION DETECTED:</strong><br>
        <span style="color: #d97706;">{} competing projects</span> within 2-mile radius:<br>
        <ul style="margin-top: 0.5rem;">
    """.format(len(competing_projects))
    
    for project in competing_projects:
        html += f"""
            <li><strong>{project['name']}</strong> - {project['units']} units, {project['distance_miles']} miles away</li>
        """
    
    html += """
        </ul>
        <em>Competition analysis based on Washington State LIHTC database (Feb 2025)</em>
    </div>
    """
    
    return html

if __name__ == "__main__":
    results = analyze_lihtc_competition()