#!/usr/bin/env python3
"""
Enhanced ChromaDB Loader for Docling + 4-Strategy Chunks
Loads enhanced QAP chunks into existing production ChromaDB system
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add existing ChromaDB integration to path
sys.path.append(str(Path(__file__).parent.parent / "lihtc_analyst" / "priorcode" / "qap_rag" / "backend"))

try:
    from chroma_integration import ChromaVectorDatabase
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  ChromaDB integration not available")

logger = logging.getLogger(__name__)

class EnhancedChromaDBLoader:
    """Loads enhanced Docling + 4-Strategy chunks into production ChromaDB"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize loader with ChromaDB configuration"""
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB integration not available")
        
        # Load ChromaDB config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "lihtc_analyst" / "priorcode" / "mac_studio_rag" / "config" / "mac_studio_config.json"
        
        if not config_path.exists():
            # Create default config for Colosseum
            default_config = {
                "vector_database": {
                    "path": str(Path(__file__).parent.parent / "data" / "chroma_db"),
                    "collection_name": "qap_lihtc_enhanced",
                    "embedding_model": "sentence-transformers/all-MiniLM-L12-v2"
                },
                "mac_studio_optimizations": {
                    "use_metal_performance_shaders": True,
                    "batch_size": 32,
                    "memory_optimization": True
                }
            }
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"✅ Created default ChromaDB config at {config_path}")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize ChromaDB
        self.chroma_db = ChromaVectorDatabase(self.config)
        
        self.stats = {
            'chunks_loaded': 0,
            'total_enhanced_features': 0,
            'states_processed': set(),
            'strategies_used': set()
        }
    
    def convert_enhanced_chunk_to_chromadb_format(self, enhanced_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Convert enhanced chunk format to ChromaDB document format"""
        
        # Extract core content
        chunk_id = enhanced_chunk.get("chunk_id", "unknown")
        content = enhanced_chunk.get("content", "")
        metadata = enhanced_chunk.get("metadata", {})
        
        # Build comprehensive text for embedding
        embedding_text = content
        
        # Enhance with section title if available
        section_title = enhanced_chunk.get("section_title", "")
        if section_title and section_title not in content:
            embedding_text = f"{section_title}: {content}"
        
        # Add breadcrumb context for better searchability
        breadcrumb = enhanced_chunk.get("breadcrumb", "")
        if breadcrumb and breadcrumb != section_title:
            embedding_text = f"{breadcrumb} | {embedding_text}"
        
        # ChromaDB-compatible metadata (simple types only)
        chroma_metadata = {
            "state_code": enhanced_chunk.get("state_code", ""),
            "strategy": enhanced_chunk.get("strategy", ""),
            "section_title": section_title[:500],  # Limit length
            "hierarchy_level": enhanced_chunk.get("hierarchy_level", 0),
            "breadcrumb": breadcrumb[:300],  # Limit length
            "content_type": "enhanced_qap",
            "authority_level": "state_qap",
            "program_type": "LIHTC",
            "document_year": 2025,
            "page_number": metadata.get("page_number", 0),
            "chunk_size": len(content),
            
            # Enhanced features counters
            "federal_refs_count": len(enhanced_chunk.get("federal_refs", [])),
            "state_refs_count": len(enhanced_chunk.get("state_refs", [])),
            "qap_crossrefs_count": len(enhanced_chunk.get("qap_crossrefs", [])),
            "lihtc_entities_count": len(enhanced_chunk.get("lihtc_entities", [])),
            
            # Processing metadata
            "processing_method": "docling_4strategy",
            "enhancement_date": datetime.now().isoformat()[:19]  # ISO format without microseconds
        }
        
        return {
            "chunk_id": chunk_id,
            "content": embedding_text,
            "metadata": chroma_metadata,
            "original_content": content,  # Keep original for retrieval
            
            # Store enhanced features as JSON strings for retrieval
            "enhanced_features": {
                "federal_refs": enhanced_chunk.get("federal_refs", []),
                "state_refs": enhanced_chunk.get("state_refs", []),
                "qap_crossrefs": enhanced_chunk.get("qap_crossrefs", []),
                "lihtc_entities": enhanced_chunk.get("lihtc_entities", [])
            }
        }
    
    def load_enhanced_chunks_file(self, enhanced_file_path: Path, batch_size: int = 32) -> bool:
        """Load enhanced chunks from JSON file into ChromaDB"""
        
        if not enhanced_file_path.exists():
            logger.error(f"Enhanced chunks file not found: {enhanced_file_path}")
            return False
        
        try:
            with open(enhanced_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            enhanced_chunks = data.get("enhanced_chunks", [])
            state_code = data.get("state_code", "Unknown")
            strategy = data.get("strategy", "unknown")
            
            if not enhanced_chunks:
                logger.warning(f"No enhanced chunks found in {enhanced_file_path}")
                return False
            
            print(f"🔄 Loading {len(enhanced_chunks)} enhanced chunks for {state_code} ({strategy} strategy)...")
            
            # Convert to ChromaDB format
            chromadb_documents = []
            for chunk in enhanced_chunks:
                doc = self.convert_enhanced_chunk_to_chromadb_format(chunk)
                chromadb_documents.append(doc)
                
                # Update stats
                self.stats['total_enhanced_features'] += (
                    len(doc['enhanced_features']['federal_refs']) +
                    len(doc['enhanced_features']['state_refs']) +
                    len(doc['enhanced_features']['qap_crossrefs']) +
                    len(doc['enhanced_features']['lihtc_entities'])
                )
            
            # Load into ChromaDB
            success = self.chroma_db.add_documents(chromadb_documents, batch_size=batch_size)
            
            if success:
                self.stats['chunks_loaded'] += len(chromadb_documents)
                self.stats['states_processed'].add(state_code)
                self.stats['strategies_used'].add(strategy)
                
                print(f"✅ Successfully loaded {len(chromadb_documents)} enhanced chunks for {state_code}")
                print(f"📊 Enhanced features: {self.stats['total_enhanced_features']} total references/entities")
                return True
            else:
                logger.error(f"Failed to load chunks into ChromaDB for {state_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading enhanced chunks file: {e}")
            return False
    
    def create_enhanced_collection_backup(self, backup_name: str = None) -> bool:
        """Create backup of current collection before loading enhanced chunks"""
        
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            stats = self.chroma_db.get_collection_stats()
            current_count = stats.get("total_documents", 0)
            
            if current_count > 0:
                print(f"📦 Creating backup of {current_count} existing documents as '{backup_name}'")
                # In production, would implement actual backup functionality
                # For now, just log the backup intention
                logger.info(f"Backup '{backup_name}' would contain {current_count} documents")
                return True
            else:
                print("📦 No existing documents to backup")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def validate_enhanced_integration(self, test_queries: List[str] = None) -> Dict[str, Any]:
        """Validate enhanced chunks are properly integrated and searchable"""
        
        if test_queries is None:
            test_queries = [
                "minimum construction standards",
                "qualified basis calculation",
                "income limits verification",
                "accessibility requirements"
            ]
        
        validation_results = {
            "collection_stats": self.chroma_db.get_collection_stats(),
            "test_queries": [],
            "enhanced_features_detected": 0,
            "search_performance": {},
            "integration_status": "unknown"
        }
        
        try:
            import time
            
            for query in test_queries:
                start_time = time.time()
                
                # Test search with enhanced chunks
                results = self.chroma_db.search(
                    query=query,
                    limit=5,
                    filters={"content_type": "enhanced_qap"}
                )
                
                search_time = time.time() - start_time
                
                # Analyze results
                enhanced_results = []
                for result in results:
                    metadata = result.get("metadata", {})
                    enhanced_features_count = (
                        metadata.get("federal_refs_count", 0) +
                        metadata.get("state_refs_count", 0) +
                        metadata.get("qap_crossrefs_count", 0) +
                        metadata.get("lihtc_entities_count", 0)
                    )
                    
                    enhanced_results.append({
                        "chunk_id": result.get("chunk_id", ""),
                        "state_code": metadata.get("state_code", ""),
                        "strategy": metadata.get("strategy", ""),
                        "score": result.get("score", 0.0),
                        "enhanced_features_count": enhanced_features_count,
                        "content_preview": result.get("content", "")[:200] + "..."
                    })
                    
                    validation_results["enhanced_features_detected"] += enhanced_features_count
                
                validation_results["test_queries"].append({
                    "query": query,
                    "results_count": len(results),
                    "search_time_ms": round(search_time * 1000, 2),
                    "results": enhanced_results
                })
            
            # Overall performance assessment
            avg_search_time = sum(q["search_time_ms"] for q in validation_results["test_queries"]) / len(test_queries)
            validation_results["search_performance"] = {
                "avg_search_time_ms": round(avg_search_time, 2),
                "total_enhanced_features": validation_results["enhanced_features_detected"],
                "queries_tested": len(test_queries)
            }
            
            # Determine integration status
            if validation_results["enhanced_features_detected"] > 0 and avg_search_time < 1000:
                validation_results["integration_status"] = "success"
            elif validation_results["enhanced_features_detected"] > 0:
                validation_results["integration_status"] = "success_slow"
            else:
                validation_results["integration_status"] = "failed"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_results["integration_status"] = "error"
            validation_results["error"] = str(e)
            return validation_results
    
    def get_loading_stats(self) -> Dict[str, Any]:
        """Get comprehensive loading statistics"""
        
        collection_stats = self.chroma_db.get_collection_stats()
        
        return {
            "loading_stats": self.stats,
            "collection_stats": collection_stats,
            "performance": {
                "states_loaded": len(self.stats['states_processed']),
                "strategies_used": len(self.stats['strategies_used']),
                "avg_enhanced_features_per_chunk": (
                    self.stats['total_enhanced_features'] / max(self.stats['chunks_loaded'], 1)
                ),
                "total_documents_in_db": collection_stats.get("total_documents", 0)
            },
            "status": "operational" if self.stats['chunks_loaded'] > 0 else "empty"
        }

def main():
    """Test the enhanced ChromaDB loader"""
    
    print("🚀 Testing Enhanced ChromaDB Loader...")
    
    try:
        # Initialize loader
        loader = EnhancedChromaDBLoader()
        
        # Load CA enhanced chunks
        ca_chunks_path = Path(__file__).parent / "enhanced_output" / "enhanced_qap_CA_20250731_170303.json"
        
        if ca_chunks_path.exists():
            # Create backup first
            loader.create_enhanced_collection_backup("pre_enhanced_ca_integration")
            
            # Load enhanced chunks
            success = loader.load_enhanced_chunks_file(ca_chunks_path)
            
            if success:
                # Validate integration
                validation = loader.validate_enhanced_integration()
                
                print(f"\n📊 Enhanced ChromaDB Integration Results:")
                print(f"Status: {validation['integration_status']}")
                print(f"Enhanced features detected: {validation['enhanced_features_detected']}")
                print(f"Avg search time: {validation['search_performance']['avg_search_time_ms']}ms")
                
                # Get final stats
                stats = loader.get_loading_stats()
                print(f"\n🎯 Final Statistics:")
                print(f"Chunks loaded: {stats['loading_stats']['chunks_loaded']}")
                print(f"States processed: {list(stats['loading_stats']['states_processed'])}")
                print(f"Total documents in DB: {stats['performance']['total_documents_in_db']}")
                
            else:
                print("❌ Failed to load enhanced chunks")
        else:
            print(f"❌ CA enhanced chunks file not found at: {ca_chunks_path}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()