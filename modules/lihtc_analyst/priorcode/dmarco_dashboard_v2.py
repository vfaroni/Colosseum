"""
D'Marco's Deal Dashboard V2 - Simplified and Fixed
A clean, functional dashboard for LIHTC land acquisition
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import os

# Page config
st.set_page_config(
    page_title="D'Marco's Deal Dashboard",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS - Simplified for better compatibility
st.markdown("""
<style>
    /* Simple, clean styling */
    .main > div {
        padding-top: 2rem;
    }
    
    .stTabs {
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #007AFF;
        color: white;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .property-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .hot-badge {
        background-color: #FF3B30;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    
    .warm-badge {
        background-color: #FF9500;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    
    .cold-badge {
        background-color: #007AFF;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'notes_db' not in st.session_state:
    st.session_state.notes_db = {}
if 'lead_temps' not in st.session_state:
    st.session_state.lead_temps = {}

# Quick tags
QUICK_TAGS = [
    "motivated-seller", "quick-close", "price-negotiable", 
    "flood-risk", "great-location", "high-competition",
    "needs-rezoning", "utilities-available", "owner-financing"
]

# Load data
@st.cache_data
def load_property_data():
    """Load property data from Excel"""
    try:
        file_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/CoStar_Land_Analysis_20250616_203751.xlsx"
        df = pd.read_excel(file_path, sheet_name='All_Land_Analysis')
        # Ensure we have the columns we need
        if 'Land_Viability_Score' not in df.columns:
            df['Land_Viability_Score'] = 85  # Default score
        if 'Sale Price' not in df.columns and 'Sale_Price' in df.columns:
            df['Sale Price'] = df['Sale_Price']
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Return sample data
        return pd.DataFrame({
            'Address': ['123 Main St', '456 Oak Ave', '789 Elm Dr'],
            'City': ['Austin', 'Dallas', 'Houston'],
            'State': ['TX', 'TX', 'TX'],
            'Sale Price': [200000, 300000, 250000],
            'Land_Viability_Score': [95, 88, 92],
            'Latitude': [30.2672, 32.7767, 29.7604],
            'Longitude': [-97.7431, -96.7970, -95.3698]
        })

def get_lead_temp(address):
    """Get lead temperature for a property"""
    return st.session_state.lead_temps.get(address, "cold")

def set_lead_temp(address, temp):
    """Set lead temperature for a property"""
    st.session_state.lead_temps[address] = temp

def add_note(address, note_text, tags):
    """Add a note to a property"""
    if address not in st.session_state.notes_db:
        st.session_state.notes_db[address] = []
    
    st.session_state.notes_db[address].append({
        'timestamp': datetime.now(),
        'text': note_text,
        'tags': tags
    })

def get_notes(address):
    """Get notes for a property"""
    return st.session_state.notes_db.get(address, [])

# Main app
def main():
    st.title("🏗️ D'Marco's Deal Dashboard")
    st.subheader("Your LIHTC Land Acquisition Command Center")
    
    # Load data
    df = load_property_data()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hot_count = sum(1 for addr in df['Address'] if get_lead_temp(addr) == 'hot')
        st.metric("🔥 Hot Leads", hot_count)
    
    with col2:
        viable_count = len(df[df['Land_Viability_Score'] >= 80])
        st.metric("✅ Viable Sites", viable_count)
    
    with col3:
        total_value = df['Sale Price'].sum() / 1_000_000
        st.metric("💰 Total Value", f"${total_value:.1f}M")
    
    with col4:
        st.metric("📅 Follow-ups Today", 3)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Leads", "📍 Map View", "📊 All Properties", "📚 Learning"])
    
    with tab1:
        st.subheader("Properties Requiring Immediate Attention")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search properties, notes, or tags...")
        with col2:
            sort_by = st.selectbox("Sort by", ["Lead Temperature", "Score", "Price"])
        
        # Display properties
        for idx, row in df.head(10).iterrows():
            display_property_card(row, idx)
    
    with tab2:
        st.subheader("Property Map")
        display_map(df)
    
    with tab3:
        st.subheader("All Properties")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            temp_filter = st.multiselect("Lead Status", ["hot", "warm", "cold"])
        with col2:
            score_filter = st.slider("Min Score", 0, 100, 70)
        with col3:
            price_filter = st.slider("Max Price ($K)", 0, 1000, 500)
        
        # Filter dataframe
        display_df = df.copy()
        if temp_filter:
            display_df = display_df[display_df['Address'].apply(lambda x: get_lead_temp(x) in temp_filter)]
        display_df = display_df[display_df['Land_Viability_Score'] >= score_filter]
        display_df = display_df[display_df['Sale Price'] <= price_filter * 1000]
        
        # Add lead status column
        display_df['Lead Status'] = display_df['Address'].apply(get_lead_temp)
        
        # Display table
        st.dataframe(display_df[['Address', 'City', 'Sale Price', 'Land_Viability_Score', 'Lead Status']])
    
    with tab4:
        st.subheader("LIHTC Quick Reference")
        
        with st.expander("🏠 What is LIHTC?"):
            st.write("""
            **Low-Income Housing Tax Credit** - The primary financing tool for affordable housing.
            - 4% credits: Rehabilitation/acquisition projects
            - 9% credits: New construction
            - 30-year affordability requirement
            """)
        
        with st.expander("📍 QCT and DDA Explained"):
            st.write("""
            **QCT (Qualified Census Tract)**: Low-income areas qualifying for basis boost
            **DDA (Difficult Development Area)**: High-cost areas qualifying for basis boost
            **Benefit**: 30% increase in eligible basis = more tax credits!
            """)
        
        with st.expander("🚫 Fatal Flaws - TDHCA Rules"):
            st.write("""
            **One Mile Three Year Rule**: No LIHTC projects within 1 mile in last 3 years
            **Two Mile Same Year Rule**: 9% deals in large counties (Harris, Dallas, etc.)
            **These are automatic disqualifiers!**
            """)

def display_property_card(row, idx):
    """Display a property card with actions"""
    address = row['Address']
    score = row.get('Land_Viability_Score', 0)
    price = row.get('Sale Price', 0)
    lead_temp = get_lead_temp(address)
    
    # Create columns for the card
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Property info
        st.markdown(f"**{address}**")
        st.caption(f"Score: {score}/100 | Price: ${price:,.0f}")
        
        # Latest note
        notes = get_notes(address)
        if notes:
            latest = notes[-1]
            st.caption(f"📝 {latest['text'][:100]}...")
            if latest['tags']:
                st.caption(f"Tags: {', '.join(latest['tags'])}")
    
    with col2:
        # Lead status badge
        if lead_temp == "hot":
            st.markdown('<span class="hot-badge">🔥 HOT</span>', unsafe_allow_html=True)
        elif lead_temp == "warm":
            st.markdown('<span class="warm-badge">🟠 WARM</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="cold-badge">❄️ COLD</span>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Note", key=f"note_{idx}"):
            show_note_dialog(address)
    
    with col2:
        if st.button("📞 Contact", key=f"contact_{idx}"):
            st.info("Broker: Example Realty - (512) 555-0123")
    
    with col3:
        new_temp = st.selectbox(
            "Status",
            ["hot", "warm", "cold"],
            index=["hot", "warm", "cold"].index(lead_temp),
            key=f"temp_{idx}"
        )
        if new_temp != lead_temp:
            set_lead_temp(address, new_temp)
            st.rerun()
    
    st.divider()

def show_note_dialog(address):
    """Show note-taking dialog"""
    with st.form(key=f"note_form_{address}"):
        st.subheader(f"Add Note for {address}")
        
        note_text = st.text_area("Note", height=100)
        
        # Quick tags
        st.write("Quick Tags:")
        selected_tags = []
        cols = st.columns(3)
        for i, tag in enumerate(QUICK_TAGS):
            with cols[i % 3]:
                if st.checkbox(tag):
                    selected_tags.append(tag)
        
        # Submit
        if st.form_submit_button("Save Note"):
            if note_text:
                add_note(address, note_text, selected_tags)
                st.success("Note saved!")
                st.rerun()

def display_map(df):
    """Display interactive map"""
    fig = go.Figure()
    
    # Add markers for each property
    for idx, row in df.iterrows():
        lead_temp = get_lead_temp(row['Address'])
        color = {'hot': 'red', 'warm': 'orange', 'cold': 'blue'}.get(lead_temp, 'gray')
        
        fig.add_trace(go.Scattermapbox(
            lat=[row.get('Latitude', 30.0)],
            lon=[row.get('Longitude', -97.0)],
            mode='markers',
            marker=dict(size=12, color=color),
            text=f"{row['Address']}<br>Score: {row.get('Land_Viability_Score', 0)}",
            name=lead_temp
        ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=31.0, lon=-98.0),
            zoom=5
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()