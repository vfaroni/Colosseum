"""
Texas LIHTC Deal Sourcing Dashboard
Business-focused interface for identifying and contacting land opportunities
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path
import glob
# Import required modules with error handling
try:
    from hud_rent_integration import HUDRentIntegrator
    HUD_RENT_AVAILABLE = True
except ImportError as e:
    st.warning(f"HUD rent integration not available: {e}")
    HUD_RENT_AVAILABLE = False

try:
    from tdhca_scoring_engine import TdhcaScoringEngine
    TDHCA_SCORING_AVAILABLE = True
except ImportError as e:
    st.warning(f"TDHCA scoring engine not available: {e}")
    TDHCA_SCORING_AVAILABLE = False

try:
    from column_mapper import quick_fix_dashboard_data
    COLUMN_MAPPER_AVAILABLE = True
except ImportError as e:
    st.warning(f"Column mapper not available: {e}")
    COLUMN_MAPPER_AVAILABLE = False
    # Create fallback function
    def quick_fix_dashboard_data(df):
        return df

# Page configuration
st.set_page_config(
    page_title="Texas Affordable Housing Deal Pipeline",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for business styling
st.markdown("""
    <style>
    .deal-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .demo-banner {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .eligible-card {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .warning-card {
        background: linear-gradient(90deg, #f59e0b, #d97706);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .contact-info {
        background-color: #f8fafc;
        padding: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .score-high { color: #059669; font-weight: bold; }
    .score-medium { color: #d97706; font-weight: bold; }
    .score-low { color: #dc2626; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="deal-header">🏢 Texas Affordable Housing Deal Pipeline</h1>', unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_analysis_data(file_path=None):
    """Load the merged analysis data"""
    if file_path and Path(file_path).exists():
        return pd.read_excel(file_path, sheet_name=0)
    
    # Find most recent merged file
    merged_files = glob.glob('*MERGED*.xlsx')
    if merged_files:
        latest_file = max(merged_files, key=lambda x: Path(x).stat().st_mtime)
        return pd.read_excel(latest_file, sheet_name=0)
    
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
    
    # Add eligibility based on one_mile_compliant
    sample_df = pd.DataFrame(sample_data)
    sample_df['eligibility'] = sample_df['one_mile_compliant'].map({True: 'ELIGIBLE', False: 'INELIGIBLE'})
    
    return sample_df

# File loading
uploaded_file = st.file_uploader(
    "Upload Analysis Results", 
    type=['xlsx'],
    help="Upload the merged CoStar + Analysis Excel file"
)

try:
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        demo_mode = False
        st.success("✅ File loaded successfully! Applying universal column mapping...")
        # Apply universal column mapping and fixes
        df = quick_fix_dashboard_data(df)
    else:
        df = load_analysis_data()
        if df is not None:
            demo_mode = False
            df = quick_fix_dashboard_data(df)
        else:
            demo_mode = False
    
    if df is None:
        st.markdown('<div class="demo-banner">No data file uploaded - Running in demo mode with sample data</div>', unsafe_allow_html=True)
        df = create_sample_data()
        demo_mode = True
    
except Exception as e:
    st.error(f"Error loading file: {str(e)}")
    st.markdown('<div class="demo-banner">File loading failed - Running in demo mode with sample data</div>', unsafe_allow_html=True)
    df = create_sample_data()
    demo_mode = True

# Data cleaning and preparation
def clean_city_data(df):
    """Fix city data - use actual city over 'other'"""
    if 'City' in df.columns:
        # If there are other city columns, use them as backup
        city_columns = [col for col in df.columns if 'city' in col.lower()]
        
        # Create a cleaned city column
        df['City_Clean'] = df['City'].copy()
        
        # Replace 'other' or null values with better data if available
        mask = (df['City_Clean'].isna()) | (df['City_Clean'].str.lower() == 'other')
        
        for col in city_columns:
            if col != 'City':
                df.loc[mask, 'City_Clean'] = df.loc[mask, col]
                mask = (df['City_Clean'].isna()) | (df['City_Clean'].str.lower() == 'other')
    
    return df

df = clean_city_data(df)

# Initialize HUD rent integrator and add rent data
@st.cache_data
def add_rent_data(df):
    """Add HUD AMI rent data to the dataframe"""
    if HUD_RENT_AVAILABLE:
        rent_integrator = HUDRentIntegrator()
        return rent_integrator.add_rents_to_dataframe(df)
    return df

# Add rent data with caching
if HUD_RENT_AVAILABLE:
    try:
        df = add_rent_data(df)
        st.success("✅ HUD rent data loaded successfully")
    except Exception as e:
        st.warning(f"⚠️ Could not load HUD rent data: {str(e)}")
        st.info("Dashboard will work without rent data, but revenue analysis will be limited.")
else:
    st.info("ℹ️ HUD rent integration not available - revenue analysis will be limited.")

# Add scoring columns for 4% vs 9% deals
# Initialize comprehensive TDHCA scoring engine
if TDHCA_SCORING_AVAILABLE:
    try:
        scoring_engine = TdhcaScoringEngine()
        # Calculate comprehensive scoring
        df = scoring_engine.calculate_comprehensive_scoring(df)
    except Exception as e:
        st.warning(f"⚠️ Could not run TDHCA scoring: {str(e)}")
        # Add basic scoring columns as fallback
        if '4pct_score' not in df.columns:
            df['4pct_score'] = 50
        if '9pct_score' not in df.columns:
            df['9pct_score'] = 50
else:
    st.info("ℹ️ TDHCA scoring engine not available - using basic scoring.")
    # Add basic scoring columns as fallback
    if '4pct_score' not in df.columns:
        df['4pct_score'] = 50
    if '9pct_score' not in df.columns:
        df['9pct_score'] = 50

# Add deal quality categories (legacy function for compatibility)
def categorize_deals(df):
    """Categorize deals by quality - now uses comprehensive scoring"""
    
    # 4% Deal Categories (use new column names)
    score_col_4p = '4pct_total_score' if '4pct_total_score' in df.columns else '4pct_score'
    if score_col_4p in df.columns:
        df['4pct_category'] = pd.cut(df[score_col_4p], 
                                    bins=[0, 30, 60, 100], 
                                    labels=['Low Priority', 'Medium Priority', 'High Priority'])
    else:
        df['4pct_category'] = 'Unknown'
    
    # 9% Deal Categories (use new column names)
    score_col_9p = '9pct_total_score' if '9pct_total_score' in df.columns else '9pct_score'
    if score_col_9p in df.columns:
        df['9pct_category'] = pd.cut(df[score_col_9p], 
                                    bins=[0, 35, 70, 100], 
                                    labels=['Low Priority', 'Medium Priority', 'High Priority'])
    else:
        df['9pct_category'] = 'Unknown'
    
    # Overall deal recommendation
    df['deal_quality'] = 'Review Needed'
    
    # Create legacy score columns for compatibility if they don't exist
    if '4pct_score' not in df.columns and score_col_4p in df.columns:
        df['4pct_score'] = df[score_col_4p]
    if '9pct_score' not in df.columns and score_col_9p in df.columns:
        df['9pct_score'] = df[score_col_9p]
    
    # Use comprehensive recommendations if available
    if 'deal_recommendation' in df.columns:
        recommendation_map = {
            'RECOMMEND 9% - Competitive scoring': 'Excellent Opportunity',
            'RECOMMEND 4% - Viable but not 9% competitive': 'Good Opportunity', 
            'NOT RECOMMENDED - Low scoring both types': 'Marginal Opportunity',
            'NOT RECOMMENDED - Fatal flaw': 'Poor Opportunity'
        }
        df['deal_quality'] = df['deal_recommendation'].map(recommendation_map).fillna('Review Needed')
    else:
        # Fallback to legacy scoring
        if '4pct_score' in df.columns and '9pct_score' in df.columns:
            # High quality: Eligible + High scores
            high_4pct = (df.get('eligibility', 'ELIGIBLE') == 'ELIGIBLE') & (df['4pct_score'] >= 60)
            high_9pct = (df.get('eligibility', 'ELIGIBLE') == 'ELIGIBLE') & (df['9pct_score'] >= 70)
            
            df.loc[high_4pct | high_9pct, 'deal_quality'] = 'Excellent Opportunity'
            
            # Medium quality: Eligible + Medium scores
            med_4pct = (df.get('eligibility', 'ELIGIBLE') == 'ELIGIBLE') & (df['4pct_score'].between(30, 59))
            med_9pct = (df.get('eligibility', 'ELIGIBLE') == 'ELIGIBLE') & (df['9pct_score'].between(35, 69))
            
            df.loc[(med_4pct | med_9pct) & (df['deal_quality'] != 'Excellent Opportunity'), 'deal_quality'] = 'Good Opportunity'
            
            # Low quality: Eligible but low scores or ineligible
            if 'eligibility' in df.columns:
                df.loc[df['eligibility'] != 'ELIGIBLE', 'deal_quality'] = 'Poor Opportunity'
    
    return df

df = categorize_deals(df)

# Debug information
with st.expander("🔍 Data Debug Info"):
    st.write(f"**Total properties loaded:** {len(df)}")
    st.write(f"**Columns available:** {len(df.columns)}")
    if 'deal_quality' in df.columns:
        st.write(f"**Deal quality categories:** {df['deal_quality'].value_counts().to_dict()}")
    if 'County' in df.columns:
        st.write(f"**Counties available:** {len(df['County'].unique())}")
    if 'eligibility' in df.columns:
        st.write(f"**Eligibility status:** {df['eligibility'].value_counts().to_dict()}")
    
    # Show sample of rent columns if available
    rent_cols = [col for col in df.columns if 'AMI_rent' in col]
    if rent_cols:
        st.write(f"**Rent data columns:** {len(rent_cols)} columns available")
        st.write(f"**Properties with rent data:** {df[rent_cols[0]].notna().sum()}")
    else:
        st.write("**Rent data:** Not available")

# Sidebar filters
st.sidebar.header("🎯 Deal Sourcing Filters")

# Deal type toggle
deal_type = st.sidebar.radio(
    "Focus on:",
    options=['Both 4% & 9%', '4% Credit Only', '9% Credit Only', 'Best Opportunities']
)

# Quality filter
available_qualities = df['deal_quality'].unique().tolist()
default_qualities = []

# Set defaults based on what's available
if 'Excellent Opportunity' in available_qualities:
    default_qualities.append('Excellent Opportunity')
if 'Good Opportunity' in available_qualities:
    default_qualities.append('Good Opportunity')

# If no good categories, use the first available option
if not default_qualities and available_qualities:
    default_qualities = [available_qualities[0]]

quality_filter = st.sidebar.multiselect(
    "Deal Quality:",
    options=available_qualities,
    default=default_qualities
)

# Score thresholds
if deal_type in ['4% Credit Only', 'Both 4% & 9%']:
    min_4pct_score = st.sidebar.slider("Minimum 4% Score:", 0, 100, 30, 5)
else:
    min_4pct_score = 0

if deal_type in ['9% Credit Only', 'Both 4% & 9%']:
    min_9pct_score = st.sidebar.slider("Minimum 9% Score:", 0, 100, 35, 5)
else:
    min_9pct_score = 0

# Geographic filters
st.sidebar.subheader("Geographic Filters")
counties = sorted(df['County'].dropna().unique())

# Ensure we have counties to select
if len(counties) > 0:
    default_counties = counties[:5] if len(counties) > 5 else counties
else:
    default_counties = []

selected_counties = st.sidebar.multiselect(
    "Target Counties:",
    options=counties,
    default=default_counties
)

# Exclude competing projects
exclude_competition = st.sidebar.checkbox(
    "Exclude sites with LIHTC competition", 
    value=True
)

# Contact information toggle
show_contact_info = st.sidebar.checkbox("Show Contact Information", value=True)

# Apply filters
# Start with base dataframe
filtered_df = df.copy()

# Apply quality filter
if quality_filter:
    filtered_df = filtered_df[filtered_df['deal_quality'].isin(quality_filter)]

# Apply county filter
if selected_counties:
    filtered_df = filtered_df[filtered_df['County'].isin(selected_counties)]

# Apply score filters
if '4pct_score' in filtered_df.columns and '9pct_score' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['4pct_score'] >= min_4pct_score) &
        (filtered_df['9pct_score'] >= min_9pct_score)
    ]

if exclude_competition:
    if 'one_mile_competing_count' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['one_mile_competing_count'] == 0) | 
            (filtered_df['one_mile_competing_count'].isna())
        ]
    else:
        # If competition data not available, show all eligible properties
        if 'eligibility' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['eligibility'] == 'ELIGIBLE']

# Focus on deal type
if deal_type == '4% Credit Only' and '4pct_category' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['4pct_category'] != 'Low Priority']
elif deal_type == '9% Credit Only' and '9pct_category' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['9pct_category'] != 'Low Priority']
elif deal_type == 'Best Opportunities' and 'deal_quality' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['deal_quality'] == 'Excellent Opportunity']

