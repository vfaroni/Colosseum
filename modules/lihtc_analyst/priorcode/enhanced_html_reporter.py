#!/usr/bin/env python3
"""
ENHANCED TDHCA HTML Report Generator
Creates rich visual HTML reports with all property analytics
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import urllib.parse


class EnhancedTDHCAReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load additional data files for enrichment
        base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        self.hud_ami_file = base_path / "HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.tdhca_file = base_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
    def generate_html_report(self, df: pd.DataFrame, output_dir: str = ".") -> str:
        """Generate comprehensive HTML report from analysis results"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Calculate statistics
        stats = self._calculate_statistics(df)
        
        # Generate HTML content with enhanced styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced TDHCA Analysis Report - Texas LIHTC</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6; 
            color: #333; 
            background: #f8f9fa; 
            padding: 20px;
        }}
        
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            box-shadow: 0 0 20px rgba(0,0,0,0.1); 
            border-radius: 10px; 
            overflow: hidden; 
        }}
        
        /* Header Styles */
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 40px; 
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
        
        /* Stats Section */
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
        
        /* Categories Grid */
        .categories-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 15px; 
            margin-bottom: 30px; 
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
        
        /* Deal Type Sections */
        .deal-section {{
            padding: 30px;
        }}
        
        .deal-header {{
            background: #667eea;
            color: white;
            padding: 20px 30px;
            border-radius: 10px 10px 0 0;
            margin: 0 -30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .deal-header h2 {{
            font-size: 1.8em;
            font-weight: 600;
        }}
        
        .deal-stats {{
            display: flex;
            gap: 30px;
        }}
        
        .deal-stat {{
            text-align: center;
        }}
        
        .deal-stat-number {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .deal-stat-label {{
            font-size: 0.8em;
            opacity: 0.8;
        }}
        
        /* Property Cards - Enhanced */
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
        
        .property-header.viable, .property-header.competitive {{ 
            border-left-color: #28a745; 
            background: #f8fff9; 
        }}
        .property-header.marginal, .property-header.possible {{ 
            border-left-color: #ffc107; 
            background: #fffcf0; 
        }}
        .property-header.weak {{ 
            border-left-color: #dc3545; 
            background: #fff5f5; 
        }}
        .property-header.fatal-flaw {{ 
            border-left-color: #dc3545; 
            background: #fff5f5; 
        }}
        .property-header.error {{ 
            border-left-color: #6c757d; 
            background: #f8f9fa; 
        }}
        
        .property-title {{ 
            font-size: 1.3em; 
            font-weight: 600; 
            color: #495057; 
        }}
        
        .property-category {{ 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            font-weight: 600; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }}
        
        .category-viable, .category-competitive {{ 
            background: #d4edda; 
            color: #155724; 
        }}
        .category-marginal, .category-possible {{ 
            background: #fff3cd; 
            color: #856404; 
        }}
        .category-weak {{ 
            background: #f8d7da; 
            color: #721c24; 
        }}
        .category-fatal-flaw {{ 
            background: #721c24; 
            color: white; 
        }}
        
        /* Property Details */
        .property-details {{ 
            padding: 20px; 
            background: #fafafa; 
            border-top: 1px solid #dee2e6; 
        }}
        
        .details-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
            gap: 15px; 
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
            font-size: 0.95em; 
            border-bottom: 2px solid #667eea; 
            padding-bottom: 5px; 
        }}
        
        .detail-item {{ 
            margin-bottom: 8px; 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-start; 
            font-size: 0.85em;
        }}
        
        .detail-label {{ 
            font-weight: 500; 
            color: #6c757d; 
            flex-shrink: 0; 
            min-width: 100px; 
        }}
        
        .detail-value {{ 
            color: #495057; 
            font-weight: 600; 
            text-align: right; 
            flex: 1; 
        }}
        
        /* Poverty Indicators */
        .poverty-indicator {{ 
            padding: 2px 6px; 
            border-radius: 12px; 
            font-size: 0.7em; 
            font-weight: 600; 
            margin-left: 5px; 
        }}
        .poverty-low {{ background: #d4edda; color: #155724; }}
        .poverty-borderline {{ background: #fff3cd; color: #856404; }}
        .poverty-high {{ background: #f8d7da; color: #721c24; }}
        
        /* Rent Grid */
        .rent-grid {{ 
            display: grid; 
            grid-template-columns: 1fr; 
            gap: 6px; 
            margin-top: 8px; 
        }}
        
        .rent-item {{ 
            background: #f8f9fa; 
            padding: 6px; 
            border-radius: 4px; 
            font-size: 0.8em; 
        }}
        
        .rent-label {{ 
            font-weight: 500; 
            color: #6c757d; 
            font-size: 0.75em; 
        }}
        
        .rent-values {{ 
            font-weight: 600; 
            color: #495057; 
            font-size: 0.8em; 
        }}
        
        /* Benefits List */
        .benefits-list {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 6px; 
            margin-top: 8px; 
        }}
        
        .benefit-tag {{ 
            background: #28a745; 
            color: white; 
            padding: 3px 8px; 
            border-radius: 12px; 
            font-size: 0.7em; 
            font-weight: 500; 
        }}
        
        /* Enhanced 2x2 Navigation Grid */
        .links-section {{ 
            margin-top: 10px; 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 8px; 
            max-width: 280px; 
        }}

        .link-btn {{ 
            display: inline-flex; 
            align-items: center; 
            justify-content: center;
            padding: 8px 12px; 
            text-decoration: none; 
            border-radius: 6px; 
            font-size: 0.75em; 
            font-weight: 500; 
            transition: all 0.3s; 
            border: none; 
            cursor: pointer; 
            white-space: nowrap;
            text-align: center;
        }}
        
        .google-maps-link {{ background: #4285f4; color: white; }}
        .google-maps-link:hover {{ background: #3367d6; }}
        .apple-maps-link {{ background: #000000; color: white; }}
        .apple-maps-link:hover {{ background: #333333; }}
        .census-data-link {{ background: #28a745; color: white; }}
        .census-data-link:hover {{ background: #218838; }}
        .hud-poverty-link {{ background: #dc3545; color: white; }}
        .hud-poverty-link:hover {{ background: #c82333; }}
        
        /* Footer */
        .footer {{ 
            background: #495057; 
            color: white; 
            text-align: center; 
            padding: 20px; 
            font-size: 0.9em; 
        }}
        
        .company-name {{ 
            color: #ffffff; 
            font-weight: 600; 
            margin-top: 5px; 
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .property-header {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
            .stats-grid, .categories-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
            .details-grid {{ grid-template-columns: 1fr; }}
            .links-section {{ grid-template-columns: 1fr; max-width: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced TDHCA Analysis Report</h1>
            <div class="subtitle">Texas LIHTC Site Analysis with Rich Data - Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</div>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['total_properties']}</div>
                    <div class="stat-label">Total Properties</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['4p_viable']}</div>
                    <div class="stat-label">4% Viable Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['9p_competitive']}</div>
                    <div class="stat-label">9% Competitive Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['qct_dda_sites']}</div>
                    <div class="stat-label">QCT/DDA Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['one_mile_compliant']}</div>
                    <div class="stat-label">1-Mile Compliant</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['low_poverty']}</div>
                    <div class="stat-label">Low Poverty Areas</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 15px; color: #495057;">Project Categories</h3>
            <div class="categories-grid">
                <div class="category-card best">
                    <div style="font-size: 1.8em; font-weight: bold; color: #28a745;">🥇 {stats['total_best']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">BEST Projects</div>
                </div>
                <div class="category-card good">
                    <div style="font-size: 1.8em; font-weight: bold; color: #007bff;">🥈 {stats['total_good']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">GOOD Projects</div>
                </div>
                <div class="category-card maybe">
                    <div style="font-size: 1.8em; font-weight: bold; color: #ffc107;">🥉 {stats['total_maybe']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">MAYBE Projects</div>
                </div>
                <div class="category-card firm-no">
                    <div style="font-size: 1.8em; font-weight: bold; color: #dc3545;">❌ {stats['total_no']}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">FIRM NO</div>
                </div>
            </div>
        </div>
"""

        # Add 4% Deal Section
        html_content += self._generate_deal_section(df, '4pct', stats)
        
        # Add 9% Deal Section  
        html_content += self._generate_deal_section(df, '9pct', stats)
        
        # Add footer
        html_content += """
        <div class="footer">
            <p>Enhanced TDHCA Analysis Report - Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Based on 2025 Qualified Allocation Plan (QAP)</p>
            <div class="company-name">Structured Consultants LLC</div>
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        output_file = output_dir / f"Enhanced_TDHCA_Report_{self.timestamp}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Enhanced HTML report saved to: {output_file}")
        return str(output_file)
    
    def _calculate_statistics(self, df: pd.DataFrame) -> dict:
        """Calculate summary statistics from analysis results"""
        
        # Count viable/competitive projects for both deal types
        viable_4p = df[df['4pct_Category'] == 'VIABLE']
        competitive_9p = df[df['9pct_Category'] == 'COMPETITIVE']
        
        # Combined best projects
        best_combined = df[(df['4pct_Category'] == 'VIABLE') | (df['9pct_Category'] == 'COMPETITIVE')]
        
        stats = {
            'total_properties': len(df),
            '4p_viable': len(df[df['4pct_Category'] == 'VIABLE']),
            '4p_marginal': len(df[df['4pct_Category'] == 'MARGINAL']),
            '4p_fatal_flaw': len(df[df['4pct_Category'] == 'FATAL FLAW']),
            '9p_competitive': len(df[df['9pct_Category'] == 'COMPETITIVE']),
            '9p_possible': len(df[df['9pct_Category'] == 'POSSIBLE']),
            '9p_weak': len(df[df['9pct_Category'] == 'WEAK']),
            '9p_fatal_flaw': len(df[df['9pct_Category'] == 'FATAL FLAW']),
            'qct_dda_sites': len(df[(df['QCT_Status'] == True) | (df['DDA_Status'] == True)]),
            'one_mile_compliant': len(df[df['4pct_One_Mile_Compliant'] == True]),
            'low_poverty': len(df[df['Poverty_Rate'] < 20]) if 'Poverty_Rate' in df.columns else 0,
            # Combined categories (take best of either deal type)
            'total_best': len(best_combined),
            'total_good': len(df[(df['4pct_Category'].isin(['VIABLE', 'MARGINAL'])) | 
                               (df['9pct_Category'].isin(['COMPETITIVE', 'POSSIBLE']))]),
            'total_maybe': len(df[(df['4pct_Category'] == 'MARGINAL') | (df['9pct_Category'] == 'POSSIBLE')]),
            'total_no': len(df[(df['4pct_Category'] == 'FATAL FLAW') | (df['9pct_Category'] == 'FATAL FLAW')])
        }
        
        return stats
    
    def _generate_deal_section(self, df: pd.DataFrame, deal_type: str, stats: dict) -> str:
        """Generate HTML section for a specific deal type"""
        
        if deal_type == '4pct':
            title = "4% Tax-Exempt Bond Properties"
            categories = ['VIABLE', 'MARGINAL']
            stat_keys = ['4p_viable', '4p_marginal', '4p_fatal_flaw']
        else:
            title = "9% Competitive HTC Properties"
            categories = ['COMPETITIVE', 'POSSIBLE']
            stat_keys = ['9p_competitive', '9p_possible', '9p_fatal_flaw']
        
        html = f"""
        <div class="deal-section">
            <div class="deal-header">
                <h2>{title}</h2>
                <div class="deal-stats">
                    <div class="deal-stat">
                        <div class="deal-stat-number">{stats[stat_keys[0]]}</div>
                        <div class="deal-stat-label">{categories[0]}</div>
                    </div>
                    <div class="deal-stat">
                        <div class="deal-stat-number">{stats[stat_keys[1]]}</div>
                        <div class="deal-stat-label">{categories[1]}</div>
                    </div>
                    <div class="deal-stat">
                        <div class="deal-stat-number">{stats[stat_keys[2]]}</div>
                        <div class="deal-stat-label">FATAL FLAW</div>
                    </div>
                </div>
            </div>
"""
        
        # Get top properties for this deal type
        category_col = f'{deal_type}_Category'
        top_properties = df[df[category_col].isin(categories)].head(10)
        
        if len(top_properties) == 0:
            html += '<p style="text-align: center; color: #666; padding: 40px;">No viable properties found for this deal type.</p>'
        else:
            for idx, prop in top_properties.iterrows():
                html += self._generate_enhanced_property_card(prop, deal_type)
        
        html += """
        </div>
"""
        
        return html
    
    def _generate_enhanced_property_card(self, prop: pd.Series, deal_type: str) -> str:
        """Generate ENHANCED property card with all sections from old analyzer"""
        
        category = prop[f'{deal_type}_Category']
        category_class = category.lower().replace(' ', '-')
        
        # Get key data
        address = prop.get('Address', 'Unknown Address')
        census_tract = prop.get('Census_Tract', 'N/A')
        county = prop.get('County', 'Unknown')
        poverty_rate = prop.get('Poverty_Rate', 100)
        median_income = prop.get('Median_Income', 0)
        total_pop = prop.get('Total_Population', 0)
        
        # Poverty indicator
        if poverty_rate < 20.0:
            poverty_class = "poverty-low"
            poverty_text = "✅ LOW"
        elif 19.0 <= poverty_rate <= 21.0:
            poverty_class = "poverty-borderline" 
            poverty_text = "⚠️ BORDERLINE"
        else:
            poverty_class = "poverty-high"
            poverty_text = "❌ HIGH"
        
        html = f"""
        <div class="property">
            <div class="property-header {category_class}">
                <div class="property-title">{address}</div>
                <div class="property-category category-{category_class}">{category}</div>
            </div>
            <div class="property-details">
                <div class="details-grid">
"""
        
        # Deal-specific scoring section
        if deal_type == '4pct':
            html += f"""
                    <div class="detail-section">
                        <h4>🏠 4% Bond Deal Scoring</h4>
                        <div class="detail-item">
                            <span class="detail-label">Category:</span>
                            <span class="detail-value">{category}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">1-Mile Rule:</span>
                            <span class="detail-value">{'✅ Compliant' if prop.get('4pct_One_Mile_Compliant') else '❌ Fail'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Competitors:</span>
                            <span class="detail-value">{int(prop.get('One_Mile_Competitors', 0))}</span>
                        </div>
"""
        else:  # 9% deal
            html += f"""
                    <div class="detail-section">
                        <h4>🏛️ 9% LIHTC Scoring</h4>
                        <div class="detail-item">
                            <span class="detail-label">Category:</span>
                            <span class="detail-value">{category}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Points Est:</span>
                            <span class="detail-value">{int(prop.get('9pct_Points_Est', 0))}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Same Tract:</span>
                            <span class="detail-value">{int(prop.get('TDHCA_Same_Tract_Score', 0))}/5</span>
                        </div>
"""
        
        # Add federal benefits if present
        if prop.get('QCT_Status') or prop.get('DDA_Status'):
            benefits = []
            if prop.get('QCT_Status'):
                benefits.append("QCT")
            if prop.get('DDA_Status'):
                benefits.append("DDA")
            html += f"""
                        <div class="benefits-list">
                            <span class="benefit-tag">30% Boost: {'/'.join(benefits)}</span>
                        </div>
"""
        
        html += """
                    </div>
"""
        
        # Market Analysis Section
        html += f"""
                    <div class="detail-section">
                        <h4>🎯 Market Analysis</h4>
                        <div class="detail-item">
                            <span class="detail-label">Saturation:</span>
                            <span class="detail-value">{prop.get('Market_Saturation', 'N/A')}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">1-Mile Comp:</span>
                            <span class="detail-value">{int(prop.get('One_Mile_Competitors', 0))} projects</span>
                        </div>
"""
        
        # Add nearest competitor if exists
        if pd.notna(prop.get('Nearest_Competitor_Name')):
            html += f"""
                        <div class="detail-item">
                            <span class="detail-label">Nearest:</span>
                            <span class="detail-value" style="font-size: 0.75em;">{prop.get('Nearest_Competitor_Name', 'Unknown')[:30]}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Distance:</span>
                            <span class="detail-value">{prop.get('Nearest_Competitor_Distance', 0):.2f} mi ({prop.get('Nearest_Competitor_Year', 'N/A')})</span>
                        </div>
"""
        
        html += """
                    </div>
"""
        
        # Demographics Section
        html += f"""
                    <div class="detail-section">
                        <h4>📊 Demographics</h4>
                        <div class="detail-item">
                            <span class="detail-label">Poverty Rate:</span>
                            <span class="detail-value">
                                {poverty_rate:.1f}%
                                <span class="poverty-indicator {poverty_class}">{poverty_text}</span>
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Med. Income:</span>
                            <span class="detail-value">${median_income:,}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Population:</span>
                            <span class="detail-value">{total_pop:,}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Census Tract:</span>
                            <span class="detail-value">{census_tract}</span>
                        </div>
                    </div>
"""
        
        # HUD Area Data Section (if available)
        if pd.notna(prop.get('HUD_Area_Name')):
            html += f"""
                    <div class="detail-section">
                        <h4>🏠 HUD Area Data</h4>
                        <div class="detail-item">
                            <span class="detail-label">Area:</span>
                            <span class="detail-value" style="font-size: 0.75em;">{prop.get('HUD_Area_Name', 'N/A')[:40]}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{prop.get('Metro_Status', 'N/A')}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Median AMI:</span>
                            <span class="detail-value">${int(prop.get('Median_AMI', 0)):,}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">4P 50% Inc:</span>
                            <span class="detail-value">${int(prop.get('4P_50pct_Income', 0)):,}</span>
                        </div>
                        
                        <div class="rent-grid">
                            <div class="rent-item">
                                <div class="rent-label">1BR Rent Limits</div>
                                <div class="rent-values">${int(prop.get('Rent_1BR_60pct', 0)):,} @ 60% / ${int(prop.get('Rent_1BR_80pct', 0)):,} @ 80%</div>
                            </div>
                            <div class="rent-item">
                                <div class="rent-label">2BR Rent Limits</div>
                                <div class="rent-values">${int(prop.get('Rent_2BR_60pct', 0)):,} @ 60% / ${int(prop.get('Rent_2BR_80pct', 0)):,} @ 80%</div>
                            </div>
                            <div class="rent-item">
                                <div class="rent-label">3BR Rent Limits</div>
                                <div class="rent-values">${int(prop.get('Rent_3BR_60pct', 0)):,} @ 60% / ${int(prop.get('Rent_3BR_80pct', 0)):,} @ 80%</div>
                            </div>
                        </div>
                    </div>
"""
        
        # Enhanced Location & Navigation Section with 2x2 Grid
        if pd.notna(prop.get('Latitude')) and pd.notna(prop.get('Longitude')):
            lat = prop.get('Latitude')
            lon = prop.get('Longitude')
            
            # Encode address for URLs
            encoded_address = urllib.parse.quote_plus(address)
            
            # Generate map URLs
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
            apple_maps_url = f"https://maps.apple.com/?q={encoded_address}"
            
            # Census reporter URL
            census_data_url = None
            if census_tract and len(str(census_tract)) >= 11:
                census_data_url = f"https://censusreporter.org/profiles/14000US{census_tract}/"
            
            # HUD poverty map
            hud_poverty_url = "https://www.huduser.gov/portal/maps/hcv/home.html"
            
            html += f"""
                    <div class="detail-section">
                        <h4>📍 Location & Navigation</h4>
                        <div class="detail-item">
                            <span class="detail-label">Coordinates:</span>
                            <span class="detail-value">{lat:.4f}, {lon:.4f}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">County:</span>
                            <span class="detail-value">{county}</span>
                        </div>
                        
                        <div class="links-section">
                            <a href="{google_maps_url}" target="_blank" class="link-btn google-maps-link">🗺️ Google Maps</a>
                            <a href="{apple_maps_url}" target="_blank" class="link-btn apple-maps-link">🍎 Apple Maps</a>
"""
            
            if census_data_url:
                html += f"""                            <a href="{census_data_url}" target="_blank" class="link-btn census-data-link">📊 Census Data</a>
"""
            
            html += f"""                            <a href="{hud_poverty_url}" target="_blank" class="link-btn hud-poverty-link">🏘️ HUD Poverty</a>
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
        </div>
"""
        
        return html


# Integration function to work with the analyzer
def generate_enhanced_report_from_analysis(excel_file: str, output_dir: str = None):
    """Generate enhanced HTML report from Excel analysis results"""
    
    # Use code directory if no output_dir specified
    if output_dir is None:
        output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
    
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name='All_Properties')
    
    # Create report generator
    generator = EnhancedTDHCAReportGenerator()
    
    # Generate HTML report
    html_file = generator.generate_html_report(df, output_dir)
    
    return html_file


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        print(f"Generating enhanced HTML report from: {excel_file}")
        html_file = generate_enhanced_report_from_analysis(excel_file)
        print(f"✅ Enhanced HTML report generated: {html_file}")
    else:
        print("Usage: python enhanced_tdhca_html_reporter.py <excel_file>")
        print("Example: python enhanced_tdhca_html_reporter.py Enhanced_CoStar_TX_Land_TDHCA_Analysis_20240602_123456.xlsx")