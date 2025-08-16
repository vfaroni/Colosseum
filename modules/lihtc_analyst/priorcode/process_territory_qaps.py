#!/usr/bin/env python3
"""
Process Territory QAPs for LIHTC RAG System
Handles Guam and attempts to get Virgin Islands and Northern Mariana Islands
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil
import subprocess

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from qap_pdf_processor import QAPPDFProcessor

class TerritoryQAPProcessor:
    """Process territory QAPs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_dir = self.base_dir / "QAP"
        self.processor = QAPPDFProcessor(base_dir)
        
        # Territory information
        self.territories = {
            'GU': {
                'name': 'Guam',
                'pdf': 'GU_2024_QAP_Draft.pdf',
                'year': 2024,
                'status': 'downloaded',
                'url': 'https://www.ghura.org/sites/default/files/2024_qap_draft.pdf'
            },
            'VI': {
                'name': 'Virgin Islands',
                'pdf': 'VI_QAP_Current.pdf',
                'year': 2024,
                'status': 'pending',
                'url': None  # Need to find
            },
            'MP': {
                'name': 'Northern Mariana Islands',
                'pdf': 'MP_2023_2024_QAP.pdf',
                'year': 2024,
                'status': 'pending',
                'url': 'https://www.nmhcgov.net/default.asp?secID=49'  # Main page
            },
            'AS': {
                'name': 'American Samoa',
                'pdf': None,
                'year': 2024,
                'status': 'uses_section_1602',
                'note': 'Uses Section 1602 program instead of traditional LIHTC'
            }
        }
        
    def download_missing_pdfs(self) -> Dict[str, Path]:
        """Try to download missing territory PDFs"""
        downloaded = {}
        
        for code, info in self.territories.items():
            if info['status'] == 'pending' and info.get('url'):
                print(f"\n🔄 Attempting to download {code} QAP...")
                # For now, we'll need manual download
                print(f"   ℹ️  Please manually download from: {info['url']}")
                
        return downloaded
    
    def find_available_pdfs(self) -> Dict[str, Path]:
        """Find already downloaded PDFs"""
        found_pdfs = {}
        
        for state_code, info in self.territories.items():
            if info.get('pdf'):
                pdf_path = self.qap_dir / state_code / 'raw' / info['pdf']
                if pdf_path.exists():
                    found_pdfs[state_code] = pdf_path
                    print(f"✅ Found {state_code}: {info['pdf']}")
                else:
                    # Check if just downloaded
                    alt_path = self.qap_dir / state_code / 'raw' / f"{state_code}_2024_QAP_Draft.pdf"
                    if alt_path.exists():
                        found_pdfs[state_code] = alt_path
                        print(f"✅ Found {state_code}: {alt_path.name}")
                    
        return found_pdfs
    
    def process_territory(self, code: str, pdf_path: Path) -> Dict:
        """Process a single territory's QAP"""
        print(f"\n🔄 Processing {code} - {self.territories[code]['name']}")
        
        try:
            # Process the PDF
            chunks = self.processor.process_pdf(code, pdf_path)
            
            if not chunks:
                return {'error': f'No chunks created for {code}'}
            
            # Save chunks to state directory
            state_dir = self.qap_dir / '_processed' / code
            state_dir.mkdir(parents=True, exist_ok=True)
            
            # Save all chunks
            chunks_file = state_dir / f"{code}_all_chunks.json"
            with open(chunks_file, 'w') as f:
                json.dump([chunk.__dict__ for chunk in chunks], f, indent=2)
            
            # Create summary
            summary = {
                'state_code': code,
                'state_name': self.territories[code]['name'],
                'document_year': self.territories[code]['year'],
                'total_chunks': len(chunks),
                'processing_date': datetime.now().isoformat(),
                'source_pdf': pdf_path.name,
                'status': 'processed',
                'content_types': {},
                'program_types': {},
                'is_territory': True,
                'allocation_type': 'small_state_minimum'
            }
            
            # Count content and program types
            for chunk in chunks:
                content_type = chunk.content_type
                program_type = chunk.program_type
                
                summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
                summary['program_types'][program_type] = summary['program_types'].get(program_type, 0) + 1
            
            # Save summary
            summary_file = state_dir / f"{code}_processing_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Successfully processed {code}:")
            print(f"   - Total chunks: {len(chunks)}")
            print(f"   - Content types: {summary['content_types']}")
            print(f"   - Saved to: {state_dir}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Error processing {code}: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def update_master_index(self, processed_territories: List[str]) -> None:
        """Update the master chunk index with new territories"""
        master_index_path = self.qap_dir / '_processed' / 'master_chunk_index.json'
        
        # Load existing index
        if master_index_path.exists():
            with open(master_index_path, 'r') as f:
                master_data = json.load(f)
        else:
            master_data = {
                'total_chunks': 0,
                'states_processed': [],
                'chunks_by_state': {}
            }
        
        # Update with new territories
        for code in processed_territories:
            if code not in master_data['states_processed']:
                master_data['states_processed'].append(code)
            
            # Load territory chunks
            chunks_file = self.qap_dir / '_processed' / code / f"{code}_all_chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    chunks = json.load(f)
                
                # Add basic chunk info to master index
                master_data['chunks_by_state'][code] = []
                for chunk in chunks[:5]:  # Just first 5 for index
                    master_data['chunks_by_state'][code].append({
                        'chunk_id': chunk['chunk_id'],
                        'section_title': chunk.get('section_title', ''),
                        'program_type': chunk.get('program_type', 'both'),
                        'content_type': chunk.get('content_type', 'text'),
                        'chunk_size': chunk.get('chunk_size', 0)
                    })
        
        # Recalculate total chunks
        total_chunks = 0
        for state in master_data['states_processed']:
            chunks_file = self.qap_dir / '_processed' / state / f"{state}_all_chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    state_chunks = json.load(f)
                    total_chunks += len(state_chunks)
        
        master_data['total_chunks'] = total_chunks
        master_data['processing_date'] = datetime.now().isoformat()
        
        # Save updated index
        with open(master_index_path, 'w') as f:
            json.dump(master_data, f, indent=2)
        
        print(f"\n✅ Updated master index:")
        print(f"   - Total jurisdictions: {len(master_data['states_processed'])}")
        print(f"   - Total chunks: {master_data['total_chunks']}")
    
    def create_coverage_report(self) -> None:
        """Create a coverage report for all jurisdictions"""
        master_index_path = self.qap_dir / '_processed' / 'master_chunk_index.json'
        
        if master_index_path.exists():
            with open(master_index_path, 'r') as f:
                master_data = json.load(f)
            
            # Expected jurisdictions
            states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                     'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                     'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                     'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                     'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
                     'DC', 'PR', 'VI', 'GU', 'MP', 'AS']
            
            covered = master_data['states_processed']
            missing = [s for s in states if s not in covered]
            
            print(f"\n📊 LIHTC QAP Coverage Report:")
            print(f"   - Target jurisdictions: {len(states)}")
            print(f"   - Covered: {len(covered)} ({len(covered)/len(states)*100:.1f}%)")
            print(f"   - Missing: {len(missing)}")
            
            if missing:
                print(f"   - Still need: {', '.join(missing)}")
            else:
                print("   🎉 100% COVERAGE ACHIEVED!")
    
    def run(self) -> None:
        """Main processing workflow"""
        print("🚀 Processing Territory QAPs")
        print("=" * 60)
        
        # Find available PDFs
        found_pdfs = self.find_available_pdfs()
        
        if not found_pdfs:
            print("\n❌ No territory PDFs found to process!")
            return
        
        # Process each found PDF
        processed_territories = []
        results = {}
        
        for code, pdf_path in found_pdfs.items():
            result = self.process_territory(code, pdf_path)
            results[code] = result
            
            if 'error' not in result:
                processed_territories.append(code)
        
        # Update master index
        if processed_territories:
            self.update_master_index(processed_territories)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Processing Summary:")
        print(f"   - Territories processed: {len(processed_territories)}")
        
        if processed_territories:
            print("\n✅ Successfully processed:")
            for code in processed_territories:
                info = results[code]
                print(f"   - {code}: {info.get('total_chunks', 0)} chunks")
        
        # Special note about American Samoa
        if 'AS' in self.territories:
            print(f"\n📌 Note: {self.territories['AS']['name']} uses Section 1602 program instead of traditional LIHTC")
        
        # Coverage report
        self.create_coverage_report()

def main():
    """Run the territory QAP processor"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    processor = TerritoryQAPProcessor(base_dir)
    processor.run()

if __name__ == "__main__":
    main()