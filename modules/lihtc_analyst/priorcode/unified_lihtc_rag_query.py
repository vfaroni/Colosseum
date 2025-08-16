#!/usr/bin/env python3
"""
Unified LIHTC RAG Query System
Provides advanced search capabilities across federal and state LIHTC sources
Implements authority hierarchy, conflict resolution, and cross-jurisdictional analysis
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
from collections import defaultdict, Counter
from dataclasses import dataclass
import difflib

# INTERIM SOLUTION: ChromaDB Integration for State QAP Search
# TODO: Replace with full LLM semantic search when hardware arrives
try:
    # Add mac_studio_rag backend to path for ChromaDB integration
    mac_studio_path = str(Path(__file__).parent.parent / "mac_studio_rag" / "backend")
    if mac_studio_path not in sys.path:
        sys.path.append(mac_studio_path)
    
    from chroma_integration import ChromaVectorDatabase
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  ChromaDB integration not available - state search will be limited")

# Performance optimization integration
try:
    from chromadb_performance_optimizer import ChromaDBPerformanceOptimizer
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    print("⚠️  Performance optimizer not available - using standard ChromaDB")

@dataclass
class QueryResult:
    """Individual search result with enhanced metadata"""
    chunk_id: str
    content: str
    source: str  # 'federal' or state code
    source_type: str  # IRC, CFR, Rev_Proc, QAP
    authority_level: str
    authority_score: int
    section_reference: str
    relevance_score: float
    document_title: str
    effective_date: str
    superseded_by: str
    conflicts: List[str]
    cross_references: List[str]
    state_applications: List[str]
    metadata: Dict
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert QueryResult to dictionary format expected by API"""
        return {
            "chunk_id": self.chunk_id,
            "state_code": self.source if self.source != 'federal' else None,
            "content": self.content,
            "section_title": self.section_reference,
            "program_type": self.metadata.get("program_type"),
            "content_type": self.metadata.get("content_type", self.source_type),
            "authority_level": self.authority_level,
            "score": self.relevance_score,
            "metadata": {
                **self.metadata,
                "authority_score": self.authority_score,
                "document_title": self.document_title,
                "effective_date": self.effective_date,
                "conflicts": self.conflicts,
                "cross_references": self.cross_references,
                "state_applications": self.state_applications
            }
        }

