#!/usr/bin/env python3
"""
Enhanced LIHTC RAG System Deployment
Comprehensive ChromaDB deployment with 1,719 definitions + cross-references

Created: 2025-08-01
Agent: Strike Leader
Mission: Deploy industry's most comprehensive LIHTC RAG system
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any, Optional
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_rag_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedLIHTCRAGSystem:
    """Deploy comprehensive LIHTC RAG system with enhanced definitions and cross-references"""
    
    def __init__(self, deployment_dir: str = "./enhanced_lihtc_rag"):
        self.deployment_dir = Path(deployment_dir)
        self.deployment_dir.mkdir(exist_ok=True)
        
        self.chromadb_path = self.deployment_dir / "chromadb"
        self.chromadb_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.chromadb_path))
        
        logger.info("Enhanced LIHTC RAG System Initialized")
        logger.info(f"Deployment Directory: {self.deployment_dir}")
        logger.info(f"ChromaDB Path: {self.chromadb_path}")
    
    def load_comprehensive_data(self) -> Dict[str, Any]:
        """Load all comprehensive LIHTC data"""
        logger.info("Loading comprehensive LIHTC datasets...")
        
        data_files = {
            "enhanced_definitions": "comprehensive_enhanced_definitions.json",
            "regulatory_requirements": "comprehensive_regulatory_requirements.json", 
            "cross_references": "comprehensive_cross_references.json"
        }
        
        loaded_data = {}
        
        for data_type, filename in data_files.items():
            file_path = Path(filename)
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    loaded_data[data_type] = json.load(f)
                logger.info(f"✅ Loaded {data_type}: {len(loaded_data[data_type])} items")
            else:
                logger.warning(f"⚠️ File not found: {filename}")
                loaded_data[data_type] = []
        
        return loaded_data
    
    def create_enhanced_collections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced ChromaDB collections"""
        logger.info("Creating enhanced ChromaDB collections...")
        
        collections_created = {}
        
        # 1. Enhanced Definitions Collection
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection("lihtc_enhanced_definitions")
            except:
                pass
            
            definitions_collection = self.client.create_collection(
                name="lihtc_enhanced_definitions",
                metadata={"description": "Enhanced LIHTC definitions with authority links"}
            )
            
            # Process enhanced definitions
            definitions_data = data.get("enhanced_definitions", [])
            if definitions_data:
                documents = []
                metadatas = []
                ids = []
                
                for i, definition in enumerate(definitions_data):
                    # Create searchable document text
                    doc_text = f"Term: {definition.get('term', '')}\n"
                    doc_text += f"Definition: {definition.get('definition', '')}\n"
                    doc_text += f"Context: {definition.get('context', '')}\n"
                    doc_text += f"Jurisdiction: {definition.get('jurisdiction', '')}"
                    
                    documents.append(doc_text)
                    
                    # Enhanced metadata
                    metadata = {
                        "term": definition.get("term", ""),
                        "jurisdiction": definition.get("jurisdiction", ""),
                        "source": definition.get("source", "QAP"),
                        "lihtc_relevance": definition.get("lihtc_relevance", "medium"),
                        "authority_level": definition.get("authority_level", "state"),
                        "category": definition.get("category", "general")
                    }
                    metadatas.append(metadata)
                    
                    # Generate unique ID
                    id_string = f"{definition.get('jurisdiction', '')}-{definition.get('term', '')}-{i}"
                    ids.append(hashlib.md5(id_string.encode()).hexdigest())
                
                # Add to collection in batches
                batch_size = 1000
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    definitions_collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logger.info(f"✅ Enhanced Definitions Collection: {len(documents)} items")
                collections_created["definitions"] = len(documents)
            
        except Exception as e:
            logger.error(f"❌ Failed to create definitions collection: {e}")
            collections_created["definitions"] = 0
        
        # 2. Regulatory Requirements Collection
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection("lihtc_regulatory_requirements")
            except:
                pass
            
            requirements_collection = self.client.create_collection(
                name="lihtc_regulatory_requirements",
                metadata={"description": "LIHTC regulatory requirements and compliance criteria"}
            )
            
            requirements_data = data.get("regulatory_requirements", [])
            if requirements_data:
                documents = []
                metadatas = []
                ids = []
                
                for i, requirement in enumerate(requirements_data):
                    # Create searchable document text
                    doc_text = f"Title: {requirement.get('title', '')}\n"
                    doc_text += f"Content: {requirement.get('content', '')}\n"
                    doc_text += f"Type: {requirement.get('type', '')}\n"
                    doc_text += f"Jurisdiction: {requirement.get('jurisdiction', '')}"
                    
                    documents.append(doc_text)
                    
                    # Enhanced metadata
                    metadata = {
                        "title": requirement.get("title", ""),
                        "jurisdiction": requirement.get("jurisdiction", ""),
                        "type": requirement.get("type", "requirement"),
                        "section": requirement.get("section", ""),
                        "compliance_level": requirement.get("compliance_level", "standard")
                    }
                    metadatas.append(metadata)
                    
                    # Generate unique ID
                    id_string = f"req-{requirement.get('jurisdiction', '')}-{i}"
                    ids.append(hashlib.md5(id_string.encode()).hexdigest())
                
                requirements_collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"✅ Regulatory Requirements Collection: {len(documents)} items")
                collections_created["requirements"] = len(documents)
            
        except Exception as e:
            logger.error(f"❌ Failed to create requirements collection: {e}")
            collections_created["requirements"] = 0
        
        # 3. Cross-References Collection
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection("lihtc_cross_references")
            except:
                pass
            
            references_collection = self.client.create_collection(
                name="lihtc_cross_references",
                metadata={"description": "LIHTC cross-references and authority links"}
            )
            
            references_data = data.get("cross_references", [])
            if references_data:
                documents = []
                metadatas = []
                ids = []
                
                for i, reference in enumerate(references_data):
                    # Create searchable document text
                    doc_text = f"Source: {reference.get('source_text', '')}\n"
                    doc_text += f"Target: {reference.get('target_text', '')}\n"
                    doc_text += f"Type: {reference.get('reference_type', '')}\n"
                    doc_text += f"Authority: {reference.get('authority_level', '')}"
                    
                    documents.append(doc_text)
                    
                    # Enhanced metadata
                    metadata = {
                        "source_jurisdiction": reference.get("source_jurisdiction", ""),
                        "target_jurisdiction": reference.get("target_jurisdiction", ""),
                        "reference_type": reference.get("reference_type", "internal"),
                        "authority_level": reference.get("authority_level", "state")
                    }
                    metadatas.append(metadata)
                    
                    # Generate unique ID
                    id_string = f"ref-{i}"
                    ids.append(hashlib.md5(id_string.encode()).hexdigest())
                
                references_collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"✅ Cross-References Collection: {len(documents)} items")
                collections_created["references"] = len(documents)
            
        except Exception as e:
            logger.error(f"❌ Failed to create references collection: {e}")
            collections_created["references"] = 0
        
        return collections_created
    
    def create_rag_query_interface(self) -> str:
        """Create professional RAG query interface"""
        logger.info("Creating RAG query interface...")
        
        interface_content = '''#!/usr/bin/env python3
"""
Enhanced LIHTC RAG Query Interface
Professional interface for comprehensive LIHTC research and Q&A

Generated: ''' + datetime.now().isoformat() + '''
"""

import chromadb
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

class EnhancedLIHTCRAGQuery:
    """Professional LIHTC RAG query system with multi-collection search"""
    
    def __init__(self, chromadb_path: str = "./chromadb"):
        self.client = chromadb.PersistentClient(path=chromadb_path)
        
        # Load collections
        try:
            self.definitions = self.client.get_collection("lihtc_enhanced_definitions")
            self.requirements = self.client.get_collection("lihtc_regulatory_requirements")
            self.references = self.client.get_collection("lihtc_cross_references")
            print("✅ All RAG collections loaded successfully")
        except Exception as e:
            print(f"⚠️ Some collections may not be available: {e}")
    
    def search_definitions(self, query: str, jurisdiction: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search enhanced definitions with optional jurisdiction filtering"""
        where_filter = {}
        if jurisdiction:
            where_filter["jurisdiction"] = {"$eq": jurisdiction}
        
        try:
            results = self.definitions.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1.0 - results["distances"][0][i],
                    "type": "definition"
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Definition search error: {e}")
            return []
    
    def search_requirements(self, query: str, requirement_type: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search regulatory requirements with optional type filtering"""
        where_filter = {}
        if requirement_type:
            where_filter["type"] = {"$eq": requirement_type}
        
        try:
            results = self.requirements.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1.0 - results["distances"][0][i],
                    "type": "requirement"
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Requirements search error: {e}")
            return []
    
    def search_cross_references(self, query: str, authority_level: Optional[str] = None, n_results: int = 3) -> List[Dict]:
        """Search cross-references with optional authority filtering"""
        where_filter = {}
        if authority_level:
            where_filter["authority_level"] = {"$eq": authority_level}
        
        try:
            results = self.references.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1.0 - results["distances"][0][i],
                    "type": "cross_reference"
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Cross-reference search error: {e}")
            return []
    
    def comprehensive_search(self, query: str, jurisdiction: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Comprehensive search across all collections"""
        print(f"🔍 Comprehensive LIHTC Search: {query}")
        if jurisdiction:
            print(f"📍 Jurisdiction Filter: {jurisdiction}")
        
        results = {
            "definitions": self.search_definitions(query, jurisdiction, n_results=3),
            "requirements": self.search_requirements(query, n_results=3),
            "cross_references": self.search_cross_references(query, n_results=2)
        }
        
        # Calculate total results
        total_results = sum(len(results[key]) for key in results)
        print(f"📊 Found {total_results} relevant results")
        
        return results
    
    def jurisdiction_analysis(self, jurisdiction: str) -> Dict[str, Any]:
        """Analyze specific jurisdiction coverage"""
        print(f"📍 Analyzing jurisdiction: {jurisdiction}")
        
        analysis = {
            "jurisdiction": jurisdiction,
            "definitions_count": 0,
            "requirements_count": 0,
            "cross_references_count": 0
        }
        
        try:
            # Count definitions
            def_results = self.definitions.query(
                query_texts=[""],
                n_results=1000,
                where={"jurisdiction": {"$eq": jurisdiction}},
                include=["metadatas"]
            )
            analysis["definitions_count"] = len(def_results["metadatas"][0]) if def_results["metadatas"] else 0
            
            # Count requirements
            req_results = self.requirements.query(
                query_texts=[""],
                n_results=1000,
                where={"jurisdiction": {"$eq": jurisdiction}},
                include=["metadatas"]
            )
            analysis["requirements_count"] = len(req_results["metadatas"][0]) if req_results["metadatas"] else 0
            
            # Count cross-references
            ref_results = self.references.query(
                query_texts=[""],
                n_results=1000,
                where={"source_jurisdiction": {"$eq": jurisdiction}},
                include=["metadatas"]
            )
            analysis["cross_references_count"] = len(ref_results["metadatas"][0]) if ref_results["metadatas"] else 0
            
        except Exception as e:
            print(f"⚠️ Analysis error: {e}")
        
        return analysis

def main():
    """Interactive LIHTC RAG demonstration"""
    print("🏢 Enhanced LIHTC RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    rag = EnhancedLIHTCRAGQuery()
    
    # Sample queries
    sample_queries = [
        "minimum construction standards",
        "qualified basis calculation",
        "income limits verification",
        "tenant file requirements",
        "compliance monitoring"
    ]
    
    print("🎯 Sample LIHTC Queries:")
    for i, query in enumerate(sample_queries, 1):
        print(f"{i}. {query}")
    
    print("\\n" + "=" * 50)
    print("📊 RAG System Ready for Queries!")
    print("Usage: rag.comprehensive_search('your query here')")
    
    return rag

if __name__ == "__main__":
    rag_system = main()
'''
        
        interface_path = self.deployment_dir / "enhanced_rag_interface.py"
        interface_path.write_text(interface_content)
        
        logger.info(f"✅ RAG query interface created: {interface_path}")
        return str(interface_path)
    
    def deploy_complete_system(self) -> Dict[str, Any]:
        """Deploy complete enhanced RAG system"""
        logger.info("🚀 Deploying Enhanced LIHTC RAG System...")
        
        deployment_status = {
            "start_time": datetime.now().isoformat(),
            "data_loaded": False,
            "collections_created": {},
            "interface_created": False,
            "deployment_success": False
        }
        
        try:
            # Load comprehensive data
            data = self.load_comprehensive_data()
            deployment_status["data_loaded"] = bool(data)
            
            # Create enhanced collections
            collections = self.create_enhanced_collections(data)
            deployment_status["collections_created"] = collections
            
            # Create query interface
            interface_path = self.create_rag_query_interface()
            deployment_status["interface_created"] = bool(interface_path)
            deployment_status["interface_path"] = interface_path
            
            # Determine success
            deployment_status["deployment_success"] = (
                deployment_status["data_loaded"] and
                sum(collections.values()) > 0 and
                deployment_status["interface_created"]
            )
            
            deployment_status["completion_time"] = datetime.now().isoformat()
            
            if deployment_status["deployment_success"]:
                logger.info("✅ Enhanced RAG System Deployment Complete!")
                total_items = sum(collections.values())
                logger.info(f"📊 Total Items Indexed: {total_items}")
            else:
                logger.error("❌ RAG deployment incomplete")
            
        except Exception as e:
            logger.error(f"❌ RAG deployment failed: {e}")
            deployment_status["error"] = str(e)
        
        # Save deployment status
        status_path = self.deployment_dir / "rag_deployment_status.json"
        with open(status_path, 'w') as f:
            json.dump(deployment_status, f, indent=2)
        
        return deployment_status

def main():
    """Main deployment execution"""
    print("⚔️ STRIKE LEADER: ENHANCED RAG DEPLOYMENT INITIATED")
    print("=" * 60)
    
    # Deploy enhanced RAG system
    rag_deployment = EnhancedLIHTCRAGSystem()
    status = rag_deployment.deploy_complete_system()
    
    print("=" * 60)
    if status.get("deployment_success"):
        print("✅ ENHANCED RAG SYSTEM DEPLOYED!")
        print(f"📁 Deployment Directory: {rag_deployment.deployment_dir}")
        print("🔍 Query Interface: enhanced_rag_interface.py")
        print("🚀 Ready for LLM integration!")
    else:
        print("❌ RAG DEPLOYMENT INCOMPLETE - CHECK LOGS")
    
    return status

if __name__ == "__main__":
    main()