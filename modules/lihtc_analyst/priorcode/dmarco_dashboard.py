"""
D'Marco's Land Deal Sourcing Dashboard
A comprehensive tool for tracking and managing LIHTC land opportunities in Texas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional, Tuple
import re

# Set page config with Apple-inspired design
st.set_page_config(
    page_title="D'Marco's Deal Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apple-inspired CSS styling with proper contrast
st.markdown("""
<style>
    /* Import SF Pro Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Apple Design System Colors with proper contrast */
    :root {
        --apple-blue: #007AFF;
        --apple-green: #34C759;
        --apple-orange: #FF9500;
        --apple-red: #FF3B30;
        --apple-purple: #AF52DE;
        --apple-gray: #8E8E93;
        --apple-gray-2: #C7C7CC;
        --apple-gray-3: #D1D1D6;
        --apple-gray-4: #E5E5EA;
        --apple-gray-5: #EFEFF4;
        --apple-gray-6: #F2F2F7;
        --apple-background: #FFFFFF;
        --apple-grouped-background: #F2F2F7;
        --text-primary: #000000;
        --text-secondary: #3C3C43;
        --text-tertiary: #48484A;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --apple-background: #000000;
            --apple-grouped-background: #1C1C1E;
            --apple-gray-6: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
            --text-tertiary: #C7C7CC;
        }
        
        .stApp {
            background-color: var(--apple-background);
            color: var(--text-primary);
        }
    }
    
    /* Global font and text color fixes */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
    /* Fix header and title colors */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    p, span, div {
        color: var(--text-primary);
    }
    
    /* Fix tab navigation overlap */
    .stTabs {
        margin-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--apple-gray-6);
        padding: 4px;
        border-radius: 10px;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    
    /* Main container styling */
    .main {
        padding: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Card styling with proper contrast */
    .property-card {
        background: var(--apple-grouped-background);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease-in-out;
        border: 1px solid var(--apple-gray-4);
    }
    
    .property-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }
    
    .property-card h4 {
        color: var(--text-primary) !important;
        margin: 0;
        font-weight: 600;
    }
    
    .property-card p {
        color: var(--text-secondary) !important;
        margin: 4px 0;
    }
    
    /* Lead temperature badges */
    .lead-hot {
        background: var(--apple-red);
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .lead-warm {
        background: var(--apple-orange);
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .lead-cold {
        background: var(--apple-blue);
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Tag styling */
    .tag {
        background: var(--apple-gray-5);
        color: var(--apple-gray);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-right: 4px;
        display: inline-block;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--apple-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton > button:hover {
        background: #0051D5;
        transform: translateY(-1px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--apple-gray-6);
        padding: 4px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        background: transparent;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    /* Metric styling with proper contrast */
    .metric-card {
        background: var(--apple-grouped-background);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--apple-gray-4);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary) !important;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--text-secondary) !important;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Fix Streamlit native elements */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Fix input fields */
    .stTextInput > div > div > input {
        background-color: var(--apple-grouped-background);
        color: var(--text-primary);
        border: 1px solid var(--apple-gray-4);
    }
    
    .stSelectbox > div > div > div {
        background-color: var(--apple-grouped-background);
        color: var(--text-primary);
    }
    
    /* Fix overlapping elements */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Ensure proper spacing for metrics row */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'lead_status' not in st.session_state:
    st.session_state.lead_status = {}
if 'follow_ups' not in st.session_state:
    st.session_state.follow_ups = {}
if 'selected_property' not in st.session_state:
    st.session_state.selected_property = None

# Database setup
def init_database():
    """Initialize SQLite database for persistent storage"""
    conn = sqlite3.connect('dmarco_deals.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS property_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  property_address TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  note_text TEXT,
                  tags TEXT,
                  created_by TEXT DEFAULT 'D''Marco')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS lead_tracking
                 (property_address TEXT PRIMARY KEY,
                  lead_temperature TEXT,
                  last_contact DATETIME,
                  next_follow_up DATETIME,
                  contact_count INTEGER DEFAULT 0,
                  status TEXT DEFAULT 'new')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS broker_profiles
                 (broker_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT,
                  email TEXT,
                  preferred_contact TEXT,
                  best_times TEXT,
                  responsiveness_score REAL DEFAULT 3.0,
                  notes TEXT)''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Load CoStar data
@st.cache_data
def load_property_data():
    """Load the analyzed CoStar property data"""
    try:
        # Try to load the most recent analysis file
        file_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/CoStar_Land_Analysis_20250616_203751.xlsx"
        df = pd.read_excel(file_path, sheet_name='All_Land_Analysis')
        return df
    except:
        # Create sample data if file not found
        return create_sample_data()

def create_sample_data():
    """Create sample data for testing"""
    return pd.DataFrame({
        'Address': ['4905 W Oak St', '271 The Rock Rd', 'Lot 93 Diamond Opal Lane'],
        'City': ['Palestine', 'Buchanan Dam', 'Corsicana'],
        'State': ['TX', 'TX', 'TX'],
        'Sale Price': [160000, 250000, 195000],
        'Land_Viability_Score': [95, 100, 98],
        'TDHCA_One_Mile_Count': [0, 0, 1],
        'QCT_Status': ['Yes', 'Yes', 'No'],
        'DDA_Status': ['No', 'Yes', 'Yes'],
        'FEMA_Zone': ['X', 'AE', 'X'],
        'Latitude': [31.762, 30.752, 32.095],
        'Longitude': [-95.631, -98.420, -96.469],
        'Listing Broker Company': ['ABC Realty', 'XYZ Properties', 'Best Brokers'],
        'Listing Broker Phone': ['512-555-0123', '512-555-0456', '512-555-0789']
    })

# Quick tag system
QUICK_TAGS = [
    "#motivated-seller",
    "#quick-close",
    "#price-negotiable", 
    "#flood-risk",
    "#great-location",
    "#high-competition",
    "#needs-rezoning",
    "#utilities-available",
    "#owner-financing",
    "#broker-responsive",
    "#site-visit-done",
    "#title-clear"
]

def get_lead_temperature(property_address: str) -> str:
    """Determine lead temperature based on activity"""
    conn = sqlite3.connect('dmarco_deals.db')
    c = conn.cursor()
    
    result = c.execute('''SELECT lead_temperature, last_contact 
                         FROM lead_tracking 
                         WHERE property_address = ?''', (property_address,)).fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]
    return "cold"

def add_note(property_address: str, note_text: str, tags: List[str]):
    """Add a note to a property"""
    conn = sqlite3.connect('dmarco_deals.db')
    c = conn.cursor()
    
    tags_str = ','.join(tags)
    c.execute('''INSERT INTO property_notes (property_address, note_text, tags)
                 VALUES (?, ?, ?)''', (property_address, note_text, tags_str))
    
    # Update lead tracking
    c.execute('''INSERT OR REPLACE INTO lead_tracking 
                 (property_address, last_contact, contact_count)
                 VALUES (?, datetime('now'), 
                        COALESCE((SELECT contact_count + 1 FROM lead_tracking 
                                  WHERE property_address = ?), 1))''', 
              (property_address, property_address))
    
    conn.commit()
    conn.close()

def get_property_notes(property_address: str) -> List[Dict]:
    """Get all notes for a property"""
    conn = sqlite3.connect('dmarco_deals.db')
    c = conn.cursor()
    
    notes = c.execute('''SELECT timestamp, note_text, tags 
                        FROM property_notes 
                        WHERE property_address = ?
                        ORDER BY timestamp DESC''', (property_address,)).fetchall()
    conn.close()
    
    return [{'timestamp': n[0], 'text': n[1], 'tags': n[2].split(',') if n[2] else []} 
            for n in notes]

def update_lead_temperature(property_address: str, temperature: str):
    """Update lead temperature"""
    conn = sqlite3.connect('dmarco_deals.db')
    c = conn.cursor()
    
    c.execute('''UPDATE lead_tracking 
                 SET lead_temperature = ?
                 WHERE property_address = ?''', (temperature, property_address))
    conn.commit()
    conn.close()

# Main app
def main():
    # Header with spacing
    st.markdown("# 🏗️ D'Marco's Deal Dashboard")
    st.markdown("### Your LIHTC Land Acquisition Command Center")
    
    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load property data
    df = load_property_data()
    
    # Debug info
    if len(df) == 0:
        st.error("No property data loaded. Please check the data file.")
        return
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hot_leads = sum(1 for addr in df['Address'] if get_lead_temperature(addr) == 'hot')
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{hot_leads}</div>
            <div class="metric-label">🔥 Hot Leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        viable_props = len(df[df.get('Land_Viability_Score', 0) >= 80])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{viable_props}</div>
            <div class="metric-label">✅ Viable Sites</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_value = df.get('Sale Price', pd.Series([0])).sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_value/1000000:.1f}M</div>
            <div class="metric-label">💰 Total Value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        follow_ups_today = 3  # This would be calculated from database
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{follow_ups_today}</div>
            <div class="metric-label">📅 Follow-ups Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Leads", "📍 Map View", "📊 All Properties", "📚 Learning Center"])
    
    with tab1:
        render_hot_leads_tab(df)
    
    with tab2:
        render_map_tab(df)
    
    with tab3:
        render_all_properties_tab(df)
    
    with tab4:
        render_learning_center()

def render_hot_leads_tab(df):
    """Render the hot leads tab"""
    st.markdown("### 🔥 Properties Requiring Immediate Attention")
    
    # Filter and sort options
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search properties, brokers, or notes...", 
                              placeholder="Try: #motivated-seller or broker name")
    with col2:
        sort_by = st.selectbox("Sort by", 
                              ["Lead Temperature", "Last Contact", "Property Score", "Price"])
    
    # Property cards
    for idx, row in df.head(10).iterrows():
        render_property_card(row)