class UnifiedLIHTCRAGQuery:
    """Advanced query system for unified federal + state LIHTC RAG"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_processed_dir = self.base_dir / "QAP" / "_processed"
        self.federal_processed_dir = self.base_dir / "federal" / "LIHTC_Federal_Sources" / "_processed"
        self.indexes_dir = self.qap_processed_dir / "_indexes"
        
        # Load all indexes
        self.indexes = self.load_all_indexes()
        
        # Authority hierarchy for ranking
        self.authority_hierarchy = {
            'statutory': 100,
            'regulatory': 80,
            'guidance': 60,
            'interpretive': 40,
            'state_qap': 30
        }
        
        # Query performance tracking
        self.query_stats = {
            'total_queries': 0,
            'avg_response_time': 0,
            'most_common_search_types': Counter()
        }
        
        # INTERIM SOLUTION: Initialize ChromaDB for state QAP search with performance optimization
        # TODO: Replace with LLM-based semantic search when hardware available
        self.chroma_db = None
        self.performance_optimizer = None
        
        if CHROMA_AVAILABLE:
            try:
                # Load ChromaDB config from mac_studio_rag
                config_path = Path(__file__).parent.parent / "mac_studio_rag" / "config" / "mac_studio_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    self.chroma_db = ChromaVectorDatabase(config)
                    
                    # Initialize performance optimizer if available
                    if PERFORMANCE_OPTIMIZER_AVAILABLE:
                        self.performance_optimizer = ChromaDBPerformanceOptimizer(self.chroma_db, config)
                        print(f"🚀 ChromaDB with Performance Optimizer initialized (Target: <50ms)")
                    else:
                        print(f"✅ ChromaDB initialized for state QAP search (INTERIM solution)")
                else:
                    print(f"⚠️  ChromaDB config not found at {config_path}")
            except Exception as e:
                print(f"⚠️  Failed to initialize ChromaDB: {e}")
                self.chroma_db = None
    
    def load_all_indexes(self) -> Dict:
        """Load all available indexes for unified search"""
        indexes = {}
        
        index_files = [
            'master_chunk_index.json',
            'authority_index.json',
            'effective_date_index.json',
            'federal_state_cross_ref_index.json',
            'federal_content_index.json',
            'federal_entity_index.json',
            'federal_section_index.json',
            'unified_search_config.json',
            'authority_conflict_resolver.json'
        ]
        
        for index_file in index_files:
            index_path = self.indexes_dir / index_file
            if index_path.exists():
                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        index_name = index_file.replace('.json', '')
                        indexes[index_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️  Error loading {index_file}: {e}")
        
        return indexes
    
    def search_by_authority_level(self, query: str, authority_levels: List[str] = None, 
                                 limit: int = 20) -> List[QueryResult]:
        """Search filtered by authority level (statutory, regulatory, guidance, etc.)"""
        if authority_levels is None:
            authority_levels = ['statutory', 'regulatory', 'guidance', 'interpretive', 'state_qap']
        
        results = []
        authority_index = self.indexes.get('authority_index', {})
        
        for level in authority_levels:
            if level in authority_index:
                for item in authority_index[level]:
                    content = self.get_chunk_content(item['chunk_id'])
                    if content and self.content_matches_query(content, query):
                        
                        result = QueryResult(
                            chunk_id=item['chunk_id'],
                            content=content,
                            source='federal' if item.get('source_type') else 'unknown',
                            source_type=item.get('source_type', ''),
                            authority_level=level,
                            authority_score=item.get('authority_score', 0),
                            section_reference=item.get('section_reference', ''),
                            relevance_score=self.calculate_relevance_score(content, query),
                            document_title=item.get('document_title', ''),
                            effective_date=item.get('effective_date', ''),
                            superseded_by=item.get('superseded_by', ''),
                            conflicts=[],
                            cross_references=[],
                            state_applications=[],
                            metadata=item
                        )
                        results.append(result)
        
        # Sort by authority score and relevance
        results.sort(key=lambda x: (x.authority_score, x.relevance_score), reverse=True)
        return results[:limit]
    
    def search_by_effective_date(self, query: str, date_range: Tuple[str, str] = None,
                                sort_by_date: bool = True, limit: int = 20) -> List[QueryResult]:
        """Search filtered by effective date range"""
        results = []
        effective_date_index = self.indexes.get('effective_date_index', {})
        
        for year, items in effective_date_index.items():
            # Filter by date range if specified
            if date_range:
                start_year, end_year = date_range
                if year != "Unknown" and (int(year) < int(start_year) or int(year) > int(end_year)):
                    continue
            
            for item in items:
                content = self.get_chunk_content(item['chunk_id'])
                if content and self.content_matches_query(content, query):
                    
                    result = QueryResult(
                        chunk_id=item['chunk_id'],
                        content=content,
                        source='federal',
                        source_type=item.get('source_type', ''),
                        authority_level=item.get('authority_level', ''),
                        authority_score=self.authority_hierarchy.get(item.get('authority_level', ''), 0),
                        section_reference=item.get('section_reference', ''),
                        relevance_score=self.calculate_relevance_score(content, query),
                        document_title=item.get('document_title', ''),
                        effective_date=item.get('effective_date', ''),
                        superseded_by=item.get('superseded_by', ''),
                        conflicts=[],
                        cross_references=[],
                        state_applications=[],
                        metadata=item
                    )
                    results.append(result)
        
        # Sort by date or relevance
        if sort_by_date:
            results.sort(key=lambda x: x.metadata.get('parsed_date', '1900-01-01'), reverse=True)
        else:
            results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:limit]
    
    def search_federal_state_mappings(self, query: str, states: List[str] = None,
                                    limit: int = 20) -> List[Dict]:
        """Search for federal rules and their state implementations"""
        results = []
        cross_ref_index = self.indexes.get('federal_state_cross_ref_index', {})
        
        for ref_key, items in cross_ref_index.items():
            for item in items:
                federal_content = item.get('federal_content_preview', '')
                
                if self.content_matches_query(federal_content, query):
                    implementing_states = item.get('implementing_states', [])
                    
                    # Filter by specific states if requested
                    if states:
                        implementing_states = [s for s in implementing_states if s in states]
                        if not implementing_states:
                            continue
                    
                    results.append({
                        'federal_chunk_id': item['federal_chunk_id'],
                        'federal_source_type': item.get('source_type', ''),
                        'federal_authority_level': item.get('authority_level', ''),
                        'section_reference': item.get('section_reference', ''),
                        'implementing_states': implementing_states,
                        'state_count': len(implementing_states),
                        'citation_contexts': item.get('citation_contexts', []),
                        'federal_content_preview': federal_content,
                        'document_title': item.get('document_title', ''),
                        'relevance_score': self.calculate_relevance_score(federal_content, query)
                    })
        
        # Sort by number of implementing states and relevance
        results.sort(key=lambda x: (x['state_count'], x['relevance_score']), reverse=True)
        return results[:limit]
    
    def search_with_conflict_analysis(self, query: str, include_conflicts: bool = True,
                                    resolve_conflicts: bool = True, limit: int = 20) -> List[QueryResult]:
        """Search with automatic conflict detection and resolution"""
        results = []
        
        # Get results from multiple sources
        federal_results = self.search_by_authority_level(
            query, ['statutory', 'regulatory', 'guidance', 'interpretive'], limit=limit*2
        )
        
        state_results = self.search_state_sources(query, limit=limit*2)
        
        # Combine and analyze for conflicts
        all_results = federal_results + state_results
        
        if include_conflicts:
            all_results = self.detect_conflicts(all_results, query)
        
        if resolve_conflicts:
            all_results = self.resolve_conflicts(all_results)
        
        # Sort by authority hierarchy and relevance
        all_results.sort(key=lambda x: (x.authority_score, x.relevance_score), reverse=True)
        
        return all_results[:limit]
    
    def search_state_sources(self, query: str, states: List[str] = None, limit: int = 20) -> List[QueryResult]:
        """
        Search state QAP sources using ChromaDB vector search
        INTERIM IMPLEMENTATION: Direct ChromaDB search until LLM hardware deployed
        TODO: Replace with semantic search when Llama-2-70b available
        """
        if not self.chroma_db:
            print("⚠️  ChromaDB not available - returning empty state search results")
            return []
        
        try:
            # Prepare filters for state-specific search
            filters = {}
            if states:
                # Filter by specified states
                filters["state_code"] = states
            
            # Execute optimized ChromaDB search if optimizer available
            if self.performance_optimizer:
                chroma_results, metrics = self.performance_optimizer.optimized_search(
                    query=query,
                    limit=limit,
                    filters=filters,
                    similarity_threshold=0.0
                )
                # Track performance metrics
                self.query_stats['total_queries'] += 1
                if metrics.execution_time_ms > 0:
                    self.query_stats['avg_response_time'] = (
                        (self.query_stats['avg_response_time'] * (self.query_stats['total_queries'] - 1) + 
                         metrics.execution_time_ms) / self.query_stats['total_queries']
                    )
            else:
                # Fallback to standard ChromaDB search
                chroma_results = self.chroma_db.search(
                    query=query,
                    limit=limit,
                    filters=filters,
                    similarity_threshold=0.0  # Accept all results for now
                )
            
            # Convert ChromaDB results to QueryResult format
            query_results = []
            for result in chroma_results:
                # Extract metadata
                metadata = result.get("metadata", {})
                
                query_result = QueryResult(
                    chunk_id=result.get("chunk_id", ""),
                    content=result.get("content", ""),
                    source=metadata.get("state_code", "unknown"),
                    source_type="QAP",  # All state results are QAP
                    authority_level="state_qap",
                    authority_score=self.authority_hierarchy.get("state_qap", 30),
                    section_reference=metadata.get("section_title", ""),
                    relevance_score=float(result.get("score", 0.0)),
                    document_title=f"{metadata.get('state_code', 'Unknown')} QAP",
                    effective_date="2025",  # Default for current QAPs
                    superseded_by="",
                    conflicts=[],
                    cross_references=[],
                    state_applications=[metadata.get("state_code", "")],
                    metadata=metadata
                )
                query_results.append(query_result)
            
            print(f"✅ State search returned {len(query_results)} results for query: '{query}' (states: {states})")
            return query_results
            
        except Exception as e:
            print(f"❌ ChromaDB state search failed: {e}")
            return []
    
    def cross_jurisdictional_comparison(self, query: str, comparison_type: str = 'federal_vs_states',
                                      target_states: List[str] = None) -> Dict:
        """Compare how different jurisdictions handle the same requirement"""
        
        if comparison_type == 'federal_vs_states':
            # Find federal requirement
            federal_results = self.search_by_authority_level(query, ['statutory', 'regulatory'], limit=5)
            
            # Find state implementations
            state_mappings = self.search_federal_state_mappings(query, target_states, limit=10)
            
            comparison = {
                'query': query,
                'federal_requirements': [
                    {
                        'source_type': r.source_type,
                        'authority_level': r.authority_level,
                        'section_reference': r.section_reference,
                        'content_preview': r.content[:300] + "...",
                        'effective_date': r.effective_date
                    } for r in federal_results
                ],
                'state_implementations': state_mappings,
                'analysis': {
                    'implementing_states_count': len(set().union(*[m['implementing_states'] for m in state_mappings])),
                    'variation_detected': len(state_mappings) > 1,
                    'federal_sources_count': len(federal_results)
                }
            }
            
            return comparison
        
        elif comparison_type == 'state_vs_state':
            # Compare specific states (would implement with QAP system integration)
            return {'comparison_type': comparison_type, 'note': 'State vs state comparison requires QAP integration'}
        
        return {}
    
    def advanced_entity_search(self, entity_type: str, entity_value: str = None, 
                             context_query: str = None, limit: int = 20) -> List[QueryResult]:
        """Search by specific entities (dates, money amounts, percentages, etc.)"""
        results = []
        federal_entity_index = self.indexes.get('federal_entity_index', {})
        
        if entity_type in federal_entity_index:
            for item in federal_entity_index[entity_type]:
                # Filter by entity value if specified
                if entity_value and entity_value.lower() not in item.get('value', '').lower():
                    continue
                
                content = self.get_chunk_content(item['chunk_id'])
                if content:
                    # Additional context filtering if specified
                    if context_query and not self.content_matches_query(content, context_query):
                        continue
                    
                    result = QueryResult(
                        chunk_id=item['chunk_id'],
                        content=content,
                        source='federal',
                        source_type=item.get('source_type', ''),
                        authority_level=item.get('authority_level', ''),
                        authority_score=self.authority_hierarchy.get(item.get('authority_level', ''), 0),
                        section_reference=item.get('section_reference', ''),
                        relevance_score=1.0,  # High relevance for exact entity matches
                        document_title='',
                        effective_date='',
                        superseded_by='',
                        conflicts=[],
                        cross_references=[],
                        state_applications=[],
                        metadata={
                            'entity_type': entity_type,
                            'entity_value': item.get('value', ''),
                            **item
                        }
                    )
                    results.append(result)
        
        # Sort by authority score
        results.sort(key=lambda x: x.authority_score, reverse=True)
        return results[:limit]
    
    def semantic_search_unified(self, query: str, search_namespace: str = 'unified',
                               ranking_strategy: str = 'authority_first', limit: int = 20, 
                               states: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Main unified search function with multiple ranking strategies"""
        
        self.query_stats['total_queries'] += 1
        self.query_stats['most_common_search_types'][search_namespace] += 1
        
        start_time = datetime.now()
        
        if search_namespace == 'federal':
            results = self.search_by_authority_level(query, 
                ['statutory', 'regulatory', 'guidance', 'interpretive'], limit)
        
        elif search_namespace == 'state':
            results = self.search_state_sources(query, states=states, limit=limit)
        
        elif search_namespace == 'unified':
            results = self.search_with_conflict_analysis(query, limit=limit)
        
        else:
            results = []
        
        # Apply ranking strategy
        if ranking_strategy == 'authority_first':
            results.sort(key=lambda x: (x.authority_score, x.relevance_score), reverse=True)
        elif ranking_strategy == 'chronological':
            results.sort(key=lambda x: x.effective_date, reverse=True)
        elif ranking_strategy == 'relevance':
            results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Update performance stats
        end_time = datetime.now()
        query_time = (end_time - start_time).total_seconds()
        self.query_stats['avg_response_time'] = (
            (self.query_stats['avg_response_time'] * (self.query_stats['total_queries'] - 1) + query_time) 
            / self.query_stats['total_queries']
        )
        
        # Convert QueryResult objects to dictionaries for API compatibility
        return [result.to_dict() for result in results]
    
    def get_chunk_content(self, chunk_id: str) -> str:
        """Retrieve full content for a chunk ID"""
        # Try federal content index first
        federal_content_index = self.indexes.get('federal_content_index', {})
        if chunk_id in federal_content_index:
            return federal_content_index[chunk_id].get('content', '')
        
        # If not found, would search in QAP indexes
        # This would integrate with existing QAP content retrieval
        return ""
    
    def content_matches_query(self, content: str, query: str) -> bool:
        """Simple content matching (would be enhanced with vector similarity)"""
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Split query into terms
        query_terms = re.findall(r'\b\w+\b', query_lower)
        
        # Check if all terms are present
        matches = sum(1 for term in query_terms if term in content_lower)
        return matches >= len(query_terms) * 0.6  # 60% of terms must match
    
    def calculate_relevance_score(self, content: str, query: str) -> float:
        """Calculate relevance score between content and query"""
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Simple TF-IDF-like scoring
        query_terms = re.findall(r'\b\w+\b', query_lower)
        content_terms = re.findall(r'\b\w+\b', content_lower)
        
        if not query_terms or not content_terms:
            return 0.0
        
        # Count term frequencies
        content_term_freq = Counter(content_terms)
        query_term_freq = Counter(query_terms)
        
        score = 0.0
        for term, freq in query_term_freq.items():
            if term in content_term_freq:
                # TF * IDF approximation
                tf = content_term_freq[term] / len(content_terms)
                score += tf * freq
        
        return min(score, 1.0)
    
    def detect_conflicts(self, results: List[QueryResult], query: str) -> List[QueryResult]:
        """Detect conflicts between federal and state sources"""
        # Group results by topic/section
        grouped_results = defaultdict(list)
        
        for result in results:
            # Simple grouping by section reference or content similarity
            group_key = result.section_reference or "general"
            grouped_results[group_key].append(result)
        
        # Detect conflicts within groups
        for group_key, group_results in grouped_results.items():
            if len(group_results) > 1:
                # Check for authority level conflicts
                authority_levels = set(r.authority_level for r in group_results)
                if len(authority_levels) > 1 and 'state_qap' in authority_levels:
                    # Potential federal-state conflict
                    for result in group_results:
                        if result.authority_level == 'state_qap':
                            federal_sources = [r for r in group_results if r.authority_level != 'state_qap']
                            if federal_sources:
                                result.conflicts = [f"Potential conflict with federal {r.source_type}" for r in federal_sources]
        
        return results
    
    def resolve_conflicts(self, results: List[QueryResult]) -> List[QueryResult]:
        """Resolve conflicts using authority hierarchy"""
        conflict_resolver = self.indexes.get('authority_conflict_resolver', {})
        hierarchy_scores = conflict_resolver.get('hierarchy_scores', self.authority_hierarchy)
        
        # Group conflicting results and promote higher authority
        resolved_results = []
        conflict_groups = defaultdict(list)
        
        for result in results:
            if result.conflicts:
                group_key = result.section_reference or result.content[:50]
                conflict_groups[group_key].append(result)
            else:
                resolved_results.append(result)
        
        # For each conflict group, promote highest authority
        for group_results in conflict_groups.values():
            # Sort by authority score
            group_results.sort(key=lambda x: x.authority_score, reverse=True)
            
            # Mark the highest authority as authoritative
            if group_results:
                highest_authority = group_results[0]
                highest_authority.conflicts = [f"Supersedes {len(group_results)-1} lower authority sources"]
                resolved_results.append(highest_authority)
                
                # Add lower authority sources with conflict notes
                for result in group_results[1:]:
                    result.conflicts = [f"Superseded by {highest_authority.source_type} {highest_authority.section_reference}"]
                    resolved_results.append(result)
        
        return resolved_results
    
    def export_search_results(self, results: List[QueryResult], query: str, 
                            export_format: str = 'json') -> str:
        """Export search results in various formats"""
        
        if export_format == 'json':
            export_data = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(results),
                'results': [
                    {
                        'chunk_id': r.chunk_id,
                        'content_preview': r.content[:200] + "...",
                        'source': r.source,
                        'source_type': r.source_type,
                        'authority_level': r.authority_level,
                        'authority_score': r.authority_score,
                        'section_reference': r.section_reference,
                        'relevance_score': r.relevance_score,
                        'effective_date': r.effective_date,
                        'conflicts': r.conflicts,
                        'document_title': r.document_title
                    } for r in results
                ]
            }
            return json.dumps(export_data, indent=2)
        
        elif export_format == 'markdown':
            md_content = f"# Search Results for: {query}\n\n"
            md_content += f"**Total Results:** {len(results)}  \n"
            md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n"
            
            for i, result in enumerate(results, 1):
                md_content += f"## {i}. {result.source_type} - {result.section_reference}\n\n"
                md_content += f"**Authority Level:** {result.authority_level} (Score: {result.authority_score})  \n"
                md_content += f"**Relevance:** {result.relevance_score:.2f}  \n"
                md_content += f"**Effective Date:** {result.effective_date}  \n"
                
                if result.conflicts:
                    md_content += f"**Conflicts:** {', '.join(result.conflicts)}  \n"
                
                md_content += f"\n{result.content[:300]}...\n\n---\n\n"
            
            return md_content
        
        return str(export_data)
    
    def benchmark_performance(self, test_queries: List[str] = None, iterations: int = 5) -> Dict[str, Any]:
        """Run comprehensive performance benchmark on the RAG system"""
        
        if test_queries is None:
            test_queries = [
                "minimum construction standards",
                "affordable housing requirements", 
                "tax credit allocation criteria",
                "qualified basis calculation",
                "income limits verification",
                "developer fee limitations",
                "geographic preference points",
                "compliance monitoring requirements",
                "community development priorities",
                "energy efficiency standards"
            ]
        
        print(f"🏁 Starting RAG Performance Benchmark")
        print(f"📊 Queries: {len(test_queries)} × {iterations} iterations = {len(test_queries) * iterations} total")
        
        if self.performance_optimizer:
            # Use the advanced performance optimizer
            from chromadb_performance_optimizer import benchmark_chromadb_performance
            benchmark_results = benchmark_chromadb_performance(self.chroma_db, test_queries, iterations)
            
            # Add RAG-specific metrics
            benchmark_results['rag_system_info'] = {
                'total_indexes_loaded': len(self.indexes),
                'chroma_db_available': self.chroma_db is not None,
                'performance_optimizer_enabled': True,
                'authority_hierarchy_levels': len(self.authority_hierarchy),
                'query_cache_enabled': True
            }
            
            return benchmark_results
        else:
            # Basic benchmark without optimizer
            print("⚠️  Running basic benchmark (performance optimizer not available)")
            
            import time
            start_time = time.time()
            total_queries = 0
            response_times = []
            
            for iteration in range(iterations):
                for query in test_queries:
                    query_start = time.time()
                    results = self.search_state_sources(query, limit=20)
                    query_time = (time.time() - query_start) * 1000
                    response_times.append(query_time)
                    total_queries += 1
            
            total_time = time.time() - start_time
            
            return {
                'basic_benchmark': True,
                'total_queries': total_queries,
                'total_time_seconds': total_time,
                'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
                'min_response_time_ms': min(response_times) if response_times else 0,
                'max_response_time_ms': max(response_times) if response_times else 0,
                'queries_per_second': total_queries / total_time if total_time > 0 else 0,
                'performance_grade': 'Unknown - upgrade to full optimizer for detailed analysis'
            }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report including optimizer metrics"""
        
        if self.performance_optimizer:
            return self.performance_optimizer.get_performance_report()
        else:
            return {
                'basic_stats': self.query_stats,
                'performance_optimizer_available': False,
                'recommendation': 'Install performance optimizer for detailed metrics'
            }

def main():
    """Example usage and testing"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    query_system = UnifiedLIHTCRAGQuery(base_dir)
    
    # Example searches
    print("🔍 Testing Unified LIHTC RAG Query System")
    
    # Test authority-based search
    print("\n1. Authority-based search for 'income limits':")
    results = query_system.search_by_authority_level("income limits", limit=5)
    for result in results:
        print(f"   {result.source_type} ({result.authority_level}): {result.section_reference}")
    
    # Test federal-state mapping search
    print("\n2. Federal-state mapping search for 'basis boost':")
    mappings = query_system.search_federal_state_mappings("basis boost", limit=3)
    for mapping in mappings:
        print(f"   {mapping['federal_source_type']}: {len(mapping['implementing_states'])} states")
    
    # Test cross-jurisdictional comparison
    print("\n3. Cross-jurisdictional comparison for 'compliance period':")
    comparison = query_system.cross_jurisdictional_comparison("compliance period")
    print(f"   Federal sources: {comparison.get('analysis', {}).get('federal_sources_count', 0)}")
    print(f"   Implementing states: {comparison.get('analysis', {}).get('implementing_states_count', 0)}")

if __name__ == "__main__":
    main()