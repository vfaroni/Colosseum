# First, add this import at the top of your file if it's not already there:
import urllib.parse

# Then, replace your existing create_html_report method with this updated version:

def create_html_report(self, results: List[Dict]) -> str:
    """Create professional HTML report with enhanced styling and all requested improvements"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Calculate summary statistics
    total = len(results)
    successful = len([r for r in results if "error" not in r])
    
    categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
    federal_benefits = {"qct": 0, "dda": 0, "both": 0}
    
    for result in results:
        if "error" not in result:
            category = result.get("texas_scoring", {}).get("category", "UNKNOWN")
            if category in categories:
                categories[category] += 1
            
            qct_dda = result.get("qct_dda_status", {})
            if qct_dda.get("qct_status") and qct_dda.get("dda_status"):
                federal_benefits["both"] += 1
            elif qct_dda.get("qct_status"):
                federal_benefits["qct"] += 1
            elif qct_dda.get("dda_status"):
                federal_benefits["dda"] += 1
    
    # Create HTML content with enhanced styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Texas LIHTC Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .summary h2 {{
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }}
        
        .category-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }}
        
        .category-card.best {{ border-left-color: #28a745; }}
        .category-card.good {{ border-left-color: #007bff; }}
        .category-card.maybe {{ border-left-color: #ffc107; }}
        .category-card.firm-no {{ border-left-color: #dc3545; }}
        
        .results {{
            padding: 30px;
        }}
        
        .results h2 {{
            color: #495057;
            margin-bottom: 25px;
            font-size: 1.8em;
        }}
        
        .property {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .property-header {{
            padding: 20px;
            border-left: 5px solid;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .property-header.best {{ border-left-color: #28a745; background: #f8fff9; }}
        .property-header.good {{ border-left-color: #007bff; background: #f8f9ff; }}
        .property-header.maybe {{ border-left-color: #ffc107; background: #fffcf0; }}
        .property-header.firm-no {{ border-left-color: #dc3545; background: #fff5f5; }}
        .property-header.error {{ border-left-color: #6c757d; background: #f8f9fa; }}
        
        .property-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #495057;
        }}
        
        .property-number {{
            font-size: 0.9em;
            color: #6c757d;
            font-weight: 400;
        }}
        
        .property-category {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .category-best {{ background: #d4edda; color: #155724; }}
        .category-good {{ background: #cce7ff; color: #004085; }}
        .category-maybe {{ background: #fff3cd; color: #856404; }}
        .category-firm-no {{ background: #f8d7da; color: #721c24; }}
        .category-error {{ background: #e2e3e5; color: #383d41; }}
        
        .property-details {{
            padding: 20px;
            background: #fafafa;
            border-top: 1px solid #dee2e6;
        }}
        
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}
        
        .detail-section {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        
        .detail-section h4 {{
            color: #495057;
            margin-bottom: 10px;
            font-size: 1.1em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }}
        
        .detail-item {{
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        
        .detail-label {{
            font-weight: 500;
            color: #6c757d;
            flex-shrink: 0;
            min-width: 110px;
        }}
        
        .detail-value {{
            color: #495057;
            font-weight: 600;
            text-align: right;
            flex: 1;
        }}
        
        .rent-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
        }}
        
        .rent-item {{
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .rent-label {{
            font-weight: 500;
            color: #6c757d;
            font-size: 0.8em;
        }}
        
        .rent-values {{
            font-weight: 600;
            color: #495057;
        }}
        
        .benefits-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .benefit-tag {{
            background: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .links-section {{
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .link-btn {{
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }}
        
        .google-maps-link {{
            background: #4285f4;
            color: white;
        }}
        
        .google-maps-link:hover {{
            background: #3367d6;
        }}
        
        .apple-maps-link {{
            background: #000000;
            color: white;
        }}
        
        .apple-maps-link:hover {{
            background: #333333;
        }}
        
        .census-data-link {{
            background: #28a745;
            color: white;
        }}
        
        .census-data-link:hover {{
            background: #218838;
        }}
        
        .error-message {{
            color: #dc3545;
            font-style: italic;
            padding: 10px;
            background: #f8d7da;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        .footer {{
            background: #495057;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .property-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
            
            .stats-grid,
            .categories-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
            
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            
            .links-section {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced Texas LIHTC Analysis Report</h1>
            <div class="subtitle">Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</div>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total Properties</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{successful}</div>
                    <div class="stat-label">Successfully Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{federal_benefits['qct'] + federal_benefits['both']}</div>
                    <div class="stat-label">QCT Qualified</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{federal_benefits['dda'] + federal_benefits['both']}</div>
                    <div class="stat-label">DDA Qualified</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 15px; color: #495057;">LIHTC Project Categories</h3>
            <div class="categories-grid">
                <div class="category-card best">
                    <div style="font-size: 1.8em; font-weight: bold; color: #28a745;">🥇 {categories['BEST']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">BEST Projects</div>
                </div>
                <div class="category-card good">
                    <div style="font-size: 1.8em; font-weight: bold; color: #007bff;">🥈 {categories['GOOD']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">GOOD Projects</div>
                </div>
                <div class="category-card maybe">
                    <div style="font-size: 1.8em; font-weight: bold; color: #ffc107;">🥉 {categories['MAYBE']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">MAYBE Projects</div>
                </div>
                <div class="category-card firm-no">
                    <div style="font-size: 1.8em; font-weight: bold; color: #dc3545;">❌ {categories['FIRM NO']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">FIRM NO</div>
                </div>
            </div>
        </div>
        
        <div class="results">
            <h2>Detailed Property Analysis</h2>
"""
    
    # Add detailed results with all requested enhancements
    for i, result in enumerate(results, 1):
        if "error" in result:
            html_content += f"""
        <div class="property">
            <div class="property-header error">
                <div class="property-title">❌ {result['address']} <span class="property-number">({i} of {total})</span></div>
                <div class="property-category category-error">FAILED</div>
            </div>
            <div class="property-details">
                <div class="error-message">Error: {result['error']}</div>
            </div>
        </div>
"""
            continue
        
        scoring = result.get("texas_scoring", {})
        demo = result.get("demographics", {})
        ami = result.get("ami_data", {})
        qct_dda = result.get("qct_dda_status", {})
        coords = result.get("coordinates", {})
        
        category = scoring.get("category", "UNKNOWN").lower().replace(" ", "-")
        category_display = scoring.get("category", "UNKNOWN")
        
        # Category emoji and styling
        category_info = {
            "best": {"emoji": "🥇", "class": "best"},
            "good": {"emoji": "🥈", "class": "good"},
            "maybe": {"emoji": "🥉", "class": "maybe"},
            "firm-no": {"emoji": "❌", "class": "firm-no"}
        }
        
        cat_info = category_info.get(category, {"emoji": "❓", "class": "error"})
        
        html_content += f"""
        <div class="property">
            <div class="property-header {cat_info['class']}">
                <div class="property-title">{cat_info['emoji']} {result['address']} <span class="property-number">({i} of {total})</span></div>
                <div class="property-category category-{cat_info['class']}">{category_display}</div>
            </div>
            <div class="property-details">
                <div class="details-grid">
"""
        
        # Scoring Details
        html_content += f"""
                    <div class="detail-section">
                        <h4>📊 LIHTC Scoring</h4>
                        <div class="detail-item">
                            <span class="detail-label">Category:</span>
                            <span class="detail-value">{category_display}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Opportunity Points:</span>
                            <span class="detail-value">{scoring.get('total_analyzed_points', 0)}</span>
                        </div>
"""
        
        if scoring.get("federal_benefits"):
            html_content += f"""
                        <div class="detail-item">
                            <span class="detail-label">Federal Benefits:</span>
                        </div>
                        <div class="benefits-list">
"""
            for benefit in scoring["federal_benefits"]:
                html_content += f'<span class="benefit-tag">{benefit}</span>'
            
            html_content += """
                        </div>
"""
        
        html_content += """
                    </div>
"""
        
        # Enhanced Demographics Section
        if demo and "error" not in demo:
            # Get 4-Person 50% AMI from AMI data
            four_person_ami = ""
            if ami and ami.get('income_limits', {}).get('50_pct', {}).get('4p'):
                four_person_ami = f"${ami['income_limits']['50_pct']['4p']:,}"
            else:
                four_person_ami = "N/A"
            
            html_content += f"""
                    <div class="detail-section">
                        <h4>🏘️ Demographics</h4>
                        <div class="detail-item">
                            <span class="detail-label">Poverty Rate:</span>
                            <span class="detail-value">{demo.get('poverty_rate', 'N/A')}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Median Income:</span>
                            <span class="detail-value">${demo.get('median_household_income', 0):,}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Pop. (Census Tract):</span>
                            <span class="detail-value">{demo.get('total_population', 'N/A'):,}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">4-Person 50% AMI:</span>
                            <span class="detail-value">{four_person_ami}</span>
                        </div>
                    </div>
"""
        
        # Enhanced HUD Area Data Section
        if ami:
            html_content += f"""
                    <div class="detail-section">
                        <h4>🏠 HUD Area Data</h4>
                        <div class="detail-item">
                            <span class="detail-label">Area:</span>
                            <span class="detail-value">{ami['hud_area_name']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{'Metro' if ami['metro'] else 'Non-Metro'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Median AMI:</span>
                            <span class="detail-value">${ami['median_ami']:,}</span>
                        </div>
                        
                        <div class="rent-grid">
                            <div class="rent-item">
                                <div class="rent-label">1BR Rent Limits</div>
                                <div class="rent-values">${ami['rent_limits']['60_pct']['1br']} 60% / ${ami['rent_limits']['80_pct']['1br']} 80%</div>
                            </div>
                            <div class="rent-item">
                                <div class="rent-label">2BR Rent Limits</div>
                                <div class="rent-values">${ami['rent_limits']['60_pct']['2br']} 60% / ${ami['rent_limits']['80_pct']['2br']} 80%</div>
                            </div>
                            <div class="rent-item">
                                <div class="rent-label">3BR Rent Limits</div>
                                <div class="rent-values">${ami['rent_limits']['60_pct']['3br']} 60% / ${ami['rent_limits']['80_pct']['3br']} 80%</div>
                            </div>
                        </div>
                    </div>
"""
        
        # Enhanced Location Section with all three links
        if coords:
            encoded_address = urllib.parse.quote_plus(result['address'])
            
            # Google Maps URL
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
            
            # Apple Maps URL
            apple_maps_url = f"https://maps.apple.com/?q={encoded_address}"
            
            # Census Data URL - direct link to data.census.gov tract profile
            census_tract = result.get('census_tract', '')
            if census_tract and len(census_tract) >= 11:
                census_data_url = f"https://data.census.gov/profile?g=1400000US{census_tract}"
            else:
                census_data_url = "https://data.census.gov"
            
            html_content += f"""
                    <div class="detail-section">
                        <h4>📍 Location</h4>
                        <div class="detail-item">
                            <span class="detail-label">Coordinates:</span>
                            <span class="detail-value">{coords['latitude']:.6f}, {coords['longitude']:.6f}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Census Tract:</span>
                            <span class="detail-value">{result.get('census_tract', 'N/A')}</span>
                        </div>
                        
                        <div class="links-section">
                            <a href="{google_maps_url}" target="_blank" class="link-btn google-maps-link">🗺️ Google Maps</a>
                            <a href="{apple_maps_url}" target="_blank" class="link-btn apple-maps-link">🍎 Apple Maps</a>
                            <a href="{census_data_url}" target="_blank" class="link-btn census-data-link">📊 Census Data</a>
                        </div>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
        </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            Enhanced Texas LIHTC Analysis Report | Generated by Enhanced Texas Analyzer | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>"""
    
    # Save HTML report
    html_file = self.work_dir / f"enhanced_texas_analysis_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n🌐 Enhanced HTML report saved: {html_file}")
    return str(html_file)