def render_property_card(property_data):
    """Render a single property card"""
    address = property_data.get('Address', 'Unknown')
    score = property_data.get('Land_Viability_Score', 0)
    price = property_data.get('Sale Price', 0)
    lead_temp = get_lead_temperature(address)
    
    # Determine lead badge
    lead_badge = {
        'hot': '<span class="lead-hot">🔥 HOT LEAD</span>',
        'warm': '<span class="lead-warm">🟠 WARM</span>',
        'cold': '<span class="lead-cold">❄️ COLD</span>'
    }.get(lead_temp, '<span class="lead-cold">❄️ NEW</span>')
    
    # Get latest note
    notes = get_property_notes(address)
    latest_note = notes[0]['text'][:100] + "..." if notes else "No notes yet"
    
    with st.container():
        st.markdown(f"""
        <div class="property-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4>{address}</h4>
                    <p>Score: {score}/100 | ${price:,.0f}</p>
                </div>
                <div>
                    {lead_badge}
                </div>
            </div>
            <div style="margin-top: 12px;">
                <p style="font-size: 14px; font-style: italic;">"{latest_note}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("📝 Add Note", key=f"note_{address}"):
                st.session_state.selected_property = address
        with col2:
            if st.button("📞 Contact", key=f"contact_{address}"):
                broker_company = property_data.get('Listing Broker Company', 'Unknown Broker')
                broker_phone = property_data.get('Listing Broker Phone', 'No phone listed')
                st.info(f"Broker: {broker_company} - {broker_phone}")
        with col3:
            temp_options = ["hot", "warm", "cold"]
            current_index = temp_options.index(lead_temp) if lead_temp in temp_options else 2
            new_temp = st.selectbox("Update Status", 
                                   temp_options, 
                                   index=current_index,
                                   key=f"temp_{address}")
            if new_temp != lead_temp:
                update_lead_temperature(address, new_temp)
                st.rerun()

def render_map_tab(df):
    """Render the map view tab"""
    st.markdown("### 📍 Interactive Property Map")
    
    # Create map
    fig = go.Figure()
    
    # Add property markers
    for idx, row in df.iterrows():
        lead_temp = get_lead_temperature(row.get('Address', ''))
        color = {
            'hot': '#FF3B30',
            'warm': '#FF9500', 
            'cold': '#007AFF'
        }.get(lead_temp, '#8E8E93')
        
        fig.add_trace(go.Scattermapbox(
            lat=[row.get('Latitude', 30.0)],
            lon=[row.get('Longitude', -97.0)],
            mode='markers',
            marker=dict(size=15, color=color),
            text=f"{row.get('Address', 'Unknown')}<br>Score: {row.get('Land_Viability_Score', 0)}<br>${row.get('Sale Price', 0):,.0f}",
            hoverinfo='text',
            name=lead_temp.title()
        ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=31.0, lon=-97.5),
            zoom=6
        ),
        height=600,
        showlegend=True,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_all_properties_tab(df):
    """Render all properties in a sortable table"""
    st.markdown("### 📊 Complete Property Inventory")
    
    # Add lead temperature column
    df['Lead Status'] = df['Address'].apply(get_lead_temperature)
    
    # Display options
    show_cols = st.multiselect("Show columns", 
                              df.columns.tolist(),
                              default=['Address', 'City', 'State', 'Sale Price', 
                                      'Land_Viability_Score', 'Lead Status'])
    
    # Filter by lead status
    lead_filter = st.multiselect("Filter by lead status", 
                                 ["hot", "warm", "cold", "all"],
                                 default=["all"])
    
    if "all" not in lead_filter:
        display_df = df[df['Lead Status'].isin(lead_filter)]
    else:
        display_df = df
    
    # Show table
    st.dataframe(
        display_df[show_cols],
        use_container_width=True,
        height=500
    )

def render_learning_center():
    """Render educational content for D'Marco"""
    st.markdown("### 📚 LIHTC Quick Reference Guide")
    
    with st.expander("🏠 What is LIHTC?"):
        st.markdown("""
        **Low-Income Housing Tax Credit (LIHTC)** is the most important resource for creating 
        affordable housing in the United States today.
        
        **Key Points:**
        - Provides tax credits to developers of affordable rental housing
        - 4% credits for acquisition/rehab, 9% credits for new construction
        - Properties must stay affordable for at least 30 years
        """)
    
    with st.expander("📍 Understanding QCT and DDA"):
        st.markdown("""
        **QCT (Qualified Census Tract)**: Areas where 50% of households have incomes below 
        60% of area median income.
        
        **DDA (Difficult Development Area)**: Areas with high construction, land, and utility 
        costs relative to area median income.
        
        **Why it matters**: Properties in QCT or DDA areas get a 30% basis boost = more tax credits!
        """)
    
    with st.expander("🚫 TDHCA Fatal Flaws to Avoid"):
        st.markdown("""
        **One Mile Three Year Rule**: No LIHTC projects within 1 mile completed in last 3 years
        
        **Two Mile Same Year Rule**: For 9% deals in large counties (Harris, Dallas, Tarrant, 
        Bexar, Travis)
        
        **These are FATAL FLAWS** - if violated, the deal cannot proceed!
        """)
    
    with st.expander("💬 What to Ask Brokers"):
        st.markdown("""
        1. **Motivation**: Why is the seller selling? Any urgency?
        2. **Price Flexibility**: Is the price negotiable? Owner financing available?
        3. **Utilities**: Water, sewer, electric available at the site?
        4. **Zoning**: Current zoning and any restrictions?
        5. **Environmental**: Any known issues? Previous uses of the land?
        6. **Timeline**: How quickly can we close?
        """)

# Note-taking modal
if st.session_state.selected_property:
    with st.sidebar:
        st.markdown(f"### 📝 Add Note for {st.session_state.selected_property}")
        
        note_text = st.text_area("Note", height=150)
        
        st.markdown("**Quick Tags:**")
        selected_tags = []
        cols = st.columns(3)
        for i, tag in enumerate(QUICK_TAGS):
            with cols[i % 3]:
                if st.checkbox(tag, key=f"tag_{tag}"):
                    selected_tags.append(tag)
        
        custom_tags = st.text_input("Custom tags (comma-separated)")
        if custom_tags:
            selected_tags.extend([f"#{t.strip()}" for t in custom_tags.split(',')])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Note", type="primary"):
                if note_text:
                    add_note(st.session_state.selected_property, note_text, selected_tags)
                    st.session_state.selected_property = None
                    st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.selected_property = None
                st.rerun()

if __name__ == "__main__":
    main()