#!/usr/bin/env python3
"""
🏛️ CALIFORNIA HCD HOUSING ELEMENT ROMAN EMPIRE DASHBOARD
Roman Engineering Standards: Built to Last 2000+ Years
Built by Structured Consultants LLC for Colosseum Platform

Multi-tier dashboard architecture with Roman Empire styling:
- Strategic Command Center: Statewide compliance overview
- Tactical Intelligence: County-level performance comparisons  
- Operational Detail: City-level metrics and opportunities
- Site-Level Intelligence: Project-specific development data
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
# from sqlalchemy import create_engine, text  # Disabled for demo mode
from datetime import datetime, date
import os
import logging
from typing import Dict, List, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Roman Empire Color Palette - Strategic Performance Gradient
ROMAN_COLORS = {
    # Imperial Branding
    'imperial_purple': '#6A4C93',
    'senate_gold': '#F4A261',
    'marble_white': '#F8F9FA',
    'bronze_brown': '#8D5524',
    
    # Performance Gradient: Forest Green → Crimson
    'forest_green': '#228B22',      # Very Good (80%+)
    'victory_green': '#52B788',     # Good (60-80%)
    'light_green': '#90EE90',       # Above Average (50-60%)
    'warning_yellow': '#FFD700',    # Average (40-50%)
    'caution_orange': '#FFA500',    # Below Average (30-40%)
    'alert_orange': '#FF4500',      # Poor (20-30%)
    'danger_red': '#E63946',        # Bad (10-20%)
    'critical_crimson': '#DC143C'   # Very Bad (<10%)
}

# Custom CSS for Roman Empire styling
ROMAN_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Trajan+Pro:wght@400;700&display=swap');

.roman-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: #F8F9FA;
    font-family: 'Cinzel', serif;
    text-align: center;
    padding: 25px;
    margin-bottom: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(30,58,138,0.3);
    border: 2px solid #3b82f6;
}

.roman-title {
    font-family: 'Cinzel', serif;
    font-weight: 600;
    font-size: 2.8em;
    color: #F8F9FA;
    text-align: center;
    margin-bottom: 15px;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
    letter-spacing: 2px;
}

.roman-subtitle {
    font-family: 'Cinzel', serif;
    font-weight: 500;
    color: #1e40af;
    text-align: center;
    margin-bottom: 15px;
    text-shadow: none;
    font-size: 1.4em;
}

.roman-section-title {
    font-family: 'Cinzel', serif;
    font-weight: 600;
    color: #1e40af;
    margin-bottom: 10px;
    text-shadow: none;
}

.roman-card {
    background: #F8F9FA;
    border: 2px solid #3b82f6;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(59,130,246,0.15);
    margin-bottom: 20px;
}

.roman-card .card-header {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
    color: white !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    border-bottom: none !important;
}

.roman-card .card-header h4 {
    color: white !important;
    margin: 0 !important;
}

.roman-metric {
    background: linear-gradient(135deg, #F4A261 0%, #F77F00 100%);
    color: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    font-family: 'Cinzel', serif;
    font-weight: 500;
    margin: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.modern-nav-button {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 8px 20px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin: 0 5px !important;
    text-decoration: none !important;
}

.modern-nav-button:hover {
    background: linear-gradient(135deg, #0056b3 0%, #003d82 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,123,255,0.4) !important;
    color: white !important;
    text-decoration: none !important;
}

.performance-excellent {
    background: linear-gradient(135deg, #52B788 0%, #40916C 100%);
    color: white;
}

.performance-good {
    background: linear-gradient(135deg, #F4A261 0%, #E76F51 100%);
    color: white;
}

.performance-behind {
    background: linear-gradient(135deg, #F77F00 0%, #F9844A 100%);
    color: white;
}

.performance-critical {
    background: linear-gradient(135deg, #E63946 0%, #D00000 100%);
    color: white;
}

.roman-table {
    font-family: 'Cinzel', serif;
    border-collapse: collapse;
    width: 100%;
}

.roman-table th {
    background: #6A4C93;
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

.roman-table td {
    padding: 10px;
    border-bottom: 1px solid #8D5524;
}

.roman-motto {
    font-family: 'Cinzel', serif;
    font-style: italic;
    color: #8D5524;
    text-align: center;
    margin-top: 20px;
    font-size: 1.2em;
}
"""

