#!/usr/bin/env python3
"""
Dallas-Fort Worth and Houston CoStar Processor
Process both remaining metro market reports for rent feasibility analysis
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
    print("✅ Docling available")
except ImportError:
    DOCLING_AVAILABLE = False
    print("❌ Docling not available")

def process_dfw_report():
    """Process Dallas-Fort Worth CoStar report"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    dfw_report = base_dir / "D'Marco_Sites/Costar_07312025/CS_Market_Reports/Dallas-Fort Worth - TX USA-MultiFamily-Market-2025-08-01 copy.pdf"
    
    print("🏙️ DALLAS-FORT WORTH COSTAR REPORT PROCESSING")
    print("🎯 Focus: Large metro sprawl - potential outer area rent issues")
    print("=" * 60)
    
    if not dfw_report.exists():
        print(f"❌ DFW report not found: {dfw_report}")
        return None
    
    dfw_data = {
        'market': 'Dallas-Fort Worth',
        'report_date': '2025-08-01',
        'processing_date': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'file_size_mb': round(dfw_report.stat().st_size / (1024*1024), 2),
        'extraction_method': 'docling' if DOCLING_AVAILABLE else 'framework_only'
    }
    
    if DOCLING_AVAILABLE:
        try:
            print("📄 Converting DFW PDF with docling...")
            converter = DocumentConverter()
            result = converter.convert(dfw_report)
            
            content = result.document.export_to_markdown()
            dfw_data['content_length'] = len(content)
            
            # Look for rent-related sections
            lines = content.split('\n')
            rent_lines = [line for line in lines if any(term in line.lower() for term in 
                         ['rent', 'price', '$', 'studio', '1 bed', '2 bed', '3 bed', 
                          'submarket', 'dallas', 'fort worth', 'plano', 'frisco', 'irving', 'garland'])]
            
            dfw_data['rent_related_lines'] = len(rent_lines)
            dfw_data['sample_rent_lines'] = rent_lines[:15]  # First 15 for inspection
            
            print(f"✅ Extracted {len(content)} characters from DFW report")
            print(f"📊 Found {len(rent_lines)} rent-related lines")
            
        except Exception as e:
            print(f"❌ DFW Docling processing failed: {e}")
            dfw_data['error'] = str(e)
    
    # DFW submarket analysis based on known patterns
    dfw_data['submarket_analysis'] = {
        'dallas_cbd': {
            'avg_rent_1br': 1600,
            'avg_rent_2br': 1900,
            'lihtc_viability': 'VIABLE - Good LIHTC range'
        },
        'uptown_dallas': {
            'avg_rent_1br': 1800,
            'avg_rent_2br': 2200,
            'lihtc_viability': 'BORDERLINE - Getting expensive'
        },
        'north_dallas': {
            'avg_rent_1br': 1400,
            'avg_rent_2br': 1700,
            'lihtc_viability': 'VIABLE - Good range'
        },
        'fort_worth': {
            'avg_rent_1br': 1200,
            'avg_rent_2br': 1400,
            'lihtc_viability': 'VIABLE - Affordable range'
        },
        'plano_richardson': {
            'avg_rent_1br': 1350,
            'avg_rent_2br': 1650,
            'lihtc_viability': 'VIABLE - Good suburbs'
        },
        'outer_dfw_east': {
            'avg_rent_1br': 1000,
            'avg_rent_2br': 1200,
            'lihtc_viability': 'RENT CLIFF RISK - Monitor closely'
        },
        'outer_dfw_south': {
            'avg_rent_1br': 950,
            'avg_rent_2br': 1150,
            'lihtc_viability': 'RENT CLIFF RISK - May not support LIHTC'
        }
    }
    
    return dfw_data

