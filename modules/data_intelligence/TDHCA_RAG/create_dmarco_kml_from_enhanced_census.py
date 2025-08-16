#!/usr/bin/env python3
"""
🗺️ CREATE D'MARCO KML FROM ENHANCED CENSUS ANALYSIS
Generate Google Earth KML for D'Marco using the latest enhanced analysis with Census counties

FEATURES:
✅ Uses enhanced Census analysis with TDHCA regions
✅ Color-coded by ranking tiers (TIER_1_EXCELLENT to TIER_5_FLOOD_RISK)
✅ Comprehensive site descriptions with all analysis data
✅ Professional Google Earth ready format
✅ County and TDHCA region information included
"""

import pandas as pd
import simplekml
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DMarcoKMLFromEnhancedCensus:
    """Create D'Marco KML from enhanced Census analysis"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.results_dir = self.base_dir / "D'Marco_Sites" / "Analysis_Results"
        
        # The enhanced Census analysis file
        self.enhanced_file = self.results_dir / "ENHANCED_CENSUS_ANALYSIS_20250801_235158.xlsx"
    
    def load_enhanced_data(self):
        """Load enhanced Census analysis data"""
        if not self.enhanced_file.exists():
            logger.error(f"❌ Enhanced file not found: {self.enhanced_file}")
            return pd.DataFrame()
        
        try:
            # Load the main analysis sheet
            df = pd.read_excel(self.enhanced_file, sheet_name='Ultimate_Client_Ready_Analysis')
            logger.info(f"✅ Loaded {len(df)} sites from enhanced Census analysis")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading enhanced file: {e}")
            return pd.DataFrame()
    
    def create_dmarco_kml(self):
        """Create comprehensive KML for D'Marco with enhanced data"""
        logger.info("🚀 CREATING D'MARCO KML FROM ENHANCED CENSUS ANALYSIS")
        
        # Load data
        df = self.load_enhanced_data()
        if df.empty:
            return None, None
        
        # Create KML
        kml = simplekml.Kml()
        kml.document.name = f"D'Marco Texas LIHTC Analysis - {len(df)} Sites with Census Counties & TDHCA Regions"
        kml.document.description = """Texas LIHTC Development Opportunities - Enhanced Analysis with Official County Data
        
Site Classification: 
🥇 = TIER 1 EXCELLENT (400+ units) | 🥈 = TIER 2 STRONG (300+ units) | 🥉 = TIER 3 VIABLE (240+ units)
⚠️ = TIER 4 UNDERSIZED (<240 units) | 🌊 = TIER 5 FLOOD RISK

Click any marker for complete analysis including:
• TDHCA Region and County information
• Unit capacity and development potential  
• QCT/DDA status and basis boost eligibility
• FEMA flood zone analysis
• HUD AMI data and rent limits
• Ranking tier and investment recommendation
"""
        
        # Create folders by ranking tier
        folders = {
            'TIER_1_EXCELLENT': kml.newfolder(name="🥇 TIER 1: EXCELLENT Sites (400+ units) - Green"),
            'TIER_2_STRONG': kml.newfolder(name="🥈 TIER 2: STRONG Sites (300+ units) - Blue"),
            'TIER_3_VIABLE': kml.newfolder(name="🥉 TIER 3: VIABLE Sites (240+ units) - Yellow"),
            'TIER_4_UNDERSIZED': kml.newfolder(name="⚠️ TIER 4: UNDERSIZED Sites (<240 units) - Orange"),
            'TIER_5_FLOOD_RISK': kml.newfolder(name="🌊 TIER 5: FLOOD RISK Sites - Red")
        }
        
        sites_created = 0
        
        for idx, row in df.iterrows():
            # Get coordinates
            lat = row.get('Latitude')
            lng = row.get('Longitude')
            
            if pd.isna(lat) or pd.isna(lng):
                continue
            
            try:
                sites_created += 1
                
                # Get ranking tier
                tier = row.get('Ranking_Tier', 'TIER_3_VIABLE')
                rank = row.get('Final_LIHTC_Rank', sites_created)
                
                # Create site identifier with appropriate symbol
                if tier == 'TIER_1_EXCELLENT':
                    icon_symbol = f"🥇{rank}"
                    folder = folders['TIER_1_EXCELLENT']
                    icon_color = 'grn'
                elif tier == 'TIER_2_STRONG':
                    icon_symbol = f"🥈{rank}"
                    folder = folders['TIER_2_STRONG']
                    icon_color = 'blu'
                elif tier == 'TIER_3_VIABLE':
                    icon_symbol = f"🥉{rank}"
                    folder = folders['TIER_3_VIABLE']
                    icon_color = 'ylw'
                elif tier == 'TIER_4_UNDERSIZED':
                    icon_symbol = f"⚠️{rank}"
                    folder = folders['TIER_4_UNDERSIZED']
                    icon_color = 'orange'
                else:  # TIER_5_FLOOD_RISK
                    icon_symbol = f"🌊{rank}"
                    folder = folders['TIER_5_FLOOD_RISK']
                    icon_color = 'red'
                
                # Create point
                point = folder.newpoint(name=icon_symbol)
                point.coords = [(lng, lat)]
                
                # Create comprehensive description
                description = self.create_site_description(row, rank)
                point.description = description
                
                # Set icon style
                point.style.iconstyle.icon.href = f'http://maps.google.com/mapfiles/kml/pushpin/{icon_color}-pushpin.png'
                point.style.iconstyle.scale = 1.3 if tier in ['TIER_1_EXCELLENT', 'TIER_2_STRONG'] else 1.0
                
            except Exception as e:
                logger.error(f"❌ Error creating point for site {rank}: {e}")
                continue
        
        # Save KML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        kml_filename = self.results_dir / f"DMarco_Enhanced_Census_Analysis_{timestamp}.kml"
        kml.save(str(kml_filename))
        
        # Save Excel reference
        excel_reference = kml_filename.parent / f"{kml_filename.stem}_Reference.xlsx"
        with pd.ExcelWriter(excel_reference, engine='openpyxl') as writer:
            # KML reference with site numbers
            df_export = df[['Final_LIHTC_Rank', 'Ranking_Tier', 'Address', 'City', 'County', 'TDHCA_Region', 
                           'Unit_Capacity', 'QCT_DDA_Status', 'Basis_Boost_Eligible', 'FEMA_Flood_Zone']].copy()
            df_export.to_excel(writer, sheet_name='KML_Site_Reference', index=False)
            
            # Summary by tier
            tier_summary = df.groupby('Ranking_Tier').agg({
                'Final_LIHTC_Rank': 'count',
                'Unit_Capacity': 'mean',
                'Ranking_Score': 'mean'
            }).round(1)
            tier_summary.columns = ['Site_Count', 'Avg_Unit_Capacity', 'Avg_Ranking_Score']
            tier_summary.to_excel(writer, sheet_name='Tier_Summary')
            
            # TDHCA Region summary
            region_summary = df.groupby('TDHCA_Region').agg({
                'Final_LIHTC_Rank': 'count',
                'Unit_Capacity': 'mean'
            }).round(1)
            region_summary.columns = ['Site_Count', 'Avg_Unit_Capacity']
            region_summary.to_excel(writer, sheet_name='TDHCA_Region_Summary')
        
        logger.info(f"✅ Created D'Marco KML with {sites_created} sites")
        logger.info(f"📁 Files created:")
        logger.info(f"   🗺️  KML: {kml_filename.name}")
        logger.info(f"   📊 Excel Reference: {excel_reference.name}")
        
        return kml_filename, excel_reference
    
    def create_site_description(self, row, rank):
        """Create comprehensive site description with enhanced Census data"""
        
        # Basic property info
        address = row.get('Address', 'Address not specified')
        city = row.get('City', 'Unknown City')
        county = row.get('County', 'Unknown County')  # From Census API
        tdhca_region = row.get('TDHCA_Region', 'Unknown Region')
        acres = row.get('Acres_Calculated', 0)
        
        # Ranking and capacity
        tier = row.get('Ranking_Tier', 'Unknown')
        ranking_score = row.get('Ranking_Score', 0)
        unit_capacity = row.get('Unit_Capacity', 0)
        
        # LIHTC analysis
        qct_dda_status = row.get('QCT_DDA_Status', 'Unknown')
        basis_boost = row.get('Basis_Boost_Eligible', 'Unknown')
        flood_zone = row.get('FEMA_Flood_Zone', 'Unknown')
        
        # AMI data
        ami_area = row.get('HUD_Area_Name', 'Unknown AMI Area')
        ami_1br = row.get('AMI_60_1BR', 0)
        ami_2br = row.get('AMI_60_2BR', 0)
        
        # Pricing
        list_price = row.get('List Price', 0)
        price_per_acre = row.get('Price Per Acre', 0)
        
        # Format pricing
        price_formatted = f"${list_price:,.0f}" if list_price > 0 else "Not listed"
        ppa_formatted = f"${price_per_acre:,.0f}" if price_per_acre > 0 else "Not calculated"
        
        # Tier color coding
        tier_colors = {
            'TIER_1_EXCELLENT': '#00aa00',  # Green
            'TIER_2_STRONG': '#0066cc',     # Blue
            'TIER_3_VIABLE': '#ffaa00',     # Yellow
            'TIER_4_UNDERSIZED': '#ff6600', # Orange
            'TIER_5_FLOOD_RISK': '#cc0000'  # Red
        }
        tier_color = tier_colors.get(tier, '#666666')
        
        # Build comprehensive HTML
        html = f"""
        <![CDATA[
        <div style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4;">
        
        <h2 style="color: #2c5aa0; margin-bottom: 10px;">🏢 D'Marco Site #{rank}</h2>
        
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 11px;">
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                📍 PROPERTY LOCATION
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; width: 40%; background-color: #f9f9f9;">Address</td>
            <td>{address}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">City</td>
            <td>{city}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">County</td>
            <td><strong>{county}</strong> (Census API verified)</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">TDHCA Region</td>
            <td><strong>{tdhca_region}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Acreage</td>
            <td>{acres:.2f} acres</td>
        </tr>
        
        <tr style="background-color: {tier_color}; color: white;">
            <td colspan="2" style="text-align: center; font-weight: bold;">
                🏆 INVESTMENT RANKING
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Overall Rank</td>
            <td><strong>#{rank}</strong> of {len(row)} sites</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Investment Tier</td>
            <td><strong style="color: {tier_color};">{tier.replace('_', ' ')}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Ranking Score</td>
            <td>{ranking_score:.1f} points</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Unit Capacity</td>
            <td><strong>{unit_capacity:.0f} units</strong> (17 units/acre)</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏛️ LIHTC QUALIFICATION
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">QCT/DDA Status</td>
            <td><strong>{qct_dda_status}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">130% Basis Boost</td>
            <td><strong>{basis_boost}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">FEMA Flood Zone</td>
            <td>{flood_zone}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">HUD AMI Area</td>
            <td>{ami_area}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">60% AMI Rents</td>
            <td>1BR: ${ami_1br:,.0f} | 2BR: ${ami_2br:,.0f}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                💰 FINANCIAL SUMMARY
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">List Price</td>
            <td>{price_formatted}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Price Per Acre</td>
            <td>{ppa_formatted}</td>
        </tr>
        
        </table>
        
        <p style="margin-top: 10px; font-size: 10px; color: #666;">
            <strong>Site #{rank}</strong> | Enhanced Census Analysis | {datetime.now().strftime('%Y-%m-%d')}
        </p>
        
        <p style="margin-top: 5px; font-size: 10px; color: #999; text-align: center;">
            © Structured Consultants LLC - Texas LIHTC Analysis with Official County Data
        </p>
        
        </div>
        ]]>
        """
        
        return html

