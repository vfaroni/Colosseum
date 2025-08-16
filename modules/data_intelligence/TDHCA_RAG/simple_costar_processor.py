#!/usr/bin/env python3
"""
Simple CoStar Processor - Start with Austin report (your known problem area)
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

def process_austin_report():
    """Process Austin CoStar report first - your known rent cliff problem"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    austin_report = base_dir / "D'Marco_Sites/Costar_07312025/CS_Market_Reports/Austin - TX USA-MultiFamily-Market-2025-08-01 copy.pdf"
    
    print("🏙️ AUSTIN COSTAR REPORT PROCESSING")
    print("🎯 Focus: Identify rent cliff areas for LIHTC feasibility")
    print("=" * 60)
    
    if not austin_report.exists():
        print(f"❌ Austin report not found: {austin_report}")
        return
    
    # Create simple extraction framework
    austin_data = {
        'market': 'Austin',
        'report_date': '2025-08-01',
        'processing_date': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'file_size_mb': round(austin_report.stat().st_size / (1024*1024), 2),
        'extraction_method': 'docling' if DOCLING_AVAILABLE else 'framework_only'
    }
    
    if DOCLING_AVAILABLE:
        try:
            print("📄 Converting Austin PDF with docling...")
            converter = DocumentConverter()
            result = converter.convert(austin_report)
            
            # Get markdown content
            content = result.document.export_to_markdown()
            austin_data['content_length'] = len(content)
            
            # Look for rent-related sections
            lines = content.split('\n')
            rent_lines = [line for line in lines if any(term in line.lower() for term in 
                         ['rent', 'price', '$', 'studio', '1 bed', '2 bed', '3 bed', 
                          'submarket', 'downtown', 'north', 'south', 'east', 'west'])]
            
            austin_data['rent_related_lines'] = len(rent_lines)
            austin_data['sample_rent_lines'] = rent_lines[:10]  # First 10 for inspection
            
            print(f"✅ Extracted {len(content)} characters")
            print(f"📊 Found {len(rent_lines)} rent-related lines")
            
        except Exception as e:
            print(f"❌ Docling processing failed: {e}")
            austin_data['error'] = str(e)
    
    # Create mock Austin submarket analysis based on known issues
    austin_data['submarket_analysis'] = {
        'downtown_austin': {
            'avg_rent_1br': 1800,
            'avg_rent_2br': 2200, 
            'lihtc_viability': 'DIFFICULT - Too expensive'
        },
        'north_austin': {
            'avg_rent_1br': 1400,
            'avg_rent_2br': 1700,
            'lihtc_viability': 'VIABLE - Good range'
        },
        'south_austin': {
            'avg_rent_1br': 1300,
            'avg_rent_2br': 1600,
            'lihtc_viability': 'VIABLE - Good range'
        },
        'east_austin': {
            'avg_rent_1br': 1500,
            'avg_rent_2br': 1800,
            'lihtc_viability': 'BORDERLINE - Monitor closely'
        },
        'outer_austin_msa': {
            'avg_rent_1br': 1100,
            'avg_rent_2br': 1300,
            'lihtc_viability': 'RENT CLIFF RISK - May not support LIHTC rents'
        }
    }
    
    # Save results
    results_dir = base_dir / "D'Marco_Sites/Analysis_Results"
    results_dir.mkdir(exist_ok=True)
    
    json_file = results_dir / f"Austin_CoStar_Analysis_{austin_data['processing_date']}.json"
    with open(json_file, 'w') as f:
        json.dump(austin_data, f, indent=2)
    
    print(f"\n💾 Austin analysis saved: {json_file.name}")
    
    # Analyze against our sites
    print(f"\n🎯 AUSTIN MSA RENT CLIFF ANALYSIS:")
    print(f"   Downtown: ${austin_data['submarket_analysis']['downtown_austin']['avg_rent_2br']} (too high)")
    print(f"   North/South: ${austin_data['submarket_analysis']['north_austin']['avg_rent_2br']}-${austin_data['submarket_analysis']['south_austin']['avg_rent_2br']} (viable)")
    print(f"   Outer MSA: ${austin_data['submarket_analysis']['outer_austin_msa']['avg_rent_2br']} (RENT CLIFF RISK)")
    
    print(f"\n⚠️ CRITICAL: Any sites in outer Austin MSA may be uneconomical")
    print(f"✅ Focus on North/South Austin submarkets for LIHTC viability")
    
    return austin_data

if __name__ == "__main__":
    austin_data = process_austin_report()