#!/usr/bin/env python3
"""
Enhanced LIHTC RAG Query Interface
Professional interface for comprehensive LIHTC research and Q&A

Generated: 2025-08-01T13:03:32.495177
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
    
    print("\n" + "=" * 50)
    print("📊 RAG System Ready for Queries!")
    print("Usage: rag.comprehensive_search('your query here')")
    
    return rag

if __name__ == "__main__":
    rag_system = main()
