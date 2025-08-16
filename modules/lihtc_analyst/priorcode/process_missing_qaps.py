#!/usr/bin/env python3
"""
Process Missing QAPs for LIHTC RAG System
Handles Louisiana, Montana, and territories to achieve 100% coverage
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from qap_pdf_processor import QAPPDFProcessor

class MissingQAPProcessor:
    """Process the 6 missing jurisdiction QAPs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_dir = self.base_dir / "QAP"
        self.processor = QAPPDFProcessor(base_dir)
        
        # Missing jurisdictions to process
        self.missing_jurisdictions = {
            'LA': {
                'name': 'Louisiana',
                'pdf': 'LA_2025_QAP_Draft.pdf',
                'year': 2025,
                'status': 'draft'
            },
            'MT': {
                'name': 'Montana', 
                'pdf': 'MT_2026_QAP_Final.pdf',
                'year': 2026,
                'status': 'final'
            },
            'VI': {
                'name': 'Virgin Islands',
                'pdf': 'VI_QAP_2023.pdf',  # Downloaded
                'year': 2023,
                'status': 'downloaded'
            },
            'GU': {
                'name': 'Guam',
                'pdf': None,  # To be downloaded
                'year': 2024,
                'status': 'pending'
            },
            'MP': {
                'name': 'Northern Mariana Islands',
                'pdf': None,  # To be downloaded
                'year': 2024,
                'status': 'pending'
            },
            'AS': {
                'name': 'American Samoa',
                'pdf': None,  # May not have QAP
                'year': 2024,
                'status': 'uncertain'
            }
        }
        
    def find_downloaded_pdfs(self) -> Dict[str, Path]:
        """Find already downloaded PDFs"""
        found_pdfs = {}
        
        for state_code, info in self.missing_jurisdictions.items():
            if info['pdf']:
                if state_code == 'VI':
                    # VI PDF is in _processed directory
                    pdf_path = self.qap_dir / '_processed' / state_code / info['pdf']
                else:
                    pdf_path = self.qap_dir / state_code / 'raw' / info['pdf']
                if pdf_path.exists():
                    found_pdfs[state_code] = pdf_path
                    print(f"✅ Found {state_code}: {info['pdf']}")
                else:
                    print(f"❌ Missing {state_code}: {info['pdf']} at {pdf_path}")
                    
        return found_pdfs
    
    def process_jurisdiction(self, state_code: str, pdf_path: Path) -> Dict:
        """Process a single jurisdiction's QAP"""
        print(f"\n🔄 Processing {state_code} - {self.missing_jurisdictions[state_code]['name']}")
        
        try:
            # Process the PDF
            chunks = self.processor.process_pdf(state_code, pdf_path)
            
            if not chunks:
                return {'error': f'No chunks created for {state_code}'}
            
            # Save chunks to state directory
            state_dir = self.qap_dir / '_processed' / state_code
            state_dir.mkdir(parents=True, exist_ok=True)
            
            # Save all chunks
            chunks_file = state_dir / f"{state_code}_all_chunks.json"
            with open(chunks_file, 'w') as f:
                json.dump([chunk.__dict__ for chunk in chunks], f, indent=2)
            
            # Create summary
            summary = {
                'state_code': state_code,
                'state_name': self.missing_jurisdictions[state_code]['name'],
                'document_year': self.missing_jurisdictions[state_code]['year'],
                'total_chunks': len(chunks),
                'processing_date': datetime.now().isoformat(),
                'source_pdf': pdf_path.name,
                'status': 'processed',
                'content_types': {},
                'program_types': {}
            }
            
            # Count content and program types
            for chunk in chunks:
                content_type = chunk.content_type
                program_type = chunk.program_type
                
                summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
                summary['program_types'][program_type] = summary['program_types'].get(program_type, 0) + 1
            
            # Save summary
            summary_file = state_dir / f"{state_code}_processing_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Successfully processed {state_code}:")
            print(f"   - Total chunks: {len(chunks)}")
            print(f"   - Content types: {summary['content_types']}")
            print(f"   - Saved to: {state_dir}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Error processing {state_code}: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def update_master_index(self, processed_states: List[str]) -> None:
        """Update the master chunk index with new states"""
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
        
        # Update with new states
        for state_code in processed_states:
            if state_code not in master_data['states_processed']:
                master_data['states_processed'].append(state_code)
            
            # Load state chunks
            chunks_file = self.qap_dir / '_processed' / state_code / f"{state_code}_all_chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    state_chunks = json.load(f)
                
                # Add basic chunk info to master index
                master_data['chunks_by_state'][state_code] = []
                for chunk in state_chunks[:5]:  # Just first 5 for index
                    master_data['chunks_by_state'][state_code].append({
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
        print(f"   - Total states: {len(master_data['states_processed'])}")
        print(f"   - Total chunks: {master_data['total_chunks']}")
    
    def run(self) -> None:
        """Main processing workflow"""
        print("🚀 Processing Missing QAPs for 100% Coverage")
        print("=" * 60)
        
        # Find downloaded PDFs
        found_pdfs = self.find_downloaded_pdfs()
        
        if not found_pdfs:
            print("\n❌ No PDFs found to process!")
            print("Please download the missing QAPs first.")
            return
        
        # Process each found PDF
        processed_states = []
        results = {}
        
        for state_code, pdf_path in found_pdfs.items():
            result = self.process_jurisdiction(state_code, pdf_path)
            results[state_code] = result
            
            if 'error' not in result:
                processed_states.append(state_code)
        
        # Update master index
        if processed_states:
            self.update_master_index(processed_states)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 Processing Summary:")
        print(f"   - States processed: {len(processed_states)}")
        print(f"   - States with errors: {len(results) - len(processed_states)}")
        
        if processed_states:
            print("\n✅ Successfully processed:")
            for state in processed_states:
                info = results[state]
                print(f"   - {state}: {info.get('total_chunks', 0)} chunks")
        
        # Show pending downloads
        pending = [code for code, info in self.missing_jurisdictions.items() 
                  if code not in found_pdfs]
        if pending:
            print(f"\n⏳ Still need to download QAPs for: {', '.join(pending)}")

def main():
    """Run the missing QAP processor"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    processor = MissingQAPProcessor(base_dir)
    processor.run()

if __name__ == "__main__":
    main()