#!/usr/bin/env python3
"""
Update RAG System with Enhanced Data
Integrates the improved chunks into the Mac Studio RAG system
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil

sys.path.append(str(Path(__file__).parent.parent / "mac_studio_rag" / "backend"))

class RAGEnhancementIntegrator:
    """Integrate enhanced chunks into RAG system"""
    
    def __init__(self, base_dir: str, mac_studio_dir: str):
        self.base_dir = Path(base_dir)
        self.enhanced_dir = self.base_dir / "QAP" / "_processed" / "_enhanced"
        self.mac_studio_dir = Path(mac_studio_dir)
        self.original_processed_dir = self.base_dir / "QAP" / "_processed"
        
    def backup_original_data(self) -> None:
        """Backup original processed data"""
        backup_dir = self.original_processed_dir / "_backup_before_enhancement"
        backup_dir.mkdir(exist_ok=True)
        
        print("💾 Creating backup of original data...")
        
        # Backup master index
        master_index = self.original_processed_dir / "master_chunk_index.json"
        if master_index.exists():
            shutil.copy2(master_index, backup_dir / "master_chunk_index_original.json")
        
        # Backup state chunk files (just metadata, not full files due to size)
        backup_manifest = {
            'backup_date': datetime.now().isoformat(),
            'original_states': [],
            'total_original_chunks': 0
        }
        
        for state_dir in self.original_processed_dir.iterdir():
            if state_dir.is_dir() and len(state_dir.name) <= 3:
                chunks_file = state_dir / f"{state_dir.name}_all_chunks.json"
                if chunks_file.exists():
                    with open(chunks_file, 'r') as f:
                        chunks = json.load(f)
                    backup_manifest['original_states'].append({
                        'state_code': state_dir.name,
                        'chunk_count': len(chunks)
                    })
                    backup_manifest['total_original_chunks'] += len(chunks)
        
        with open(backup_dir / "backup_manifest.json", 'w') as f:
            json.dump(backup_manifest, f, indent=2)
        
        print(f"   ✅ Backed up metadata for {len(backup_manifest['original_states'])} states")
        print(f"   📊 Original total: {backup_manifest['total_original_chunks']:,} chunks")
    
    def convert_enhanced_chunks_to_standard_format(self) -> None:
        """Convert enhanced chunks back to standard format"""
        print("\n🔄 Converting enhanced chunks to standard format...")
        
        total_converted = 0
        states_converted = 0
        
        for enhanced_file in self.enhanced_dir.glob("*_enhanced_chunks.json"):
            # Extract state code
            state_code = enhanced_file.stem.replace("_enhanced_chunks", "")
            
            print(f"   📄 Converting {state_code}...")
            
            # Load enhanced chunks
            with open(enhanced_file, 'r') as f:
                enhanced_chunks = json.load(f)
            
            # Convert back to standard format (remove enhancement fields)
            standard_chunks = []
            for chunk in enhanced_chunks:
                standard_chunk = {
                    'chunk_id': chunk['chunk_id'],
                    'state_code': chunk['state_code'],
                    'document_title': chunk['document_title'],
                    'document_year': chunk['document_year'],
                    'page_number': chunk['page_number'],
                    'section_title': chunk['section_title'],
                    'content': chunk['content'],
                    'content_type': chunk['content_type'],
                    'program_type': chunk['program_type'],
                    'chunk_size': chunk['chunk_size'],
                    'entities': chunk.get('entities', []),
                    'cross_references': chunk.get('cross_references', []),
                    'metadata': chunk.get('metadata', {})
                }
                
                # Add enhancement metadata
                standard_chunk['metadata']['enhanced'] = True
                standard_chunk['metadata']['quality_score'] = chunk.get('quality_score', 0)
                standard_chunk['metadata']['enhancement_date'] = datetime.now().isoformat()
                
                standard_chunks.append(standard_chunk)
            
            # Save to original location
            state_dir = self.original_processed_dir / state_code
            state_dir.mkdir(exist_ok=True)
            
            output_file = state_dir / f"{state_code}_all_chunks.json"
            with open(output_file, 'w') as f:
                json.dump(standard_chunks, f, indent=2)
            
            total_converted += len(standard_chunks)
            states_converted += 1
            
            print(f"      ✅ Converted {len(standard_chunks)} chunks")
        
        print(f"   📊 Total converted: {total_converted:,} chunks from {states_converted} states")
        return total_converted, states_converted
    
    def update_master_index(self, total_chunks: int, states_count: int) -> None:
        """Update master chunk index"""
        print("\n📋 Updating master chunk index...")
        
        master_index_file = self.original_processed_dir / "master_chunk_index.json"
        
        # Load existing index or create new
        if master_index_file.exists():
            with open(master_index_file, 'r') as f:
                master_data = json.load(f)
        else:
            master_data = {
                'total_chunks': 0,
                'states_processed': [],
                'chunks_by_state': {}
            }
        
        # Update with enhanced data
        master_data['total_chunks'] = total_chunks
        master_data['processing_date'] = datetime.now().isoformat()
        master_data['enhanced'] = True
        master_data['enhancement_stats'] = {
            'enhanced_states': states_count,
            'enhancement_date': datetime.now().isoformat(),
            'quality_improvements_applied': True
        }
        
        # Rebuild state samples
        master_data['chunks_by_state'] = {}
        master_data['states_processed'] = []
        
        for state_dir in self.original_processed_dir.iterdir():
            if state_dir.is_dir() and len(state_dir.name) <= 3:
                state_code = state_dir.name
                chunks_file = state_dir / f"{state_code}_all_chunks.json"
                
                if chunks_file.exists():
                    master_data['states_processed'].append(state_code)
                    
                    # Add sample chunks to index
                    with open(chunks_file, 'r') as f:
                        chunks = json.load(f)
                    
                    master_data['chunks_by_state'][state_code] = []
                    for chunk in chunks[:5]:  # First 5 chunks as sample
                        master_data['chunks_by_state'][state_code].append({
                            'chunk_id': chunk['chunk_id'],
                            'section_title': chunk.get('section_title', ''),
                            'program_type': chunk.get('program_type', 'both'),
                            'content_type': chunk.get('content_type', 'text'),
                            'chunk_size': chunk.get('chunk_size', 0),
                            'enhanced': chunk.get('metadata', {}).get('enhanced', False)
                        })
        
        # Save updated index
        with open(master_index_file, 'w') as f:
            json.dump(master_data, f, indent=2)
        
        print(f"   ✅ Updated master index with {len(master_data['states_processed'])} states")
        print(f"   📊 Total chunks in index: {master_data['total_chunks']:,}")
    
    def trigger_vector_database_rebuild(self) -> bool:
        """Trigger vector database rebuild with enhanced data"""
        print("\n🔄 Triggering vector database rebuild...")
        
        try:
            import requests
            
            # Trigger rebuild via API
            response = requests.post(
                "http://localhost:8000/admin/rebuild_vector_db",
                json={"force": True},
                timeout=300  # 5 minutes
            )
            
            if response.status_code == 200:
                print("   ✅ Vector database rebuild started")
                return True
            else:
                print(f"   ❌ Rebuild failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️  Could not trigger automatic rebuild: {e}")
            print("   ℹ️  Please manually restart the FastAPI server to rebuild vector database")
            return False
    
    def create_enhancement_report(self) -> None:
        """Create enhancement integration report"""
        print("\n📄 Creating enhancement integration report...")
        
        # Load enhancement statistics
        master_enhanced_file = self.enhanced_dir / "master_enhanced_index.json"
        if not master_enhanced_file.exists():
            print("   ❌ Enhanced master index not found")
            return
        
        with open(master_enhanced_file, 'r') as f:
            enhanced_stats = json.load(f)
        
        # Load updated master index
        master_index_file = self.original_processed_dir / "master_chunk_index.json"
        with open(master_index_file, 'r') as f:
            master_index = json.load(f)
        
        report = {
            'integration_date': datetime.now().isoformat(),
            'summary': {
                'original_chunks': enhanced_stats.get('quality_improvements', {}).get('chunks_processed', 0),
                'enhanced_chunks': enhanced_stats.get('total_enhanced_chunks', 0),
                'chunks_removed': enhanced_stats.get('quality_improvements', {}).get('chunks_processed', 0) - enhanced_stats.get('total_enhanced_chunks', 0),
                'duplicates_removed': enhanced_stats.get('quality_improvements', {}).get('duplicates_removed', 0),
                'sentences_fixed': enhanced_stats.get('quality_improvements', {}).get('sentences_fixed', 0),
                'encoding_fixed': enhanced_stats.get('quality_improvements', {}).get('encoding_fixed', 0),
                'improvement_rate': enhanced_stats.get('quality_improvements', {}).get('chunks_improved', 0) / max(1, enhanced_stats.get('quality_improvements', {}).get('chunks_processed', 1)) * 100
            },
            'quality_improvements': {
                'content_quality_issues_fixed': enhanced_stats.get('quality_improvements', {}).get('chunks_improved', 0),
                'duplicate_content_removed': enhanced_stats.get('quality_improvements', {}).get('duplicates_removed', 0),
                'encoding_issues_resolved': enhanced_stats.get('quality_improvements', {}).get('encoding_fixed', 0),
                'sentence_boundary_fixes': enhanced_stats.get('quality_improvements', {}).get('sentences_fixed', 0)
            },
            'integration_results': {
                'states_integrated': len(master_index.get('states_processed', [])),
                'total_chunks_in_system': master_index.get('total_chunks', 0),
                'system_ready_for_testing': True
            }
        }
        
        report_file = self.mac_studio_dir / "ENHANCEMENT_INTEGRATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✅ Saved integration report: {report_file}")
        
        # Print summary
        print(f"\n📊 INTEGRATION SUMMARY:")
        print(f"   Original chunks: {report['summary']['original_chunks']:,}")
        print(f"   Enhanced chunks: {report['summary']['enhanced_chunks']:,}")
        print(f"   Quality improvement rate: {report['summary']['improvement_rate']:.1f}%")
        print(f"   Duplicates removed: {report['summary']['duplicates_removed']:,}")
        print(f"   Encoding issues fixed: {report['summary']['encoding_fixed']:,}")
        print(f"   Sentence boundaries fixed: {report['summary']['sentences_fixed']:,}")
    
    def run_integration(self) -> None:
        """Run complete integration workflow"""
        print("🔄 INTEGRATING ENHANCED DATA INTO RAG SYSTEM")
        print("=" * 60)
        
        # Step 1: Backup original data
        self.backup_original_data()
        
        # Step 2: Convert enhanced chunks to standard format
        total_chunks, states_count = self.convert_enhanced_chunks_to_standard_format()
        
        # Step 3: Update master index
        self.update_master_index(total_chunks, states_count)
        
        # Step 4: Trigger vector database rebuild
        rebuild_success = self.trigger_vector_database_rebuild()
        
        # Step 5: Create integration report
        self.create_enhancement_report()
        
        print("\n" + "=" * 60)
        print("✅ ENHANCEMENT INTEGRATION COMPLETE")
        print("=" * 60)
        print(f"Enhanced chunks integrated: {total_chunks:,}")
        print(f"States updated: {states_count}")
        print(f"Vector database rebuild: {'✅ Started' if rebuild_success else '⚠️ Manual restart needed'}")
        print("Ready for quality validation testing!")

def main():
    """Run enhancement integration"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    mac_studio_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/mac_studio_rag"
    
    integrator = RAGEnhancementIntegrator(base_dir, mac_studio_dir)
    integrator.run_integration()

if __name__ == "__main__":
    main()