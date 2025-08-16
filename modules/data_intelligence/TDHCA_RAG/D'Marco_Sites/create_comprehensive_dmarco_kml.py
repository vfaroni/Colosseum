#!/usr/bin/env python3
"""
🗺️ Create D'Marco Comprehensive Google Earth KML
WINGMAN Agent - Complete Analysis with Corrected Environmental Data

KML FEATURES:
- Color-coded by overall site ranking (Green/Yellow/Red)
- Environmental risk indicators (CRITICAL vapor intrusion flagged)
- Complete LIHTC analysis data (competition, flood, cost, schools)
- Professional Google Earth ready format

Based on: create_dmarco_kml_from_good_data.py template
"""

import pandas as pd
import simplekml
from pathlib import Path
import logging
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDMarcoKML:
    """Create comprehensive KML from final integrated analysis"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Find latest comprehensive Excel file
        excel_files = list(self.base_dir.glob("DMarco_FINAL_COMPREHENSIVE_Analysis_CORRECTED_*.xlsx"))
        if excel_files:
            self.excel_file = max(excel_files, key=lambda x: x.stat().st_mtime)
        else:
            self.excel_file = None
    
    def load_comprehensive_data(self):
        """Load comprehensive analysis data"""
        if not self.excel_file or not self.excel_file.exists():
            logger.error("❌ No comprehensive analysis Excel file found")
            return pd.DataFrame()
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Comprehensive_Analysis')
            logger.info(f"✅ Loaded {len(df)} sites from {self.excel_file.name}")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading Excel: {e}")
            return pd.DataFrame()
    
    def classify_sites_for_kml(self, df):
        """Classify sites into KML priority categories"""
        df = df.copy()
        
        # Create KML classification based on overall score and environmental risk
        def get_kml_priority(row):
            overall_score = row.get('overall_score_percentage', 0)
            env_risk = row.get('environmental_risk_level_corrected', 'LOW')
            critical_concerns = row.get('critical_concerns_count', 0)
            competition_rec = row.get('competition_recommendation', '')
            
            # CRITICAL environmental risk gets special handling
            if critical_concerns > 0:
                return 'CRITICAL_Environmental'
            
            # High overall score + 9% suitable = High Priority
            if overall_score >= 80 and '9%' in str(competition_rec):
                return 'High Priority'
            
            # Good overall score OR 9% suitable = Medium Priority  
            elif overall_score >= 60 or '9%' in str(competition_rec):
                return 'Medium Priority'
            
            # Everything else = Low Priority
            else:
                return 'Low Priority'
        
        df['kml_priority'] = df.apply(get_kml_priority, axis=1)
        
        # Add KML site numbers within each priority group
        priority_groups = df.groupby('kml_priority')
        df['kml_site_number'] = 0
        
        site_counter = 1
        for priority, group in priority_groups:
            # Sort by overall score within priority
            group_sorted = group.sort_values('overall_score_percentage', ascending=False)
            for idx in group_sorted.index:
                df.loc[idx, 'kml_site_number'] = site_counter
                site_counter += 1
        
        logger.info(f"📊 KML Classification:")
        logger.info(f"   🚨 CRITICAL Environmental: {len(df[df['kml_priority'] == 'CRITICAL_Environmental'])}")
        logger.info(f"   ✅ High Priority: {len(df[df['kml_priority'] == 'High Priority'])}")
        logger.info(f"   ⭐ Medium Priority: {len(df[df['kml_priority'] == 'Medium Priority'])}")
        logger.info(f"   ⚠️  Low Priority: {len(df[df['kml_priority'] == 'Low Priority'])}")
        
        return df
    
    def create_comprehensive_kml(self):
        """Create comprehensive KML with all analysis data"""
        logger.info("🚀 CREATING COMPREHENSIVE D'MARCO KML")
        
        # Load data
        df = self.load_comprehensive_data()
        if df.empty:
            return None, None
        
        # Classify sites
        df = self.classify_sites_for_kml(df)
        
        # Create KML
        kml = simplekml.Kml()
        kml.document.name = "D'Marco LIHTC Portfolio - Comprehensive Analysis (38 Sites)"
        kml.document.description = """Site Classification: 🚨 = Critical Environmental Risk | ✓ = High Priority | * = Medium Priority | ✗ = Low Priority
