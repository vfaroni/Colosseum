#!/usr/bin/env python3
"""
Simplified LIHTC RAG Deployment
Working with existing ChromaDB and adding comprehensive search capabilities

Created: 2025-08-01
Agent: Strike Leader
Mission: Deploy functional LIHTC RAG system immediately
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
import chromadb
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedLIHTCRAG:
    """Deploy functional LIHTC RAG system using existing ChromaDB"""
    
    def __init__(self):
        # Use existing ChromaDB
        self.chromadb_path = "./lihtc_definitions_chromadb"
        
        if Path(self.chromadb_path).exists():
            self.client = chromadb.PersistentClient(path=self.chromadb_path)
            logger.info(f"✅ Using existing ChromaDB: {self.chromadb_path}")
        else:
            self.client = chromadb.PersistentClient(path="./new_lihtc_rag")
            logger.info("Creating new ChromaDB instance")
        
        # Try to get existing collection
        try:
            self.collection = self.client.get_collection("lihtc_definitions")
            logger.info("✅ Connected to existing lihtc_definitions collection")
        except:
            # Create new collection if none exists
            self.collection = self.client.create_collection("lihtc_definitions")
            logger.info("✅ Created new lihtc_definitions collection")
    
    def enhance_existing_system(self) -> Dict[str, Any]:
        """Enhance existing RAG system with comprehensive data"""
        logger.info("🚀 Enhancing existing LIHTC RAG system...")
        
        enhancement_status = {
            "start_time": datetime.now().isoformat(),
            "existing_items": 0,
            "new_items_added": 0,
            "comprehensive_data_processed": False,
            "interface_created": False
        }
        
        # Check existing collection size
        try:
            existing_count = self.collection.count()
            enhancement_status["existing_items"] = existing_count
            logger.info(f"📊 Existing collection size: {existing_count} items")
        except:
            enhancement_status["existing_items"] = 0
        
        # Load and add comprehensive data if files exist
        comprehensive_files = [
            "comprehensive_enhanced_definitions.json",
            "comprehensive_regulatory_requirements.json"
        ]
        
        new_items = 0
        for filename in comprehensive_files:
            if Path(filename).exists():
                new_items += self.add_comprehensive_data(filename)
        
        enhancement_status["new_items_added"] = new_items
        enhancement_status["comprehensive_data_processed"] = new_items > 0
        
        # Create enhanced interface
        interface_path = self.create_enhanced_interface()
        enhancement_status["interface_created"] = bool(interface_path)
        enhancement_status["interface_path"] = interface_path
        
        enhancement_status["completion_time"] = datetime.now().isoformat()
        enhancement_status["total_items"] = enhancement_status["existing_items"] + enhancement_status["new_items_added"]
        
        return enhancement_status
    
    def add_comprehensive_data(self, filename: str) -> int:
        """Add comprehensive data from file"""
        logger.info(f"Processing comprehensive data: {filename}")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            # Process jurisdiction-based data structure
            for jurisdiction, items in data.items():
                if isinstance(items, list):
                    for i, item in enumerate(items):
                        if isinstance(item, dict):
                            # Create document text
                            if "term" in item and "definition" in item:
                                doc_text = f"Term: {item['term']}\\nDefinition: {item['definition']}\\nJurisdiction: {jurisdiction}"
                            elif "title" in item and "content" in item:
                                doc_text = f"Title: {item['title']}\\nContent: {item['content']}\\nJurisdiction: {jurisdiction}"
                            else:
                                doc_text = f"Content: {str(item)}\\nJurisdiction: {jurisdiction}"
                            
                            documents.append(doc_text)
                            
                            # Create metadata
                            metadata = {
                                "jurisdiction": jurisdiction,
                                "source": filename.replace(".json", ""),
                                "type": "definition" if "term" in item else "requirement"
                            }
                            
                            # Add additional metadata if available
                            for key in ["term", "title", "category", "lihtc_relevance"]:
                                if key in item:
                                    metadata[key] = str(item[key])
                            
                            metadatas.append(metadata)
                            
                            # Create unique ID
                            id_str = f"{jurisdiction}-{filename}-{i}"
                            ids.append(id_str)
            
            # Add to collection in batches
            if documents:
                batch_size = 500
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logger.info(f"✅ Added {len(documents)} items from {filename}")
                return len(documents)
            
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")
            return 0
        
        return 0
    
    def create_enhanced_interface(self) -> str:
        """Create enhanced RAG interface"""
        logger.info("Creating enhanced RAG interface...")
        
        interface_content = f'''#!/usr/bin/env python3
"""
Enhanced LIHTC RAG Interface
Professional LIHTC research and Q&A system

