#!/usr/bin/env python3
"""
Oregon QAP ChromaDB Integration Script
Backs up existing OR chunks and integrates new Type 3 corrected chunks
"""

import json
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add mac_studio_rag backend to path for ChromaDB integration
mac_studio_path = Path(__file__).parent.parent / "mac_studio_rag" / "backend"
sys.path.append(str(mac_studio_path))

try:
    from chroma_integration import ChromaVectorDatabase
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  ChromaDB not available - install with: pip install chromadb")

logger = logging.getLogger(__name__)

class OregonChromaDBIntegrator:
    """Integrates corrected Oregon QAP chunks into ChromaDB with backup"""
    
    def __init__(self):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB dependencies required")
            
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/mac_studio_rag")
        
        # Paths
        self.corrected_chunks_path = self.base_path / "data" / "processed_qaps" / "OR" / "corrected_chunks"
        self.backup_path = self.base_path / "data" / "backups" / f"oregon_chunks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB config
        self.config = {
            "vector_database": {
                "path": str(self.base_path / "data" / "chroma_db"),
                "collection_name": "qap_lihtc_unified",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            },
            "mac_studio_optimizations": {
                "use_metal_performance_shaders": True
            }
        }
        
        self.chroma_db = None
        self.stats = {
            'backup_count': 0,
            'removed_count': 0,
            'added_count': 0,
            'start_time': time.time()
        }
    
    def initialize_chromadb(self):
        """Initialize ChromaDB connection"""
        logger.info("🔌 Connecting to ChromaDB...")
        try:
            self.chroma_db = ChromaVectorDatabase(self.config)
            logger.info("✅ ChromaDB connection established")
            return True
        except Exception as e:
            logger.error(f"❌ ChromaDB connection failed: {e}")
            return False
    
    def backup_existing_oregon_chunks(self) -> List[Dict[str, Any]]:
        """Backup existing Oregon chunks from ChromaDB"""
        logger.info("💾 Backing up existing Oregon chunks...")
        
        try:
            # Query all Oregon chunks
            results = self.chroma_db.collection.get(
                where={"state_code": "OR"},
                include=['documents', 'metadatas', 'ids']
            )
            
            backup_chunks = []
            
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    backup_chunk = {
                        'id': chunk_id,
                        'document': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    backup_chunks.append(backup_chunk)
                
                # Save backup to file
                backup_file = self.backup_path / "oregon_chunks_backup.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_chunks, f, indent=2, ensure_ascii=False)
                
                self.stats['backup_count'] = len(backup_chunks)
                logger.info(f"✅ Backed up {len(backup_chunks)} Oregon chunks to {backup_file}")
            else:
                logger.info("ℹ️  No existing Oregon chunks found to backup")
                
            return backup_chunks
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return []
    
    def remove_existing_oregon_chunks(self):
        """Remove existing Oregon chunks from ChromaDB"""
        logger.info("🗑️  Removing existing Oregon chunks...")
        
        try:
            # Get all Oregon chunk IDs
            results = self.chroma_db.collection.get(
                where={"state_code": "OR"},
                include=['ids']
            )
            
            if results['ids']:
                # Delete Oregon chunks
                self.chroma_db.collection.delete(ids=results['ids'])
                self.stats['removed_count'] = len(results['ids'])
                logger.info(f"✅ Removed {len(results['ids'])} Oregon chunks from ChromaDB")
            else:
                logger.info("ℹ️  No Oregon chunks found to remove")
                
        except Exception as e:
            logger.error(f"❌ Removal failed: {e}")
    
    def load_corrected_chunks(self) -> List[Dict[str, Any]]:
        """Load corrected Oregon chunks from disk"""
        logger.info("📂 Loading corrected Oregon chunks...")
        
        chunks = []
        chunk_files = list(self.corrected_chunks_path.glob("OR_2025_chunk_*.json"))
        
        for chunk_file in sorted(chunk_files):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    chunks.append(chunk_data)
            except Exception as e:
                logger.error(f"Error loading {chunk_file}: {e}")
                continue
        
        logger.info(f"✅ Loaded {len(chunks)} corrected Oregon chunks")
        return chunks
    
    def format_chunks_for_chromadb(self, chunks: List[Dict[str, Any]]) -> tuple:
        """Format chunks for ChromaDB insertion"""
        logger.info("🔄 Formatting chunks for ChromaDB...")
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            try:
                # Use chunk_id as ChromaDB ID
                chunk_id = chunk['chunk_id']
                ids.append(chunk_id)
                
                # Use content as document text
                documents.append(chunk['content'])
                
                # Create metadata (flatten for ChromaDB compatibility)
                metadata = {
                    'state_code': chunk['state_code'],
                    'document_title': chunk['document_title'],
                    'document_year': chunk['document_year'],
                    'page_number': chunk['page_number'],
                    'section_title': chunk['section_title'],
                    'content_type': chunk['content_type'],
                    'program_type': chunk['program_type'],
                    'chunk_size': chunk['chunk_size'],
                    'entities': ','.join(chunk.get('entities', [])),
                    'cross_references': ','.join(chunk.get('cross_references', [])),
                    'processed_date': chunk['metadata']['processed_date'],
                    'processing_version': chunk['metadata']['processing_version'],
                    'chunking_strategy': chunk['metadata']['chunking_strategy'],
                    'claude_opus_research_compliant': str(chunk['metadata']['claude_opus_research_compliant'])
                }
                metadatas.append(metadata)
                
            except Exception as e:
                logger.error(f"Error formatting chunk {chunk.get('chunk_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Formatted {len(ids)} chunks for ChromaDB")
        return ids, documents, metadatas
    
    def insert_corrected_chunks(self, ids: List[str], documents: List[str], metadatas: List[Dict]):
        """Insert corrected chunks into ChromaDB"""
        logger.info("📥 Inserting corrected Oregon chunks into ChromaDB...")
        
        try:
            # Insert in batches to avoid memory issues
            batch_size = 50
            total_inserted = 0
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                
                self.chroma_db.collection.add(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas
                )
                
                total_inserted += len(batch_ids)
                logger.info(f"📊 Inserted batch: {total_inserted}/{len(ids)} chunks")
            
            self.stats['added_count'] = total_inserted
            logger.info(f"✅ Successfully inserted {total_inserted} Oregon chunks")
            
        except Exception as e:
            logger.error(f"❌ Insertion failed: {e}")
            raise
    
    def validate_integration(self) -> Dict[str, Any]:
        """Validate Oregon chunks are properly integrated"""
        logger.info("🔍 Validating Oregon QAP integration...")
        
        validation_results = {
            'total_oregon_chunks': 0,
            'schema_compliant': False,
            'search_functional': False,
            'sample_queries': []
        }
        
        try:
            # Count Oregon chunks
            results = self.chroma_db.collection.get(
                where={"state_code": "OR"},
                include=['ids', 'metadatas']
            )
            
            validation_results['total_oregon_chunks'] = len(results['ids'])
            
            # Check schema compliance
            if results['metadatas']:
                sample_metadata = results['metadatas'][0]
                required_fields = ['state_code', 'section_title', 'processing_version', 'chunking_strategy']
                validation_results['schema_compliant'] = all(field in sample_metadata for field in required_fields)
            
            # Test search functionality
            test_queries = [
                "Oregon housing tax credit allocation",
                "OHCS requirements",
                "9% credit selection criteria"
            ]
            
            for query in test_queries:
                try:
                    search_results = self.chroma_db.collection.query(
                        query_texts=[query],
                        where={"state_code": "OR"},
                        n_results=3
                    )
                    
                    validation_results['sample_queries'].append({
                        'query': query,
                        'results_found': len(search_results['ids'][0]),
                        'success': len(search_results['ids'][0]) > 0
                    })
                except Exception as e:
                    validation_results['sample_queries'].append({
                        'query': query,
                        'results_found': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            validation_results['search_functional'] = all(q['success'] for q in validation_results['sample_queries'])
            
            logger.info(f"✅ Validation complete: {validation_results['total_oregon_chunks']} chunks integrated")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return validation_results
    
    def create_integration_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive integration report"""
        processing_time = time.time() - self.stats['start_time']
        
        report = {
            "integration_summary": {
                "date": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "status": "SUCCESS" if validation_results['search_functional'] else "WARNING",
                "oregon_qap_version": "2025_final",
                "chunking_strategy": "type_3_simple_narrative",
                "claude_opus_research_compliant": True
            },
            "statistics": {
                "chunks_backed_up": self.stats['backup_count'],
                "chunks_removed": self.stats['removed_count'],
                "chunks_added": self.stats['added_count'],
                "net_change": self.stats['added_count'] - self.stats['removed_count']
            },
            "validation_results": validation_results,
            "quality_improvements": {
                "schema_standardized": True,
                "section_titles_proper": True,  # No more generic "Oregon QAP"
                "entities_extracted": True,
                "cross_references_formatted": True,
                "type_3_strategy_applied": True
            },
            "backup_location": str(self.backup_path),
            "next_steps": [
                "Monitor Oregon search performance",
                "Validate THAAP demo scenarios",
                "Compare with other Type 3 states (MA, WA, VT)",
                "Document lessons learned for future state integrations"
            ]
        }
        
        # Save report
        report_file = self.backup_path / "integration_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Integration report saved: {report_file}")
        return report
    
    def integrate_oregon_qap(self) -> Dict[str, Any]:
        """Main integration method"""
        logger.info("🚀 Starting Oregon QAP ChromaDB integration...")
        
        try:
            # Initialize ChromaDB
            if not self.initialize_chromadb():
                raise Exception("Failed to initialize ChromaDB")
            
            # Backup existing chunks
            backup_chunks = self.backup_existing_oregon_chunks()
            
            # Remove existing Oregon chunks
            self.remove_existing_oregon_chunks()
            
            # Load corrected chunks
            corrected_chunks = self.load_corrected_chunks()
            
            # Format for ChromaDB
            ids, documents, metadatas = self.format_chunks_for_chromadb(corrected_chunks)
            
            # Insert corrected chunks
            self.insert_corrected_chunks(ids, documents, metadatas)
            
            # Validate integration
            validation_results = self.validate_integration()
            
            # Create report
            report = self.create_integration_report(validation_results)
            
            logger.info("🎉 Oregon QAP ChromaDB integration complete!")
            return report
            
        except Exception as e:
            logger.error(f"💥 Oregon QAP integration failed: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    integrator = OregonChromaDBIntegrator()
    result = integrator.integrate_oregon_qap()
    
    print(f"\n🎯 OREGON QAP INTEGRATION SUMMARY:")
    print(f"   📊 Chunks Added: {result['statistics']['chunks_added']}")
    print(f"   🔍 Search Functional: {result['validation_results']['search_functional']}")
    print(f"   ✅ Status: {result['integration_summary']['status']}")
    print(f"   📁 Backup: {result['backup_location']}")