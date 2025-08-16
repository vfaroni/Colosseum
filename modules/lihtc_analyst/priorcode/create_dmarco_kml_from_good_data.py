#!/usr/bin/env python3
"""
Create D'Marco Google Earth KML from GOOD existing data
Uses the Complete_195_Sites_With_Poverty file which has proper source attribution and all data fields.

Author: Claude Code
Date: July 2025
"""

import pandas as pd
import simplekml
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dmarco_kml_from_good_data():
    """Create KML using the existing good data file"""
    
    # Load the GOOD data with proper source attribution
    input_file = "Complete_195_Sites_With_Poverty_20250621_213017.xlsx"
    df = pd.read_excel(input_file, sheet_name='All_195_Sites_Complete')
    
    logger.info(f"✅ Loaded {len(df)} sites from good data file")
    logger.info(f"   Sources: {df['Source'].value_counts().to_dict()}")
    
    # Filter for viable sites based on anchor score or other criteria
    # Using the original anchor analysis for priority classification
    anchor_df = pd.read_excel('Complete_Anchor_Analysis_All_195_Sites_20250702_151312.xlsx', 
                             sheet_name='All_195_Sites_Ranked')
    
    # Merge to get priority classifications
    df = df.merge(anchor_df[['Latitude', 'Longitude', 'Priority_Classification', 'Anchor_Score', 
                            'Anchor_Details', 'Schools_Within_2_5mi', 'LIHTC_Within_2mi']], 
                  on=['Latitude', 'Longitude'], how='left')
    
    # Filter for viable sites (exclude "Do Not Pursue")
    viable_df = df[df['Priority_Classification'] != 'Do Not Pursue'].copy()
    viable_df = viable_df.sort_values('Anchor_Score', ascending=False).reset_index(drop=True)
    
    # Add KML site numbers
    viable_df['KML_Site_Number'] = range(1, len(viable_df) + 1)
    
    logger.info(f"📊 Filtered to {len(viable_df)} viable sites")
    
    # Create KML
    kml = simplekml.Kml()
    kml.document.name = "D'Marco LIHTC Investment Opportunities - Texas QCT/DDA Sites"
    kml.document.description = """Site Numbering: ✓ = High Priority (Green), * = Recommended (Yellow), ✗ = Caution (Red)
Example: ✓25 = High Priority Site #25 | Click any marker for full property details"""
    
    # Create folders by priority with color and symbol indicators
    folders = {
        'High Priority': kml.newfolder(name="✓ High Priority Sites (Green)"),
        'Medium Priority': kml.newfolder(name="* Recommended Sites (Yellow)"),
        'Low Priority': kml.newfolder(name="✗ Proceed with Caution (Red)")
    }
    
    sites_created = 0
    
    for idx, row in viable_df.iterrows():
        # Skip if no coordinates
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            continue
        
        sites_created += 1
        site_num = row['KML_Site_Number']
        
        # Create site number with ASCII prefix for colorblind accessibility
        priority = row.get('Priority_Classification', 'Medium Priority')
        if priority == 'High Priority':
            icon_name = f"✓{site_num}"  # Checkmark for High Priority
        elif priority == 'Medium Priority':
            icon_name = f"*{site_num}"   # Asterisk for Recommended
        else:  # Low Priority
            icon_name = f"✗{site_num}"   # X mark for Caution
        
        # Determine folder
        priority = row.get('Priority_Classification', 'Medium Priority')
        folder = folders.get(priority, folders['Medium Priority'])
        
        # Create point
        point = folder.newpoint(name=icon_name)
        point.coords = [(row['Longitude'], row['Latitude'])]
        
        # Create comprehensive description with ACTUAL data
        description = create_site_description(row, site_num)
        point.description = description
        
        # Style based on priority using Google Earth standard markers
        if priority == 'High Priority':
            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png'
            point.style.iconstyle.scale = 1.0
        elif priority == 'Medium Priority':
            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
            point.style.iconstyle.scale = 1.0
        else:  # Low Priority
            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
            point.style.iconstyle.scale = 1.0
    
    # Save KML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    kml_filename = f"DMarco_Quality_KML_{timestamp}.kml"
    kml.save(kml_filename)
    
    # Save Excel reference
    excel_filename = kml_filename.replace('.kml', '_Reference.xlsx')
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Main reference sheet
        viable_df.to_excel(writer, sheet_name='KML_Site_Reference', index=False)
        
        # Summary by source
        summary_df = viable_df.groupby('Source').agg({
            'KML_Site_Number': 'count',
            'Anchor_Score': 'mean',
            'Poverty_Rate_Pct': 'mean'
        }).round(2)
        summary_df.columns = ['Site_Count', 'Avg_Anchor_Score', 'Avg_Poverty_Rate']
        summary_df.to_excel(writer, sheet_name='Summary_By_Source')
    
    logger.info(f"✅ Created KML with {sites_created} sites")
    logger.info(f"📁 Files created:")
    logger.info(f"   • {kml_filename}")
    logger.info(f"   • {excel_filename}")
    
    return kml_filename, excel_filename