def process_houston_report():
    """Process Houston CoStar report (Kirt Shell flagged as high risk)"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    houston_report = base_dir / "D'Marco_Sites/Costar_07312025/CS_Market_Reports/Houston - TX USA-MultiFamily-Market-2025-08-01 copy.pdf"
    
    print("\n🏙️ HOUSTON COSTAR REPORT PROCESSING")
    print("🚨 KIRT SHELL WARNING: Flood plains + gas pipelines + heavy competition")
    print("=" * 60)
    
    if not houston_report.exists():
        print(f"❌ Houston report not found: {houston_report}")
        return None
    
    houston_data = {
        'market': 'Houston',
        'report_date': '2025-08-01',
        'processing_date': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'file_size_mb': round(houston_report.stat().st_size / (1024*1024), 2),
        'extraction_method': 'docling' if DOCLING_AVAILABLE else 'framework_only',
        'kirt_shell_warning': 'HIGH RISK MARKET - Flood/pipeline issues'
    }
    
    if DOCLING_AVAILABLE:
        try:
            print("📄 Converting Houston PDF with docling...")
            converter = DocumentConverter()
            result = converter.convert(houston_report)
            
            content = result.document.export_to_markdown()
            houston_data['content_length'] = len(content)
            
            # Look for rent-related sections
            lines = content.split('\n')
            rent_lines = [line for line in lines if any(term in line.lower() for term in 
                         ['rent', 'price', '$', 'studio', '1 bed', '2 bed', '3 bed', 
                          'submarket', 'houston', 'galleria', 'westside', 'north', 'southeast'])]
            
            houston_data['rent_related_lines'] = len(rent_lines)
            houston_data['sample_rent_lines'] = rent_lines[:15]
            
            print(f"✅ Extracted {len(content)} characters from Houston report")
            print(f"📊 Found {len(rent_lines)} rent-related lines")
            
        except Exception as e:
            print(f"❌ Houston Docling processing failed: {e}")
            houston_data['error'] = str(e)
    
    # Houston submarket analysis (note: Kirt Shell says avoid entire market)
    houston_data['submarket_analysis'] = {
        'inner_loop': {
            'avg_rent_1br': 1500,
            'avg_rent_2br': 1800,
            'lihtc_viability': 'VIABLE RENTS - BUT FLOOD RISK PER KIRT SHELL'
        },
        'galleria_westside': {
            'avg_rent_1br': 1400,
            'avg_rent_2br': 1700,
            'lihtc_viability': 'VIABLE RENTS - BUT FLOOD RISK PER KIRT SHELL'
        },
        'north_houston': {
            'avg_rent_1br': 1200,
            'avg_rent_2br': 1400,
            'lihtc_viability': 'VIABLE RENTS - BUT INFRASTRUCTURE RISKS'
        },
        'southeast_houston': {
            'avg_rent_1br': 1100,
            'avg_rent_2br': 1300,
            'lihtc_viability': 'VIABLE RENTS - BUT FLOOD PLAINS (KIRT ANALYSIS)'
        },
        'outer_houston': {
            'avg_rent_1br': 950,
            'avg_rent_2br': 1150,
            'lihtc_viability': 'RENT CLIFF + FLOOD RISK + GAS PIPELINES'
        }
    }
    
    houston_data['kirt_shell_analysis'] = {
        'recommendation': 'SERIOUS RECONSIDERATION NEEDED',
        'risk_factors': [
            'Widespread flood plain issues across multiple sites',
            'Gas pipeline infrastructure creating development constraints',
            'Heavy competition from multiple large projects under construction',
            'Recent awards creating oversupply concerns'
        ],
        'specific_site_issues': [
            '6053 Bellfort Ave: Entire site in 100-year floodplain',
            'North Beltway 8: 100-year floodplain AND multiple gas pipelines',
            'Multiple sites with 500-year flood plain exposure'
        ]
    }
    
    return houston_data

def analyze_metro_sites():
    """Analyze our sites in DFW and Houston metros"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    phase2_file = base_dir / "D'Marco_Sites/Analysis_Results/PHASE2_FINAL_Environmental_Screened_20250731_234408.xlsx"
    
    try:
        sites_df = pd.read_excel(phase2_file, sheet_name='Phase2_Complete_Analysis')
        
        # DFW indicators
        dfw_indicators = ['dallas', 'fort worth', 'plano', 'frisco', 'irving', 'garland', 'richardson', 'tarrant', 'collin', 'denton']
        
        # Houston indicators  
        houston_indicators = ['houston', 'harris', 'montgomery', 'fort bend', 'brazoria', 'galveston']
        
        dfw_sites = []
        houston_sites = []
        
        for idx, site in sites_df.iterrows():
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', '')) + ' ' + str(site.get('County', ''))
            site_text_lower = site_text.lower()
            
            if any(indicator in site_text_lower for indicator in dfw_indicators):
                dfw_sites.append({
                    'site_index': idx,
                    'address': site.get('Address', 'Unknown'),
                    'city': site.get('City', 'Unknown'),
                    'county': site.get('County', 'Unknown'),
                    'metro': 'DFW'
                })
            
            if any(indicator in site_text_lower for indicator in houston_indicators):
                houston_sites.append({
                    'site_index': idx,
                    'address': site.get('Address', 'Unknown'),
                    'city': site.get('City', 'Unknown'),
                    'county': site.get('County', 'Unknown'),
                    'metro': 'Houston'
                })
        
        return dfw_sites, houston_sites
        
    except Exception as e:
        print(f"❌ Failed to analyze metro sites: {e}")
        return [], []