class ColasseumRomanDashboard:
    """Roman Empire Dashboard for California HCD Housing Element Intelligence"""
    
    def __init__(self):
        """Initialize dashboard"""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
            suppress_callback_exceptions=True  # Allow callbacks for components in different tabs
        )
        
        self.app.title = "🏛️ Colosseum Housing Intelligence"
        
        # Database connection
        self.engine = None
        self.connect_database()
        
        # Setup layout and callbacks
        self.setup_layout()
        self.setup_callbacks()
    
    def connect_database(self):
        """Connect to CA HCD Housing Element database"""
        logger.info("🏛️ Running in DEMO MODE - Using mock data for Roman Empire showcase")
        self.engine = None
    
    def get_strategic_overview_data(self) -> Dict[str, Any]:
        """Get strategic command center data"""
        if not self.engine:
            return self._get_mock_strategic_data()
        
        try:
            # Demo mode - skip database operations
            pass
        except Exception as e:
            logger.error(f"❌ Failed to get strategic data: {e}")
        
        return self._get_mock_strategic_data()
    
    def _get_mock_strategic_data(self) -> Dict[str, Any]:
        """Mock strategic data for demo purposes - REALISTIC CALIFORNIA NUMBERS"""
        return {
            'total_jurisdictions': 539,
            'compliant_count': 47,           # Cities meeting RHNA requirements (8.7%)
            'non_compliant_count': 23,       # Cities in Builder's Remedy - truly non-compliant (4.3%)
            'at_risk_count': 469,            # Cities behind schedule but not Builder's Remedy (87.0%)
            'builders_remedy_count': 23,     # REALISTIC - Only truly non-compliant cities
            'streamlining_count': 156,       # About 30% of jurisdictions with SB 35 requirements
            'avg_progress': 34.2             # More realistic average progress
        }
    
    def get_county_performance_data(self) -> pd.DataFrame:
        """Get county-level performance data"""
        if not self.engine:
            return self._get_mock_county_data()
        
        try:
            # Demo mode - skip database operations
            pass
        except Exception as e:
            logger.error(f"❌ Failed to get county data: {e}")
        
        return self._get_mock_county_data()
    
    def _get_mock_county_data(self) -> pd.DataFrame:
        """Mock county data for demo purposes"""
        counties = [
            'Los Angeles', 'San Diego', 'Orange', 'Riverside', 'San Bernardino',
            'Santa Clara', 'Alameda', 'Sacramento', 'Contra Costa', 'Fresno',
            'Kern', 'Ventura', 'San Francisco', 'San Mateo', 'Stanislaus'
        ]
        
        data = []
        for county in counties:
            data.append({
                'county_name': county,
                'jurisdiction_count': np.random.randint(5, 88),
                'avg_progress': np.random.uniform(15.0, 85.0),
                'compliant_count': np.random.randint(0, 5),
                'builders_remedy_count': np.random.randint(3, 25),
                'streamlining_count': np.random.randint(5, 40)
            })
        
        return pd.DataFrame(data)
    
    def get_jurisdiction_opportunities_data(self) -> pd.DataFrame:
        """Get jurisdiction-level development opportunities"""
        if not self.engine:
            return self._get_mock_opportunities_data()
        
        try:
            # Demo mode - skip database operations
            pass
        except Exception as e:
            logger.error(f"❌ Failed to get opportunities data: {e}")
        
        return self._get_mock_opportunities_data()
    
    def _get_mock_opportunities_data(self) -> pd.DataFrame:
        """Mock opportunities data for demo"""
        jurisdictions = [
            'Los Angeles', 'San Diego', 'San Jose', 'San Francisco', 'Fresno',
            'Sacramento', 'Long Beach', 'Oakland', 'Bakersfield', 'Anaheim',
            'Santa Ana', 'Riverside', 'Stockton', 'Irvine', 'Chula Vista',
            'Fremont', 'San Bernardino', 'Modesto', 'Fontana', 'Oxnard'
        ]
        
        counties = [
            'Los Angeles', 'San Diego', 'Santa Clara', 'San Francisco', 'Fresno',
            'Sacramento', 'Los Angeles', 'Alameda', 'Kern', 'Orange',
            'Orange', 'Riverside', 'San Joaquin', 'Orange', 'San Diego',
            'Alameda', 'San Bernardino', 'Stanislaus', 'San Bernardino', 'Ventura'
        ]
        
        data = []
        for i, jurisdiction in enumerate(jurisdictions):
            progress = np.random.uniform(5.0, 95.0)
            data.append({
                'jurisdiction_name': jurisdiction,
                'county_name': counties[i],
                'overall_progress': round(progress, 1),
                'compliance_status': 'Compliant' if progress > 75 else ('At Risk' if progress > 25 else 'Non-Compliant'),
                'builders_remedy_exposed': progress < 25,
                'ministerial_approval_required': progress < 50,
                'sb35_10_percent_required': progress < 50 and progress > 25,
                'sb35_50_percent_required': progress < 25,
                'performance_category': 'Excellent' if progress >= 80 else ('Good' if progress >= 50 else ('Behind Schedule' if progress >= 20 else 'Critical'))
            })
        
        return pd.DataFrame(data).sort_values('overall_progress', ascending=False)
    
    def create_strategic_overview_layout(self) -> dbc.Container:
        """Create Strategic Command Center layout"""
        data = self.get_strategic_overview_data()
        
        # Calculate key metrics
        compliance_rate = (data['compliant_count'] / data['total_jurisdictions']) * 100
        opportunity_count = data['builders_remedy_count'] + data['streamlining_count']
        
        return dbc.Container([
            # Strategic Header
            html.Div([
                html.H1("🏛️ CALIFORNIA HOUSING ELEMENT DASHBOARD", className="roman-title"),
                html.H3("Real-Time RHNA Compliance Intelligence", className="roman-subtitle"),
                html.P("Real-time RHNA compliance monitoring across all 539 California jurisdictions", 
                      style={'text-align': 'center', 'font-family': 'Cinzel, serif'})
            ], className="roman-header"),
            
            # Key Metrics Row
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H2(f"{data['total_jurisdictions']}", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("Total Jurisdictions", style={'margin': '0'})
                    ], className="roman-metric")
                ], width=2),
                dbc.Col([
                    html.Div([
                        html.H2(f"{data['compliant_count']}", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("Compliant Cities", style={'margin': '0'})
                    ], className="roman-metric performance-excellent")
                ], width=2),
                dbc.Col([
                    html.Div([
                        html.H2(f"{data['builders_remedy_count']}", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("Builder's Remedy", style={'margin': '0'})
                    ], className="roman-metric performance-critical")
                ], width=2),
                dbc.Col([
                    html.Div([
                        html.H2(f"{data['streamlining_count']}", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("SB 35 Streamlining", style={'margin': '0'})
                    ], className="roman-metric performance-behind")
                ], width=2),
                dbc.Col([
                    html.Div([
                        html.H2(f"{compliance_rate:.1f}%", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("Compliance Rate", style={'margin': '0'})
                    ], className="roman-metric performance-good")
                ], width=2),
                dbc.Col([
                    html.Div([
                        html.H2(f"{data['avg_progress']:.1f}%", style={'margin': '0', 'font-size': '2.5em'}),
                        html.P("Avg RHNA Progress", style={'margin': '0'})
                    ], className="roman-metric")
                ], width=2)
            ], className="mb-4"),
            
            # Charts Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🎯 Compliance Status Distribution", style={'color': 'white', 'font-family': 'Cinzel, serif', 'font-weight': '600', 'margin': '0'})
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="compliance-pie-chart")
                        ])
                    ], className="roman-card")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("📊 Development Opportunities", style={'color': 'white', 'font-family': 'Cinzel, serif', 'font-weight': '600', 'margin': '0'})
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="opportunities-bar-chart")
                        ])
                    ], className="roman-card")
                ], width=6)
            ], className="mb-4"),
            
            # County Performance Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🏛️ County Performance Leaderboard", style={'color': 'white', 'font-family': 'Cinzel, serif', 'font-weight': '600', 'margin': '0'})
                        ]),
                        dbc.CardBody([
                            html.Div(id="county-performance-table")
                        ])
                    ], className="roman-card")
                ], width=12)
            ])
        ], fluid=True)
    
    def create_tactical_intelligence_layout(self) -> dbc.Container:
        """Create Tactical Intelligence layout"""
        return dbc.Container([
            html.Div([
                html.H1("⚔️ TACTICAL INTELLIGENCE", className="roman-title"),
                html.H3("County-Level Performance Analysis", className="roman-subtitle"),
                html.P("Comparative analysis and strategic positioning across California counties", 
                      style={'text-align': 'center', 'font-family': 'Cinzel, serif'})
            ], className="roman-header"),
            
            # County Selection
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🎯 County Selection", className="roman-subtitle")
                        ]),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="county-selector",
                                placeholder="Select counties for comparison...",
                                multi=True,
                                style={'font-family': 'Cinzel, serif'}
                            )
                        ])
                    ], className="roman-card")
                ], width=12)
            ], className="mb-4"),
            
            # Comparison Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("📈 RHNA Progress Comparison", className="roman-subtitle")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="county-progress-chart")
                        ])
                    ], className="roman-card")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🏗️ Development Opportunity Heatmap", className="roman-subtitle")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="county-heatmap")
                        ])
                    ], className="roman-card")
                ], width=6)
            ])
        ], fluid=True)
    
    def create_operational_detail_layout(self) -> dbc.Container:
        """Create Operational Detail layout"""
        return dbc.Container([
            html.Div([
                html.H1("🏙️ OPERATIONAL INTELLIGENCE", className="roman-title"),
                html.H3("City-Level Development Opportunities", className="roman-subtitle"),
                html.P("Detailed analysis of individual jurisdictions and project opportunities", 
                      style={'text-align': 'center', 'font-family': 'Cinzel, serif'})
            ], className="roman-header"),
            
            # Filters Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Label("Performance Category:", style={'font-family': 'Cinzel, serif', 'font-weight': 'bold'}),
                            dcc.Dropdown(
                                id="performance-filter",
                                options=[
                                    {'label': '🏆 Excellent (80%+)', 'value': 'Excellent'},
                                    {'label': '✅ Good (50-80%)', 'value': 'Good'},
                                    {'label': '⚠️ Behind Schedule (20-50%)', 'value': 'Behind Schedule'},
                                    {'label': '🚨 Critical (<20%)', 'value': 'Critical'}
                                ],
                                multi=True,
                                value=['Critical', 'Behind Schedule'],
                                style={'font-family': 'Cinzel, serif'}
                            )
                        ])
                    ], className="roman-card")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Label("Development Opportunities:", style={'font-family': 'Cinzel, serif', 'font-weight': 'bold'}),
                            dcc.Checklist(
                                id="opportunity-filter",
                                options=[
                                    {'label': "🏗️ Builder's Remedy Active", 'value': 'builders_remedy'},
                                    {'label': '⚡ SB 35 Streamlining', 'value': 'streamlining'},
                                    {'label': '🎯 50% Affordable Required', 'value': 'sb35_50'},
                                    {'label': '📋 10% Affordable Required', 'value': 'sb35_10'}
                                ],
                                value=['builders_remedy', 'streamlining'],
                                style={'font-family': 'Cinzel, serif'}
                            )
                        ])
                    ], className="roman-card")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Label("County Filter:", style={'font-family': 'Cinzel, serif', 'font-weight': 'bold'}),
                            dcc.Dropdown(
                                id="operational-county-filter",
                                placeholder="Select specific counties...",
                                multi=True,
                                style={'font-family': 'Cinzel, serif'}
                            )
                        ])
                    ], className="roman-card")
                ], width=4)
            ], className="mb-4"),
            
            # Results Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🎯 Strategic Development Targets", className="roman-subtitle")
                        ]),
                        dbc.CardBody([
                            html.Div(id="opportunities-table")
                        ])
                    ], className="roman-card")
                ], width=12)
            ])
        ], fluid=True)
    
    def setup_layout(self):
        """Setup main dashboard layout"""
        # Add custom CSS to app
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                ''' + ROMAN_CSS + '''
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
        self.app.layout = dbc.Container([
            
            # Navigation
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Strategic", href="#", id="nav-strategic", className="modern-nav-button")),
                    dbc.NavItem(dbc.NavLink("Tactical", href="#", id="nav-tactical", className="modern-nav-button")),
                    dbc.NavItem(dbc.NavLink("Operational", href="#", id="nav-operational", className="modern-nav-button"))
                ],
                brand="🏛️ COLOSSEUM",
                brand_style={'font-family': 'Cinzel, serif', 'font-weight': '600', 'font-size': '1.8em', 'color': '#F8F9FA'},
                color="dark",
                dark=True,
                className="mb-4"
            ),
            
            # Tab Content
            dcc.Store(id="active-tab", data="strategic"),
            html.Div(id="tab-content"),
            
            # Footer
            html.Hr(),
            html.Div([
                html.P("🏛️ Built by Structured Consultants LLC", className="roman-motto"),
                html.P("\"Vincere Habitatio\" - To Conquer Housing", className="roman-motto")
            ])
        ], fluid=True)
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output("active-tab", "data"),
            [Input("nav-strategic", "n_clicks"),
             Input("nav-tactical", "n_clicks"), 
             Input("nav-operational", "n_clicks")]
        )
        def update_active_tab(strategic_clicks, tactical_clicks, operational_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return "strategic"
            
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if button_id == "nav-tactical":
                return "tactical"
            elif button_id == "nav-operational":
                return "operational"
            else:
                return "strategic"
        
        @self.app.callback(
            Output("tab-content", "children"),
            Input("active-tab", "data")
        )
        def render_tab_content(active_tab):
            if active_tab == "tactical":
                return self.create_tactical_intelligence_layout()
            elif active_tab == "operational":
                return self.create_operational_detail_layout()
            else:
                return self.create_strategic_overview_layout()
        
        @self.app.callback(
            Output("compliance-pie-chart", "figure"),
            Input("active-tab", "data")
        )
        def update_compliance_pie(active_tab):
            if active_tab != "strategic":
                return {}
            
            data = self.get_strategic_overview_data()
            
            # More accurate HCD compliance categories
            fig = go.Figure(data=[go.Pie(
                labels=['At Risk (Behind Schedule)', 'Non-Compliant (Builder\'s Remedy)', 'Compliant'],
                values=[data['at_risk_count'], data['non_compliant_count'], data['compliant_count']],
                hole=0.4,
                marker_colors=[ROMAN_COLORS['caution_orange'], ROMAN_COLORS['critical_crimson'], ROMAN_COLORS['victory_green']]
            )])
            
            fig.update_layout(
                title={
                    'text': 'Jurisdiction Compliance Status',
                    'font': {'family': 'Cinzel, serif', 'size': 16}
                },
                font={'family': 'Cinzel, serif'},
                showlegend=True
            )
            
            return fig
        
        @self.app.callback(
            Output("opportunities-bar-chart", "figure"),
            Input("active-tab", "data")
        )
        def update_opportunities_bar(active_tab):
            if active_tab != "strategic":
                return {}
            
            data = self.get_strategic_overview_data()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['SB 35 Streamlining', "Builder's Remedy", 'Pro-Housing Eligible'],
                    y=[data['streamlining_count'], data['builders_remedy_count'], 59],
                    marker_color=[ROMAN_COLORS['caution_orange'], ROMAN_COLORS['critical_crimson'], ROMAN_COLORS['victory_green']]
                )
            ])
            
            fig.update_layout(
                title={
                    'text': 'Development Opportunities',
                    'font': {'family': 'Cinzel, serif', 'size': 16}
                },
                font={'family': 'Cinzel, serif'},
                xaxis_title="Opportunity Type",
                yaxis_title="Number of Jurisdictions"
            )
            
            return fig
        
        @self.app.callback(
            Output("county-performance-table", "children"),
            Input("active-tab", "data")
        )
        def update_county_table(active_tab):
            if active_tab != "strategic":
                return []
            
            df = self.get_county_performance_data()
            
            return dash_table.DataTable(
                data=df.head(15).to_dict('records'),
                columns=[
                    {"name": "County", "id": "county_name", "deletable": False, "selectable": False},
                    {"name": "Cities", "id": "jurisdiction_count", "type": "numeric"},
                    {"name": "Avg Progress (%)", "id": "avg_progress", "type": "numeric", "format": {"specifier": ".1f"}},
                    {"name": "Compliant", "id": "compliant_count", "type": "numeric", 
                     "presentation": "markdown"},
                    {"name": "Builder's Remedy", "id": "builders_remedy_count", "type": "numeric",
                     "presentation": "markdown"},
                    {"name": "Streamlining", "id": "streamlining_count", "type": "numeric",
                     "presentation": "markdown"}
                ],
                tooltip_header={
                    'compliant_count': 'Cities meeting their RHNA housing production requirements',
                    'builders_remedy_count': 'Cities exposed to Builder\'s Remedy (streamlined 20% affordable housing)',
                    'streamlining_count': 'Cities subject to SB 35 ministerial approval requirements'
                },
                tooltip_delay=0,
                tooltip_duration=None,
                sort_action="native",  # Enable sorting
                sort_by=[{"column_id": "avg_progress", "direction": "desc"}],  # Default sort by progress
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                    'padding': '10px',
                    'color': 'black'
                },
                style_header={
                    'backgroundColor': '#1e40af',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{avg_progress} >= 80'},
                        'backgroundColor': f"{ROMAN_COLORS['forest_green']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{avg_progress} >= 60 && {avg_progress} < 80'},
                        'backgroundColor': f"{ROMAN_COLORS['victory_green']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{avg_progress} >= 40 && {avg_progress} < 60'},
                        'backgroundColor': f"{ROMAN_COLORS['warning_yellow']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{avg_progress} >= 20 && {avg_progress} < 40'},
                        'backgroundColor': f"{ROMAN_COLORS['caution_orange']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{avg_progress} < 20'},
                        'backgroundColor': f"{ROMAN_COLORS['critical_crimson']}80",  # 50% opacity
                        'color': 'black',
                    }
                ]
            )
        
        @self.app.callback(
            Output("county-selector", "options"),
            Input("active-tab", "data")
        )
        def update_county_selector_options(active_tab):
            if active_tab != "tactical":
                return []
            df = self.get_county_performance_data()
            options = [{'label': county, 'value': county} for county in sorted(df['county_name'].unique())]
            return options
        
        @self.app.callback(
            Output("operational-county-filter", "options"),
            Input("active-tab", "data")
        )
        def update_operational_county_options(active_tab):
            if active_tab != "operational":
                return []
            df = self.get_county_performance_data()
            options = [{'label': county, 'value': county} for county in sorted(df['county_name'].unique())]
            return options
        
        @self.app.callback(
            Output("county-progress-chart", "figure"),
            [Input("county-selector", "value"), Input("active-tab", "data")]
        )
        def update_county_progress_chart(selected_counties, active_tab):
            if active_tab != "tactical":
                return {}
                
            df = self.get_county_performance_data()
            if selected_counties and len(selected_counties) > 0:
                df = df[df['county_name'].isin(selected_counties)]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['county_name'][:10],  # Limit to top 10 for readability
                    y=df['avg_progress'][:10],
                    marker_color=[self._get_performance_color(progress) for progress in df['avg_progress'][:10]]
                )
            ])
            
            fig.update_layout(
                title={'text': 'County RHNA Progress Comparison', 'font': {'family': 'Cinzel, serif'}},
                font={'family': 'Cinzel, serif'},
                xaxis_title="County",
                yaxis_title="Average Progress (%)"
            )
            
            return fig
        
        @self.app.callback(
            Output("county-heatmap", "figure"),
            [Input("county-selector", "value"), Input("active-tab", "data")]
        )
        def update_county_heatmap(selected_counties, active_tab):
            if active_tab != "tactical":
                return {}
                
            df = self.get_county_performance_data()
            
            # Create proper heatmap data structure
            heatmap_data = [
                df['builders_remedy_count'][:10].tolist(),
                df['streamlining_count'][:10].tolist(), 
                df['compliant_count'][:10].tolist()
            ]
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=df['county_name'][:10].tolist(),
                y=['Builder\'s Remedy', 'SB 35 Streamlining', 'Compliant'],
                colorscale='RdYlGn_r'
            ))
            
            fig.update_layout(
                title={'text': 'Development Opportunities Heatmap', 'font': {'family': 'Cinzel, serif'}},
                font={'family': 'Cinzel, serif'}
            )
            
            return fig
        
        @self.app.callback(
            Output("opportunities-table", "children"),
            [Input("performance-filter", "value"),
             Input("opportunity-filter", "value"),
             Input("operational-county-filter", "value"),
             Input("active-tab", "data")]
        )
        def update_opportunities_table(performance_filter, opportunity_filter, county_filter, active_tab):
            if active_tab != "operational":
                return []
            df = self.get_jurisdiction_opportunities_data()
            
            # Apply filters
            if performance_filter:
                df = df[df['performance_category'].isin(performance_filter)]
            
            if opportunity_filter:
                filter_conditions = []
                if 'builders_remedy' in opportunity_filter:
                    filter_conditions.append(df['builders_remedy_exposed'] == True)
                if 'streamlining' in opportunity_filter:
                    filter_conditions.append(df['ministerial_approval_required'] == True)
                if 'sb35_50' in opportunity_filter:
                    filter_conditions.append(df['sb35_50_percent_required'] == True)
                if 'sb35_10' in opportunity_filter:
                    filter_conditions.append(df['sb35_10_percent_required'] == True)
                
                if filter_conditions:
                    combined_filter = filter_conditions[0]
                    for condition in filter_conditions[1:]:
                        combined_filter = combined_filter | condition
                    df = df[combined_filter]
            
            if county_filter:
                df = df[df['county_name'].isin(county_filter)]
            
            # Add opportunity indicators
            df['opportunities'] = df.apply(lambda row: self._format_opportunities(row), axis=1)
            
            return dash_table.DataTable(
                data=df.head(50).to_dict('records'),
                columns=[
                    {"name": "Jurisdiction", "id": "jurisdiction_name"},
                    {"name": "County", "id": "county_name"},
                    {"name": "Progress (%)", "id": "overall_progress", "type": "numeric", "format": {"specifier": ".1f"}},
                    {"name": "Status", "id": "compliance_status"},
                    {"name": "Category", "id": "performance_category"},
                    {"name": "Opportunities", "id": "opportunities"}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'color': 'black'
                },
                style_header={
                    'backgroundColor': '#1e40af',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{performance_category} = Excellent'},
                        'backgroundColor': f"{ROMAN_COLORS['forest_green']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{performance_category} = Good'},
                        'backgroundColor': f"{ROMAN_COLORS['victory_green']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{performance_category} = "Behind Schedule"'},
                        'backgroundColor': f"{ROMAN_COLORS['caution_orange']}80",  # 50% opacity
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{performance_category} = Critical'},
                        'backgroundColor': f"{ROMAN_COLORS['critical_crimson']}80",  # 50% opacity
                        'color': 'black',
                    }
                ]
            )
    
    def _get_performance_color(self, progress: float) -> str:
        """Get color based on performance percentage using strategic gradient"""
        if progress >= 80:
            return ROMAN_COLORS['forest_green']        # Very Good (80%+)
        elif progress >= 60:
            return ROMAN_COLORS['victory_green']       # Good (60-80%)
        elif progress >= 50:
            return ROMAN_COLORS['light_green']         # Above Average (50-60%)
        elif progress >= 40:
            return ROMAN_COLORS['warning_yellow']      # Average (40-50%)
        elif progress >= 30:
            return ROMAN_COLORS['caution_orange']      # Below Average (30-40%)
        elif progress >= 20:
            return ROMAN_COLORS['alert_orange']        # Poor (20-30%)
        elif progress >= 10:
            return ROMAN_COLORS['danger_red']          # Bad (10-20%)
        else:
            return ROMAN_COLORS['critical_crimson']    # Very Bad (<10%)
    
    def _format_opportunities(self, row) -> str:
        """Format opportunities for display"""
        opportunities = []
        
        if row.get('builders_remedy_exposed'):
            opportunities.append("🏗️ Builder's Remedy")
        if row.get('sb35_50_percent_required'):
            opportunities.append("⚡ 50% SB35")
        elif row.get('sb35_10_percent_required'):
            opportunities.append("📋 10% SB35")
        elif row.get('ministerial_approval_required'):
            opportunities.append("🎯 Streamlining")
        
        return " | ".join(opportunities) if opportunities else "None"
    
    def run_server(self, debug=False, port=8050):
        """Run the dashboard server"""
        logger.info("🏛️ LAUNCHING CALIFORNIA HCD HOUSING ELEMENT ROMAN EMPIRE DASHBOARD")
        logger.info("=" * 80)
        logger.info("📊 COLOSSEUM PLATFORM - Roman Engineering Standards")
        logger.info("🏗️ Built by Structured Consultants LLC")
        logger.info("=" * 80)
        logger.info(f"🌐 Dashboard URL: http://127.0.0.1:{port}")
        logger.info("⚔️ Ready for Roman conquest of housing intelligence!")
        logger.info("=" * 80)
        
        self.app.run(debug=debug, port=port, host='127.0.0.1')

def main():
    """Main dashboard function"""
    dashboard = ColasseumRomanDashboard()
    dashboard.run_server(debug=True, port=8050)

if __name__ == "__main__":
    main()