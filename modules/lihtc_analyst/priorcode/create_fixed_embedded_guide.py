#!/usr/bin/env python3
"""
Create Fixed Site Visit Guide with Proper Data Extraction and Improved Styling
Fixes data extraction issues and improves contrast/readability

Author: Bill Rice, Structured Consultants LLC
Date: June 26, 2025
"""

import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic

class FixedEmbeddedGuide:
    """Creates site visit guide with fixed data extraction and better styling"""
    
    def __init__(self):
        self.base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets"
        self.tdhca_file = f"{self.base_path}/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        self.census_api_key = '06ece0121263282cd9ffd753215b007b8f9a3dfc'
        self.tdhca_data = None
        self.poverty_cache = {}
        
        self.load_tdhca_data()
        
        # Site coordinates (manually verified - addresses may not exist yet)
        self.sites = [
            {
                'name': '615 N Saginaw Blvd, Saginaw, TX 76179',
                'short_name': 'Saginaw',
                'acres': 6.38,
                'price': 1845000,
                'lat': 32.8598,  # Saginaw, TX city center area
                'lng': -97.2186,
                'county': 'Tarrant',
                'note': 'Coordinates approximated - exact address may not exist'
            },
            {
                'name': '2002 Mansfield Webb Rd, Mansfield, TX 76002', 
                'short_name': 'Mansfield',
                'acres': 3.67,
                'price': 1680000,
                'lat': 32.612960,  # User provided corrected coordinates
                'lng': -97.106047,
                'county': 'Tarrant',
                'note': 'User-corrected coordinates'
            },
            {
                'name': '1051 W Marshall Dr, Grand Prairie, TX 75051',
                'short_name': 'Grand Prairie',
                'acres': 7.35,
                'price': 1100000,
                'lat': 32.7461,  # Grand Prairie area
                'lng': -97.0100,
                'county': 'Dallas',
                'note': 'Coordinates approximated - exact address may not exist'
            },
            {
                'name': '7100 W Camp Wisdom Rd, Dallas, TX 75249',
                'short_name': 'Dallas',
                'acres': 6.08,
                'price': 1100000,
                'lat': 32.6780,  # Southwest Dallas area
                'lng': -96.9150,
                'county': 'Dallas',
                'note': 'Coordinates approximated - exact address may not exist'
            },
            {
                'name': '1497 US-67, Cedar Hill, TX 75104',
                'short_name': 'Cedar Hill (US-67)',
                'acres': 8.557,
                'price': 4325000,
                'lat': 32.5885,  # Cedar Hill area along US-67
                'lng': -96.9560,
                'county': 'Dallas',
                'note': 'Coordinates approximated - exact address may not exist'
            },
            {
                'name': '1000 S Joe Wilson Rd, Cedar Hill, TX 75104',
                'short_name': 'Cedar Hill (Joe Wilson)',
                'acres': 4.0,
                'price': 550000,
                'lat': 32.5850,  # Cedar Hill area
                'lng': -96.9565,
                'county': 'Dallas',
                'note': 'Coordinates approximated - exact address may not exist'
            }
        ]
    
    def load_tdhca_data(self):
        """Load TDHCA project data for competition analysis"""
        try:
            if Path(self.tdhca_file).exists():
                self.tdhca_data = pd.read_excel(self.tdhca_file, sheet_name='PropInventory')
                
                # Clean coordinates
                self.tdhca_data['Latitude11'] = pd.to_numeric(self.tdhca_data['Latitude11'], errors='coerce')
                self.tdhca_data['Longitude11'] = pd.to_numeric(self.tdhca_data['Longitude11'], errors='coerce')
                self.tdhca_data = self.tdhca_data.dropna(subset=['Latitude11', 'Longitude11'])
                
                if 'Year' in self.tdhca_data.columns:
                    self.tdhca_data['Year'] = pd.to_numeric(self.tdhca_data['Year'], errors='coerce')
                
                print(f"✅ Loaded {len(self.tdhca_data)} TDHCA projects for competition analysis")
                print(f"✅ Available columns: {list(self.tdhca_data.columns)}")
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
    
    def get_tract_poverty_rate(self, lat, lng):
        """Get poverty rate for census tract using Census API"""
        
        cache_key = f"{lat:.6f},{lng:.6f}"
        if cache_key in self.poverty_cache:
            return self.poverty_cache[cache_key]
        
        try:
            # Use FCC API to get tract, then Census for poverty
            fcc_url = f"https://geo.fcc.gov/api/census/area"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            
            response = requests.get(fcc_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    tract_fips = data['results'][0]['block_fips'][:11]  # First 11 digits = state+county+tract
                    state_fips = tract_fips[:2]
                    county_fips = tract_fips[2:5] 
                    tract_code = tract_fips[5:11]
                    
                    # Get poverty data from ACS
                    census_url = 'https://api.census.gov/data/2022/acs/acs5'
                    census_params = {
                        'get': 'B17001_002E,B17001_001E,NAME',
                        'for': f'tract:{tract_code}',
                        'in': f'state:{state_fips} county:{county_fips}',
                        'key': self.census_api_key
                    }
                    
                    time.sleep(0.2)  # Rate limiting
                    census_response = requests.get(census_url, params=census_params, timeout=30)
                    
                    if census_response.status_code == 200:
                        census_data = census_response.json()
                        if len(census_data) > 1:
                            values = census_data[1]
                            below_poverty = float(values[0]) if values[0] not in ['null', None, '', '-666666666'] else 0
                            total_pop = float(values[1]) if values[1] not in ['null', None, '', '-666666666'] else 0
                            
                            if total_pop > 0:
                                poverty_rate = (below_poverty / total_pop) * 100
                                result = {
                                    'poverty_rate': round(poverty_rate, 1),
                                    'census_tract': tract_fips,
                                    'tract_name': values[2] if len(values) > 2 else '',
                                    'total_population': int(total_pop),
                                    'below_poverty': int(below_poverty),
                                    'low_poverty_bonus': poverty_rate <= 20.0,
                                    'success': True
                                }
                                self.poverty_cache[cache_key] = result
                                return result
                                
        except Exception as e:
            print(f"Warning: Could not get poverty data for {lat}, {lng}: {e}")
        
        # Return failure result
        result = {
            'poverty_rate': None,
            'census_tract': None,
            'tract_name': None,
            'total_population': None,
            'below_poverty': None,
            'low_poverty_bonus': None,
            'success': False
        }
        self.poverty_cache[cache_key] = result
        return result
    
    def get_competing_projects(self, lat, lng, radius_miles=2.0):
        """Get competing LIHTC projects within specified radius - FIXED DATA EXTRACTION"""
        competing_projects = []
        
        if self.tdhca_data is None:
            return competing_projects
        
        try:
            site_coords = (lat, lng)
            current_year = datetime.now().year
            
            for idx, project in self.tdhca_data.iterrows():
                try:
                    project_coords = (project['Latitude11'], project['Longitude11'])
                    distance_miles = geodesic(site_coords, project_coords).miles
                    
                    if distance_miles <= radius_miles:
                        project_year = int(project.get('Year', 0))
                        years_ago = current_year - project_year
                        
                        # Determine risk level
                        risk_level = 'Low Risk'
                        is_fatal_9pct = False
                        
                        if distance_miles <= 1.0 and years_ago <= 3:
                            risk_level = 'HIGH RISK - One Mile Rule'
                            is_fatal_9pct = True
                        elif distance_miles <= 2.0 and years_ago <= 1:
                            risk_level = 'MEDIUM RISK - Two Mile Rule'
                        
                        # FIXED: Use correct column names
                        dev_name = project.get('Development Name', 'Unknown Development')
                        if pd.isna(dev_name) or dev_name == '':
                            dev_name = 'Unnamed Project'
                            
                        address = project.get('Project Address ', 'Address Not Available')  # Note space after Address
                        if pd.isna(address) or address == '':
                            address = 'Address Not Available'
                            
                        city = project.get('Project City', 'City Not Available')
                        if pd.isna(city) or city == '':
                            city = 'City Not Available'
                            
                        county = project.get('Project County', 'County Not Available')
                        if pd.isna(county) or county == '':
                            county = 'County Not Available'
                            
                        units = project.get('Total Units', 'Unknown')
                        if pd.isna(units):
                            units = 'Unknown'
                        
                        # FIXED: Population Served instead of Program
                        population_served = project.get('Population Served', 'Unknown')
                        if pd.isna(population_served) or population_served == '':
                            population_served = 'Unknown'
                        
                        # Get Program Type (Family, Elderly, etc.)
                        program_type = project.get('Program Type', 'Unknown')
                        if pd.isna(program_type) or program_type == '':
                            program_type = 'Unknown'
                        
                        competing_projects.append({
                            'name': str(dev_name),
                            'address': str(address),
                            'city': str(city),
                            'county': str(county),
                            'units': str(units),
                            'year': project_year,
                            'program_type': str(program_type),
                            'population_served': str(population_served),
                            'distance_miles': round(distance_miles, 2),
                            'years_ago': years_ago,
                            'risk_level': risk_level,
                            'fatal_9pct': is_fatal_9pct
                        })
                        
                except Exception as e:
                    print(f"Warning: Error processing project at index {idx}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in competition analysis: {e}")
        
        # Sort by distance
        competing_projects.sort(key=lambda x: x['distance_miles'])
        return competing_projects
    
    def create_embedded_html_guide(self):
        """Create HTML guide with all data embedded directly in content"""
        
        print("🚀 Collecting poverty and competition data for all sites...")
        
        # Collect all data for sites
        sites_with_data = []
        for i, site in enumerate(self.sites):
            print(f"   Processing site {i+1}/6: {site['short_name']}")
            
            # Get poverty data
            poverty_data = self.get_tract_poverty_rate(site['lat'], site['lng'])
            
            # Get competition data
            competing_projects = self.get_competing_projects(site['lat'], site['lng'])
            
            # Calculate summary stats
            site['poverty_data'] = poverty_data
            site['competing_projects'] = competing_projects
            site['competition_count_1mi'] = len([p for p in competing_projects if p['distance_miles'] <= 1.0])
            site['competition_count_2mi'] = len([p for p in competing_projects if p['distance_miles'] <= 2.0])
            site['fatal_9pct_count'] = len([p for p in competing_projects if p['fatal_9pct']])
            
            sites_with_data.append(site)
        
        # Read the original markdown guide
        md_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/DMarco_Site_Visit_Guide_June2025.md")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML and inject site data
        enhanced_html = self.create_html_with_fixed_styling(md_content, sites_with_data)
        
        # Save enhanced version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/DMarco_Fixed_Final_Guide_{timestamp}.html")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_html)
        
        print(f"✅ Fixed final guide created: {output_file}")
        return output_file, sites_with_data
    
    def create_html_with_fixed_styling(self, md_content, sites_data):
        """Create HTML with improved contrast and styling"""
        
        # Start with improved HTML structure
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D'Marco Site Visit Guide - Enhanced with Live Data</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 15px; }}
        h2 {{ color: #2b6cb0; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-top: 40px; }}
        h3 {{ color: #2d3748; margin-top: 30px; }}
        h4 {{ color: #4a5568; margin-top: 25px; }}
        
        .site-section {{
            background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
            color: #1a202c;
            padding: 30px;
            border-radius: 12px;
            margin: 40px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-left: 6px solid #3182ce;
        }}
        
        .site-header {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 25px;
        }}
        
        .site-details {{
            background: rgba(49, 130, 206, 0.1);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #3182ce;
        }}
        
        .data-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .data-stat {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .data-stat h4 {{
            margin: 0 0 5px 0;
            font-size: 1.6em;
            font-weight: bold;
            color: #2d3748;
        }}
        
        .data-stat p {{
            margin: 0;
            font-size: 0.9em;
            color: #4a5568;
        }}
        
        .competition-projects {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border: 1px solid #e2e8f0;
        }}
        
        .project-item {{
            background: white;
            color: #2d3748;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 5px solid #68d391;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .project-item.fatal {{
            border-left-color: #f56565;
            background: #fed7d7;
        }}
        
        .project-item.medium-risk {{
            border-left-color: #ed8936;
            background: #feebc8;
        }}
        
        .project-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .detail-item {{
            font-size: 0.95em;
            padding: 8px;
            background: #f7fafc;
            border-radius: 4px;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #2d3748;
            display: block;
        }}
        
        .detail-value {{
            color: #4a5568;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .risk-high {{ background: #f56565; color: white; }}
        .risk-medium {{ background: #ed8936; color: white; }}
        .risk-low {{ background: #68d391; color: white; }}
        
        .poverty-bonus {{
            background: #68d391;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }}
        
        .no-bonus {{
            background: #a0aec0;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            display: inline-block;
            margin: 10px 0;
        }}
        
        .questions-section {{
            background: #edf2f7;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #3182ce;
        }}
        
        .quick-links {{
            margin-top: 15px;
            padding: 10px;
            background: rgba(49, 130, 206, 0.05);
            border-radius: 6px;
            border: 1px solid rgba(49, 130, 206, 0.2);
        }}
        
        .quick-links a {{
            color: #3182ce;
            text-decoration: none;
            font-weight: 500;
            margin-right: 15px;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}
        
        .quick-links a:hover {{
            background-color: rgba(49, 130, 206, 0.1);
            text-decoration: underline;
        }}
        
        .census-link {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        @media (max-width: 768px) {{
            .site-header {{ grid-template-columns: 1fr; }}
            .data-summary {{ grid-template-columns: repeat(2, 1fr); }}
            .project-details {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 id="top">D'Marco Site Visit Underwriting Guide</h1>
        <h2>LIHTC Underwriting Analysis - June 26, 2025</h2>
        
        <h3>Executive Summary</h3>
        <p>This guide provides detailed LIHTC underwriting questions and analysis points for D'Marco's site visit to 6 Texas properties. Each site includes live TDHCA competition data and census tract poverty rates for immediate field validation.</p>
        
        {self.generate_fixed_sites_html(sites_data)}
        
        {self.generate_checklist_html()}
        
        <hr style="margin: 50px 0;">
        <p><strong>Prepared by:</strong> Bill Rice, Structured Consultants LLC<br>
        <strong>Date:</strong> June 26, 2025<br>
        <strong>Analysis Basis:</strong> Texas LIHTC Production System Documentation</p>
    </div>
</body>
</html>
"""
        return html_template
    
    def generate_fixed_sites_html(self, sites_data):
        """Generate HTML for all sites with FIXED data display"""
        sites_html = ""
        
        for i, site in enumerate(sites_data, 1):
            poverty = site['poverty_data']
            competing = site['competing_projects']
            
            # Determine 9% viability
            viability_9pct = "VIABLE" if site['fatal_9pct_count'] == 0 else "AVOID - Fatal Flaw"
            viability_class = "risk-low" if site['fatal_9pct_count'] == 0 else "risk-high"
            
            # Poverty bonus status
            poverty_bonus_html = ""
            if poverty['success'] and poverty['poverty_rate'] is not None:
                if poverty['low_poverty_bonus']:
                    poverty_bonus_html = f'<div class="poverty-bonus">✅ 9% Low Poverty Bonus Eligible ({poverty["poverty_rate"]}% ≤ 20%)</div>'
                else:
                    poverty_bonus_html = f'<div class="no-bonus">No 9% Poverty Bonus ({poverty["poverty_rate"]}% > 20%)</div>'
            else:
                poverty_bonus_html = '<div class="no-bonus">Poverty Data Unavailable</div>'
            
            sites_html += f"""
        <div class="site-section">
            <div class="site-header">
                <div>
                    <h2>Site #{i}: {site['name']}</h2>
                    <p><strong>{site['acres']} acres • ${site['price']:,} • ${site['price']/site['acres']:,.0f} per acre</strong></p>
                    <p><strong>County:</strong> {site['county']} | <strong>TDHCA Region:</strong> 3 (Dallas-Fort Worth Metro)</p>
                    {poverty_bonus_html}
                </div>
                <div class="site-details">
                    <h4>Live Data Summary</h4>
                    <p><strong>Coordinates:</strong> {site['lat']:.6f}, {site['lng']:.6f}</p>
                    <p><strong>Census Tract:</strong> {self.generate_census_links(poverty, site)}</p>
                    <p><strong>Poverty Rate:</strong> {poverty.get('poverty_rate', 'Unknown')}%</p>
                    <div class="quick-links">
                        <strong>Quick Links:</strong><br>
                        {self.generate_map_links(site)}
                    </div>
                </div>
            </div>
            
            <div class="data-summary">
                <div class="data-stat">
                    <h4>{site['competition_count_1mi']}</h4>
                    <p>Within 1 Mile</p>
                </div>
                <div class="data-stat">
                    <h4>{site['competition_count_2mi']}</h4>
                    <p>Within 2 Miles</p>
                </div>
                <div class="data-stat">
                    <h4>{site['fatal_9pct_count']}</h4>
                    <p>Fatal 9% Flaws</p>
                </div>
                <div class="data-stat">
                    <h4><span class="{viability_class}">{viability_9pct}</span></h4>
                    <p>9% Viability</p>
                </div>
            </div>
            
            {self.generate_fixed_competition_html(competing)}
            {self.generate_site_questions_html(site)}
        </div>
"""
        
        return sites_html
    
    def generate_fixed_competition_html(self, competing_projects):
        """Generate HTML for competing projects with FIXED data display"""
        if not competing_projects:
            return """
            <div class="competition-projects">
                <h4>✅ No Competing LIHTC Projects Found</h4>
                <p>Clean site with no LIHTC competition within 2 miles - excellent for both 4% and 9% deals!</p>
            </div>
            """
        
        html = f"""
            <div class="competition-projects">
                <h4>🏢 Competing LIHTC Projects ({len(competing_projects)} found)</h4>
        """
        
        for project in competing_projects:
            risk_class = 'fatal' if project['fatal_9pct'] else ('medium-risk' if 'MEDIUM' in project['risk_level'] else '')
            risk_badge = 'risk-high' if project['fatal_9pct'] else ('risk-medium' if 'MEDIUM' in project['risk_level'] else 'risk-low')
            
            html += f"""
                <div class="project-item {risk_class}">
                    <h4>{project['name']}</h4>
                    <span class="risk-badge {risk_badge}">{project['risk_level']}</span>
                    
                    <div class="project-details">
                        <div class="detail-item">
                            <span class="detail-label">Distance</span>
                            <span class="detail-value">{project['distance_miles']} miles</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Year</span>
                            <span class="detail-value">{project['year']} ({project['years_ago']} years ago)</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Units</span>
                            <span class="detail-value">{project['units']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Program Type</span>
                            <span class="detail-value">{project['program_type']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Population</span>
                            <span class="detail-value">{project['population_served']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Address</span>
                            <span class="detail-value">{project['address']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">City</span>
                            <span class="detail-value">{project['city']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">County</span>
                            <span class="detail-value">{project['county']}</span>
                        </div>
                    </div>
                </div>
            """
        
        html += "</div>"
        return html
    
    def generate_census_links(self, poverty_data, site):
        """Generate links to Census data sources - FIXED URLs"""
        if not poverty_data['success'] or not poverty_data['census_tract']:
            return "Unknown"
        
        tract_number = poverty_data['census_tract']
        
        # FIXED: Correct Census.gov URLs that actually work
        # Poverty data table for specific tract
        census_poverty_url = f"https://data.census.gov/table/ACSST5Y2022.S1701?g=1400000US{tract_number}"
        
        # Census Reporter (better alternative with cleaner interface)
        census_reporter_url = f"https://censusreporter.org/profiles/14000US{tract_number}/"
        
        return f'''
        <a href="{census_poverty_url}" target="_blank" class="census-link" style="color: #3182ce; text-decoration: none;">{tract_number}</a>
        <br><small>
        <a href="{census_reporter_url}" target="_blank" style="color: #3182ce; font-size: 0.8em;">📊 Census Reporter Profile</a>
        </small>
        '''
    
    def generate_map_links(self, site):
        """Generate links to Google Maps (Apple Maps removed due to coordinate issues)"""
        lat = site['lat']
        lng = site['lng']
        address = site['name'].replace(' ', '+').replace(',', '%2C')
        
        # Google Maps with coordinates (most accurate)
        google_coords_url = f"https://www.google.com/maps?q={lat},{lng}&z=17"
        
        # Google Maps with address search (backup)
        google_search_url = f"https://www.google.com/maps/search/{address}"
        
        # Google Maps Street View
        streetview_url = f"https://www.google.com/maps/@{lat},{lng},3a,75y,0h,90t/data=!3m6!1e1!3m4!1s0x0:0x0!2e0!7i16384!8i8192"
        
        return f'''
        <a href="{google_coords_url}" target="_blank" style="color: #3182ce; text-decoration: none; margin-right: 15px;">
        🗺️ Google Maps</a>
        <a href="{google_search_url}" target="_blank" style="color: #3182ce; text-decoration: none; margin-right: 15px;">
        🔍 Search Address</a>
        <a href="{streetview_url}" target="_blank" style="color: #3182ce; text-decoration: none;">
        👁️ Street View</a>
        '''
    
    def generate_site_questions_html(self, site):
        """Generate underwriting questions specific to each site"""
        return f"""
            <div class="questions-section">
                <h4>🎯 Key Underwriting Questions for This Site</h4>
                <ul>
                    <li><strong>Land Value Justification:</strong> Why ${site['price']/site['acres']:,.0f} per acre? What premium factors justify this pricing?</li>
                    <li><strong>Development Density:</strong> Can this {site['acres']}-acre site support 150+ units efficiently?</li>
                    <li><strong>Site Conditions:</strong> Any topography, environmental, or utility challenges?</li>
                    <li><strong>Zoning & Entitlements:</strong> Current zoning allows multifamily? Timeline for approvals?</li>
                    <li><strong>Market Rents:</strong> What are comparable 1BR/2BR rents in immediate area?</li>
                    <li><strong>Municipal Support:</strong> City/county attitude toward affordable housing?</li>
                    <li><strong>Infrastructure:</strong> Sewer capacity, traffic impact requirements, storm drainage?</li>
                </ul>
            </div>
        """
    
    def generate_checklist_html(self):
        """Generate comprehensive underwriting checklist"""
        return """
        <h2>🔍 Comprehensive Underwriting Checklist</h2>
        
        <h3>Pre-Development Due Diligence</h3>
        <ul>
            <li><strong>Environmental Phase I Assessment</strong> - Any red flags or concerns?</li>
            <li><strong>Geotechnical Soil Report</strong> - Foundation and construction implications?</li>
            <li><strong>Title Report</strong> - Easements, restrictions, or encumbrances?</li>
            <li><strong>Survey</strong> - Accurate boundaries and developable area calculation?</li>
        </ul>

        <h3>Municipal & Regulatory Analysis</h3>
        <ul>
            <li><strong>Zoning Compliance</strong> - Current zoning allows intended use?</li>
            <li><strong>Variance Requirements</strong> - Any zoning relief needed?</li>
            <li><strong>Subdivision/Site Plan</strong> - Municipal approval process and timeline?</li>
            <li><strong>Impact Fees</strong> - Traffic, parks, school district contributions?</li>
        </ul>

        <h3>Market & Competition Validation</h3>
        <ul>
            <li><strong>LIHTC Competition</strong> - Verify data above with local market knowledge</li>
            <li><strong>Market Rate Competition</strong> - Rent levels and absorption rates</li>
            <li><strong>Demographic Analysis</strong> - Target renter population presence</li>
            <li><strong>Economic Drivers</strong> - Employment base and income trends</li>
        </ul>

        <h3>TDHCA Specific Considerations</h3>
        
        <h4>4% Tax-Exempt Bond Deals (Recommended for Sites with Competition)</h4>
        <ul>
            <li>Non-competitive process - first-come, first-served</li>
            <li>No fatal flaw rules apply</li>
            <li>Lower scoring requirements</li>
            <li>Faster application timeline</li>
        </ul>

        <h4>9% Competitive Tax Credit Deals (Clean Sites Only)</h4>
        <ul>
            <li><strong>Fatal Flaw Rules:</strong> ANY LIHTC within 1 mile in last 3 years = FATAL</li>
            <li><strong>Large County Rules:</strong> Dallas/Tarrant apply 2-mile same-year restrictions</li>
            <li><strong>Scoring Advantages:</strong> Low poverty bonus (≤20%) = 2 points</li>
            <li><strong>Construction Costs:</strong> Region 3 carries 15% premium above state average</li>
        </ul>
        """

def main():
    print("🚀 Creating FIXED Final Site Visit Guide...")
    
    guide = FixedEmbeddedGuide()
    output_file, sites_data = guide.create_embedded_html_guide()
    
    print(f"\n📊 Fixed Data Summary:")
    for site in sites_data:
        poverty_rate = site['poverty_data'].get('poverty_rate', 'Unknown')
        poverty_bonus = "✅ Low Poverty Bonus" if site['poverty_data'].get('low_poverty_bonus') else "❌ No Bonus"
        fatal_count = site['fatal_9pct_count']
        viability = "VIABLE" if fatal_count == 0 else "AVOID"
        
        print(f"   {site['short_name']}: {poverty_rate}% poverty ({poverty_bonus}), {site['competition_count_1mi']} competitors, 9% = {viability}")
        
        # Show first competing project if any
        if site['competing_projects']:
            first_comp = site['competing_projects'][0]
            print(f"      → {first_comp['name']} at {first_comp['address']}, {first_comp['city']}")
    
    print(f"\n✅ FIXED guide ready with improved contrast and complete data!")
    print(f"   File: {output_file}")
    print(f"   Features: Fixed data extraction, improved contrast, complete project details")

if __name__ == "__main__":
    main()