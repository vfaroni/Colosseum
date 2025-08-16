#!/usr/bin/env python3
"""
Definitions Search Interface - Phase 2A
Professional definitions search with PDF source verification
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Import existing ChromaDB integration
import sys
sys.path.append(str(Path(__file__).parent.parent / "lihtc_analyst" / "priorcode" / "qap_rag" / "backend"))

try:
    from chroma_integration import ChromaVectorDatabase
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class DefinitionsSearchInterface:
    """Professional definitions search with source verification"""
    
    def __init__(self, definitions_dir: Path = None):
        """Initialize definitions search interface"""
        
        if definitions_dir is None:
            definitions_dir = Path(__file__).parent / "definitions_output"
        
        self.definitions_dir = definitions_dir
        self.definitions_database = {}
        self.definitions_index = {}
        
        # Load all definitions databases
        self._load_definitions_databases()
        
        # Initialize ChromaDB for enhanced search (optional)
        self.chroma_db = None
        if CHROMA_AVAILABLE:
            try:
                config_path = Path(__file__).parent.parent / "lihtc_analyst" / "priorcode" / "mac_studio_rag" / "config" / "mac_studio_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Create separate collection for definitions
                    config['vector_database']['collection_name'] = 'qap_definitions'
                    self.chroma_db = ChromaVectorDatabase(config)
                    print("✅ Definitions ChromaDB initialized")
            except Exception as e:
                print(f"⚠️  ChromaDB initialization failed: {e}")
    
    def _load_definitions_databases(self):
        """Load all definitions databases from directory"""
        
        if not self.definitions_dir.exists():
            print(f"⚠️  Definitions directory not found: {self.definitions_dir}")
            return
        
        definitions_files = list(self.definitions_dir.glob("*_definitions_database_*.json"))
        
        for definitions_file in definitions_files:
            try:
                with open(definitions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                state_code = data.get('state_code', 'Unknown')
                self.definitions_database[state_code] = data
                
                # Create search index
                for definition in data.get('definitions', []):
                    term = definition['term'].lower()
                    if term not in self.definitions_index:
                        self.definitions_index[term] = []
                    self.definitions_index[term].append({
                        'state': state_code,
                        'definition': definition
                    })
                
                print(f"📖 Loaded {len(data.get('definitions', []))} definitions from {state_code}")
                
            except Exception as e:
                print(f"⚠️  Error loading {definitions_file}: {e}")
        
        print(f"✅ Loaded definitions from {len(self.definitions_database)} states")
        print(f"📊 Total unique terms: {len(self.definitions_index)}")
    
    def search_definitions(self, query: str, states: List[str] = None, 
                          category: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search definitions with filters"""
        
        results = []
        query_lower = query.lower().strip()
        
        # Direct term lookup
        if query_lower in self.definitions_index:
            for entry in self.definitions_index[query_lower]:
                if states is None or entry['state'] in states:
                    if category is None or entry['definition']['category'] == category:
                        results.append(self._format_search_result(entry, 1.0))
        
        # Fuzzy search in terms
        for term, entries in self.definitions_index.items():
            if query_lower != term and query_lower in term:
                for entry in entries:
                    if states is None or entry['state'] in states:
                        if category is None or entry['definition']['category'] == category:
                            # Calculate similarity score
                            score = self._calculate_similarity(query_lower, term)
                            results.append(self._format_search_result(entry, score))
        
        # Search in definitions text
        for state, db_data in self.definitions_database.items():
            if states is None or state in states:
                for definition in db_data.get('definitions', []):
                    if category is None or definition['category'] == category:
                        definition_text = definition['definition'].lower()
                        if query_lower in definition_text and query_lower not in definition['term'].lower():
                            score = self._calculate_text_relevance(query_lower, definition_text)
                            if score > 0.3:  # Relevance threshold
                                results.append(self._format_search_result({
                                    'state': state,
                                    'definition': definition
                                }, score))
        
        # Remove duplicates and sort by score
        unique_results = {}
        for result in results:
            key = f"{result['state']}_{result['definition_id']}"
            if key not in unique_results or result['relevance_score'] > unique_results[key]['relevance_score']:
                unique_results[key] = result
        
        sorted_results = sorted(unique_results.values(), key=lambda x: x['relevance_score'], reverse=True)
        return sorted_results[:limit]
    
    def _format_search_result(self, entry: Dict, score: float) -> Dict[str, Any]:
        """Format search result with enhanced metadata"""
        
        definition = entry['definition']
        
        return {
            'definition_id': definition['definition_id'],
            'state': entry['state'],
            'term': definition['term'],
            'definition': definition['definition'],
            'section_reference': definition['section_reference'],
            'pdf_page': definition.get('pdf_page'),
            'category': definition['category'],
            'relevance_score': score,
            'source_verification': {
                'pdf_available': True,  # Would check actual PDF availability
                'view_source_url': f"/view_pdf/{entry['state']}_QAP_2025.pdf#page={definition.get('pdf_page', 1)}",
                'download_pdf_url': f"/download_pdf/{entry['state']}_QAP_2025.pdf"
            },
            'extraction_confidence': definition.get('extraction_confidence', 0.8),
            'pattern_used': definition.get('pattern_used', 'unknown')
        }
    
    def _calculate_similarity(self, query: str, term: str) -> float:
        """Calculate similarity between query and term"""
        
        # Simple similarity based on common characters and position
        common_chars = sum(1 for a, b in zip(query, term) if a == b)
        length_similarity = min(len(query), len(term)) / max(len(query), len(term))
        char_similarity = common_chars / max(len(query), len(term))
        
        return (length_similarity + char_similarity) / 2
    
    def _calculate_text_relevance(self, query: str, text: str) -> float:
        """Calculate relevance of query in definition text"""
        
        query_words = query.split()
        text_words = text.split()
        
        if not query_words or not text_words:
            return 0.0
        
        # Count query words in text
        matches = sum(1 for word in query_words if word in text_words)
        
        # Calculate density of matches
        density = matches / len(query_words)
        
        # Bonus for exact phrase match
        if query in text:
            density += 0.2
        
        return min(density, 1.0)
    
    def get_cross_jurisdictional_comparison(self, term: str) -> Dict[str, Any]:
        """Compare how different states define the same term"""
        
        term_lower = term.lower()
        
        if term_lower not in self.definitions_index:
            return {
                'term': term,
                'found_in_states': [],
                'total_states': 0,
                'comparison': {}
            }
        
        entries = self.definitions_index[term_lower]
        comparison = {}
        
        for entry in entries:
            state = entry['state']
            definition = entry['definition']
            
            comparison[state] = {
                'definition': definition['definition'],
                'section_reference': definition['section_reference'],
                'pdf_page': definition.get('pdf_page'),
                'category': definition['category'],
                'extraction_confidence': definition.get('extraction_confidence', 0.8)
            }
        
        return {
            'term': term,
            'found_in_states': list(comparison.keys()),
            'total_states': len(comparison),
            'comparison': comparison,
            'analysis': {
                'consistent_definitions': self._analyze_definition_consistency(comparison),
                'common_keywords': self._extract_common_keywords(comparison),
                'variations_detected': len(set(comp['definition'] for comp in comparison.values())) > 1
            }
        }
    
    def _analyze_definition_consistency(self, comparison: Dict) -> bool:
        """Analyze if definitions are consistent across states"""
        
        if len(comparison) <= 1:
            return True
        
        definitions = [comp['definition'].lower() for comp in comparison.values()]
        
        # Simple consistency check - if definitions are very similar
        first_def = definitions[0]
        similarities = [self._calculate_text_relevance(first_def, other_def) for other_def in definitions[1:]]
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 1.0
        return avg_similarity > 0.7  # Threshold for consistency
    
    def _extract_common_keywords(self, comparison: Dict) -> List[str]:
        """Extract common keywords across definitions"""
        
        all_words = []
        for comp in comparison.values():
            words = re.findall(r'\\b\\w+\\b', comp['definition'].lower())
            all_words.extend(words)
        
        # Count word frequency
        from collections import Counter
        word_counts = Counter(all_words)
        
        # Return words that appear in multiple definitions
        common_words = [word for word, count in word_counts.items() 
                       if count > 1 and len(word) > 3]
        
        return common_words[:10]  # Top 10 common words
    
    def create_definitions_report(self, output_file: Path = None) -> str:
        """Create comprehensive definitions report"""
        
        if output_file is None:
            output_file = Path(__file__).parent / "definitions_report.md"
        
        report_lines = [
            "# 📖 DEFINITIONS DATABASE REPORT",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 **DATABASE STATISTICS**",
            ""
        ]
        
        # Statistics
        total_definitions = sum(len(db['definitions']) for db in self.definitions_database.values())
        unique_terms = len(self.definitions_index)
        
        report_lines.extend([
            f"- **Total Definitions**: {total_definitions:,}",
            f"- **Unique Terms**: {unique_terms:,}",
            f"- **States Covered**: {len(self.definitions_database)}",
            f"- **Average Definitions per State**: {total_definitions // len(self.definitions_database) if self.definitions_database else 0}",
            ""
        ])
        
        # Category breakdown
        all_categories = {}
        for db in self.definitions_database.values():
            for definition in db.get('definitions', []):
                category = definition['category']
                all_categories[category] = all_categories.get(category, 0) + 1
        
        report_lines.extend([
            "## 🏷️ **CATEGORIES**",
            ""
        ])
        
        for category, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{category.title()}**: {count} definitions")
        
        report_lines.extend(["", "## 🔍 **SAMPLE DEFINITIONS**", ""])
        
        # Sample definitions from each state
        for state, db in self.definitions_database.items():
            report_lines.extend([
                f"### {state} Definitions",
                ""
            ])
            
            sample_definitions = db.get('definitions', [])[:3]  # First 3
            for definition in sample_definitions:
                report_lines.extend([
                    f"**{definition['term']}** ({definition['section_reference']})",
                    f"{definition['definition'][:200]}...",
                    f"*Category: {definition['category']}, PDF Page: {definition.get('pdf_page', 'Unknown')}*",
                    ""
                ])
        
        # Multi-state terms
        multi_state_terms = {term: entries for term, entries in self.definitions_index.items() 
                           if len(entries) > 1}
        
        if multi_state_terms:
            report_lines.extend([
                "## 🔄 **CROSS-JURISDICTIONAL TERMS**",
                f"*Terms defined in multiple states: {len(multi_state_terms)}*",
                ""
            ])
            
            for term, entries in list(multi_state_terms.items())[:5]:  # Top 5
                states_list = [entry['state'] for entry in entries]
                report_lines.append(f"- **{term.title()}**: {', '.join(states_list)}")
        
        report_content = "\\n".join(report_lines)
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Definitions report saved to: {output_file}")
        return report_content
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        
        total_definitions = sum(len(db['definitions']) for db in self.definitions_database.values())
        
        # Category statistics
        category_stats = {}
        confidence_stats = []
        
        for db in self.definitions_database.values():
            for definition in db.get('definitions', []):
                category = definition['category']
                category_stats[category] = category_stats.get(category, 0) + 1
                confidence_stats.append(definition.get('extraction_confidence', 0.8))
        
        avg_confidence = sum(confidence_stats) / len(confidence_stats) if confidence_stats else 0
        
        return {
            'total_definitions': total_definitions,
            'unique_terms': len(self.definitions_index),
            'states_covered': len(self.definitions_database),
            'categories': category_stats,
            'average_confidence': round(avg_confidence, 3),
            'cross_jurisdictional_terms': len([term for term, entries in self.definitions_index.items() if len(entries) > 1])
        }