def create_site_description(row, site_num):
    """Create comprehensive site description using ACTUAL data"""
    
    # Property identification
    name = row.get('Name', '')
    if pd.isna(name) or str(name) == 'nan':
        name = f"Property #{site_num}"
    
    address = row.get('Address', 'Not specified')
    city = row.get('City', 'Unknown')
    
    # Size in acres (convert from SF if needed)
    acres = calculate_acres(row)
    
    # Price information
    sale_price = format_currency(row.get('Sale Price'))
    price_per_acre = format_currency(row.get('Price Per AC Land'))
    
    # D'Marco requested fields
    sale_status = row.get('Sale Status', 'Unknown')
    days_on_market = row.get('Days On Market', 'N/A')
    if pd.notna(days_on_market) and days_on_market != 'N/A':
        try:
            days_on_market = f"{int(days_on_market)} days"
        except:
            pass
    
    market = row.get('Market', 'Not specified')
    submarket = row.get('Submarket', '')
    if pd.notna(submarket):
        market_display = f"{market} / {submarket}"
    else:
        market_display = market
    
    zoning = row.get('Zoning', 'Not specified')
    land_improvements = row.get('Land Improvements', 'None noted')
    
    # Investment metrics
    priority = row.get('Priority_Classification', 'Unknown')
    anchor_score = row.get('Anchor_Score', 0)
    score_4pct = row.get('final_4pct_ranking', row.get('Ranking_4pct', 'N/A'))
    score_9pct = row.get('final_9pct_ranking', row.get('Ranking_9pct', 'N/A'))
    
    # Regulatory data - using ACTUAL columns
    tdhca_region = row.get('TDHCA_Region', 'Unknown')
    poverty_rate = row.get('Poverty_Rate_Pct', 'N/A')
    if pd.notna(poverty_rate) and poverty_rate != 'N/A':
        poverty_display = f"{float(poverty_rate):.1f}%"
        if float(poverty_rate) <= 20:
            poverty_display += " ✅ (9% Low Poverty Bonus)"
    else:
        poverty_display = "Not available"
    
    # QCT/DDA Status - using ACTUAL data
    qct_status = row.get('QCT_Status', 'Unknown')
    dda_status = row.get('DDA_Status', 'Unknown')
    qct_dda_display = f"QCT: {qct_status} | DDA: {dda_status}"
    
    # Flood zone - check multiple columns
    flood_zone = row.get('FEMA_Flood_Zone', row.get('CoStar_Flood_Zone', row.get('Flood Zone', 'Unknown')))
    
    # Source
    data_source = row.get('Source', 'Unknown')
    
    # Broker info
    broker_info = format_broker_info(row)
    
    # Anchor details
    anchor_details = row.get('Anchor_Details', 'Not evaluated')
    schools_count = row.get('Schools_Within_2_5mi', 0)
    if pd.isna(schools_count):
        schools_count = 0
    
    lihtc_count = row.get('LIHTC_Within_2mi', 0)
    if pd.isna(lihtc_count):
        lihtc_count = 0
    
    # Build HTML
    html = f"""
    <![CDATA[
    <div style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4;">
    
    <h2 style="color: #2c5aa0; margin-bottom: 10px;">🏢 {name}</h2>
    
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 11px;">
    
    <tr style="background-color: #f0f8ff;">
        <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
            📍 PROPERTY DETAILS
        </td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; width: 40%; background-color: #f9f9f9;">Address</td>
        <td>{address}, {city}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Coordinates</td>
        <td>{row['Latitude']:.6f}, {row['Longitude']:.6f}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Size</td>
        <td>{acres}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Sale Price</td>
        <td>{sale_price}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Price Per Acre</td>
        <td>{price_per_acre}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Sale Status</td>
        <td>{sale_status}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Days on Market</td>
        <td>{days_on_market}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Market/Submarket</td>
        <td>{market_display}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Zoning</td>
        <td>{zoning}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Land Improvements</td>
        <td>{land_improvements}</td>
    </tr>
    
    <tr style="background-color: #f0f8ff;">
        <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
            🎯 INVESTMENT ANALYSIS
        </td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Priority</td>
        <td><strong>{priority}</strong></td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Anchor Score</td>
        <td>{anchor_score:.1f} / 5.0</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">4% Credit Ranking</td>
        <td>{score_4pct}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">9% Credit Ranking</td>
        <td>{score_9pct}</td>
    </tr>
    
    <tr style="background-color: #f0f8ff;">
        <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
            🏛️ REGULATORY DATA
        </td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">TDHCA Region</td>
        <td>{tdhca_region}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Poverty Rate</td>
        <td>{poverty_display}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">QCT/DDA Status</td>
        <td>{qct_dda_display}</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">FEMA Flood Zone</td>
        <td>{flood_zone}</td>
    </tr>
    
    <tr style="background-color: #f0f8ff;">
        <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
            🏫 ANCHOR ANALYSIS
        </td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Schools (2.5 mi)</td>
        <td>{int(schools_count)} schools</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">LIHTC Projects (2 mi)</td>
        <td>{int(lihtc_count)} projects</td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Infrastructure</td>
        <td>{anchor_details}</td>
    </tr>
    
    <tr style="background-color: #f0f8ff;">
        <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
            📞 CONTACT INFO
        </td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Data Source</td>
        <td><strong>{data_source}</strong></td>
    </tr>
    
    <tr>
        <td style="font-weight: bold; background-color: #f9f9f9;">Broker Info</td>
        <td>{broker_info}</td>
    </tr>
    
    </table>
    
    <p style="margin-top: 10px; font-size: 10px; color: #666;">
        <strong>Site #{site_num}</strong> | Generated {datetime.now().strftime('%Y-%m-%d')}
    </p>
    
    <p style="margin-top: 5px; font-size: 10px; color: #999; text-align: center;">
        © Structured Consultants LLC
    </p>
    
    </div>
    ]]>
    """
    
    return html

