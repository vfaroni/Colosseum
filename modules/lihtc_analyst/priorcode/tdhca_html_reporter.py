#!/usr/bin/env python3
"""
TDHCA HTML Report Generator
Creates visual HTML reports for TDHCA-compliant analysis results
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json


class TDHCAReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_html_report(self, df: pd.DataFrame, output_dir: str = ".") -> str:
        """Generate comprehensive HTML report from analysis results"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Calculate statistics
        stats = self._calculate_statistics(df)
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TDHCA Accurate Analysis Report - Texas LIHTC</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Header Styles */
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
        
        /* Stats Grid */
        .stats-section {{
            margin-bottom: 40px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Deal Type Sections */
        .deal-section {{
            margin-bottom: 50px;
        }}
        
        .deal-header {{
            background: #2a5298;
            color: white;
            padding: 20px 30px;
            border-radius: 10px 10px 0 0;
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
        
        /* Property Cards */
        .properties-container {{
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .property-card {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
            transition: all 0.2s;
        }}
        
        .property-card:hover {{
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .property-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        
        .property-address {{
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .category-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
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
        
        /* Property Details Grid */
        .property-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .detail-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .detail-label {{
            font-weight: 500;
            color: #666;
            font-size: 0.9em;
        }}
        
        .detail-value {{
            font-weight: 600;
            color: #333;
        }}
        
        /* Status Indicators */
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }}
        
        .status-pass {{
            background: #28a745;
        }}
        
        .status-fail {{
            background: #dc3545;
        }}
        
        .status-neutral {{
            background: #6c757d;
        }}
        
        /* Compliance Section */
        .compliance-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
        }}
        
        .compliance-header {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 10px;
            font-size: 0.95em;
        }}
        
        .compliance-list {{
            list-style: none;
        }}
        
        .compliance-item {{
            padding: 5px 0;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .compliance-pass {{
            color: #155724;
        }}
        
        .compliance-fail {{
            color: #721c24;
        }}
        
        .compliance-action {{
            color: #004085;
        }}
        
        /* Key Rules Reference */
        .rules-reference {{
            background: #e9ecef;
            padding: 30px;
            border-radius: 10px;
            margin-top: 40px;
        }}
        
        .rules-reference h3 {{
            color: #495057;
            margin-bottom: 20px;
        }}
        
        .rules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .rule-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2a5298;
        }}
        
        .rule-title {{
            font-weight: 600;
            color: #2a5298;
            margin-bottom: 8px;
        }}
        
        .rule-description {{
            font-size: 0.9em;
            color: #666;
            line-height: 1.5;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
            margin-top: 50px;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .deal-header {{
                flex-direction: column;
                gap: 20px;
            }}
            
            .property-details {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TDHCA Accurate Analysis Report</h1>
            <div class="subtitle">Texas LIHTC Site Analysis - {datetime.now().strftime("%B %d, %Y")}</div>
        </div>
        
        <div class="stats-section">
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
                    <div class="stat-label">QCT/DDA Sites (30% Boost)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['one_mile_compliant']}</div>
                    <div class="stat-label">1-Mile Rule Compliant</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['low_poverty']}</div>
                    <div class="stat-label">Low Poverty Areas</div>
                </div>
            </div>
        </div>
"""
        
        # Add 4% Deal Section
        html_content += self._generate_deal_section(df, '4pct', stats)
        
        # Add 9% Deal Section  
        html_content += self._generate_deal_section(df, '9pct', stats)
        
        # Add Rules Reference
        html_content += """
        <div class="rules-reference">
            <h3>Key TDHCA Distance Requirements (2025 QAP)</h3>
            <div class="rules-grid">
                <div class="rule-card">
                    <div class="rule-title">One Mile Three Year Rule</div>
                    <div class="rule-description">
                        Applies to BOTH 4% and 9% deals. No new construction within 1 mile of 
                        developments serving the same population that received credits in prior 3 years.
                    </div>
                </div>
                <div class="rule-card">
                    <div class="rule-title">Two Mile Same Year Rule</div>
                    <div class="rule-description">
                        9% ONLY - In counties >1M population, no two awards in same year within 2 miles.
                    </div>
                </div>
                <div class="rule-card">
                    <div class="rule-title">QCT/DDA 30% Basis Boost</div>
                    <div class="rule-description">
                        Properties in Qualified Census Tracts or Difficult Development Areas receive 
                        30% increase in eligible basis for both 4% and 9% deals.
                    </div>
                </div>
                <div class="rule-card">
                    <div class="rule-title">4% Resolution Requirements</div>
                    <div class="rule-description">
                        4% deals require resolution of no objection from local government and 
                        public hearings by municipality/county.
                    </div>
                </div>
                <div class="rule-card">
                    <div class="rule-title">9% Competitive Scoring</div>
                    <div class="rule-description">
                        9% deals compete on underserved area points, opportunity index distances to 
                        amenities, proximity to jobs, and other QAP scoring criteria.
                    </div>
                </div>
                <div class="rule-card">
                    <div class="rule-title">Census Tract Concentration</div>
                    <div class="rule-description">
                        New construction in census tracts with >20% HTC units requires local 
                        government resolution stating no objection.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>TDHCA Accurate Analysis Report - Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Based on 2025 Qualified Allocation Plan (QAP) - 10 TAC Chapter 11</p>
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        output_file = output_dir / f"TDHCA_Analysis_Report_{self.timestamp}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved to: {output_file}")
        return str(output_file)
    
    def _calculate_statistics(self, df: pd.DataFrame) -> dict:
        """Calculate summary statistics from analysis results"""
        
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
            'low_poverty': len(df[df['Poverty_Rate'] < 20]) if 'Poverty_Rate' in df.columns else 0
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
            <div class="properties-container">
"""
        
        # Get top properties for this deal type
        category_col = f'{deal_type}_Category'
        top_properties = df[df[category_col].isin(categories)].head(10)
        
        if len(top_properties) == 0:
            html += '<p style="text-align: center; color: #666; padding: 40px;">No viable properties found for this deal type.</p>'
        else:
            for idx, prop in top_properties.iterrows():
                html += self._generate_property_card(prop, deal_type)
        
        html += """
            </div>
        </div>
"""
        
        return html
    
    def _generate_property_card(self, prop: pd.Series, deal_type: str) -> str:
        """Generate HTML for a single property card"""
        
        category = prop[f'{deal_type}_Category']
        category_class = category.lower().replace(' ', '-')
        
        # Build compliance items
        compliance_items = []
        
        # One mile rule
        if prop.get('4pct_One_Mile_Compliant'):
            compliance_items.append(('pass', '✓ Meets 1-mile/3-year rule'))
        else:
            competitors = prop.get('One_Mile_Competitors', 0)
            compliance_items.append(('fail', f'✗ {competitors} projects within 1 mile'))
        
        # QCT/DDA
        if prop.get('QCT_Status') or prop.get('DDA_Status'):
            boost_type = []
            if prop.get('QCT_Status'):
                boost_type.append('QCT')
            if prop.get('DDA_Status'):
                boost_type.append('DDA')
            compliance_items.append(('pass', f'✓ 30% basis boost ({"/".join(boost_type)})'))
        
        # Demographics
        if pd.notna(prop.get('Poverty_Rate')) and prop['Poverty_Rate'] < 20:
            compliance_items.append(('pass', f'✓ Low poverty area ({prop["Poverty_Rate"]:.1f}%)'))
        
        # Deal-specific items
        if deal_type == '4pct':
            compliance_items.append(('action', '→ Need local government resolution'))
            compliance_items.append(('action', '→ Need public hearings'))
        else:
            # 9% specific
            points = prop.get('9pct_Points_Est', 0)
            compliance_items.append(('neutral', f'Estimated points: {points}'))
            tract_score = prop.get('TDHCA_Same_Tract_Score', 0)
            compliance_items.append(('neutral', f'Underserved area score: {tract_score}/5'))
        
        html = f"""
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{prop.get('Address', 'Unknown Address')}</div>
                <div class="category-badge category-{category_class}">{category}</div>
            </div>
            
            <div class="property-details">
                <div class="detail-item">
                    <span class="detail-label">Census Tract:</span>
                    <span class="detail-value">{prop.get('Census_Tract', 'N/A')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">County:</span>
                    <span class="detail-value">{prop.get('County', 'Unknown')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Median Income:</span>
                    <span class="detail-value">${prop.get('Median_Income', 0):,}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Coordinates:</span>
                    <span class="detail-value">{prop.get('Latitude', 0):.4f}, {prop.get('Longitude', 0):.4f}</span>
                </div>
            </div>
            
            <div class="compliance-section">
                <div class="compliance-header">Compliance & Action Items:</div>
                <ul class="compliance-list">
"""
        
        for status, text in compliance_items:
            html += f"""
                    <li class="compliance-item compliance-{status}">
                        <span class="status-indicator status-{status}"></span>
                        {text}
                    </li>
"""
        
        html += """
                </ul>
            </div>
        </div>
"""
        
        return html


# Integration function to work with the analyzer
def generate_reports_from_analysis(excel_file: str, output_dir: str = "."):
    """Generate HTML reports from Excel analysis results"""
    
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name='All_Properties')
    
    # Create report generator
    generator = TDHCAReportGenerator()
    
    # Generate HTML report
    html_file = generator.generate_html_report(df, output_dir)
    
    return html_file


if __name__ == "__main__":
    # Example usage
    excel_file = "CoStar_TX_Land_TDHCA_Analysis_20240101_123456.xlsx"
    html_file = generate_reports_from_analysis(excel_file)
    print(f"HTML report generated: {html_file}")
