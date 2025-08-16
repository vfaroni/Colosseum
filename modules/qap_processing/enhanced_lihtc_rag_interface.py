#!/usr/bin/env python3
"""
Enhanced LIHTC RAG Interface
Professional LIHTC research and Q&A system

Generated: 2025-08-01T13:05:53.177010
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
            print(f"📊 Collection size: {self.collection.count()} items")
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {e}")
            self.ready = False
    
    def search(self, query: str, jurisdiction: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search LIHTC knowledge base"""
        if not self.ready:
            return []
        
        where_filter = None
        if jurisdiction:
            where_filter = {"jurisdiction": {"$eq": jurisdiction}}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1.0 - results["distances"][0][i],
                    "rank": i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def jurisdiction_search(self, jurisdiction: str, query: str = "", n_results: int = 10) -> List[Dict]:
        """Search specific jurisdiction"""
        print(f"📍 Searching {jurisdiction} for: {query or 'all content'}")
        return self.search(query, jurisdiction, n_results)
    
    def definition_search(self, term: str, n_results: int = 5) -> List[Dict]:
        """Search for specific term definitions"""
        query = f"term definition {term}"
        return self.search(query, n_results=n_results)
    
    def compliance_search(self, topic: str, n_results: int = 5) -> List[Dict]:
        """Search for compliance requirements"""
        query = f"compliance requirement {topic}"
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
                user_input = input("\n❓ Query: ").strip()
                
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
                    self.display_results(results, f"{jurisdiction}: {query}")
                
                elif command == "definition" and len(parts) > 1:
                    term = " ".join(parts[1:])
                    results = self.definition_search(term)
                    self.display_results(results, f"Definition: {term}")
                
                elif command == "compliance" and len(parts) > 1:
                    topic = " ".join(parts[1:])
                    results = self.compliance_search(topic)
                    self.display_results(results, f"Compliance: {topic}")
                
                else:
                    # Default search
                    results = self.search(user_input)
                    self.display_results(results, user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def display_results(self, results: List[Dict], query: str):
        """Display search results"""
        print(f"\n🔍 Results for: {query}")
        print(f"📊 Found {len(results)} results")
        print("-" * 60)
        
        for result in results:
            metadata = result["metadata"]
            jurisdiction = metadata.get("jurisdiction", "Unknown")
            source_type = metadata.get("type", "definition")
            
            print(f"{result['rank']}. [{jurisdiction}] {source_type.title()}")
            print(f"   {result['content'][:200]}...")
            print(f"   Relevance: {result['relevance_score']:.3f}")
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
            print(f"\n✅ Quick Test: Found {len(test_results)} results for 'minimum construction standards'")
        
        # Start interactive session
        rag.interactive_session()
    else:
        print("❌ RAG system not ready")

if __name__ == "__main__":
    main()