Generated: {datetime.now().isoformat()}
"""

import chromadb
from typing import Dict, List, Optional, Any
import json

class LIHTCRAGInterface:
    """Professional LIHTC RAG interface with comprehensive search"""
    
    def __init__(self, chromadb_path: str = "./lihtc_definitions_chromadb"):
        try:
            self.client = chromadb.PersistentClient(path=chromadb_path)
            self.collection = self.client.get_collection("lihtc_definitions")
            self.ready = True
            print("✅ LIHTC RAG System Ready")
            print(f"📊 Collection size: {{self.collection.count()}} items")
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {{e}}")
            self.ready = False
    
    def search(self, query: str, jurisdiction: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search LIHTC knowledge base"""
        if not self.ready:
            return []
        
        where_filter = None
        if jurisdiction:
            where_filter = {{"jurisdiction": {{"$eq": jurisdiction}}}}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({{
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1.0 - results["distances"][0][i],
                    "rank": i + 1
                }})
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search error: {{e}}")
            return []
    
    def jurisdiction_search(self, jurisdiction: str, query: str = "", n_results: int = 10) -> List[Dict]:
        """Search specific jurisdiction"""
        print(f"📍 Searching {{jurisdiction}} for: {{query or 'all content'}}")
        return self.search(query, jurisdiction, n_results)
    
    def definition_search(self, term: str, n_results: int = 5) -> List[Dict]:
        """Search for specific term definitions"""
        query = f"term definition {{term}}"
        return self.search(query, n_results=n_results)
    
    def compliance_search(self, topic: str, n_results: int = 5) -> List[Dict]:
        """Search for compliance requirements"""
        query = f"compliance requirement {{topic}}"
        return self.search(query, n_results=n_results)
    
    def interactive_session(self):
        """Interactive LIHTC Q&A session"""
        print("🏢 LIHTC Expert Assistant")
        print("=" * 40)
        print("Commands:")
        print("- search [query]")
        print("- jurisdiction [state] [query]")
        print("- definition [term]")
        print("- compliance [topic]")
        print("- quit")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\\n❓ Query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == "search" and len(parts) > 1:
                    query = " ".join(parts[1:])
                    results = self.search(query)
                    self.display_results(results, query)
                
                elif command == "jurisdiction" and len(parts) > 2:
                    jurisdiction = parts[1].upper()
                    query = " ".join(parts[2:])
                    results = self.jurisdiction_search(jurisdiction, query)
                    self.display_results(results, f"{{jurisdiction}}: {{query}}")
                
                elif command == "definition" and len(parts) > 1:
                    term = " ".join(parts[1:])
                    results = self.definition_search(term)
                    self.display_results(results, f"Definition: {{term}}")
                
                elif command == "compliance" and len(parts) > 1:
                    topic = " ".join(parts[1:])
                    results = self.compliance_search(topic)
                    self.display_results(results, f"Compliance: {{topic}}")
                
                else:
                    # Default search
                    results = self.search(user_input)
                    self.display_results(results, user_input)
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {{e}}")
    
    def display_results(self, results: List[Dict], query: str):
        """Display search results"""
        print(f"\\n🔍 Results for: {{query}}")
        print(f"📊 Found {{len(results)}} results")
        print("-" * 60)
        
        for result in results:
            metadata = result["metadata"]
            jurisdiction = metadata.get("jurisdiction", "Unknown")
            source_type = metadata.get("type", "definition")
            
            print(f"{{result['rank']}}. [{{jurisdiction}}] {{source_type.title()}}")
            print(f"   {{result['content'][:200]}}...")
            print(f"   Relevance: {{result['relevance_score']:.3f}}")
            print()

def main():
    """Main interface"""
    rag = LIHTCRAGInterface()
    
    if rag.ready:
        print("🎯 LIHTC RAG System Ready!")
        print("💡 Try: 'minimum construction standards'")
        print("💡 Try: 'jurisdiction CA qualified basis'")
        print("💡 Try: 'definition income limits'")
        
        # Quick test
        test_results = rag.search("minimum construction standards")
        if test_results:
            print(f"\\n✅ Quick Test: Found {{len(test_results)}} results for 'minimum construction standards'")
        
        # Start interactive session
        rag.interactive_session()
    else:
        print("❌ RAG system not ready")

if __name__ == "__main__":
    main()
'''
        
        interface_path = Path("enhanced_lihtc_rag_interface.py")
        with open(interface_path, 'w') as f:
            f.write(interface_content)
        
        logger.info(f"✅ Enhanced RAG interface created: {interface_path}")
        return str(interface_path)

def main():
    """Main deployment execution"""
    print("⚔️ STRIKE LEADER: SIMPLIFIED RAG DEPLOYMENT")
    print("=" * 50)
    
    # Deploy simplified RAG system
    rag = SimplifiedLIHTCRAG()
    status = rag.enhance_existing_system()
    
    print("=" * 50)
    print("✅ RAG SYSTEM ENHANCED!")
    print(f"📊 Total Items: {status['total_items']}")
    print(f"🆕 New Items: {status['new_items_added']}")
    print("🔍 Interface: enhanced_lihtc_rag_interface.py")
    print("🚀 Ready for testing!")
    
    return status

if __name__ == "__main__":
    main()