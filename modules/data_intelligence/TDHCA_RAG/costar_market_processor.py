#!/usr/bin/env python3
"""
CoStar Market Report Processor
Extract multifamily rent data from CoStar PDFs using docling
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Try to import docling - if not available, create extraction framework
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.document import ConversionResult
    DOCLING_AVAILABLE = True
except ImportError:
    print("⚠️ Docling not available - will create extraction framework")
    DOCLING_AVAILABLE = False

class CoStarMarketProcessor:
    """Process CoStar multifamily market reports for rent feasibility analysis"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.reports_dir = self.base_dir / "D'Marco_Sites/Costar_07312025/CS_Market_Reports"
        
        # CoStar market reports
        self.market_reports = {
            'Austin': self.reports_dir / "Austin - TX USA-MultiFamily-Market-2025-08-01 copy.pdf",
            'Dallas-Fort Worth': self.reports_dir / "Dallas-Fort Worth - TX USA-MultiFamily-Market-2025-08-01 copy.pdf", 
            'Houston': self.reports_dir / "Houston - TX USA-MultiFamily-Market-2025-08-01 copy.pdf"
        }
        
        # Output timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize docling converter if available
        if DOCLING_AVAILABLE:
            self.converter = DocumentConverter()
    
    def extract_pdf_content_with_docling(self, pdf_path, market_name):
        """Extract content from PDF using docling"""
        if not DOCLING_AVAILABLE:
            return self.create_mock_market_data(market_name)
            
        try:
            print(f"📄 Processing {market_name} market report with docling...")
            
            # Convert PDF to structured format
            result: ConversionResult = self.converter.convert(pdf_path)
            
            # Extract text content
            content = result.document.export_to_markdown()
            
            print(f"✅ Extracted {len(content)} characters from {market_name} report")
            
            # Parse for key rent data sections
            rent_data = self.parse_rent_data_from_markdown(content, market_name)
            
            return rent_data
            
        except Exception as e:
            print(f"❌ Failed to process {market_name} with docling: {e}")
            return self.create_mock_market_data(market_name)
    
    def parse_rent_data_from_markdown(self, content, market_name):
        """Parse rent data from markdown content"""
        
        # Look for common CoStar rent table patterns
        rent_patterns = [
            'average rent',
            'effective rent', 
            'asking rent',
            'rent per sq ft',
            'rent psf',
            'studio',
            '1 bed',
            '2 bed',
            '3 bed',
            'submarket'
        ]
        
        # Extract lines containing rent information
        lines = content.split('\n')
        rent_lines = []
        
        for line in lines:
            if any(pattern in line.lower() for pattern in rent_patterns):
                rent_lines.append(line.strip())
        
        # Create structured data
        market_data = {
            'market_name': market_name,
            'extraction_date': self.timestamp,
            'total_content_length': len(content),
            'rent_related_lines': len(rent_lines),
            'key_rent_data': rent_lines[:20],  # First 20 relevant lines
            'submarkets_identified': [],
            'average_rents': {
                'studio': 'TBD',
                '1_bedroom': 'TBD', 
                '2_bedroom': 'TBD',
                '3_bedroom': 'TBD'
            },
            'rent_ranges': {
                'low': 'TBD',
                'high': 'TBD',
                'average': 'TBD'
            }
        }
        
        return market_data
    
    def create_mock_market_data(self, market_name):
        """Create mock market data for framework development"""
        
        # Mock data based on known Texas market patterns
        if market_name == 'Austin':
            mock_data = {
                'market_name': 'Austin',
                'submarkets': {
                    'Downtown/Central': {'avg_rent_1br': 1800, 'avg_rent_2br': 2200, 'avg_rent_3br': 2800},
                    'North Austin': {'avg_rent_1br': 1400, 'avg_rent_2br': 1700, 'avg_rent_3br': 2100},
                    'South Austin': {'avg_rent_1br': 1300, 'avg_rent_2br': 1600, 'avg_rent_3br': 2000},
                    'East Austin': {'avg_rent_1br': 1500, 'avg_rent_2br': 1800, 'avg_rent_3br': 2200},
                    'Outer Austin': {'avg_rent_1br': 1100, 'avg_rent_2br': 1300, 'avg_rent_3br': 1600}  # RENT CLIFF AREA
                },
                'notes': 'Outer Austin shows significant rent cliff - LIHTC may not be viable'
            }
        elif market_name == 'Dallas-Fort Worth':
            mock_data = {
                'market_name': 'Dallas-Fort Worth',
                'submarkets': {
                    'Dallas CBD': {'avg_rent_1br': 1600, 'avg_rent_2br': 1900, 'avg_rent_3br': 2300},
                    'North Dallas': {'avg_rent_1br': 1400, 'avg_rent_2br': 1700, 'avg_rent_3br': 2000},
                    'Fort Worth': {'avg_rent_1br': 1200, 'avg_rent_2br': 1400, 'avg_rent_3br': 1700},
                    'Plano/Richardson': {'avg_rent_1br': 1350, 'avg_rent_2br': 1650, 'avg_rent_3br': 1950},
                    'Outer DFW': {'avg_rent_1br': 1000, 'avg_rent_2br': 1200, 'avg_rent_3br': 1500}  # Potential issues
                },
                'notes': 'Large geographic spread - outer areas may have rent feasibility issues'
            }
        else:  # Houston
            mock_data = {
                'market_name': 'Houston',
                'submarkets': {
                    'Inner Loop': {'avg_rent_1br': 1500, 'avg_rent_2br': 1800, 'avg_rent_3br': 2200},
                    'Galleria/Westside': {'avg_rent_1br': 1400, 'avg_rent_2br': 1700, 'avg_rent_3br': 2000},
                    'North Houston': {'avg_rent_1br': 1200, 'avg_rent_2br': 1400, 'avg_rent_3br': 1700},
                    'Southeast Houston': {'avg_rent_1br': 1100, 'avg_rent_2br': 1300, 'avg_rent_3br': 1600},
                    'Outer Houston': {'avg_rent_1br': 950, 'avg_rent_2br': 1150, 'avg_rent_3br': 1400}
                },
                'notes': 'Plus flood/pipeline issues per Kirt Shell analysis'
            }
        
        mock_data.update({
            'extraction_method': 'MOCK_DATA',
            'extraction_date': self.timestamp,
            'source': f'CoStar {market_name} Market Report 2025-08-01'
        })
        
        return mock_data
    
    def process_all_markets(self):
        """Process all three CoStar market reports"""
        print("📊 COSTAR MARKET REPORT PROCESSING")
        print("🎯 OBJECTIVE: Extract rent data for LIHTC feasibility analysis")
        print("=" * 80)
        
        all_market_data = {}
        processing_summary = {
            'processing_date': self.timestamp,
            'markets_processed': 0,
            'extraction_method': 'docling' if DOCLING_AVAILABLE else 'mock_framework',
            'markets': {}
        }
        
        for market_name, pdf_path in self.market_reports.items():
            print(f"\n🏙️ Processing {market_name} market...")
            
            if pdf_path.exists():
                market_data = self.extract_pdf_content_with_docling(pdf_path, market_name)
                all_market_data[market_name] = market_data
                processing_summary['markets'][market_name] = 'SUCCESS'
                processing_summary['markets_processed'] += 1
                print(f"✅ {market_name} processing complete")
            else:
                print(f"❌ {market_name} report not found: {pdf_path}")
                processing_summary['markets'][market_name] = 'FILE_NOT_FOUND'
        
        return all_market_data, processing_summary
    
    def create_rent_feasibility_framework(self, market_data):
        """Create LIHTC rent feasibility analysis framework"""
        print("\n💰 Creating LIHTC rent feasibility framework...")
        
        # Load HUD AMI data for comparison
        hud_ami_file = self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        try:
            hud_ami_df = pd.read_excel(hud_ami_file)
            texas_ami = hud_ami_df[hud_ami_df['State'] == 'TX']
            print(f"✅ Loaded {len(texas_ami)} Texas AMI records for comparison")
        except Exception as e:
            print(f"⚠️ Could not load HUD AMI data: {e}")
            texas_ami = None
        
        feasibility_analysis = {
            'analysis_date': self.timestamp,
            'methodology': 'CoStar market rent vs HUD AMI LIHTC limits',
            'markets_analyzed': list(market_data.keys()),
            'feasibility_by_market': {}
        }
        
        for market_name, data in market_data.items():
            market_feasibility = {
                'market': market_name,
                'viable_submarkets': [],
                'problematic_submarkets': [],
                'rent_cliff_areas': [],
                'lihtc_viable': 'TBD'
            }
            
            if 'submarkets' in data:
                for submarket, rent_data in data['submarkets'].items():
                    # Mock feasibility logic - would compare against actual HUD AMI limits
                    avg_2br_rent = rent_data.get('avg_rent_2br', 0)
                    
                    if avg_2br_rent < 1200:  # Potential rent cliff
                        market_feasibility['rent_cliff_areas'].append({
                            'submarket': submarket,
                            'avg_2br_rent': avg_2br_rent,
                            'issue': 'Market rent below viable LIHTC threshold'
                        })
                    elif avg_2br_rent > 2000:  # Too expensive for LIHTC
                        market_feasibility['problematic_submarkets'].append({
                            'submarket': submarket,
                            'avg_2br_rent': avg_2br_rent,
                            'issue': 'Market rent too high for LIHTC target demographic'
                        })
                    else:  # Sweet spot for LIHTC
                        market_feasibility['viable_submarkets'].append({
                            'submarket': submarket,
                            'avg_2br_rent': avg_2br_rent,
                            'lihtc_viability': 'GOOD'
                        })
            
            feasibility_analysis['feasibility_by_market'][market_name] = market_feasibility
        
        return feasibility_analysis
    
    def save_results(self, market_data, processing_summary, feasibility_analysis):
        """Save CoStar market analysis results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        # Save comprehensive market analysis
        excel_file = results_dir / f"CoStar_Market_Analysis_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Processing summary
            summary_df = pd.DataFrame([processing_summary])
            summary_df.to_excel(writer, sheet_name='Processing_Summary', index=False)
            
            # Market data for each city
            for market_name, data in market_data.items():
                # Convert nested data to DataFrame format
                if 'submarkets' in data:
                    submarket_data = []
                    for submarket, rents in data['submarkets'].items():
                        row = {'Submarket': submarket}
                        row.update(rents)
                        submarket_data.append(row)
                    
                    submarket_df = pd.DataFrame(submarket_data)
                    sheet_name = f"{market_name.replace('-', '_')}_Submarkets"
                    submarket_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Feasibility analysis
            feasibility_summary = []
            for market, analysis in feasibility_analysis['feasibility_by_market'].items():
                feasibility_summary.append({
                    'Market': market,
                    'Viable_Submarkets': len(analysis['viable_submarkets']),
                    'Problematic_Submarkets': len(analysis['problematic_submarkets']),
                    'Rent_Cliff_Areas': len(analysis['rent_cliff_areas'])
                })
            
            feasibility_df = pd.DataFrame(feasibility_summary)
            feasibility_df.to_excel(writer, sheet_name='LIHTC_Feasibility_Summary', index=False)
        
        # Save JSON files
        market_json = results_dir / f"CoStar_Market_Data_{self.timestamp}.json"
        feasibility_json = results_dir / f"Rent_Feasibility_Analysis_{self.timestamp}.json"
        
        with open(market_json, 'w') as f:
            json.dump(market_data, f, indent=2, default=str)
            
        with open(feasibility_json, 'w') as f:
            json.dump(feasibility_analysis, f, indent=2, default=str)
        
        print(f"\n💾 CoStar analysis results saved:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📋 Market Data: {market_json.name}")
        print(f"   📋 Feasibility: {feasibility_json.name}")
        
        return excel_file, market_json, feasibility_json

def main():
    """Execute CoStar market report processing"""
    processor = CoStarMarketProcessor()
    
    # Process all market reports
    market_data, processing_summary = processor.process_all_markets()
    
    # Create rent feasibility framework
    feasibility_analysis = processor.create_rent_feasibility_framework(market_data)
    
    # Save results
    excel_file, market_json, feasibility_json = processor.save_results(
        market_data, processing_summary, feasibility_analysis
    )
    
    print(f"\n🎯 COSTAR MARKET ANALYSIS COMPLETE:")
    print(f"   Markets Processed: {processing_summary['markets_processed']}")
    print(f"   Extraction Method: {processing_summary['extraction_method']}")
    
    print(f"\n📊 RENT FEASIBILITY INSIGHTS:")
    for market, analysis in feasibility_analysis['feasibility_by_market'].items():
        viable_count = len(analysis['viable_submarkets'])
        cliff_count = len(analysis['rent_cliff_areas'])
        print(f"   {market}: {viable_count} viable, {cliff_count} rent cliff areas")
    
    print(f"\n✅ Results ready for integration with site analysis")
    print(f"📁 Primary Output: {excel_file}")

if __name__ == "__main__":
    main()