def main():
    """Test the definitions search interface"""
    
    print("🔍 Testing Definitions Search Interface...")
    
    try:
        # Initialize search interface
        search_interface = DefinitionsSearchInterface()
        
        # Get database stats
        stats = search_interface.get_database_stats()
        print(f"\\n📊 **DATABASE STATISTICS**:")
        print(f"Total definitions: {stats['total_definitions']}")
        print(f"Unique terms: {stats['unique_terms']}")
        print(f"States covered: {stats['states_covered']}")
        print(f"Average confidence: {stats['average_confidence']}")
        
        # Test searches
        test_queries = [
            "accessible housing",
            "qualified basis",
            "income limits",
            "allocation"
        ]
        
        print(f"\\n🔍 **TEST SEARCHES**:")
        for query in test_queries:
            results = search_interface.search_definitions(query, limit=3)
            print(f"\\nQuery: '{query}' ({len(results)} results)")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. **{result['term']}** ({result['state']})")
                print(f"     {result['definition'][:100]}...")
                print(f"     Score: {result['relevance_score']:.2f}, Page: {result['pdf_page']}")
        
        # Test cross-jurisdictional comparison
        if stats['cross_jurisdictional_terms'] > 0:
            print(f"\\n🔄 **CROSS-JURISDICTIONAL COMPARISON**:")
            # Find a term that exists in multiple states
            multi_state_term = None
            for term, entries in search_interface.definitions_index.items():
                if len(entries) > 1:
                    multi_state_term = term
                    break
            
            if multi_state_term:
                comparison = search_interface.get_cross_jurisdictional_comparison(multi_state_term)
                print(f"Term: '{multi_state_term.title()}'")
                print(f"Found in {comparison['total_states']} states: {', '.join(comparison['found_in_states'])}")
                print(f"Consistent definitions: {comparison['analysis']['consistent_definitions']}")
        
        # Create report
        report = search_interface.create_definitions_report()
        print(f"\\n✅ Definitions search interface test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()