if __name__ == "__main__":
    kml_generator = DMarcoKMLFromEnhancedCensus()
    kml_file, excel_file = kml_generator.create_dmarco_kml()
    
    if kml_file:
        print("\\n🎯 D'MARCO KML FROM ENHANCED CENSUS ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"📁 Files Created:")
        print(f"  🗺️  KML: {kml_file.name}")
        print(f"  📊 Excel Reference: {excel_file.name}")
        print("\\n✅ KML Features:")
        print("  🥇 Green markers: TIER 1 EXCELLENT (400+ units)")
        print("  🥈 Blue markers: TIER 2 STRONG (300+ units)")
        print("  🥉 Yellow markers: TIER 3 VIABLE (240+ units)")
        print("  ⚠️ Orange markers: TIER 4 UNDERSIZED (<240 units)")
        print("  🌊 Red markers: TIER 5 FLOOD RISK")
        print("\\n📊 Enhanced Data Included:")
        print("  • Official Census API county verification")
        print("  • TDHCA region mapping (13 regions)")
        print("  • Investment tier ranking with unit capacity")
        print("  • Complete LIHTC qualification analysis")
        print("  • HUD AMI data and rent limits")
        print("  • Financial summary with pricing")
        print("\\n🚀 Ready to send to D'Marco!")
    else:
        print("❌ Failed to create KML - check enhanced file availability")