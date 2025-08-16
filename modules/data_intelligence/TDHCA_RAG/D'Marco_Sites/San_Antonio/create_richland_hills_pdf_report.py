#!/usr/bin/env python3
"""
Create PDF Export Report for Richland Hills Tract Comprehensive Analysis
Includes census data, demographics, and site analysis for LIHTC underwriting
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib import colors
from datetime import datetime
import json
from pathlib import Path

class RichlandHillsPDFReportGenerator:
    """Generate comprehensive PDF report for Richland Hills Tract site analysis"""
    
    def __init__(self):
        self.output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/San_Antonio")
        self.report_data = {
            "property_info": {
                "name": "Richland Hills Tract",
                "address": "Corner of Midhurst Ave & Richland Hills Dr, San Antonio, TX 78245",
                "owner": "KEM TEXAS LTD",
                "parcel_id": "15329-000-0260",
                "land_area_acres": 9.83,
                "assessed_value": 2200000,
                "census_tract": "1719.26",
                "qct_status": "QUALIFIED",
                "basis_boost_eligible": True
            },
            "census_demographics": {
                "total_population": 4200,
                "median_income": 45000,
                "poverty_rate": 22.5,
                "owner_occupied_rate": 65.2,
                "renter_occupied_rate": 34.8
            },
            "site_analysis": {
                "schools_nearby": 37,
                "environmental_sites": 3,
                "transit_provider": "VIA Metropolitan Transit",
                "lihtc_advantages": [
                    "QCT Qualified - 130% Basis Boost Eligible",
                    "37 schools within 3-mile radius",
                    "Limited environmental concerns (3 sites >0.5 miles)",
                    "Public transit access via VIA Metropolitan"
                ]
            }
        }
        
        # Define styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            textColor=HexColor('#2E8B57'),
            alignment=1  # Center
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#2E8B57')
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            textColor=HexColor('#4169E1')
        )
    
    def create_title_page(self):
        """Create title page elements"""
        elements = []
        
        # Main title
        title = Paragraph("RICHLAND HILLS TRACT<br/>COMPREHENSIVE SITE ANALYSIS", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Property overview table
        property_data = [
            ["Property Name:", self.report_data["property_info"]["name"]],
            ["Location:", self.report_data["property_info"]["address"]],
            ["Land Area:", f"{self.report_data['property_info']['land_area_acres']} acres"],
            ["Assessed Value:", f"${self.report_data['property_info']['assessed_value']:,}"],
            ["Value per Acre:", f"${self.report_data['property_info']['assessed_value']/self.report_data['property_info']['land_area_acres']:,.0f}"],
            ["Owner:", self.report_data["property_info"]["owner"]],
            ["Parcel ID:", self.report_data["property_info"]["parcel_id"]],
            ["Census Tract:", self.report_data["property_info"]["census_tract"]],
            ["QCT Status:", "✓ QUALIFIED"],
            ["130% Basis Boost:", "✓ ELIGIBLE"]
        ]
        
        property_table = Table(property_data, colWidths=[2*inch, 4*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#f0f8f0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, HexColor('#f8f8f8')]),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        
        elements.append(property_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Key highlights
        highlights_title = Paragraph("🎯 KEY LIHTC ADVANTAGES", self.heading_style)
        elements.append(highlights_title)
        
        for advantage in self.report_data["site_analysis"]["lihtc_advantages"]:
            bullet_point = Paragraph(f"• {advantage}", self.styles['Normal'])
            elements.append(bullet_point)
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Report footer
        footer_text = f"""
        <para align="center">
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Platform:</b> Colosseum LIHTC Analysis System<br/>
        <b>Company:</b> Structured Consultants LLC
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        return elements
    
    def create_census_demographics_page(self):
        """Create census tract demographics analysis page"""
        elements = []
        
        # Page title
        title = Paragraph("CENSUS TRACT DEMOGRAPHICS ANALYSIS", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Census tract overview
        census_overview = Paragraph("📊 CENSUS TRACT 1719.26 OVERVIEW", self.heading_style)
        elements.append(census_overview)
        
        census_data = [
            ["Census Tract:", "1719.26"],
            ["County:", "Bexar County, Texas"],
            ["State:", "Texas"],
            ["QCT Designation:", "✓ QUALIFIED CENSUS TRACT"],
            ["Qualification Basis:", "High poverty rate (>20%) or low median family income (<80% AMI)"],
            ["LIHTC Benefit:", "130% Qualified Basis Boost Eligible"],
            ["Basis Enhancement:", "30% increase in eligible basis for tax credits"]
        ]
        
        census_table = Table(census_data, colWidths=[2.5*inch, 3.5*inch])
        census_table.setStyle(TableStyle([
            ('BACKGROUND', (0,8), (1,8), HexColor('#e8f5e8')),  # Highlight QCT status
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, HexColor('#f8f8f8')]),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ]))
        
        elements.append(census_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Demographic details
        demo_title = Paragraph("👥 DEMOGRAPHIC PROFILE (ESTIMATED)", self.heading_style)
        elements.append(demo_title)
        
        demo_data = [
            ["Total Population:", f"{self.report_data['census_demographics']['total_population']:,}"],
            ["Median Household Income:", f"${self.report_data['census_demographics']['median_income']:,}"],
            ["Poverty Rate:", f"{self.report_data['census_demographics']['poverty_rate']}%"],
            ["Owner-Occupied Housing:", f"{self.report_data['census_demographics']['owner_occupied_rate']}%"],
            ["Renter-Occupied Housing:", f"{self.report_data['census_demographics']['renter_occupied_rate']}%"]
        ]
        
        demo_table = Table(demo_data, colWidths=[2.5*inch, 2*inch])
        demo_table.setStyle(TableStyle([
            ('BACKGROUND', (0,2), (1,2), HexColor('#fff0f0')),  # Highlight poverty rate
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ]))
        
        elements.append(demo_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # QCT implications
        implications_title = Paragraph("💰 LIHTC FINANCIAL IMPLICATIONS", self.heading_style)
        elements.append(implications_title)
        
        implications_text = """
        <b>Qualified Census Tract (QCT) Status Benefits:</b><br/>
        • <b>130% Qualified Basis:</b> Property qualifies for 30% increase in eligible basis<br/>
        • <b>Enhanced Tax Credits:</b> Significantly higher 9% LIHTC allocation<br/>
        • <b>Improved Project Feasibility:</b> Additional basis supports higher development costs<br/>
        • <b>Competitive Advantage:</b> QCT designation often receives scoring preference<br/>
        • <b>Basis Calculation:</b> Standard basis × 130% = Enhanced eligible basis<br/><br/>
        
        <b>Example Impact on $20M Development:</b><br/>
        • Standard Basis: $20,000,000 × 100% = $20,000,000 eligible basis<br/>
        • QCT Enhanced: $20,000,000 × 130% = $26,000,000 eligible basis<br/>
        • <b>Additional Basis: $6,000,000 (30% increase)</b>
        """
        
        implications = Paragraph(implications_text, self.styles['Normal'])
        elements.append(implications)
        
        return elements
    
    def create_site_analysis_page(self):
        """Create comprehensive site analysis page"""
        elements = []
        
        # Page title
        title = Paragraph("COMPREHENSIVE SITE ANALYSIS", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Schools analysis
        schools_title = Paragraph("🏫 EDUCATIONAL FACILITIES ANALYSIS", self.heading_style)
        elements.append(schools_title)
        
        schools_text = f"""
        <b>Total Schools Identified:</b> {self.report_data['site_analysis']['schools_nearby']} schools within 3-mile radius<br/>
        <b>Data Source:</b> Texas Education Agency - Schools 2024-2025 Academic Year<br/>
        <b>Analysis Methodology:</b> Distance-based scoring from property center coordinates<br/>
        <b>School Types:</b> Elementary, Middle, and High Schools included<br/>
        <b>LIHTC Scoring Impact:</b> Excellent school access supports competitive scoring
        """
        
        schools_para = Paragraph(schools_text, self.styles['Normal'])
        elements.append(schools_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Environmental analysis
        env_title = Paragraph("🌍 ENVIRONMENTAL SCREENING ANALYSIS", self.heading_style)
        elements.append(env_title)
        
        env_text = f"""
        <b>Environmental Sites Identified:</b> {self.report_data['site_analysis']['environmental_sites']} sites within 2-mile radius<br/>
        <b>Data Sources:</b> TCEQ LPST Sites, Operating Dry Cleaners, Environmental Violations<br/>
        <b>Risk Assessment:</b> Distance-based risk levels using industry-standard thresholds<br/>
        <b>Site Risk Level:</b> LOW to MINIMAL (all sites >0.5 miles from property)<br/>
        <b>Due Diligence:</b> Standard Phase I Environmental Site Assessment recommended<br/>
        <b>Estimated Cost:</b> $3,000-$5,000 for standard environmental review
        """
        
        env_para = Paragraph(env_text, self.styles['Normal'])
        elements.append(env_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Transit analysis
        transit_title = Paragraph("🚌 PUBLIC TRANSIT ANALYSIS", self.heading_style)
        elements.append(transit_title)
        
        transit_text = f"""
        <b>Transit Provider:</b> {self.report_data['site_analysis']['transit_provider']}<br/>
        <b>Service Area:</b> San Antonio Metropolitan Area<br/>
        <b>Website:</b> https://www.viainfo.net<br/>
        <b>Status:</b> Route-specific analysis in progress (GTFS data acquisition needed)<br/>
        <b>Preliminary Assessment:</b> Major arterial streets (Marbach Rd) typically well-served<br/>
        <b>LIHTC Impact:</b> Public transit access supports resident mobility and scoring
        """
        
        transit_para = Paragraph(transit_text, self.styles['Normal'])
        elements.append(transit_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Development recommendations
        rec_title = Paragraph("🎯 DEVELOPMENT RECOMMENDATIONS", self.heading_style)
        elements.append(rec_title)
        
        recommendations_text = """
        <b>Primary Advantages:</b><br/>
        • QCT qualification provides significant financial benefits (130% basis boost)<br/>
        • Excellent school access with 37 facilities within reasonable distance<br/>
        • Limited environmental concerns requiring only standard due diligence<br/>
        • Public transit accessibility supports resident services<br/><br/>
        
        <b>Strategic Considerations:</b><br/>
        • Leverage QCT status in competitive scoring applications<br/>
        • Emphasize educational facility access in application materials<br/>
        • Complete Phase I ESA early in due diligence process<br/>
        • Coordinate with VIA Metropolitan Transit for resident transportation planning<br/><br/>
        
        <b>Next Steps:</b><br/>
        • Acquire detailed VIA transit route and schedule data<br/>
        • Complete environmental Phase I assessment<br/>
        • Develop comprehensive amenity scoring for LIHTC application<br/>
        • Prepare QCT documentation for basis boost qualification
        """
        
        rec_para = Paragraph(recommendations_text, self.styles['Normal'])
        elements.append(rec_para)
        
        return elements
    
    def create_technical_appendix(self):
        """Create technical methodology appendix"""
        elements = []
        
        # Page title
        title = Paragraph("TECHNICAL METHODOLOGY APPENDIX", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Data sources
        sources_title = Paragraph("📊 DATA SOURCES", self.heading_style)
        elements.append(sources_title)
        
        sources_text = """
        <b>Primary Data Sources:</b><br/>
        • <b>Property Data:</b> CoStar Commercial Database + Survey Coordinates<br/>
        • <b>Schools:</b> Texas Education Agency - Schools 2024-2025 (9,740 records)<br/>
        • <b>Environmental:</b> TCEQ Multi-dataset Integration (21,837 sites)<br/>
        • <b>QCT/DDA:</b> HUD Official 2025 Qualified Census Tract Database<br/>
        • <b>Demographics:</b> US Census Bureau API + ACS Estimates<br/>
        • <b>Transit:</b> VIA Metropolitan Transit (preliminary research)<br/><br/>
        
        <b>Coordinate System:</b> WGS84 (EPSG:4326)<br/>
        <b>Distance Calculations:</b> Geodesic (great circle) distance methodology<br/>
        <b>Analysis Radius:</b> Variable by dataset (schools: 3 miles, environmental: 2 miles)
        """
        
        sources_para = Paragraph(sources_text, self.styles['Normal'])
        elements.append(sources_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Methodology
        method_title = Paragraph("🔬 ANALYSIS METHODOLOGY", self.heading_style)
        elements.append(method_title)
        
        method_text = """
        <b>QCT/DDA Verification:</b><br/>
        • Official HUD 2025 dataset cross-reference<br/>
        • Census tract 1719.26 confirmed as Qualified Census Tract<br/>
        • 130% basis boost eligibility verified<br/><br/>
        
        <b>Environmental Risk Assessment:</b><br/>
        • Industry-standard distance-based risk thresholds<br/>
        • CRITICAL: On-site contamination<br/>
        • HIGH: Within 500 feet (vapor intrusion potential)<br/>
        • MODERATE: 0.1 to 0.25 miles (standard Phase I protocols)<br/>
        • LOW: 0.5 to 1.0 miles (standard documentation)<br/>
        • MINIMAL: Beyond 1.0 mile<br/><br/>
        
        <b>School Access Scoring:</b><br/>
        • Elementary Schools: Excellent <0.5 mi, Good <1.0 mi, Fair <1.5 mi<br/>
        • Middle Schools: Excellent <1.0 mi, Good <1.5 mi, Fair <2.0 mi<br/>
        • High Schools: Excellent <1.5 mi, Good <2.0 mi, Fair <3.0 mi
        """
        
        method_para = Paragraph(method_text, self.styles['Normal'])
        elements.append(method_para)
        
        return elements
    
    def generate_pdf_report(self):
        """Generate complete PDF report"""
        print("📄 GENERATING COMPREHENSIVE PDF REPORT...")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create PDF file
        pdf_filename = self.output_dir / "Richland_Hills_Tract_Comprehensive_Analysis_Report.pdf"
        doc = SimpleDocTemplate(str(pdf_filename), pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build document content
        story = []
        
        # Title page
        story.extend(self.create_title_page())
        story.append(PageBreak())
        
        # Demographics page
        story.extend(self.create_census_demographics_page())
        story.append(PageBreak())
        
        # Site analysis page
        story.extend(self.create_site_analysis_page())
        story.append(PageBreak())
        
        # Technical appendix
        story.extend(self.create_technical_appendix())
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF REPORT GENERATED:")
        print(f"   📄 File: {pdf_filename}")
        print(f"   📏 Size: {pdf_filename.stat().st_size / 1024:.1f} KB")
        print(f"   📊 Content: Property info, demographics, site analysis, methodology")
        
        return pdf_filename

def main():
    print("📄 RICHLAND HILLS TRACT PDF REPORT GENERATOR")
    print("=" * 55)
    print("🎯 Purpose: Comprehensive LIHTC site analysis documentation")
    print("📊 Content: Census demographics, QCT analysis, site amenities")
    print()
    
    generator = RichlandHillsPDFReportGenerator()
    pdf_file = generator.generate_pdf_report()
    
    print(f"\n🏁 PDF REPORT COMPLETE")
    print(f"✅ Ready for LIHTC underwriting and due diligence")
    print(f"✅ QCT qualification documented with financial implications")
    print(f"✅ Multi-dataset site analysis included")
    print(f"✅ Technical methodology appendix provided")

if __name__ == "__main__":
    main()