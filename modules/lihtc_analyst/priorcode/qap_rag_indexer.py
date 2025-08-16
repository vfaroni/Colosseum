#!/usr/bin/env python3
"""
QAP RAG Indexing System
Creates searchable indexes for RAG implementation across all processed QAP chunks
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from collections import defaultdict
import re

class QAPRAGIndexer:
    """Create comprehensive indexes for RAG search across QAP chunks"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.processed_dir = self.base_dir / "QAP" / "_processed"
        self.index_dir = self.processed_dir / "_indexes"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Load master index
        self.master_index = self.load_master_index()
        
        # Initialize indexes
        self.content_index = {}
        self.entity_index = defaultdict(list)
        self.section_index = defaultdict(list)
        self.program_index = defaultdict(list)
        self.state_index = defaultdict(list)
        self.keyword_index = defaultdict(set)
        
    def load_master_index(self) -> Dict:
        """Load the master chunk index"""
        master_file = self.processed_dir / "master_chunk_index.json"
        if master_file.exists():
            with open(master_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_all_chunks(self) -> List[Dict]:
        """Load all processed chunks from all states"""
        all_chunks = []
        
        for state_code in self.master_index.get('states_processed', []):
            state_file = self.processed_dir / state_code / f"{state_code}_all_chunks.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    chunks = json.load(f)
                    all_chunks.extend(chunks)
        
        return all_chunks
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search indexing"""
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out common stop words and short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'under', 'over', 'shall', 'will', 'must',
            'may', 'can', 'should', 'would', 'could', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        keywords = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def create_content_index(self, chunks: List[Dict]):
        """Create full-text content index"""
        print("📝 Creating content index...")
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            content = chunk.get('content', '')
            
            # Store full content
            self.content_index[chunk_id] = {
                'content': content,
                'state_code': chunk['state_code'],
                'section_title': chunk.get('section_title', ''),
                'program_type': chunk.get('program_type', 'both'),
                'content_type': chunk.get('content_type', 'text'),
                'chunk_size': chunk.get('chunk_size', 0),
                'page_number': chunk.get('page_number', 0),
                'document_title': chunk.get('document_title', ''),
                'entities': chunk.get('entities', []),
                'cross_references': chunk.get('cross_references', [])
            }
            
            # Extract and index keywords
            keywords = self.extract_keywords(content)
            for keyword in keywords:
                self.keyword_index[keyword].add(chunk_id)
    
    def create_entity_index(self, chunks: List[Dict]):
        """Create entity-based index (dates, money, percentages, etc.)"""
        print("🏷️  Creating entity index...")
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            entities = chunk.get('entities', [])
            
            for entity in entities:
                if ':' in entity:
                    entity_type, entity_value = entity.split(':', 1)
                    self.entity_index[entity_type].append({
                        'chunk_id': chunk_id,
                        'value': entity_value,
                        'state_code': chunk['state_code'],
                        'section_title': chunk.get('section_title', '')
                    })
    
    def create_section_index(self, chunks: List[Dict]):
        """Create section-based index"""
        print("📑 Creating section index...")
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            section = chunk.get('section_title', 'Unknown')
            
            self.section_index[section].append({
                'chunk_id': chunk_id,
                'state_code': chunk['state_code'],
                'program_type': chunk.get('program_type', 'both'),
                'content_type': chunk.get('content_type', 'text'),
                'chunk_size': chunk.get('chunk_size', 0)
            })
    
    def create_program_index(self, chunks: List[Dict]):
        """Create program type index (9%, 4%, both)"""
        print("🎯 Creating program index...")
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            program_type = chunk.get('program_type', 'both')
            
            self.program_index[program_type].append({
                'chunk_id': chunk_id,
                'state_code': chunk['state_code'],
                'section_title': chunk.get('section_title', ''),
                'content_type': chunk.get('content_type', 'text')
            })
    
    def create_state_index(self, chunks: List[Dict]):
        """Create state-based index"""
        print("🗺️  Creating state index...")
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            state_code = chunk['state_code']
            
            self.state_index[state_code].append({
                'chunk_id': chunk_id,
                'section_title': chunk.get('section_title', ''),
                'program_type': chunk.get('program_type', 'both'),
                'content_type': chunk.get('content_type', 'text'),
                'document_title': chunk.get('document_title', ''),
                'page_number': chunk.get('page_number', 0)
            })
    
    def create_similarity_index(self, chunks: List[Dict]):
        """Create index for finding similar content across states"""
        print("🔍 Creating similarity index...")
        
        similarity_index = defaultdict(list)
        
        # Group chunks by similar section titles
        section_groups = defaultdict(list)
        for chunk in chunks:
            section_title = chunk.get('section_title', '').lower()
            # Normalize section titles
            normalized_section = re.sub(r'[^\w\s]', '', section_title)
            normalized_section = re.sub(r'\s+', ' ', normalized_section).strip()
            
            if normalized_section:
                section_groups[normalized_section].append({
                    'chunk_id': chunk['chunk_id'],
                    'state_code': chunk['state_code'],
                    'original_title': chunk.get('section_title', ''),
                    'program_type': chunk.get('program_type', 'both')
                })
        
        # Keep only sections that appear in multiple states
        for section, chunk_list in section_groups.items():
            states_in_section = set(c['state_code'] for c in chunk_list)
            if len(states_in_section) > 1:  # Cross-state similarity
                similarity_index[section] = chunk_list
        
        return dict(similarity_index)
    
    def create_search_index(self):
        """Create comprehensive search index"""
        print("🔎 Creating advanced search index...")
        
        # Create inverted index for fast search
        inverted_index = defaultdict(set)
        
        for keyword, chunk_ids in self.keyword_index.items():
            inverted_index[keyword] = chunk_ids
        
        # Add entity-based search terms
        for entity_type, entities in self.entity_index.items():
            for entity in entities:
                # Add entity values as searchable terms
                entity_keywords = self.extract_keywords(entity['value'])
                for keyword in entity_keywords:
                    inverted_index[f"{entity_type}_{keyword}"].add(entity['chunk_id'])
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in inverted_index.items()}
    
    def save_indexes(self):
        """Save all indexes to files"""
        print("💾 Saving indexes...")
        
        # Convert sets to lists for JSON serialization
        keyword_index_serializable = {
            k: list(v) for k, v in self.keyword_index.items()
        }
        
        indexes_to_save = {
            'content_index.json': self.content_index,
            'entity_index.json': dict(self.entity_index),
            'section_index.json': dict(self.section_index),
            'program_index.json': dict(self.program_index),
            'state_index.json': dict(self.state_index),
            'keyword_index.json': keyword_index_serializable
        }
        
        # Save each index
        for filename, index_data in indexes_to_save.items():
            filepath = self.index_dir / filename
            with open(filepath, 'w') as f:
                json.dump(index_data, f, indent=2)
        
        # Create similarity index
        chunks = self.load_all_chunks()
        similarity_index = self.create_similarity_index(chunks)
        with open(self.index_dir / 'similarity_index.json', 'w') as f:
            json.dump(similarity_index, f, indent=2)
        
        # Create search index
        search_index = self.create_search_index()
        with open(self.index_dir / 'search_index.json', 'w') as f:
            json.dump(search_index, f, indent=2)
    
    def create_search_statistics(self, chunks: List[Dict]) -> Dict:
        """Create search statistics for the RAG system"""
        stats = {
            'total_chunks': len(chunks),
            'total_states': len(set(c['state_code'] for c in chunks)),
            'total_keywords': len(self.keyword_index),
            'total_entities': sum(len(entities) for entities in self.entity_index.values()),
            'total_sections': len(self.section_index),
            'avg_chunk_size': sum(c.get('chunk_size', 0) for c in chunks) / len(chunks) if chunks else 0,
            'content_type_breakdown': {},
            'program_type_breakdown': {},
            'state_breakdown': {},
            'entity_type_breakdown': {}
        }
        
        # Count content types
        for chunk in chunks:
            content_type = chunk.get('content_type', 'unknown')
            stats['content_type_breakdown'][content_type] = stats['content_type_breakdown'].get(content_type, 0) + 1
        
        # Count program types
        for chunk in chunks:
            program_type = chunk.get('program_type', 'unknown')
            stats['program_type_breakdown'][program_type] = stats['program_type_breakdown'].get(program_type, 0) + 1
        
        # Count by state
        for chunk in chunks:
            state = chunk.get('state_code', 'unknown')
            stats['state_breakdown'][state] = stats['state_breakdown'].get(state, 0) + 1
        
        # Count entity types
        for entity_type, entities in self.entity_index.items():
            stats['entity_type_breakdown'][entity_type] = len(entities)
        
        return stats
    
    def build_all_indexes(self) -> Dict:
        """Build all indexes and return statistics"""
        print("🏗️  Building comprehensive RAG indexes...")
        
        # Load all chunks
        chunks = self.load_all_chunks()
        print(f"📦 Loaded {len(chunks)} chunks from {len(self.master_index.get('states_processed', []))} states")
        
        if not chunks:
            print("❌ No chunks found to index!")
            return {}
        
        # Create all indexes
        self.create_content_index(chunks)
        self.create_entity_index(chunks)
        self.create_section_index(chunks)
        self.create_program_index(chunks)
        self.create_state_index(chunks)
        
        # Save indexes
        self.save_indexes()
        
        # Generate statistics
        stats = self.create_search_statistics(chunks)
        
        # Save statistics
        stats_file = self.index_dir / 'indexing_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def create_rag_config(self, stats: Dict):
        """Create RAG system configuration file"""
        print("⚙️  Creating RAG configuration...")
        
        config = {
            'version': '1.0',
            'created_date': datetime.now().isoformat(),
            'data_sources': {
                'states_processed': self.master_index.get('states_processed', []),
                'total_chunks': stats.get('total_chunks', 0),
                'total_documents': len(set(chunk['document_title'] for chunk in self.load_all_chunks()))
            },
            'index_files': {
                'content_index': str(self.index_dir / 'content_index.json'),
                'entity_index': str(self.index_dir / 'entity_index.json'),
                'section_index': str(self.index_dir / 'section_index.json'),
                'program_index': str(self.index_dir / 'program_index.json'),
                'state_index': str(self.index_dir / 'state_index.json'),
                'keyword_index': str(self.index_dir / 'keyword_index.json'),
                'similarity_index': str(self.index_dir / 'similarity_index.json'),
                'search_index': str(self.index_dir / 'search_index.json')
            },
            'search_capabilities': {
                'full_text_search': True,
                'entity_search': True,
                'program_specific_search': True,
                'cross_state_comparison': True,
                'section_based_search': True,
                'similarity_search': True
            },
            'supported_queries': [
                'What are the scoring criteria for 9% LIHTC in Texas?',
                'How do AMI requirements differ between states?',
                'What are the deadlines for California vs Hawaii applications?',
                'Find all references to minimum density requirements',
                'Compare preservation policies across states'
            ],
            'statistics': stats
        }
        
        config_file = self.index_dir / 'rag_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def generate_indexing_report(self, stats: Dict) -> str:
        """Generate comprehensive indexing report"""
        report = f"""
=== QAP RAG INDEXING REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

INDEXING RESULTS:
- Total Chunks Indexed: {stats.get('total_chunks', 0):,}
- States Processed: {stats.get('total_states', 0)} ({', '.join(self.master_index.get('states_processed', []))})
- Total Keywords: {stats.get('total_keywords', 0):,}
- Total Entities: {stats.get('total_entities', 0):,}
- Total Sections: {stats.get('total_sections', 0):,}
- Average Chunk Size: {stats.get('avg_chunk_size', 0):.0f} characters

CONTENT TYPE BREAKDOWN:
"""
        
        for content_type, count in stats.get('content_type_breakdown', {}).items():
            report += f"- {content_type.title()}: {count:,} chunks\n"
        
        report += f"""
PROGRAM TYPE BREAKDOWN:
"""
        for program_type, count in stats.get('program_type_breakdown', {}).items():
            report += f"- {program_type}: {count:,} chunks\n"
        
        report += f"""
STATE BREAKDOWN:
"""
        for state, count in stats.get('state_breakdown', {}).items():
            report += f"- {state}: {count:,} chunks\n"
        
        report += f"""
ENTITY TYPE BREAKDOWN:
"""
        for entity_type, count in stats.get('entity_type_breakdown', {}).items():
            report += f"- {entity_type}: {count:,} entities\n"
        
        report += f"""
INDEX FILES CREATED:
- Content Index: {self.index_dir}/content_index.json
- Entity Index: {self.index_dir}/entity_index.json
- Section Index: {self.index_dir}/section_index.json
- Program Index: {self.index_dir}/program_index.json
- State Index: {self.index_dir}/state_index.json
- Keyword Index: {self.index_dir}/keyword_index.json
- Similarity Index: {self.index_dir}/similarity_index.json
- Search Index: {self.index_dir}/search_index.json
- RAG Config: {self.index_dir}/rag_config.json

NEXT STEPS:
1. Implement RAG query interface
2. Build vector database for semantic search
3. Create web interface for multi-state QAP queries
4. Integrate with existing CTCAC analysis tools
"""
        
        return report

def main():
    """Build comprehensive RAG indexes for all processed QAP chunks"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🔍 Starting QAP RAG Indexing System...")
    
    indexer = QAPRAGIndexer(base_dir)
    
    # Build all indexes
    stats = indexer.build_all_indexes()
    
    if stats:
        # Create RAG configuration
        config = indexer.create_rag_config(stats)
        
        # Generate and display report
        report = indexer.generate_indexing_report(stats)
        print(report)
        
        # Save report
        report_file = indexer.index_dir / f"indexing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"💾 Report saved to: {report_file}")
        
        print("🎯 TASK COMPLETED: Build indexing system for RAG implementation")
    else:
        print("❌ No data to index - check PDF processing results")

if __name__ == "__main__":
    main()