Example: 🚨21 = Site 21 with Critical Environmental Risk | ✓23 = High Priority Site 23
Click any marker for complete LIHTC analysis including competition, flood, cost, schools, and environmental data."""
        
        # Create folders by priority with enhanced descriptions
        folders = {
            'CRITICAL_Environmental': kml.newfolder(name="🚨 CRITICAL Environmental Risk (Vapor Intrusion Concerns)"),
            'High Priority': kml.newfolder(name="✓ High Priority Sites (Green - Excellent Overall)"),
            'Medium Priority': kml.newfolder(name="* Medium Priority Sites (Yellow - Good Opportunities)"),
            'Low Priority': kml.newfolder(name="✗ Low Priority Sites (Red - Proceed with Caution)")
        }
        
        sites_created = 0
        
        for idx, row in df.iterrows():
            # Skip if no coordinates
            if pd.isna(row.get('coordinates', [None, None])[0]) or pd.isna(row.get('coordinates', [None, None])[1]):
                continue
            
            try:
                # Parse coordinates
                coords = row.get('coordinates', [None, None])
                if isinstance(coords, str):
                    # Handle string format: "[lat, lng]"
                    coords = coords.strip('[]').split(',')
                    lat, lng = float(coords[0]), float(coords[1])
                else:
                    lat, lng = coords[0], coords[1]
                
                sites_created += 1
                
                site_num = int(row.get('kml_site_number', sites_created))
                site_index = row.get('site_index', site_num)
                priority = row.get('kml_priority', 'Medium Priority')
                
                # Create site identifier with appropriate symbol
                if priority == 'CRITICAL_Environmental':
                    icon_name = f"🚨{site_index}"  # Warning symbol for environmental
                elif priority == 'High Priority':
                    icon_name = f"✓{site_index}"   # Checkmark for High Priority
                elif priority == 'Medium Priority':
                    icon_name = f"*{site_index}"    # Asterisk for Medium
                else:
                    icon_name = f"✗{site_index}"   # X mark for Low Priority
                
                # Get folder
                folder = folders.get(priority, folders['Medium Priority'])
                
                # Create point
                point = folder.newpoint(name=icon_name)
                point.coords = [(lng, lat)]
                
                # Create comprehensive description
                description = self.create_site_description(row, site_index)
                point.description = description
                
                # Style based on priority
                if priority == 'CRITICAL_Environmental':
                    # Purple for critical environmental risk
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/purple-pushpin.png'
                    point.style.iconstyle.scale = 1.2  # Larger for visibility
                elif priority == 'High Priority':
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png'
                    point.style.iconstyle.scale = 1.0
                elif priority == 'Medium Priority':
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
                    point.style.iconstyle.scale = 1.0
                else:  # Low Priority
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
                    point.style.iconstyle.scale = 1.0
                
            except Exception as e:
                logger.error(f"❌ Error creating point for site {row.get('site_index', 'unknown')}: {e}")
                continue
        
        # Save KML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        kml_filename = self.base_dir / f"DMarco_Comprehensive_Analysis_{timestamp}.kml"
        kml.save(str(kml_filename))
        
        # Save Excel reference
        excel_reference = kml_filename.parent / f"{kml_filename.stem}_Reference.xlsx"
        with pd.ExcelWriter(excel_reference, engine='openpyxl') as writer:
            # KML reference with site numbers
            df.to_excel(writer, sheet_name='KML_Site_Reference', index=False)
            
            # Summary by priority
            priority_summary = df.groupby('kml_priority').agg({
                'site_index': 'count',
                'overall_score_percentage': 'mean',
                'construction_cost_per_unit': 'mean',
                'school_amenity_score': 'mean'
            }).round(1)
            priority_summary.columns = ['Site_Count', 'Avg_Overall_Score_%', 'Avg_Cost_Per_Unit', 'Avg_School_Score']
            priority_summary.to_excel(writer, sheet_name='Priority_Summary')
            
            # Environmental risk summary
            env_summary = df.groupby('environmental_risk_level_corrected').agg({
                'site_index': 'count',
                'critical_concerns_count': 'sum',
                'high_concerns_count': 'sum'
            })
            env_summary.columns = ['Site_Count', 'Total_Critical_Concerns', 'Total_High_Concerns']
            env_summary.to_excel(writer, sheet_name='Environmental_Summary')
        
        logger.info(f"✅ Created KML with {sites_created} sites")
        logger.info(f"📁 Files created:")
        logger.info(f"   🗺️  KML: {kml_filename.name}")
        logger.info(f"   📊 Excel Reference: {excel_reference.name}")
        
        return kml_filename, excel_reference
    
    def create_site_description(self, row, site_index):
        """Create comprehensive site description with all analysis data"""
        
        # Basic property info
        county = row.get('county', 'Unknown County')
        address = row.get('address', 'Address not specified')
        acreage = row.get('acreage', 'Not specified')
        
        # Overall ranking
        overall_score = row.get('overall_score_percentage', 0)
        overall_rating = row.get('overall_rating', 'Unknown')
        overall_rank = row.get('overall_rank', 'N/A')
        
        # Competition analysis
        competition_rec = row.get('competition_recommendation', 'Unknown')
        competing_1mi = row.get('competing_projects_1_mile', 0)
        competing_2mi = row.get('competing_projects_2_mile', 0)
        
        # QCT/DDA status
        qct_status = row.get('qct_designation', 'Unknown')
        dda_status = row.get('dda_designation', 'Unknown')
        basis_boost = row.get('basis_boost_eligible', 'Unknown')
        
        # Environmental (corrected)
        env_risk = row.get('environmental_risk_level_corrected', 'Unknown')
        critical_concerns = row.get('critical_concerns_count', 0)
        high_concerns = row.get('high_concerns_count', 0)
        total_concerns = row.get('total_environmental_concerns', 0)
        vapor_intrusion = row.get('vapor_intrusion_concern', 'NO')
        phase_i_rec = row.get('phase_i_esa_recommendation', 'Standard Phase I ESA')
        env_details = row.get('environmental_concerns_detail', 'No details available')
        
        # Flood analysis
        flood_zone = row.get('flood_zone', 'Unknown')
        flood_risk = row.get('flood_risk_level', 'Unknown')
        flood_insurance = row.get('flood_insurance_required', 'Unknown')
        
        # Cost analysis
        regional_market = row.get('regional_market', 'Unknown')
        cost_per_unit = row.get('construction_cost_per_unit', 0)
        cost_variance = row.get('cost_variance_percentage', 0)
        
        # School amenities
        school_score = row.get('school_amenity_score', 0)
        school_rating = row.get('school_rating', 'Unknown')
        schools_total = row.get('schools_within_3_miles', 0)
        elementary = row.get('elementary_schools', 0)
        middle = row.get('middle_schools', 0)
        high = row.get('high_schools', 0)
        
        # Format currency
        cost_formatted = f"${cost_per_unit:,.0f}" if cost_per_unit > 0 else "Not calculated"
        
        # Color coding for environmental risk
        if env_risk == 'CRITICAL':
            env_color = '#ff0000'  # Red
            env_icon = '🚨'
        elif env_risk == 'HIGH':
            env_color = '#ff8800'  # Orange  
            env_icon = '⚠️'
        elif env_risk == 'MEDIUM':
            env_color = '#ffaa00'  # Yellow-orange
            env_icon = '⚡'
        else:
            env_color = '#00aa00'  # Green
            env_icon = '✅'
        
        # Build comprehensive HTML
        html = f"""
        <![CDATA[
        <div style="font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4;">
        
        <h2 style="color: #2c5aa0; margin-bottom: 10px;">🏢 D'Marco Site #{site_index}</h2>
        
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 11px;">
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                📍 PROPERTY OVERVIEW
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; width: 40%; background-color: #f9f9f9;">Location</td>
            <td>{address}<br/><strong>{county}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Acreage</td>
            <td>{acreage}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Overall Ranking</td>
            <td><strong>#{overall_rank}</strong> of 38 sites ({overall_score:.1f}% - {overall_rating})</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏆 LIHTC COMPETITION ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Credit Recommendation</td>
            <td><strong>{competition_rec}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Competing Projects</td>
            <td>1 mile: {competing_1mi} | 2 miles: {competing_2mi}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">QCT Status</td>
            <td>{qct_status}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">DDA Status</td>
            <td>{dda_status}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">130% Basis Boost</td>
            <td><strong>{basis_boost}</strong></td>
        </tr>
        
        <tr style="background-color: {env_color}; color: white;">
            <td colspan="2" style="text-align: center; font-weight: bold;">
                {env_icon} ENVIRONMENTAL SCREENING
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Risk Level</td>
            <td><strong style="color: {env_color};">{env_risk}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Environmental Concerns</td>
            <td>Critical: {critical_concerns} | High: {high_concerns} | Total: {total_concerns}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Vapor Intrusion Risk</td>
            <td><strong>{'🚨 YES - IMMEDIATE ATTENTION' if vapor_intrusion == 'YES' else '✅ NO'}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Phase I ESA Required</td>
            <td>{phase_i_rec}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Environmental Details</td>
            <td style="font-size: 10px;">{env_details}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🌊 FLOOD RISK ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">FEMA Flood Zone</td>
            <td><strong>{flood_zone}</strong></td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Flood Risk Level</td>
            <td>{flood_risk}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Flood Insurance</td>
            <td>{'Required' if flood_insurance else 'Not Required'}</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                💰 COST ANALYSIS
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Regional Market</td>
            <td>{regional_market}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Cost Per Unit</td>
            <td>{cost_formatted}</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Cost Variance</td>
            <td>{cost_variance:+.1f}% vs baseline</td>
        </tr>
        
        <tr style="background-color: #f0f8ff;">
            <td colspan="2" style="text-align: center; font-weight: bold; color: #2c5aa0;">
                🏫 SCHOOL AMENITIES
            </td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">School Score</td>
            <td><strong>{school_score}/75</strong> ({school_rating})</td>
        </tr>
        
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">Schools (3 mi)</td>
            <td>Total: {schools_total} | Elem: {elementary} | Middle: {middle} | High: {high}</td>
        </tr>
        
        </table>
        
        <p style="margin-top: 10px; font-size: 10px; color: #666;">
            <strong>Site #{site_index}</strong> | Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        </p>
        
        <p style="margin-top: 5px; font-size: 10px; color: #999; text-align: center;">
            © Structured Consultants LLC - Comprehensive LIHTC Analysis
        </p>
        
        </div>
        ]]>
        """
        
        return html

if __name__ == "__main__":
    kml_generator = ComprehensiveDMarcoKML()
    kml_file, excel_file = kml_generator.create_comprehensive_kml()
    
    if kml_file:
        print("\n🎯 D'MARCO COMPREHENSIVE KML COMPLETE")
        print("=" * 60)
        print(f"📁 Files Created:")
        print(f"  🗺️  KML: {kml_file.name}")
        print(f"  📊 Excel Reference: {excel_file.name}")
        print("\n✅ KML Features:")
        print("  🚨 Purple markers: Critical environmental risk (vapor intrusion)")
        print("  ✅ Green markers: High priority sites")
        print("  ⭐ Yellow markers: Medium priority sites")
        print("  ⚠️  Red markers: Low priority sites")
        print("\n📊 Complete Analysis Data:")
        print("  • LIHTC competition analysis (9% vs 4% credits)")
        print("  • Environmental screening with vapor intrusion alerts")
        print("  • Flood risk assessment with insurance requirements")
        print("  • Regional cost modifiers and construction costs")
        print("  • School amenities scoring (75-point system)")
        print("  • Overall site rankings (1-38)")
    else:
        print("❌ Failed to create KML - check Excel file availability")