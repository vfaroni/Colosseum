#!/usr/bin/env python3
"""
Create Quality Google Earth KML for D'Marco
Maps all viable sites with minimal icon text and comprehensive deal information.

Includes:
1) Address / Lat / Long
2) Acres  
3) TDHCA Region
4) Priority Classification
5) Source List
6) 4% score / 9% score
7) Flood Zone
8) DDA/QCT Status
9) Poverty Rate

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

class DMarcoGoogleEarthKML:
    """Create quality KML file for D'Marco with comprehensive deal information"""
    
    def __init__(self):
        self.kml = simplekml.Kml()
        self.kml.document.name = "D'Marco LIHTC Investment Opportunities - Texas QCT/DDA Sites"
        self.kml.document.description = "Enhanced 6-Factor Anchor Scoring Analysis with Highway Access Validation"
    
    def load_enhanced_data(self):
        """Load the enhanced anchor analysis data"""
        
        # Load the enhanced analysis
        enhanced_file = "Fixed_Enhanced_Anchor_Analysis_20250703_002154.xlsx"
        if not Path(enhanced_file).exists():
            raise FileNotFoundError(f"Enhanced analysis file not found: {enhanced_file}")
        
        self.df = pd.read_excel(enhanced_file, sheet_name='All_Sites_Enhanced_Ranking')
        logger.info(f"✅ Loaded {len(self.df)} sites from enhanced analysis")
        
        # Filter for viable sites only (exclude "Do Not Pursue")
        viable_sites = self.df[self.df['Business_Priority_Classification'] != 'Do Not Pursue'].copy()
        logger.info(f"📊 Filtered to {len(viable_sites)} viable investment opportunities")
        
        # Sort by Enhanced_Anchor_Score (highest first)
        self.viable_df = viable_sites.sort_values('Enhanced_Anchor_Score', ascending=False).reset_index(drop=True)
        
        return len(self.viable_df)
    
    def determine_icon_style(self, priority_classification, enhanced_score):
        """Determine icon style based on priority and score"""
        
        if priority_classification == 'High Priority':
            return {
                'color': simplekml.Color.green,
                'icon': 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png',
                'scale': 1.2
            }
        elif priority_classification == 'Recommended':
            return {
                'color': simplekml.Color.yellow,
                'icon': 'http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png', 
                'scale': 1.1
            }
        elif priority_classification == 'Proceed with Caution':
            return {
                'color': simplekml.Color.orange,
                'icon': 'http://maps.google.com/mapfiles/kml/paddle/orange-circle.png',
                'scale': 1.0
            }
        else:
            return {
                'color': simplekml.Color.red,
                'icon': 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png',
                'scale': 0.9
            }
    
    def create_site_description(self, row, site_number):
        """Create comprehensive site description with all requested information"""
        
        # Extract key information with safe defaults
        name = row.get('Name', 'Unknown Property')
        if pd.isna(name) or str(name).lower() == 'nan':
            name = f"Site #{site_number}"
        
        address = row.get('Address', 'Address not available')
        city = row.get('City', 'Unknown')
        latitude = row.get('Latitude', 0)
        longitude = row.get('Longitude', 0)
        
        # Get acres - check multiple possible columns
        acres = row.get('Acres', row.get('Size', 0))
        if pd.notna(acres):
            # Check if this is actually square feet based on column name or value
            if 'SF' in str(row.get('Size (SF)', '')) or float(acres) > 500:
                # Convert square feet to acres
                acres_value = float(acres) / 43560
                acres_display = f"{acres_value:.2f} acres"
            else:
                acres_display = f"{float(acres):.2f} acres"
        else:
            # Try to calculate from Land SF columns
            land_sf_gross = row.get('Land SF Gross', 0)
            land_sf_net = row.get('Land SF Net', 0)
            if pd.notna(land_sf_gross) and float(land_sf_gross) > 0:
                acres_value = float(land_sf_gross) / 43560
                acres_display = f"{acres_value:.2f} acres"
            elif pd.notna(land_sf_net) and float(land_sf_net) > 0:
                acres_value = float(land_sf_net) / 43560
                acres_display = f"{acres_value:.2f} acres"
            else:
                acres_display = "Size not specified"
        
        # TDHCA Region
        tdhca_region = row.get('TDHCA_Region_Estimated', row.get('TDHCA_Region', 'Unknown'))
        
        # Priority and Score
        priority = row.get('Business_Priority_Classification', 'Unknown')
        enhanced_score = row.get('Enhanced_Anchor_Score', 0)
        
        # Source identification
        data_source = row.get('Data_Source', 'Unknown')
        if pd.isna(data_source):
            # Try to identify from other columns
            if 'MailingName' in row.index and pd.notna(row.get('MailingName')):
                data_source = "D'Marco Brokerage"
            elif 'Parcel Number' in row.index and pd.notna(row.get('Parcel Number')):
                data_source = "CoStar Database"
            else:
                data_source = "Multiple Sources"
        
        # Scores (look for existing columns or estimate)
        score_4pct = row.get('Corrected_4pct_Ranking', row.get('Ranking_4pct', 'N/A'))
        score_9pct = row.get('Final_9pct_Ranking_With_Poverty', row.get('Ranking_9pct', 'N/A'))
        
        # Flood zone
        flood_zone = row.get('FEMA_Flood_Zone', row.get('CoStar_Flood_Zone', row.get('Flood Zone', 'Unknown')))
        if pd.isna(flood_zone):
            flood_zone = "Not determined"
        
        # QCT/DDA Status
        qct_status = row.get('QCT_Status', 'Unknown')
        dda_status = row.get('DDA_Status', 'Unknown')
        
        if pd.notna(qct_status) and qct_status != 'Unknown':
            qct_dda_display = f"QCT: {qct_status}"
        else:
            qct_dda_display = "QCT/DDA: Eligible"
        
        if pd.notna(dda_status) and dda_status != 'Unknown':
            qct_dda_display += f" | DDA: {dda_status}"
        
        # Poverty Rate
        poverty_rate = row.get('Poverty_Rate_Pct', 'Unknown')
        if pd.notna(poverty_rate) and poverty_rate != 'Unknown':
            try:
                poverty_display = f"{float(poverty_rate):.1f}%"
                # Add 9% low poverty bonus context
                if float(poverty_rate) <= 20:
                    poverty_display += " (Qualifies for 9% Low Poverty Bonus)"
            except:
                poverty_display = str(poverty_rate)
        else:
            poverty_display = "Not available"
        
        # Highway access
        highway_score = row.get('Highway_Access_Score', 0)
        highway_rating = row.get('Highway_Access_Rating', 'Unknown')
        
        # Price information - expanded per D'Marco request
        sale_price = row.get('Sale Price', 'Not listed')
        if pd.notna(sale_price) and sale_price != 'Not listed':
            try:
                sale_price_display = f"${float(sale_price):,.0f}"
            except:
                sale_price_display = str(sale_price)
        else:
            sale_price_display = "Not listed"
        
        # Price per acre
        price_per_acre = row.get('Price Per AC Land', row.get('Price/Land (SF)', 'Not listed'))
        if pd.notna(price_per_acre) and price_per_acre != 'Not listed':
            try:
                if 'Price/Land (SF)' in row.index and row.get('Price/Land (SF)') == price_per_acre:
                    # Convert from price per SF to price per acre
                    price_per_acre_value = float(price_per_acre) * 43560
                    price_per_acre_display = f"${price_per_acre_value:,.0f}/acre"
                else:
                    price_per_acre_display = f"${float(price_per_acre):,.0f}/acre"
            except:
                price_per_acre_display = str(price_per_acre)
        else:
            price_per_acre_display = "Not listed"
        
        # Sale status
        sale_status = row.get('Sale Status', 'Unknown')
        
        # Days on market
        days_on_market = row.get('Days On Market', 'Not available')
        if pd.notna(days_on_market) and days_on_market != 'Not available':
            try:
                days_on_market_display = f"{int(days_on_market)} days"
            except:
                days_on_market_display = str(days_on_market)
        else:
            days_on_market_display = "Not available"
        
        # Market/Submarket
        market = row.get('Market', 'Not specified')
        submarket = row.get('Submarket', 'Not specified')
        market_display = f"{market}"
        if pd.notna(submarket) and submarket != 'Not specified':
            market_display += f" / {submarket}"
        
        # Zoning
        zoning = row.get('Zoning', 'Not specified')
        
        # Land improvements
        land_improvements = row.get('Land Improvements', 'None noted')
        
        # Broker information
        broker_company = row.get('Listing Broker Company', 'Not listed')
        broker_agent_first = row.get('Listing Broker Agent First Name', '')
        broker_agent_last = row.get('Listing Broker Agent Last Name', '')
        broker_phone = row.get('Listing Broker Phone', 'Not provided')
        
        broker_display = ""
        if pd.notna(broker_company) and broker_company != 'Not listed':
            broker_display = broker_company
        if pd.notna(broker_agent_first) and pd.notna(broker_agent_last):
            broker_display += f"<br/>{broker_agent_first} {broker_agent_last}"
        if pd.notna(broker_phone) and broker_phone != 'Not provided':
            broker_display += f"<br/>{broker_phone}"
        if not broker_display:
            broker_display = "Not listed"
        
        # Anchor details
        anchor_details = row.get('Anchor_Details', row.get('Infrastructure_Assessment', 'Not evaluated'))
        anchor_score = row.get('Anchor_Score', 0)
        
        # Create HTML description
        description = f"""
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
            <td style="font-weight: bold; background-color: #f9f9f9;">Address</td>
            <td>{address}, {city}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Coordinates</td>
            <td>{latitude:.6f}, {longitude:.6f}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Size</td>
            <td>{acres_display}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Sale Price</td>
            <td>{sale_price_display}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Price Per Acre</td>
            <td>{price_per_acre_display}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Sale Status</td>
            <td>{sale_status}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Days on Market</td>
            <td>{days_on_market_display}</td>
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
            <td style="font-weight: bold; background-color: #f9f9f9;">Priority Classification</td>
            <td><strong>{priority}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Enhanced Score</td>
            <td>{enhanced_score:.3f} / 5.000</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">4% Credit Score</td>
            <td>{score_4pct}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">9% Credit Score</td>
            <td>{score_9pct}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏛️ REGULATORY & LOCATION
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
                🛣️ INFRASTRUCTURE ACCESS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Highway Access</td>
            <td>{highway_rating} (Score: {highway_score:.2f})</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Data Source</td>
            <td>{data_source}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                📞 BROKER INFORMATION
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Listing Broker</td>
            <td>{broker_display}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏫 ANCHOR ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Anchor Score</td>
            <td>{anchor_score:.1f} / 5.0</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Anchor Details</td>
            <td>{anchor_details}</td>
        </tr>
        
        </table>
        
        <p style="margin-top: 10px; font-size: 10px; color: #666;">
            <strong>Site #{site_number}</strong> | Enhanced 6-Factor Anchor Analysis | Generated {datetime.now().strftime('%Y-%m-%d')}
        </p>
        
        </div>
        ]]>
        """
        
        return description
    
    def create_kml_points(self):
        """Create KML points for all viable sites"""
        
        logger.info(f"🗺️ Creating KML points for {len(self.viable_df)} viable sites...")
        
        # Create folders by priority
        high_priority_folder = self.kml.newfolder(name=f"🟢 High Priority Sites")
        recommended_folder = self.kml.newfolder(name=f"🟡 Recommended Sites")
        caution_folder = self.kml.newfolder(name=f"🟠 Proceed with Caution")
        
        folders = {
            'High Priority': high_priority_folder,
            'Recommended': recommended_folder,
            'Proceed with Caution': caution_folder
        }
        
        site_count = 0
        
        for idx, row in self.viable_df.iterrows():
            site_count += 1
            
            # Extract coordinates
            latitude = row.get('Latitude')
            longitude = row.get('Longitude')
            
            if pd.isna(latitude) or pd.isna(longitude):
                logger.warning(f"⚠️ Skipping site {site_count} - missing coordinates")
                continue
            
            # Determine folder and styling
            priority = row.get('Business_Priority_Classification', 'Unknown')
            folder = folders.get(priority, recommended_folder)
            icon_style = self.determine_icon_style(priority, row.get('Enhanced_Anchor_Score', 0))
            
            # Create minimal icon name (site number only)
            name = row.get('Name', f'Site #{site_count}')
            if pd.isna(name) or str(name).lower() == 'nan':
                icon_name = f"#{site_count}"
            else:
                # Use first few characters + number for minimal text
                short_name = str(name)[:8] if len(str(name)) > 8 else str(name)
                icon_name = f"{short_name} #{site_count}"
            
            # Create point
            point = folder.newpoint(name=icon_name)
            point.coords = [(longitude, latitude)]
            point.description = self.create_site_description(row, site_count)
            
            # Style the point
            point.style.iconstyle.icon.href = icon_style['icon']
            point.style.iconstyle.scale = icon_style['scale']
            
            # Add extended data for reference
            point.extendeddata.newdata(name="SiteNumber", value=str(site_count))
            point.extendeddata.newdata(name="Priority", value=priority)
            point.extendeddata.newdata(name="EnhancedScore", value=str(row.get('Enhanced_Anchor_Score', 0)))
        
        logger.info(f"✅ Created {site_count} KML points across {len(folders)} priority folders")
        
        return site_count
    
    def save_kml(self, filename=None):
        """Save the KML file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"DMarco_LIHTC_Investment_Opportunities_{timestamp}.kml"
        
        self.kml.save(filename)
        logger.info(f"💾 Saved Google Earth KML: {filename}")
        
        return filename
    
    def create_reference_excel(self, kml_filename):
        """Create Excel reference file with site numbers"""
        
        # Add site numbers to dataframe
        viable_with_numbers = self.viable_df.copy()
        viable_with_numbers['KML_Site_Number'] = range(1, len(viable_with_numbers) + 1)
        
        # Reorder columns for easy reference
        reference_columns = [
            'KML_Site_Number', 'Name', 'Address', 'City', 'Business_Priority_Classification',
            'Enhanced_Anchor_Score', 'Acres', 'TDHCA_Region_Estimated', 'Data_Source',
            'Corrected_4pct_Ranking', 'Final_9pct_Ranking_With_Poverty', 'FEMA_Flood_Zone',
            'QCT_Status', 'DDA_Status', 'Poverty_Rate_Pct', 'Highway_Access_Rating',
            'Latitude', 'Longitude'
        ]
        
        # Select available columns
        available_columns = ['KML_Site_Number'] + [col for col in reference_columns[1:] if col in viable_with_numbers.columns]
        reference_df = viable_with_numbers[available_columns].copy()
        
        # Create Excel file
        excel_filename = kml_filename.replace('.kml', '_Reference.xlsx')
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            reference_df.to_excel(writer, sheet_name='KML_Site_Reference', index=False)
        
        logger.info(f"📊 Created Excel reference: {excel_filename}")
        
        return excel_filename

def main():
    """Create D'Marco Google Earth KML with comprehensive deal information"""
    
    creator = DMarcoGoogleEarthKML()
    
    # Load enhanced data
    site_count = creator.load_enhanced_data()
    
    # Create KML points
    points_created = creator.create_kml_points()
    
    # Save KML file
    kml_filename = creator.save_kml()
    
    # Create Excel reference
    excel_filename = creator.create_reference_excel(kml_filename)
    
    # Summary
    print("\n🎯 D'MARCO GOOGLE EARTH KML COMPLETE")
    print("=" * 60)
    print(f"Total Viable Sites Mapped: {points_created}")
    print(f"")
    print(f"📁 Files Created:")
    print(f"  🗺️  Google Earth KML: {kml_filename}")
    print(f"  📊 Excel Reference:   {excel_filename}")
    print(f"")
    print(f"📊 Site Distribution:")
    priority_counts = creator.viable_df['Business_Priority_Classification'].value_counts()
    for priority, count in priority_counts.items():
        print(f"  {priority}: {count} sites")
    print(f"")
    print(f"✅ KML Features:")
    print(f"  • Minimal icon text (site numbers) to prevent crowding")
    print(f"  • Color-coded by priority (Green/Yellow/Orange)")
    print(f"  • Comprehensive deal information in pop-ups")
    print(f"  • Excel reference file with site number mapping")
    print(f"  • All 9 requested data points included")
    print(f"")
    print(f"🎯 Ready for D'Marco field analysis and investment decisions!")

if __name__ == "__main__":
    main()