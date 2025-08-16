#!/usr/bin/env python3
"""
🗺️ ENHANCED D'MARCO KML WITH FULL DATA
Generate comprehensive Google Earth KML with all analysis data

ENHANCED FEATURES:
✅ Complete 60% AMI rent schedule (1BR-4BR)
✅ School count and access scoring
✅ Competition project analysis
✅ County and TDHCA region information
✅ Investment tier color coding
✅ Comprehensive site descriptions
"""

import pandas as pd
import simplekml
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDMarcoKMLWithFullData:
    """Create comprehensive D'Marco KML with all enhanced data"""
    
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
    
    def create_comprehensive_dmarco_kml(self):
        """Create comprehensive KML for D'Marco with all enhanced data"""
        logger.info("🚀 CREATING COMPREHENSIVE D'MARCO KML WITH FULL DATA")
        
        # Load data
        df = self.load_enhanced_data()
        if df.empty:
            return None, None
        
        # Create KML
        kml = simplekml.Kml()
        kml.document.name = f"D'Marco Texas LIHTC Analysis - {len(df)} Sites - Comprehensive Data"
        kml.document.description = """Texas LIHTC Development Opportunities - Complete Analysis with Enhanced Data
        
Site Classification: 
🥇 = TIER 1 EXCELLENT (400+ units) | 🥈 = TIER 2 STRONG (300+ units) | 🥉 = TIER 3 VIABLE (240+ units)
⚠️ = TIER 4 UNDERSIZED (<240 units) | 🌊 = TIER 5 FLOOD RISK

Each marker includes:
• Complete 60% AMI rent schedule (1BR-4BR)
• School counts and access scoring
• Competition analysis and project counts
• Official county and TDHCA region data
• Investment tier ranking and unit capacity
• LIHTC qualification and basis boost status
• Financial summary and pricing analysis
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
                
                # Create comprehensive description with all data
                description = self.create_comprehensive_site_description(row, rank)
                point.description = description
                
                # Set icon style
                point.style.iconstyle.icon.href = f'http://maps.google.com/mapfiles/kml/pushpin/{icon_color}-pushpin.png'
                point.style.iconstyle.scale = 1.3 if tier in ['TIER_1_EXCELLENT', 'TIER_2_STRONG'] else 1.0
                
            except Exception as e:
                logger.error(f"❌ Error creating point for site {rank}: {e}")
                continue
        
        # Save KML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        kml_filename = self.results_dir / f"DMarco_COMPREHENSIVE_Analysis_{timestamp}.kml"
        kml.save(str(kml_filename))
        
        # Save Excel reference with comprehensive data
        excel_reference = kml_filename.parent / f"{kml_filename.stem}_Reference.xlsx"
        with pd.ExcelWriter(excel_reference, engine='openpyxl') as writer:
            # Comprehensive site reference
            df_export = df[['Final_LIHTC_Rank', 'Ranking_Tier', 'Address', 'City', 'County', 'TDHCA_Region', 
                           'Unit_Capacity', 'QCT_DDA_Status', 'Basis_Boost_Eligible', 'FEMA_Flood_Zone',
                           'AMI_60_1BR', 'AMI_60_2BR', 'AMI_60_3BR', 'AMI_60_4BR', 
                           'Schools_Within_1_Mile', 'Schools_Within_2_Miles', 'School_Access_Score']].copy()
            df_export.to_excel(writer, sheet_name='Comprehensive_Reference', index=False)
            
            # Summary by tier
            tier_summary = df.groupby('Ranking_Tier').agg({
                'Final_LIHTC_Rank': 'count',
                'Unit_Capacity': 'mean',
                'Ranking_Score': 'mean',
                'AMI_60_2BR': 'mean',
                'Schools_Within_1_Mile': 'mean'
            }).round(1)
            tier_summary.columns = ['Site_Count', 'Avg_Unit_Capacity', 'Avg_Ranking_Score', 'Avg_2BR_Rent', 'Avg_Schools_1Mi']
            tier_summary.to_excel(writer, sheet_name='Tier_Summary')
            
            # TDHCA Region summary
            region_summary = df.groupby('TDHCA_Region').agg({
                'Final_LIHTC_Rank': 'count',
                'Unit_Capacity': 'mean',
                'AMI_60_2BR': 'mean'
            }).round(1)
            region_summary.columns = ['Site_Count', 'Avg_Unit_Capacity', 'Avg_2BR_Rent']
            region_summary.to_excel(writer, sheet_name='TDHCA_Region_Summary')
        
        logger.info(f"✅ Created comprehensive D'Marco KML with {sites_created} sites")
        logger.info(f"📁 Files created:")
        logger.info(f"   🗺️  KML: {kml_filename.name}")
        logger.info(f"   📊 Excel Reference: {excel_reference.name}")
        
        return kml_filename, excel_reference
    
    def create_comprehensive_site_description(self, row, rank):
        """Create comprehensive site description with all enhanced data"""
        
        # Basic property info
        address = row.get('Address', 'Address not specified')
        city = row.get('City', 'Unknown City')
        county = row.get('County', 'Unknown County')
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
        
        # Complete AMI rent data (1BR-4BR)
        ami_area = row.get('HUD_Area_Name', 'Unknown AMI Area')
        ami_1br = row.get('AMI_60_1BR', 0)
        ami_2br = row.get('AMI_60_2BR', 0)
        ami_3br = row.get('AMI_60_3BR', 0)
        ami_4br = row.get('AMI_60_4BR', 0)
        ami_100pct = row.get('4_Person_AMI_100pct', 0)
        
        # School information
        schools_1mi = row.get('Schools_Within_1_Mile', 0)
        schools_2mi = row.get('Schools_Within_2_Miles', 0)
        school_score = row.get('School_Access_Score', 0)
        
        # Competition data (check for various column names)
        competing_1mi = row.get('Competing_Projects_1_Mile', row.get('competing_projects_1_mile', 0))
        competing_2mi = row.get('Competing_Projects_2_Mile', row.get('competing_projects_2_mile', 0))
        
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
        
        # Build comprehensive HTML with all data
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
            <td><strong>#{rank}</strong> of 155 sites</td>
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
            <td style="font-weight: bold; background-color: #f9f9f9;">100% AMI (4-person)</td>
            <td>${ami_100pct:,.0f}</td>
        </tr>
        
        <tr style="background-color: #e8f5e8;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                💰 60% AMI RENT SCHEDULE
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">1 Bedroom</td>
            <td><strong>${ami_1br:,.0f}/month</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">2 Bedroom</td>
            <td><strong>${ami_2br:,.0f}/month</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">3 Bedroom</td>
            <td><strong>${ami_3br:,.0f}/month</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">4 Bedroom</td>
            <td><strong>${ami_4br:,.0f}/month</strong></td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏫 SCHOOL ACCESS ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Schools (1 mile)</td>
            <td><strong>{schools_1mi:.0f} schools</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Schools (2 miles)</td>
            <td><strong>{schools_2mi:.0f} schools</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">School Access Score</td>
            <td>{school_score:.1f}/100</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏆 COMPETITION ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Competing Projects (1 mi)</td>
            <td>{competing_1mi:.0f} projects</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Competing Projects (2 mi)</td>
            <td>{competing_2mi:.0f} projects</td>
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
            <strong>Site #{rank}</strong> | Comprehensive Analysis | {datetime.now().strftime('%Y-%m-%d')}
        </p>
        
        <p style="margin-top: 5px; font-size: 10px; color: #999; text-align: center;">
            © Structured Consultants LLC - Complete Texas LIHTC Analysis
        </p>
        
        </div>
        ]]>
        """
        
        return html