def calculate_acres(row):
    """Calculate acres display from various possible fields"""
    # Check direct acres field
    if 'Acres' in row and pd.notna(row['Acres']):
        return f"{float(row['Acres']):.2f} acres"
    
    # Check Size (SF) field
    if 'Size (SF)' in row and pd.notna(row['Size (SF)']):
        acres = float(row['Size (SF)']) / 43560
        return f"{acres:.2f} acres"
    
    # Check Land SF fields
    if 'Land SF Gross' in row and pd.notna(row['Land SF Gross']):
        acres = float(row['Land SF Gross']) / 43560
        return f"{acres:.2f} acres"
    
    return "Size not specified"

def format_currency(value):
    """Format currency values"""
    if pd.isna(value) or value == 'Not listed':
        return "Not listed"
    try:
        return f"${float(value):,.0f}"
    except:
        return str(value)

def format_broker_info(row):
    """Format broker information"""
    parts = []
    
    company = row.get('Listing Broker Company', '')
    if pd.notna(company) and str(company).strip():
        parts.append(str(company))
    
    first = row.get('Listing Broker Agent First Name', '')
    last = row.get('Listing Broker Agent Last Name', '')
    if pd.notna(first) and pd.notna(last) and str(first).strip() and str(last).strip():
        parts.append(f"{str(first)} {str(last)}")
    
    phone = row.get('Listing Broker Phone', '')
    if pd.notna(phone) and str(phone).strip():
        parts.append(str(phone))
    
    return "<br/>".join(parts) if parts else "Not listed"

if __name__ == "__main__":
    kml_file, excel_file = create_dmarco_kml_from_good_data()
    
    print("\n🎯 D'MARCO QUALITY KML COMPLETE")
    print("=" * 60)
    print(f"📁 Files Created:")
    print(f"  🗺️  KML: {kml_file}")
    print(f"  📊 Excel: {excel_file}")
    print("\n✅ Using GOOD data with:")
    print("  • Proper source attribution (CoStar, D'Marco Brent, D'Marco Brian)")
    print("  • Actual TDHCA regions (not all Region 8)")
    print("  • Real poverty data")
    print("  • QCT/DDA status")
    print("  • Complete anchor analysis (schools, LIHTC projects)")
    print("  • All broker information")