# Main dashboard
# Summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🎯 Target Properties", f"{len(filtered_df):,}")

with col2:
    if 'deal_quality' in filtered_df.columns:
        excellent_count = len(filtered_df[filtered_df['deal_quality'] == 'Excellent Opportunity'])
        st.metric("⭐ Excellent Deals", f"{excellent_count:,}")
    else:
        st.metric("⭐ Excellent Deals", "N/A")

with col3:
    if '4pct_score' in filtered_df.columns:
        avg_4pct = filtered_df['4pct_score'].mean()
        st.metric("📊 Avg 4% Score", f"{avg_4pct:.1f}" if not pd.isna(avg_4pct) else "N/A")
    else:
        st.metric("📊 Avg 4% Score", "N/A")

with col4:
    if '9pct_score' in filtered_df.columns:
        avg_9pct = filtered_df['9pct_score'].mean()
        st.metric("📊 Avg 9% Score", f"{avg_9pct:.1f}" if not pd.isna(avg_9pct) else "N/A")
    else:
        st.metric("📊 Avg 9% Score", "N/A")

with col5:
    if 'weighted_avg_rent_60AMI' in filtered_df.columns:
        avg_rent = filtered_df['weighted_avg_rent_60AMI'].mean()
        st.metric("💰 Avg 60% AMI Rent", f"${avg_rent:.0f}/mo" if not pd.isna(avg_rent) else "N/A")
    elif 'asking_price' in filtered_df.columns:
        avg_price = filtered_df['asking_price'].mean()
        st.metric("💰 Avg Price", f"${avg_price/1000:.0f}K" if not pd.isna(avg_price) else "N/A")
    else:
        st.metric("💰 Avg Rent", "N/A")