if __name__ == "__main__":
    kml_generator = EnhancedDMarcoKMLWithFullData()
    kml_file, excel_file = kml_generator.create_comprehensive_dmarco_kml()
    
    if kml_file:
        print("\\n🎯 COMPREHENSIVE D'MARCO KML WITH FULL DATA COMPLETE")
        print("=" * 70)
        print(f"📁 Files Created:")
        print(f"  🗺️  KML: {kml_file.name}")
        print(f"  📊 Excel Reference: {excel_file.name}")
        print("\\n✅ Enhanced KML Features:")
        print("  🏠 Complete 60% AMI rent schedule (1BR-4BR)")
        print("  🏫 School counts and access scoring")
        print("  🏆 Competition project analysis")
        print("  🗺️ Official county and TDHCA region data")
        print("  💰 Investment tier ranking and financial summary")
        print("  🏛️ Complete LIHTC qualification analysis")
        print("\\n📊 Investment Tier Color Coding:")
        print("  🥇 Green: TIER 1 EXCELLENT (400+ units)")
        print("  🥈 Blue: TIER 2 STRONG (300+ units)")
        print("  🥉 Yellow: TIER 3 VIABLE (240+ units)")
        print("  ⚠️ Orange: TIER 4 UNDERSIZED (<240 units)")
        print("  🌊 Red: TIER 5 FLOOD RISK")
        print("\\n🚀 Complete analysis ready for D'Marco!")
    else:
        print("❌ Failed to create comprehensive KML")