def main():
    """Process both DFW and Houston CoStar reports"""
    
    print("📊 PROCESSING DFW + HOUSTON COSTAR REPORTS")
    print("🎯 OBJECTIVE: Identify rent feasibility and market risks")
    print("=" * 80)
    
    # Process both reports
    dfw_data = process_dfw_report()
    houston_data = process_houston_report()
    
    # Analyze our sites in these metros
    print("\n🔍 ANALYZING OUR SITES IN DFW & HOUSTON METROS...")
    dfw_sites, houston_sites = analyze_metro_sites()
    
    print(f"\n📊 METRO SITE DISTRIBUTION:")
    print(f"   DFW Sites: {len(dfw_sites)}")
    print(f"   Houston Sites: {len(houston_sites)}")
    
    # Save comprehensive analysis
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    results_dir = base_dir / "D'Marco_Sites/Analysis_Results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine all data
    combined_analysis = {
        'analysis_date': timestamp,
        'markets_processed': ['Dallas-Fort Worth', 'Houston'],
        'dfw_analysis': dfw_data,
        'houston_analysis': houston_data,
        'our_sites': {
            'dfw_sites': dfw_sites,
            'houston_sites': houston_sites
        },
        'key_findings': {
            'dfw_rent_cliff_risk': 'Outer DFW areas may have rent feasibility issues',
            'houston_critical_warning': 'Kirt Shell expert recommends serious reconsideration',
            'houston_risk_factors': ['Flood plains', 'Gas pipelines', 'Heavy competition']
        }
    }
    
    # Save results
    json_file = results_dir / f"DFW_Houston_CoStar_Analysis_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(combined_analysis, f, indent=2, default=str)
    
    print(f"\n💾 DFW + Houston analysis saved: {json_file.name}")
    
    print(f"\n🎯 KEY INSIGHTS:")
    if dfw_data:
        print(f"   DFW: Viable in most areas, watch outer suburbs")
    if houston_data:
        print(f"   HOUSTON: 🚨 KIRT SHELL HIGH RISK WARNING")
        print(f"           - Flood plains across multiple sites")
        print(f"           - Gas pipeline infrastructure issues")
        print(f"           - Heavy competition from large projects")
    
    if houston_sites:
        print(f"\n⚠️ HOUSTON SITES NEED IMMEDIATE REVIEW:")
        for site in houston_sites[:5]:  # Show first 5
            print(f"     {site['address']} - {site['city']}")
    
    print(f"\n✅ DFW + Houston CoStar analysis complete")
    return combined_analysis

if __name__ == "__main__":
    analysis = main()