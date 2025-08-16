"""
Simple Texas Land Analysis Viewer
Focused on sortable, filterable table view with export capabilities
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import glob
from pathlib import Path
import numpy as np
from tdhca_scoring_engine import TdhcaScoringEngine

# Page config
st.set_page_config(
    page_title="Texas Property Database",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Texas Property Database")

# Load data
@st.cache_data
def load_excel_file(file_path):
    """Load Excel file and return dataframe"""
    return pd.read_excel(file_path, sheet_name=0)

@st.cache_data
def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    n_properties = 15
    
    counties = ['Harris', 'Dallas', 'Travis', 'Bexar', 'Tarrant']
    cities = ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth']
    
    sample_data = {
        'Address': [f"{1000 + i} Sample St" for i in range(n_properties)],
        'City': np.random.choice(cities, n_properties),
        'County': np.random.choice(counties, n_properties),
        'grocery_store_distance_miles': np.random.uniform(0.1, 5.0, n_properties),
        'elementary_school_distance_miles': np.random.uniform(0.1, 3.0, n_properties),
        'hospital_distance_miles': np.random.uniform(0.5, 15.0, n_properties),
        'city_population': np.random.choice([50000, 100000, 250000, 500000, 1000000], n_properties),
        'one_mile_compliant': np.random.choice([True, False], n_properties, p=[0.8, 0.2]),
        'same_tract_points': np.random.choice([0, 2, 3, 4, 5], n_properties)
    }
    
    return pd.DataFrame(sample_data)

# File selection
st.sidebar.header("Data Source")

# Option 1: Upload file
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=['xlsx'])

# Option 2: Select from existing files
existing_files = glob.glob("*MERGED*.xlsx") + glob.glob("*TEST.xlsx")
existing_files.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)

selected_file = None
if existing_files and not uploaded_file:
    selected_file = st.sidebar.selectbox(
        "Or select existing file:",
        options=["None"] + existing_files
    )

# Load data
df = None
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)
    st.success(f"Loaded uploaded file: {uploaded_file.name}")
elif selected_file and selected_file != "None":
    df = load_excel_file(selected_file)
    st.success(f"Loaded: {selected_file}")

if df is None:
    st.info("No data file selected - Running in demo mode with sample data")
    # Create sample data for demonstration
    df = create_sample_data()
    demo_mode = True
else:
    demo_mode = False

# Add basic scoring summary if not present
if 'deal_recommendation' not in df.columns:
    scoring_engine = TdhcaScoringEngine()
    df = scoring_engine.calculate_comprehensive_scoring(df)

# Display basic info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Properties", f"{len(df):,}")
with col2:
    if 'eligibility' in df.columns:
        eligible = (df['eligibility'] == 'ELIGIBLE').sum()
        st.metric("Eligible Properties", f"{eligible:,}")
with col3:
    st.metric("Total Columns", len(df.columns))

# Filters
st.sidebar.header("Filters")

# Column selector for display
all_columns = df.columns.tolist()
default_display_cols = [
    'Address', 'City', 'County', 'eligibility',
    'grocery_store_distance_miles', 'pharmacy_distance_miles', 
    'hospital_distance_miles', 'elementary_school_distance_miles',
    'transit_stop_distance_miles', 'park_distance_miles',
    'one_mile_compliant', 'city_population'
]
default_display_cols = [col for col in default_display_cols if col in all_columns]

display_columns = st.sidebar.multiselect(
    "Columns to display:",
    options=all_columns,
    default=default_display_cols if default_display_cols else all_columns[:10]
)

# Filter by eligibility
if 'eligibility' in df.columns:
    eligibility_filter = st.sidebar.multiselect(
        "Eligibility Status:",
        options=df['eligibility'].unique().tolist(),
        default=df['eligibility'].unique().tolist()
    )
    df_filtered = df[df['eligibility'].isin(eligibility_filter)]
else:
    df_filtered = df

# Filter by county
if 'County' in df.columns:
    counties = sorted(df['County'].dropna().unique().tolist())
    selected_counties = st.sidebar.multiselect(
        "Counties:",
        options=counties,
        default=counties
    )
    df_filtered = df_filtered[df_filtered['County'].isin(selected_counties)]

# Quick filters
st.sidebar.subheader("Quick Filters")

# Properties with missing grocery stores
if 'grocery_store_distance_miles' in df.columns:
    if st.sidebar.checkbox("Only properties missing grocery stores"):
        df_filtered = df_filtered[df_filtered['grocery_store_distance_miles'].isna()]

# Properties with all amenities found
amenity_cols = [col for col in df.columns if col.endswith('_distance_miles')]
if amenity_cols and st.sidebar.checkbox("Only properties with all amenities found"):
    df_filtered = df_filtered[df_filtered[amenity_cols].notna().all(axis=1)]

# Distance threshold filters
st.sidebar.subheader("Distance Thresholds")
if 'grocery_store_distance_miles' in df.columns:
    max_grocery = st.sidebar.number_input(
        "Max grocery distance (miles):", 
        min_value=0.0, 
        value=999.0,
        step=0.5
    )
    df_filtered = df_filtered[
        (df_filtered['grocery_store_distance_miles'] <= max_grocery) | 
        (df_filtered['grocery_store_distance_miles'].isna())
    ]

# Main data display
st.subheader(f"Property Data ({len(df_filtered):,} properties)")

# Prepare display dataframe
if display_columns:
    display_df = df_filtered[display_columns].copy()
else:
    display_df = df_filtered.copy()

# Format numeric columns
for col in display_df.columns:
    if 'distance_miles' in col:
        display_df[col] = display_df[col].round(2)
    elif col == 'city_population' and col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else ""
        )

# Sort options
sort_column = st.selectbox(
    "Sort by:",
    options=['None'] + [col for col in display_df.columns if col not in ['Address']],
    index=0
)

if sort_column != 'None':
    # For formatted columns, sort by original values
    if sort_column == 'city_population' and sort_column in df_filtered.columns:
        display_df = display_df.iloc[df_filtered[sort_column].argsort()]
    else:
        display_df = display_df.sort_values(sort_column)

# Display the dataframe
st.dataframe(
    display_df,
    use_container_width=True,
    height=600
)

# Export options
st.subheader("Export Options")
col1, col2, col3 = st.columns(3)

with col1:
    # CSV export
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📄 Download as CSV",
        data=csv,
        file_name=f"texas_land_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    # Excel export
    if st.button("📊 Prepare Excel Download"):
        # Create Excel file in memory
        from io import BytesIO
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            display_df.to_excel(writer, sheet_name='Filtered Data', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': ['Total Properties', 'Displayed Properties', 'Filter Date'],
                'Value': [len(df), len(df_filtered), datetime.now().strftime('%Y-%m-%d %H:%M')]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📊 Download Excel",
            data=output,
            file_name=f"texas_land_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col3:
    # Show statistics
    if st.button("📈 Show Statistics"):
        stats_df = display_df.describe()
        st.dataframe(stats_df)

# Summary statistics
with st.expander("📊 View Summary Statistics"):
    if amenity_cols:
        st.subheader("Distance Statistics")
        
        stats_data = []
        for col in amenity_cols:
            if col in df_filtered.columns:
                col_data = df_filtered[col].dropna()
                if len(col_data) > 0:
                    stats_data.append({
                        'Amenity': col.replace('_distance_miles', '').replace('_', ' ').title(),
                        'Count': len(col_data),
                        'Missing': len(df_filtered) - len(col_data),
                        'Average': f"{col_data.mean():.2f}",
                        'Median': f"{col_data.median():.2f}",
                        'Min': f"{col_data.min():.2f}",
                        'Max': f"{col_data.max():.2f}"
                    })
        
        if stats_data:
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption(f"Data loaded: {len(df):,} properties | Displaying: {len(df_filtered):,} properties | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")