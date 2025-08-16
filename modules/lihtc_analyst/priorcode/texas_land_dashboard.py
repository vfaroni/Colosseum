"""
Texas LIHTC Land Analysis Dashboard
Interactive web interface for viewing and analyzing land analysis results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path
from tdhca_scoring_engine import TdhcaScoringEngine
import glob

# Page configuration
st.set_page_config(
    page_title="Texas Land Opportunity Explorer",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .demo-banner {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏘️ Texas Land Opportunity Explorer</h1>', unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data(file_path=None):
    """Load the analysis data from Excel file"""
    if file_path and Path(file_path).exists():
        return pd.read_excel(file_path, sheet_name='Complete Data')
    
    # Try to find the most recent merged file
    import glob
    merged_files = glob.glob('*MERGED*.xlsx')
    if merged_files:
        latest_file = max(merged_files, key=lambda x: Path(x).stat().st_mtime)
        return pd.read_excel(latest_file, sheet_name='Complete Data')
    
    return None

# Sample data for demo mode
@st.cache_data
def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    n_properties = 25
    
    counties = ['Harris', 'Dallas', 'Travis', 'Bexar', 'Tarrant', 'Collin', 'Fort Bend']
    cities = ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth', 'Plano', 'Sugar Land']
    
    sample_data = {
        'Address': [f"{1000 + i} Sample St" for i in range(n_properties)],
        'City': np.random.choice(cities, n_properties),
        'County': np.random.choice(counties, n_properties),
        'Latitude': np.random.uniform(29.0, 33.0, n_properties),
        'Longitude': np.random.uniform(-106.0, -94.0, n_properties),
        'grocery_store_distance_miles': np.random.uniform(0.1, 5.0, n_properties),
        'elementary_school_distance_miles': np.random.uniform(0.1, 3.0, n_properties),
        'hospital_distance_miles': np.random.uniform(0.5, 15.0, n_properties),
        'transit_stop_distance_miles': np.random.uniform(0.1, 2.0, n_properties),
        'pharmacy_distance_miles': np.random.uniform(0.2, 4.0, n_properties),
        'park_distance_miles': np.random.uniform(0.1, 3.0, n_properties),
        'city_population': np.random.choice([50000, 100000, 250000, 500000, 1000000, 2000000], n_properties),
        'one_mile_compliant': np.random.choice([True, False], n_properties, p=[0.8, 0.2]),
        'one_mile_competing_count': np.random.choice([0, 1, 2, 3], n_properties, p=[0.6, 0.25, 0.1, 0.05]),
        'two_mile_compliant': np.random.choice([True, False], n_properties, p=[0.85, 0.15]),
        'same_tract_points': np.random.choice([0, 2, 3, 4, 5], n_properties, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
        'Census_Tract': [f"48{np.random.randint(1, 999):03d}{np.random.randint(1, 99):02d}" for _ in range(n_properties)]
    }
    
    return pd.DataFrame(sample_data)

# File uploader
uploaded_file = st.file_uploader(
    "Upload Analysis Results (Excel file)", 
    type=['xlsx'],
    help="Upload the merged analysis Excel file"
)

# Load data
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name='Complete Data')
else:
    df = load_data()

if df is None:
    st.markdown('<div class="demo-banner">No data file uploaded - Running in demo mode with sample data</div>', unsafe_allow_html=True)
    # Create sample data for demonstration
    df = create_sample_data()
    demo_mode = True
else:
    demo_mode = False

# Add comprehensive TDHCA scoring if not already present
if '4pct_total_score' not in df.columns or '9pct_total_score' not in df.columns:
    scoring_engine = TdhcaScoringEngine()
    df = scoring_engine.calculate_comprehensive_scoring(df)

# Data preprocessing
if 'eligibility' not in df.columns:
    df['eligibility'] = 'Unknown'

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Eligibility filter
eligibility_options = df['eligibility'].unique().tolist()
selected_eligibility = st.sidebar.multiselect(
    "Eligibility Status",
    options=eligibility_options,
    default=eligibility_options
)

# County filter
county_options = sorted(df['County'].dropna().unique().tolist())
selected_counties = st.sidebar.multiselect(
    "Counties",
    options=county_options,
    default=county_options[:5] if len(county_options) > 5 else county_options
)

# Distance filters
st.sidebar.subheader("Distance Filters (miles)")

# Grocery distance
if 'grocery_store_distance_miles' in df.columns:
    grocery_min = float(df['grocery_store_distance_miles'].min(skipna=True) if not df['grocery_store_distance_miles'].isna().all() else 0)
    grocery_max = float(df['grocery_store_distance_miles'].max(skipna=True) if not df['grocery_store_distance_miles'].isna().all() else 20)
    grocery_range = st.sidebar.slider(
        "Grocery Store Distance",
        min_value=grocery_min,
        max_value=grocery_max,
        value=(grocery_min, grocery_max),
        step=0.1
    )
else:
    grocery_range = (0, 20)

# Transit distance
if 'transit_stop_distance_miles' in df.columns:
    transit_min = float(df['transit_stop_distance_miles'].min(skipna=True) if not df['transit_stop_distance_miles'].isna().all() else 0)
    transit_max = float(df['transit_stop_distance_miles'].max(skipna=True) if not df['transit_stop_distance_miles'].isna().all() else 10)
    transit_range = st.sidebar.slider(
        "Transit Stop Distance",
        min_value=transit_min,
        max_value=transit_max,
        value=(transit_min, transit_max),
        step=0.1
    )
else:
    transit_range = (0, 10)

# City population filter
if 'city_population' in df.columns:
    pop_min = int(df['city_population'].min(skipna=True) if not df['city_population'].isna().all() else 0)
    pop_max = int(df['city_population'].max(skipna=True) if not df['city_population'].isna().all() else 1000000)
    pop_range = st.sidebar.slider(
        "City Population",
        min_value=pop_min,
        max_value=pop_max,
        value=(pop_min, pop_max),
        step=1000
    )
else:
    pop_range = (0, 1000000)

# Apply filters
filtered_df = df[
    (df['eligibility'].isin(selected_eligibility)) &
    (df['County'].isin(selected_counties))
]

if 'grocery_store_distance_miles' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['grocery_store_distance_miles'].between(grocery_range[0], grocery_range[1], inclusive='both')) |
        (filtered_df['grocery_store_distance_miles'].isna())
    ]

if 'transit_stop_distance_miles' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['transit_stop_distance_miles'].between(transit_range[0], transit_range[1], inclusive='both')) |
        (filtered_df['transit_stop_distance_miles'].isna())
    ]

if 'city_population' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['city_population'].between(pop_range[0], pop_range[1], inclusive='both')) |
        (filtered_df['city_population'].isna())
    ]

# Main content area
# Summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Properties",
        f"{len(filtered_df):,}",
        f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
    )

with col2:
    eligible_count = len(filtered_df[filtered_df['eligibility'] == 'ELIGIBLE'])
    st.metric(
        "Eligible Properties",
        f"{eligible_count:,}",
        f"{eligible_count / len(filtered_df) * 100:.1f}%" if len(filtered_df) > 0 else "0%"
    )

with col3:
    if 'grocery_store_distance_miles' in filtered_df.columns:
        avg_grocery = filtered_df['grocery_store_distance_miles'].mean()
        st.metric(
            "Avg Grocery Distance",
            f"{avg_grocery:.2f} mi" if not pd.isna(avg_grocery) else "N/A"
        )
    else:
        st.metric("Avg Grocery Distance", "N/A")

with col4:
    if 'transit_stop_distance_miles' in filtered_df.columns:
        avg_transit = filtered_df['transit_stop_distance_miles'].mean()
        st.metric(
            "Avg Transit Distance",
            f"{avg_transit:.2f} mi" if not pd.isna(avg_transit) else "N/A"
        )
    else:
        st.metric("Avg Transit Distance", "N/A")

with col5:
    if 'one_mile_competing_count' in filtered_df.columns:
        competition_count = filtered_df['one_mile_competing_count'].sum()
        st.metric(
            "Properties w/ Competition",
            f"{(filtered_df['one_mile_competing_count'] > 0).sum():,}"
        )
    else:
        st.metric("Properties w/ Competition", "N/A")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Table", "📈 Analytics", "🗺️ Geographic View", "📋 Summary Report"])

with tab1:
    st.subheader("Property Data Table")
    
    # Column selector
    available_cols = filtered_df.columns.tolist()
    default_cols = [
        'Address', 'City', 'County', 'eligibility', 
        'grocery_store_distance_miles', 'pharmacy_distance_miles',
        'elementary_school_distance_miles', 'transit_stop_distance_miles',
        'city_population', 'one_mile_competing_count'
    ]
    default_cols = [col for col in default_cols if col in available_cols]
    
    selected_columns = st.multiselect(
        "Select columns to display:",
        options=available_cols,
        default=default_cols
    )
    
    # Display filtered data
    if selected_columns:
        display_df = filtered_df[selected_columns].copy()
        
        # Format numeric columns
        for col in display_df.columns:
            if 'distance_miles' in col:
                display_df[col] = display_df[col].round(2)
            elif col == 'city_population':
                display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"filtered_texas_land_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("Analytics Dashboard")
    
    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Eligibility pie chart
        if 'eligibility' in filtered_df.columns:
            eligibility_counts = filtered_df['eligibility'].value_counts()
            fig_pie = px.pie(
                values=eligibility_counts.values,
                names=eligibility_counts.index,
                title="Eligibility Distribution",
                color_discrete_map={'ELIGIBLE': '#2ecc71', 'INELIGIBLE': '#e74c3c'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Distance distribution
        if 'grocery_store_distance_miles' in filtered_df.columns:
            fig_hist = px.histogram(
                filtered_df[filtered_df['grocery_store_distance_miles'].notna()],
                x='grocery_store_distance_miles',
                nbins=30,
                title="Grocery Store Distance Distribution",
                labels={'grocery_store_distance_miles': 'Distance (miles)', 'count': 'Number of Properties'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with chart_col2:
        # County distribution
        county_counts = filtered_df['County'].value_counts().head(10)
        fig_bar = px.bar(
            x=county_counts.values,
            y=county_counts.index,
            orientation='h',
            title="Top 10 Counties by Property Count",
            labels={'x': 'Number of Properties', 'y': 'County'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Proximity score scatter
        if all(col in filtered_df.columns for col in ['grocery_store_distance_miles', 'transit_stop_distance_miles']):
            fig_scatter = px.scatter(
                filtered_df,
                x='grocery_store_distance_miles',
                y='transit_stop_distance_miles',
                color='eligibility',
                title="Grocery vs Transit Distance",
                labels={
                    'grocery_store_distance_miles': 'Grocery Distance (miles)',
                    'transit_stop_distance_miles': 'Transit Distance (miles)'
                },
                color_discrete_map={'ELIGIBLE': '#2ecc71', 'INELIGIBLE': '#e74c3c'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("🗺️ Interactive Property Map")
    
    # Map controls
    col1, col2, col3 = st.columns(3)
    with col1:
        map_style = st.selectbox(
            "Map Style",
            ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain"],
            index=0
        )
    with col2:
        color_by = st.selectbox(
            "Color Properties By",
            ["eligibility", "recommended_credit_type", "County"] if "recommended_credit_type" in filtered_df.columns else ["eligibility", "County"],
            index=0
        )
    with col3:
        marker_size = st.selectbox(
            "Marker Size",
            ["Fixed", "4% Score", "9% Score"],
            index=0
        )
    
    if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
        # Validate coordinates
        map_df = filtered_df[
            filtered_df['Latitude'].notna() & 
            filtered_df['Longitude'].notna() & 
            (filtered_df['Latitude'] >= 25.0) & 
            (filtered_df['Latitude'] <= 37.0) &  # Texas latitude bounds
            (filtered_df['Longitude'] >= -107.0) & 
            (filtered_df['Longitude'] <= -93.0)  # Texas longitude bounds
        ].copy()
        
        if len(map_df) > 0:
            # Prepare hover data
            hover_cols = ['Address', 'City', 'County']
            if '4pct_total_score' in map_df.columns:
                hover_cols.append('4pct_total_score')
            if '9pct_total_score' in map_df.columns:
                hover_cols.append('9pct_total_score')
            if 'deal_recommendation' in map_df.columns:
                hover_cols.append('deal_recommendation')
            
            # Determine marker size
            size_col = None
            if marker_size == "4% Score" and '4pct_total_score' in map_df.columns:
                size_col = '4pct_total_score'
                map_df['marker_size'] = np.clip(map_df[size_col], 5, 25)
            elif marker_size == "9% Score" and '9pct_total_score' in map_df.columns:
                size_col = '9pct_total_score'
                map_df['marker_size'] = np.clip(map_df[size_col], 5, 25)
            else:
                map_df['marker_size'] = 10
            
            # Create enhanced color mapping
            if color_by == "eligibility":
                color_map = {'ELIGIBLE': '#2ecc71', 'INELIGIBLE': '#e74c3c', 'Unknown': '#3498db'}
            elif color_by == "recommended_credit_type" and "recommended_credit_type" in map_df.columns:
                color_map = {'9% CREDIT': '#e74c3c', '4% CREDIT': '#f39c12', 'NEITHER': '#95a5a6'}
            elif color_by == "County":
                # Generate colors for counties
                unique_counties = map_df['County'].unique()
                colors = px.colors.qualitative.Set3[:len(unique_counties)]
                color_map = dict(zip(unique_counties, colors))
            else:
                color_map = None
            
            # Create map with clustering for dense areas
            if len(map_df) > 50:
                st.info(f"📍 Displaying {len(map_df)} properties with enhanced visualization for dense areas")
            
            fig_map = px.scatter_mapbox(
                map_df,
                lat="Latitude",
                lon="Longitude",
                color=color_by,
                size='marker_size' if marker_size != "Fixed" else None,
                hover_data=hover_cols,
                zoom=6,
                height=700,
                title=f"Property Locations - Colored by {color_by.title()}",
                color_discrete_map=color_map
            )
            
            # Enhanced map styling
            fig_map.update_layout(
                mapbox_style=map_style,
                margin={"r":0,"t":50,"l":0,"b":0},
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left", 
                    x=0.01
                )
            )
            
            # Add Texas state outline if available
            fig_map.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    opacity=0.8
                )
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Map statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Properties Mapped", len(map_df))
            with col2:
                eligible_count = (map_df.get('eligibility', '') == 'ELIGIBLE').sum()
                st.metric("Eligible on Map", eligible_count)
            with col3:
                unique_counties = map_df['County'].nunique()
                st.metric("Counties", unique_counties)
            with col4:
                if '9pct_total_score' in map_df.columns:
                    avg_score = map_df['9pct_total_score'].mean()
                    st.metric("Avg 9% Score", f"{avg_score:.1f}")
                else:
                    st.metric("Valid Coordinates", f"{len(map_df)}/{len(filtered_df)}")
                    
        else:
            st.warning("⚠️ No properties with valid Texas coordinates to display on map.")
            st.info("Valid coordinates must be within Texas bounds: Lat 25-37°N, Lon 93-107°W")
    else:
        st.error("❌ Latitude and Longitude columns not found in data.")

with tab4:
    st.subheader("Summary Report")
    
    # Generate summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Eligibility Summary")
        eligibility_summary = filtered_df['eligibility'].value_counts()
        for status, count in eligibility_summary.items():
            percentage = (count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.write(f"**{status}**: {count:,} properties ({percentage:.1f}%)")
        
        st.markdown("### Distance Statistics")
        distance_cols = [col for col in filtered_df.columns if 'distance_miles' in col]
        
        stats_data = []
        for col in distance_cols:
            if col in filtered_df.columns:
                col_data = filtered_df[col].dropna()
                if len(col_data) > 0:
                    stats_data.append({
                        'Amenity': col.replace('_distance_miles', '').replace('_', ' ').title(),
                        'Average': f"{col_data.mean():.2f}",
                        'Median': f"{col_data.median():.2f}",
                        'Min': f"{col_data.min():.2f}",
                        'Max': f"{col_data.max():.2f}"
                    })
        
        if stats_data:
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### County Summary")
        county_summary = filtered_df.groupby('County').agg({
            'eligibility': lambda x: (x == 'ELIGIBLE').sum(),
            'Address': 'count'
        }).rename(columns={'eligibility': 'Eligible Count', 'Address': 'Total Count'})
        
        county_summary['Eligibility Rate'] = (
            county_summary['Eligible Count'] / county_summary['Total Count'] * 100
        ).round(1)
        
        county_summary = county_summary.sort_values('Total Count', ascending=False).head(15)
        st.dataframe(county_summary, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>"
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"Total records: {len(df):,} | Filtered: {len(filtered_df):,}"
    f"</div>",
    unsafe_allow_html=True
)