#!/usr/bin/env python3
"""
Create Enhanced Site Visit Guide with TDHCA Competition Data Integration
Embeds actual competing LIHTC projects data into interactive HTML guide

Author: Bill Rice, Structured Consultants LLC
Date: June 26, 2025
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic

class EnhancedSiteVisitGuide:
    """Creates interactive HTML guide with embedded TDHCA competition data"""
    
    def __init__(self):
        self.base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets"
        self.tdhca_file = f"{self.base_path}/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        self.tdhca_data = None
        self.load_tdhca_data()
        
        # Site coordinates (corrected Mansfield coordinates included)
        self.sites = [
            {
                'name': '615 N Saginaw Blvd, Saginaw, TX 76179',
                'acres': 6.38,
                'price': 1845000,
                'lat': 32.8673,
                'lng': -97.2192,
                'county': 'Tarrant'
            },
            {
                'name': '2002 Mansfield Webb Rd, Mansfield, TX 76002', 
                'acres': 3.67,
                'price': 1680000,
                'lat': 32.612960,
                'lng': -97.106047,
                'county': 'Tarrant'
            },
            {
                'name': '1051 W Marshall Dr, Grand Prairie, TX 75051',
                'acres': 7.35,
                'price': 1100000,
                'lat': 32.7459,
                'lng': -97.0103,
                'county': 'Dallas'
            },
            {
                'name': '7100 W Camp Wisdom Rd, Dallas, TX 75249',
                'acres': 6.08,
                'price': 1100000,
                'lat': 32.6779,
                'lng': -96.9147,
                'county': 'Dallas'
            },
            {
                'name': '1497 US-67, Cedar Hill, TX 75104',
                'acres': 8.557,
                'price': 4325000,
                'lat': 32.5884,
                'lng': -96.9561,
                'county': 'Dallas'
            },
            {
                'name': '1000 S Joe Wilson Rd, Cedar Hill, TX 75104',
                'acres': 4.0,
                'price': 550000,
                'lat': 32.5851,
                'lng': -96.9564,
                'county': 'Dallas'
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
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
    
    def get_competing_projects(self, lat, lng, radius_miles=2.0):
        """Get competing LIHTC projects within specified radius"""
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
                        
                        # Determine project type and risk level
                        risk_level = 'Low'
                        is_fatal_9pct = False
                        
                        if distance_miles <= 1.0 and years_ago <= 3:
                            risk_level = 'HIGH - One Mile Rule'
                            is_fatal_9pct = True
                        elif distance_miles <= 2.0 and years_ago <= 1:
                            risk_level = 'MEDIUM - Two Mile Rule'
                        
                        competing_projects.append({
                            'name': project.get('Development Name', 'Unknown'),
                            'address': project.get('Property Address', 'Address Unknown'),
                            'city': project.get('Property City', 'City Unknown'),
                            'county': project.get('Property County', 'County Unknown'),
                            'units': project.get('Total Units', 'Unknown'),
                            'year': project_year,
                            'program_type': project.get('Program', 'Unknown'),
                            'distance_miles': round(distance_miles, 2),
                            'years_ago': years_ago,
                            'risk_level': risk_level,
                            'fatal_9pct': is_fatal_9pct
                        })
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error in competition analysis: {e}")
        
        # Sort by distance
        competing_projects.sort(key=lambda x: x['distance_miles'])
        return competing_projects
    
    def create_enhanced_html_guide(self):
        """Create enhanced HTML guide with embedded competition data"""
        
        # Get competition data for all sites
        sites_with_competition = []
        for site in self.sites:
            competing_projects = self.get_competing_projects(site['lat'], site['lng'])
            site['competing_projects'] = competing_projects
            site['competition_count_1mi'] = len([p for p in competing_projects if p['distance_miles'] <= 1.0])
            site['competition_count_2mi'] = len([p for p in competing_projects if p['distance_miles'] <= 2.0])
            site['fatal_9pct_count'] = len([p for p in competing_projects if p['fatal_9pct']])
            sites_with_competition.append(site)
        
        # Read the original markdown guide
        md_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/DMarco_Site_Visit_Guide_June2025.md")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to basic HTML (simplified)
        html_content = self.convert_md_to_html(md_content)
        
        # Create enhanced HTML with embedded data
        enhanced_html = self.create_interactive_html_template(html_content, sites_with_competition)
        
        # Save enhanced version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/DMarco_Enhanced_Site_Visit_Guide_{timestamp}.html")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_html)
        
        print(f"✅ Enhanced HTML guide created: {output_file}")
        return output_file, sites_with_competition
    
    def convert_md_to_html(self, md_content):
        """Basic markdown to HTML conversion"""
        import re
        
        html = md_content
        
        # Headers
        html = re.sub(r'^# (.*?)$', r'<h1 id="top">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Lists
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- \[ \] (.*?)$', r'<li><input type="checkbox"> \1</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive <li> elements in <ul>
        html = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Paragraphs
        html = html.replace('\n\n', '</p><p>')
        html = '<p>' + html + '</p>'
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html
    
    def create_interactive_html_template(self, content, sites_data):
        """Create interactive HTML template with competition data"""
        
        # Convert sites data to JSON for JavaScript
        sites_json = json.dumps(sites_data, indent=2)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D'Marco Site Visit Guide - Enhanced with Competition Data</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 1400px;
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
        .competition-widget {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        .competition-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .competition-stat {{
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .competition-stat h4 {{
            margin: 0 0 5px 0;
            font-size: 1.8em;
            font-weight: bold;
        }}
        .competition-projects {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .project-item {{
            background: rgba(255, 255, 255, 0.9);
            color: #2c3e50;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 5px solid #3498db;
        }}
        .project-item.fatal {{
            border-left-color: #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }}
        .project-item.medium-risk {{
            border-left-color: #f39c12;
            background: rgba(243, 156, 18, 0.1);
        }}
        .project-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .detail-item {{
            font-size: 0.9em;
        }}
        .detail-label {{
            font-weight: bold;
            color: #34495e;
        }}
        .risk-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .risk-high {{ background: #e74c3c; color: white; }}
        .risk-medium {{ background: #f39c12; color: white; }}
        .risk-low {{ background: #27ae60; color: white; }}
        .site-selector {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            min-width: 250px;
        }}
        .site-selector select {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        .toggle-button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px 0;
            width: 100%;
        }}
        .toggle-button:hover {{
            background: #2980b9;
        }}
        .hidden {{
            display: none;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        h1 {{ border-bottom: 3px solid #3498db; padding-bottom: 15px; }}
        h2 {{ border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 40px; }}
        @media (max-width: 768px) {{
            .site-selector {{ position: relative; margin-bottom: 20px; }}
            .competition-summary {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="site-selector">
        <h4 style="margin-top: 0;">Site Navigation</h4>
        <select id="siteSelector" onchange="showSiteCompetition()">
            <option value="">Select a site...</option>
            <option value="0">Saginaw - 615 N Saginaw Blvd</option>
            <option value="1">Mansfield - 2002 Mansfield Webb Rd</option>
            <option value="2">Grand Prairie - 1051 W Marshall Dr</option>
            <option value="3">Dallas - 7100 W Camp Wisdom Rd</option>
            <option value="4">Cedar Hill - 1497 US-67</option>
            <option value="5">Cedar Hill - 1000 S Joe Wilson Rd</option>
        </select>
        <button class="toggle-button" onclick="toggleAllCompetition()">Show All Competition</button>
        <button class="toggle-button" onclick="scrollToTop()">↑ Back to Top</button>
    </div>

    <div class="container">
        {content}
        
        <div id="competitionData" class="hidden">
            <h2>🎯 Live TDHCA Competition Analysis</h2>
            <p><em>Real-time analysis of competing LIHTC projects using TDHCA database (3,264+ projects)</em></p>
            
            <div id="allSitesCompetition">
                <!-- Competition data will be inserted here by JavaScript -->
            </div>
            
            <div id="selectedSiteCompetition">
                <!-- Selected site competition will be shown here -->
            </div>
        </div>
    </div>

    <script>
        // Embedded sites data with competition information
        const SITES_DATA = {sites_json};
        
        function showSiteCompetition() {{
            const selector = document.getElementById('siteSelector');
            const selectedIndex = selector.value;
            const competitionDiv = document.getElementById('competitionData');
            const selectedSiteDiv = document.getElementById('selectedSiteCompetition');
            const allSitesDiv = document.getElementById('allSitesCompetition');
            
            if (selectedIndex === '') {{
                competitionDiv.classList.add('hidden');
                return;
            }}
            
            const site = SITES_DATA[parseInt(selectedIndex)];
            competitionDiv.classList.remove('hidden');
            allSitesDiv.classList.add('hidden');
            
            // Generate HTML for selected site
            selectedSiteDiv.innerHTML = generateSiteCompetitionHTML(site);
            selectedSiteDiv.classList.remove('hidden');
        }}
        
        function toggleAllCompetition() {{
            const competitionDiv = document.getElementById('competitionData');
            const allSitesDiv = document.getElementById('allSitesCompetition');
            const selectedSiteDiv = document.getElementById('selectedSiteCompetition');
            
            if (competitionDiv.classList.contains('hidden')) {{
                competitionDiv.classList.remove('hidden');
                allSitesDiv.classList.remove('hidden');
                selectedSiteDiv.classList.add('hidden');
                
                // Generate HTML for all sites
                allSitesDiv.innerHTML = generateAllSitesCompetitionHTML();
            }} else {{
                competitionDiv.classList.add('hidden');
            }}
        }}
        
        function generateSiteCompetitionHTML(site) {{
            const fatalCount = site.competing_projects.filter(p => p.fatal_9pct).length;
            const oneToTwoMile = site.competing_projects.filter(p => p.distance_miles > 1.0 && p.distance_miles <= 2.0).length;
            
            let html = `
                <div class="competition-widget">
                    <h3>📍 ${{site.name}}</h3>
                    <p><strong>${{site.acres}} acres • $${{(site.price/1000000).toFixed(2)}}M • $${{Math.round(site.price/site.acres)}} per acre</strong></p>
                    
                    <div class="competition-summary">
                        <div class="competition-stat">
                            <h4>${{site.competition_count_1mi}}</h4>
                            <p>Within 1 Mile</p>
                        </div>
                        <div class="competition-stat">
                            <h4>${{site.competition_count_2mi}}</h4>
                            <p>Within 2 Miles</p>
                        </div>
                        <div class="competition-stat">
                            <h4>${{fatalCount}}</h4>
                            <p>9% Fatal Flaws</p>
                        </div>
                        <div class="competition-stat">
                            <h4>${{fatalCount > 0 ? 'AVOID' : 'VIABLE'}}</h4>
                            <p>9% Recommendation</p>
                        </div>
                    </div>
            `;
            
            if (site.competing_projects.length > 0) {{
                html += `
                    <div class="competition-projects">
                        <h4>🏢 Competing LIHTC Projects</h4>
                `;
                
                site.competing_projects.forEach(project => {{
                    const riskClass = project.fatal_9pct ? 'fatal' : (project.risk_level.includes('MEDIUM') ? 'medium-risk' : '');
                    const riskBadge = project.fatal_9pct ? 'risk-high' : (project.risk_level.includes('MEDIUM') ? 'risk-medium' : 'risk-low');
                    
                    html += `
                        <div class="project-item ${{riskClass}}">
                            <strong>${{project.name}}</strong>
                            <span class="risk-badge ${{riskBadge}}">${{project.risk_level}}</span>
                            <div class="project-details">
                                <div class="detail-item">
                                    <span class="detail-label">Distance:</span> ${{project.distance_miles}} miles
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Year:</span> ${{project.year}} (${{project.years_ago}} years ago)
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Units:</span> ${{project.units}}
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Program:</span> ${{project.program_type}}
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Address:</span> ${{project.address}}, ${{project.city}}
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">County:</span> ${{project.county}}
                                </div>
                            </div>
                        </div>
                    `;
                }});
                
                html += `</div>`;
            }} else {{
                html += `
                    <div class="competition-projects">
                        <h4>✅ No Competing Projects Found</h4>
                        <p>Clean site with no LIHTC competition within 2 miles - excellent for both 4% and 9% deals!</p>
                    </div>
                `;
            }}
            
            html += `</div>`;
            return html;
        }}
        
        function generateAllSitesCompetitionHTML() {{
            let html = '<h3>🏢 Competition Summary - All Sites</h3>';
            
            SITES_DATA.forEach((site, index) => {{
                const fatalCount = site.competing_projects.filter(p => p.fatal_9pct).length;
                const riskLevel = fatalCount > 0 ? 'HIGH RISK' : (site.competition_count_1mi > 0 ? 'MEDIUM RISK' : 'LOW RISK');
                const riskClass = fatalCount > 0 ? 'risk-high' : (site.competition_count_1mi > 0 ? 'risk-medium' : 'risk-low');
                
                html += `
                    <div class="competition-widget" style="margin: 20px 0;">
                        <h4>${{site.name.split(',')[0]}}</h4>
                        <div class="competition-summary">
                            <div class="competition-stat">
                                <h4>${{site.competition_count_1mi}}</h4>
                                <p>1 Mile</p>
                            </div>
                            <div class="competition-stat">
                                <h4>${{site.competition_count_2mi}}</h4>
                                <p>2 Miles</p>
                            </div>
                            <div class="competition-stat">
                                <h4>${{fatalCount}}</h4>
                                <p>Fatal Flaws</p>
                            </div>
                            <div class="competition-stat">
                                <span class="risk-badge ${{riskClass}}">${{riskLevel}}</span>
                            </div>
                        </div>
                    </div>
                `;
            }});
            
            return html;
        }}
        
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Enhanced Site Visit Guide Loaded');
            console.log(`Competition data for ${{SITES_DATA.length}} sites loaded`);
        }});
    </script>
</body>
</html>
"""

def main():
    print("🚀 Creating Enhanced Site Visit Guide with TDHCA Competition Data...")
    
    guide = EnhancedSiteVisitGuide()
    output_file, sites_data = guide.create_enhanced_html_guide()
    
    print(f"\n📊 Competition Analysis Summary:")
    for site in sites_data:
        fatal_count = site['fatal_9pct_count']
        print(f"   {site['name'].split(',')[0]}: {site['competition_count_1mi']} within 1mi, {fatal_count} fatal flaws")
    
    print(f"\n✅ Enhanced guide ready for D'Marco's site visit!")
    print(f"   File: {output_file}")
    print(f"   Features: Interactive competition data, site navigation, real TDHCA project details")

if __name__ == "__main__":
    main()