# Tabs for different views
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Deal Pipeline", "📞 Contact List", "💰 Rent Analysis", "📊 Market Analysis", "🗺️ Property Map", "📋 Deal Comparison"])

with tab1:
    st.subheader("🎯 LIHTC Deal Pipeline")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔥 Show Hot Deals"):
            hot_deals = filtered_df[
                (filtered_df['deal_quality'] == 'Excellent Opportunity') &
                (filtered_df['4pct_score'] >= 70)
            ].head(10)
            st.dataframe(hot_deals[['Address', 'City_Clean', '4pct_score', '9pct_score', 'deal_quality']])
    
    with col2:
        if st.button("🏆 Best 9% Deals"):
            best_9pct = filtered_df.nlargest(10, '9pct_score')
            st.dataframe(best_9pct[['Address', 'City_Clean', '9pct_score', 'same_tract_points']])
    
    with col3:
        if st.button("💡 Best 4% Deals"):
            best_4pct = filtered_df.nlargest(10, '4pct_score')
            st.dataframe(best_4pct[['Address', 'City_Clean', '4pct_score', 'city_population']])
    
    with col4:
        if st.button("📍 No Competition"):
            if 'one_mile_competing_count' in filtered_df.columns:
                no_comp = filtered_df[filtered_df['one_mile_competing_count'] == 0].head(10)
                st.dataframe(no_comp[['Address', 'City_Clean', '4pct_score', '9pct_score']])
            else:
                st.info("Competition data not available in this dataset")
    
    # Main data table with business columns (filter to available columns)
    base_columns = [
        'Address', 'City_Clean', 'County', 'deal_quality',
        '4pct_score', '4pct_category', '9pct_score', '9pct_category',
        'grocery_store_distance_miles', 'elementary_school_distance_miles',
        'city_population'
    ]
    
    # Add optional columns if they exist
    optional_columns = ['one_mile_competing_count', 'same_tract_points', 'eligibility']
    
    business_columns = [col for col in base_columns if col in filtered_df.columns]
    business_columns.extend([col for col in optional_columns if col in filtered_df.columns])
    
    # Add rent columns if available
    rent_columns = ['weighted_avg_rent_50AMI', 'weighted_avg_rent_60AMI', 
                   'annual_income_per_unit_50AMI', 'annual_income_per_unit_60AMI']
    
    # Add pricing/size columns if available
    optional_columns = ['asking_price', 'price_per_acre', 'total_acres', 'poverty_rate', 
                       'broker_name', 'broker_phone', 'broker_email'] + rent_columns
    
    for col in optional_columns:
        if col in filtered_df.columns:
            business_columns.append(col)
    
    # Filter to existing columns
    display_columns = [col for col in business_columns if col in filtered_df.columns]
    
    st.dataframe(
        filtered_df[display_columns].sort_values(['deal_quality', '9pct_score'], ascending=[True, False]),
        use_container_width=True,
        height=500
    )
    
    # Export deals
    csv = filtered_df[display_columns].to_csv(index=False)
    st.download_button(
        "📥 Export Deal Pipeline",
        data=csv,
        file_name=f"lihtc_deal_pipeline_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("📞 Contact & Outreach List")
    
    # Filter for deals worth contacting
    contact_worthy = filtered_df[
        (filtered_df['deal_quality'].isin(['Excellent Opportunity', 'Good Opportunity'])) &
        ((filtered_df['4pct_score'] >= 40) | (filtered_df['9pct_score'] >= 45))
    ].copy()
    
    if len(contact_worthy) > 0:
        # Group by broker if available
        if 'broker_name' in contact_worthy.columns:
            st.write(f"📋 **{len(contact_worthy)} properties to contact across {contact_worthy['broker_name'].nunique()} brokers**")
            
            # Broker summary
            broker_summary = contact_worthy.groupby('broker_name').agg({
                'Address': 'count',
                '4pct_score': 'mean',
                '9pct_score': 'mean',
                'broker_phone': 'first',
                'broker_email': 'first'
            }).rename(columns={'Address': 'Property Count'}).round(1)
            
            st.dataframe(broker_summary, use_container_width=True)
        
        # Contact details
        contact_columns = ['Address', 'City_Clean', 'deal_quality', '4pct_score', '9pct_score']
        
        if show_contact_info:
            contact_cols = ['broker_name', 'broker_phone', 'broker_email', 'asking_price']
            contact_columns.extend([col for col in contact_cols if col in contact_worthy.columns])
        
        st.dataframe(
            contact_worthy[contact_columns].sort_values('9pct_score', ascending=False),
            use_container_width=True
        )
        
        # Email template generator
        if st.button("📧 Generate Email Template"):
            st.code(f"""
Subject: LIHTC Development Interest - Texas Land Opportunities

Dear [Broker Name],

We are actively seeking land opportunities for LIHTC development in Texas. 
We've identified {len(contact_worthy)} properties in your portfolio that align with our investment criteria.

Properties of Interest:
{chr(10).join([f"- {row['Address']}, {row['City_Clean']} (Score: {row['4pct_score']:.0f}/100)" for _, row in contact_worthy.head(5).iterrows()])}

We can move quickly on qualified deals and would appreciate the opportunity to discuss these properties.

Best regards,
[Your Name]
[Your Company]
[Your Contact Information]
            """)
    
    else:
        st.info("No properties meet contact criteria with current filters.")

with tab3:
    st.subheader("💰 HUD AMI Rent Analysis")
    
    # Check if rent data is available
    rent_cols = [col for col in filtered_df.columns if 'AMI_rent' in col]
    
    if rent_cols:
        st.success(f"✅ HUD AMI rent data loaded for {filtered_df[rent_cols[0]].notna().sum()} properties")
        
        # County rent comparison
        st.subheader("📊 Rent by County")
        
        if 'weighted_avg_rent_60AMI' in filtered_df.columns:
            county_rents = filtered_df.groupby('County').agg({
                'weighted_avg_rent_50AMI': 'mean',
                'weighted_avg_rent_60AMI': 'mean',
                'annual_income_per_unit_50AMI': 'mean',
                'annual_income_per_unit_60AMI': 'mean',
                'Address': 'count'
            }).round(0)
            
            county_rents.columns = [
                'Avg 50% AMI Rent', 'Avg 60% AMI Rent', 
                'Annual Income 50% AMI', 'Annual Income 60% AMI', 
                'Property Count'
            ]
            
            county_rents = county_rents.sort_values('Avg 60% AMI Rent', ascending=False)
            st.dataframe(county_rents, use_container_width=True)
        
        # Rent distribution charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'weighted_avg_rent_60AMI' in filtered_df.columns:
                fig_rent_dist = px.histogram(
                    filtered_df[filtered_df['weighted_avg_rent_60AMI'].notna()],
                    x='weighted_avg_rent_60AMI',
                    nbins=20,
                    title="60% AMI Rent Distribution",
                    labels={'weighted_avg_rent_60AMI': 'Monthly Rent ($)', 'count': 'Properties'}
                )
                st.plotly_chart(fig_rent_dist, use_container_width=True)
        
        with col2:
            if 'annual_income_per_unit_60AMI' in filtered_df.columns:
                fig_income_dist = px.histogram(
                    filtered_df[filtered_df['annual_income_per_unit_60AMI'].notna()],
                    x='annual_income_per_unit_60AMI',
                    nbins=20,
                    title="Annual Income per Unit (60% AMI)",
                    labels={'annual_income_per_unit_60AMI': 'Annual Income ($)', 'count': 'Properties'}
                )
                st.plotly_chart(fig_income_dist, use_container_width=True)
        
        # Detailed rent breakdown for top counties
        st.subheader("🏠 Detailed Rent Breakdown by Unit Type")
        
        top_counties = filtered_df['County'].value_counts().head(5).index.tolist()
        selected_county = st.selectbox("Select County for Detailed Analysis:", top_counties)
        
        if selected_county and HUD_RENT_AVAILABLE:
            # Show detailed rent table for selected county
            try:
                rent_integrator = HUDRentIntegrator()
                county_rent_summary = rent_integrator.get_rent_summary(selected_county)
            except:
                county_rent_summary = pd.DataFrame()
            
            if not county_rent_summary.empty:
                st.dataframe(county_rent_summary, use_container_width=True, hide_index=True)
                
                # Calculate potential revenue scenarios
                st.subheader("💰 Revenue Scenarios")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    unit_count = st.number_input("Total Units:", min_value=50, max_value=500, value=100, step=10)
                
                with col2:
                    occupancy = st.slider("Occupancy Rate:", min_value=0.85, max_value=0.98, value=0.95, step=0.01)
                
                with col3:
                    ami_mix = st.selectbox("AMI Mix:", ["50% AMI Only", "60% AMI Only", "Mixed (70% at 60%, 30% at 50%)"])
                
                # Calculate revenue projections
                if 'weighted_avg_rent_50AMI' in filtered_df.columns and 'weighted_avg_rent_60AMI' in filtered_df.columns:
                    county_data = filtered_df[filtered_df['County'] == selected_county]
                    if len(county_data) > 0:
                        avg_rent_50 = county_data['weighted_avg_rent_50AMI'].iloc[0]
                        avg_rent_60 = county_data['weighted_avg_rent_60AMI'].iloc[0]
                        
                        if pd.notna(avg_rent_50) and pd.notna(avg_rent_60):
                            if ami_mix == "50% AMI Only":
                                monthly_revenue = unit_count * avg_rent_50 * occupancy
                            elif ami_mix == "60% AMI Only":
                                monthly_revenue = unit_count * avg_rent_60 * occupancy
                            else:  # Mixed
                                monthly_revenue = unit_count * (avg_rent_60 * 0.7 + avg_rent_50 * 0.3) * occupancy
                            
                            annual_revenue = monthly_revenue * 12
                            
                            # Display projections
                            st.markdown("### 📈 Revenue Projections")
                            
                            proj_col1, proj_col2, proj_col3 = st.columns(3)
                            
                            with proj_col1:
                                st.metric("Monthly Gross Revenue", f"${monthly_revenue:,.0f}")
                            
                            with proj_col2:
                                st.metric("Annual Gross Revenue", f"${annual_revenue:,.0f}")
                            
                            with proj_col3:
                                st.metric("Revenue per Unit", f"${annual_revenue/unit_count:,.0f}/year")
        
        # Top revenue opportunities
        st.subheader("🎯 Top Revenue Opportunities")
        
        if 'annual_income_per_unit_60AMI' in filtered_df.columns:
            top_revenue = filtered_df.nlargest(10, 'annual_income_per_unit_60AMI')[
                ['Address', 'City_Clean', 'County', 'weighted_avg_rent_60AMI', 
                 'annual_income_per_unit_60AMI', 'deal_quality']
            ].copy()
            
            # Format currency columns
            for col in ['weighted_avg_rent_60AMI', 'annual_income_per_unit_60AMI']:
                if col in top_revenue.columns:
                    top_revenue[col] = top_revenue[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
            
            st.dataframe(top_revenue, use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ HUD AMI rent data not available. Check HUD file path or run rent integration.")
        
        # Show instruction to add rent data
        st.info("""
        **To add HUD AMI rent data:**
        1. Ensure HUD2025_AMI_Rent_Data_Static.xlsx is in the correct path
        2. Or upload a file with rent data by county
        3. Restart the dashboard to reload data
        """)

with tab4:
    st.subheader("📊 Market Analysis")
    
    # Market overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Deal quality distribution
        quality_dist = filtered_df['deal_quality'].value_counts()
        fig_quality = px.pie(
            values=quality_dist.values,
            names=quality_dist.index,
            title="Deal Quality Distribution",
            color_discrete_map={
                'Excellent Opportunity': '#10b981',
                'Good Opportunity': '#f59e0b',
                'Review Needed': '#6b7280',
                'Not Viable - Competition Issues': '#ef4444'
            }
        )
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Score distribution
        fig_scores = go.Figure()
        fig_scores.add_trace(go.Histogram(x=filtered_df['4pct_score'], name='4% Scores', opacity=0.7))
        fig_scores.add_trace(go.Histogram(x=filtered_df['9pct_score'], name='9% Scores', opacity=0.7))
        fig_scores.update_layout(title="Score Distribution", barmode='overlay')
        st.plotly_chart(fig_scores, use_container_width=True)
    
    # County analysis
    county_analysis = filtered_df.groupby('County').agg({
        'Address': 'count',
        '4pct_score': 'mean',
        '9pct_score': 'mean',
        'deal_quality': lambda x: (x == 'Excellent Opportunity').sum()
    }).rename(columns={
        'Address': 'Total Properties',
        'deal_quality': 'Excellent Deals'
    }).round(1)
    
    county_analysis = county_analysis.sort_values('Excellent Deals', ascending=False)
    
    st.subheader("County Rankings")
    st.dataframe(county_analysis, use_container_width=True)

with tab6:
    st.subheader("📋 Deal Comparison Tool")
    
    # Property selector for comparison
    excellent_deals = filtered_df[filtered_df['deal_quality'] == 'Excellent Opportunity']
    
    if len(excellent_deals) >= 2:
        # Select properties to compare
        prop_options = [f"{row['Address']}, {row['City_Clean']}" for _, row in excellent_deals.iterrows()]
        
        selected_props = st.multiselect(
            "Select properties to compare:",
            options=prop_options[:20],  # Limit to first 20 for performance
            default=prop_options[:3] if len(prop_options) >= 3 else prop_options[:2]
        )
        
        if selected_props:
            # Get indices of selected properties
            selected_indices = [prop_options.index(prop) for prop in selected_props]
            comparison_df = excellent_deals.iloc[selected_indices]
            
            # Comparison metrics
            # Base comparison metrics (filter to available columns)
            base_comparison = [
                'Address', 'City_Clean', 'County', '4pct_score', '9pct_score',
                'grocery_store_distance_miles', 'elementary_school_distance_miles',
                'transit_stop_distance_miles', 'city_population'
            ]
            
            optional_comparison = ['one_mile_competing_count', 'same_tract_points', 'eligibility']
            
            comparison_metrics = [col for col in base_comparison if col in comparison_df.columns]
            comparison_metrics.extend([col for col in optional_comparison if col in comparison_df.columns])
            
            # Add financial columns if available
            financial_cols = ['asking_price', 'price_per_acre', 'total_acres']
            comparison_metrics.extend([col for col in financial_cols if col in comparison_df.columns])
            
            # Add rent columns if available
            rent_comparison_cols = ['weighted_avg_rent_50AMI', 'weighted_avg_rent_60AMI', 
                                  'annual_income_per_unit_50AMI', 'annual_income_per_unit_60AMI']
            comparison_metrics.extend([col for col in rent_comparison_cols if col in comparison_df.columns])
            
            # Display comparison
            comparison_display = comparison_df[comparison_metrics].T
            comparison_display.columns = [f"Property {i+1}" for i in range(len(selected_props))]
            
            st.dataframe(comparison_display, use_container_width=True)
            
            # Visual comparison
            if len(selected_props) >= 2:
                scores_comparison = comparison_df[['4pct_score', '9pct_score']].copy()
                scores_comparison.index = [f"Property {i+1}" for i in range(len(selected_props))]
                
                fig_comparison = px.bar(
                    scores_comparison,
                    title="Score Comparison",
                    labels={'value': 'Score', 'index': 'Property'}
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
    
    else:
        st.info("Need at least 2 excellent deals to compare. Adjust filters to see more opportunities.")

with tab5:
    st.subheader("🗺️ Deal Pipeline Map")
    
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
            # Map controls
            col1, col2 = st.columns(2)
            with col1:
                map_color = st.selectbox(
                    "Color by:",
                    ["deal_quality", "recommended_credit_type", "County"],
                    index=0
                )
            with col2:
                map_size = st.selectbox(
                    "Size by:",
                    ["Fixed", "4% Score", "9% Score"],
                    index=1
                )
            
            # Prepare hover data
            hover_cols = ['Address', 'City_Clean', 'County', 'deal_quality']
            if '4pct_total_score' in map_df.columns:
                hover_cols.append('4pct_total_score')
            if '9pct_total_score' in map_df.columns:
                hover_cols.append('9pct_total_score')
            if 'recommended_credit_type' in map_df.columns:
                hover_cols.append('recommended_credit_type')
            
            # Determine marker size
            if map_size == "4% Score" and '4pct_total_score' in map_df.columns:
                map_df['marker_size'] = np.clip(map_df['4pct_total_score'] / 3, 3, 20)
            elif map_size == "9% Score" and '9pct_total_score' in map_df.columns:
                map_df['marker_size'] = np.clip(map_df['9pct_total_score'] / 3, 3, 20)
            else:
                map_df['marker_size'] = 8
            
            # Color mapping for deal quality
            if map_color == "deal_quality":
                color_map = {
                    'Excellent Opportunity': '#2ecc71',
                    'Good Opportunity': '#f39c12', 
                    'Marginal Opportunity': '#e67e22',
                    'Poor Opportunity': '#e74c3c'
                }
            elif map_color == "recommended_credit_type":
                color_map = {
                    '9% CREDIT': '#e74c3c',
                    '4% CREDIT': '#f39c12', 
                    'NEITHER': '#95a5a6'
                }
            else:
                color_map = None
            
            fig_map = px.scatter_mapbox(
                map_df,
                lat="Latitude",
                lon="Longitude",
                color=map_color,
                size='marker_size' if map_size != "Fixed" else None,
                hover_data=hover_cols,
                zoom=6,
                height=600,
                title=f"Deal Pipeline - {len(map_df)} Properties",
                color_discrete_map=color_map
            )
            
            fig_map.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":50,"l":0,"b":0},
                showlegend=True
            )
            
            fig_map.update_traces(
                marker=dict(
                    line=dict(width=1, color='white'),
                    opacity=0.7
                )
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Map insights
            col1, col2, col3 = st.columns(3)
            with col1:
                excellent_count = (map_df['deal_quality'] == 'Excellent Opportunity').sum()
                st.metric("🎯 Excellent Deals", excellent_count)
            with col2:
                if 'one_mile_competing_count' in map_df.columns:
                    no_competition = (map_df['one_mile_competing_count'] == 0).sum()
                    st.metric("🏆 No Competition", no_competition)
                else:
                    eligible_count = (map_df.get('eligibility', '') == 'ELIGIBLE').sum()
                    st.metric("✅ Eligible", eligible_count)
            with col3:
                if '9pct_total_score' in map_df.columns:
                    high_score = (map_df['9pct_total_score'] >= 20).sum()
                    st.metric("📈 High 9% Scores", high_score)
                else:
                    st.metric("📍 Mapped", len(map_df))
                    
        else:
            st.warning("No properties with valid coordinates to display")
    else:
        st.error("Coordinate data not available")

# Footer with action items
st.markdown("---")
st.markdown("### 🎯 Next Actions")

next_actions = []
if len(filtered_df[filtered_df['deal_quality'] == 'Excellent Opportunity']) > 0:
    next_actions.append(f"✅ Contact brokers for {len(filtered_df[filtered_df['deal_quality'] == 'Excellent Opportunity'])} excellent opportunities")

if 'one_mile_competing_count' in filtered_df.columns and len(filtered_df[filtered_df['one_mile_competing_count'] == 0]) > 0:
    next_actions.append(f"🎯 Prioritize {len(filtered_df[filtered_df['one_mile_competing_count'] == 0])} sites with no competition")

if len(filtered_df[filtered_df['9pct_score'] >= 70]) > 0:
    next_actions.append(f"🏆 Focus on {len(filtered_df[filtered_df['9pct_score'] >= 70])} high-scoring 9% opportunities")

for action in next_actions:
    st.markdown(action)

st.caption(f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Analyzing {len(df):,} total properties")