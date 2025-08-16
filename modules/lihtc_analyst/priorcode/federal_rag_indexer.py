#!/usr/bin/env python3
"""
Federal LIHTC RAG Indexing System
Creates federal-specific searchable indexes and integrates with existing 49-state QAP RAG system
Extends the proven QAP indexing approach with federal authority, effective dates, and cross-references
"""

import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from collections import defaultdict
import re

class FederalRAGIndexer:
    """Create federal-specific indexes and integrate with existing QAP RAG system"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.federal_processed_dir = self.base_dir / "federal" / "LIHTC_Federal_Sources" / "_processed"
        self.qap_processed_dir = self.base_dir / "QAP" / "_processed"
        self.federal_index_dir = self.federal_processed_dir / "_indexes"
        self.federal_index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize federal-specific indexes
        self.authority_index = defaultdict(list)        # Authority hierarchy index
        self.effective_date_index = defaultdict(list)   # Time-based index
        self.federal_state_cross_ref_index = defaultdict(list)  # Federal-state mapping
        
        # Enhanced traditional indexes for federal content
        self.federal_content_index = {}
        self.federal_entity_index = defaultdict(list)
        self.federal_section_index = defaultdict(list)
        
        # Integration with existing QAP system
        self.unified_master_index = {}
        
    def load_federal_chunks(self) -> List[Dict]:
        """Load all processed federal chunks"""
        all_chunks = []
        
        chunks_dir = self.federal_processed_dir / "chunks"
        if not chunks_dir.exists():
            print(f"⚠️  Federal chunks directory not found: {chunks_dir}")
            return all_chunks
        
        for chunk_file in chunks_dir.glob("federal_*.json"):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunks = json.load(f)
                    all_chunks.extend(chunks)
                    print(f"📁 Loaded {len(chunks)} chunks from {chunk_file.name}")
            except Exception as e:
                print(f"❌ Error loading {chunk_file}: {e}")
        
        return all_chunks
    
    def load_existing_qap_master_index(self) -> Dict:
        """Load the existing QAP master index for integration"""
        master_file = self.qap_processed_dir / "master_chunk_index.json"
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def create_authority_index(self, chunks: List[Dict]):
        """Create authority hierarchy index (statutory > regulatory > guidance > interpretive)"""
        print("⚖️  Creating federal authority hierarchy index...")
        
        authority_hierarchy = {
            'statutory': 100,    # IRC Section 42
            'regulatory': 80,    # CFR regulations  
            'guidance': 60,      # Revenue Procedures
            'interpretive': 40   # PLRs, Revenue Rulings
        }
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            authority_level = chunk.get('authority_level', 'interpretive')
            authority_score = authority_hierarchy.get(authority_level, 0)
            
            self.authority_index[authority_level].append({
                'chunk_id': chunk_id,
                'source_type': chunk.get('source_type', ''),
                'section_reference': chunk.get('section_reference', ''),
                'authority_score': authority_score,
                'document_title': chunk.get('document_title', ''),
                'content_preview': chunk.get('content', '')[:200] + "...",
                'effective_date': chunk.get('effective_date', ''),
                'superseded_by': chunk.get('superseded_by', '')
            })
        
        # Sort each authority level by authority score and effective date
        for authority_level in self.authority_index:
            self.authority_index[authority_level].sort(
                key=lambda x: (x['authority_score'], x['effective_date']), 
                reverse=True
            )
        
        print(f"    ✅ Indexed {sum(len(chunks) for chunks in self.authority_index.values())} chunks by authority level")
    
    def create_effective_date_index(self, chunks: List[Dict]):
        """Create time-based index for federal rule changes"""
        print("📅 Creating effective date index...")
        
        # Group by year and create chronological ordering
        date_pattern = re.compile(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})')
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            effective_date = chunk.get('effective_date', '')
            
            # Parse effective date
            year = "Unknown"
            month = "Unknown"
            parsed_date = None
            
            if effective_date:
                match = date_pattern.search(effective_date)
                if match:
                    month_name, day, year = match.groups()
                    year = int(year)
                    
                    # Convert month name to number
                    month_mapping = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    month_num = month_mapping.get(month_name.lower(), 1)
                    
                    try:
                        parsed_date = date(year, month_num, int(day))
                        month = f"{year}-{month_num:02d}"
                    except ValueError:
                        pass
            
            # Index by year
            year_key = str(year)
            self.effective_date_index[year_key].append({
                'chunk_id': chunk_id,
                'source_type': chunk.get('source_type', ''),
                'authority_level': chunk.get('authority_level', ''),
                'section_reference': chunk.get('section_reference', ''),
                'effective_date': effective_date,
                'parsed_date': parsed_date.isoformat() if parsed_date else None,
                'month': month,
                'document_title': chunk.get('document_title', ''),
                'superseded_by': chunk.get('superseded_by', ''),
                'content_preview': chunk.get('content', '')[:200] + "..."
            })
        
        # Sort each year by parsed date
        for year in self.effective_date_index:
            self.effective_date_index[year].sort(
                key=lambda x: x['parsed_date'] or '1900-01-01',
                reverse=True  # Most recent first
            )
        
        print(f"    ✅ Indexed {sum(len(chunks) for chunks in self.effective_date_index.values())} chunks by effective date")
    
    def create_federal_state_cross_reference_index(self, chunks: List[Dict]):
        """Create index mapping federal rules to state implementations"""
        print("🔗 Creating federal-state cross-reference index...")
        
        # Load QAP chunks to find state references to federal sources
        qap_chunks = self.load_qap_chunks_for_cross_reference()
        
        # Pattern to identify federal references in state QAPs
        federal_patterns = {
            'IRC_Section_42': [
                r'26\s+U\.?S\.?C\.?\s*§?\s*42',
                r'[Ss]ection\s+42',
                r'IRC\s+[Ss]ection\s+42',
                r'Internal\s+Revenue\s+Code\s+[Ss]ection\s+42'
            ],
            'CFR_1_42': [
                r'26\s+CFR\s*§?\s*1\.42',
                r'Treasury\s+Regulation\s*§?\s*1\.42',
                r'Reg\.?\s*§?\s*1\.42'
            ],
            'Revenue_Procedures': [
                r'Rev\.?\s*Proc\.?\s*\d{4}-\d+',
                r'Revenue\s+Procedure\s+\d{4}-\d+'
            ]
        }
        
        # Map federal chunks to their implementing states
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            source_type = chunk.get('source_type', '')
            section_ref = chunk.get('section_reference', '')
            content = chunk.get('content', '')
            
            # Find state QAPs that reference this federal source
            implementing_states = []
            citation_contexts = []
            
            # Search through QAP chunks for references
            for state_chunk in qap_chunks:
                state_content = state_chunk.get('content', '').lower()
                
                # Check if this QAP chunk cites the federal source
                patterns = federal_patterns.get(source_type, [])
                for pattern in patterns:
                    if re.search(pattern, state_content, re.IGNORECASE):
                        state_code = state_chunk.get('state_code', '')
                        if state_code and state_code not in implementing_states:
                            implementing_states.append(state_code)
                            
                            # Extract citation context
                            match = re.search(pattern, state_content, re.IGNORECASE)
                            if match:
                                start = max(0, match.start() - 100)
                                end = min(len(state_content), match.end() + 100)
                                context = state_content[start:end].strip()
                                citation_contexts.append({
                                    'state': state_code,
                                    'context': context,
                                    'section': state_chunk.get('section_title', '')
                                })
            
            # Create cross-reference entry
            cross_ref_key = f"{source_type}_{section_ref}".replace(' ', '_').replace('§', 'sec')
            
            self.federal_state_cross_ref_index[cross_ref_key].append({
                'federal_chunk_id': chunk_id,
                'source_type': source_type,
                'authority_level': chunk.get('authority_level', ''),
                'section_reference': section_ref,
                'implementing_states': implementing_states,
                'state_count': len(implementing_states),
                'citation_contexts': citation_contexts,
                'federal_content_preview': content[:200] + "...",
                'document_title': chunk.get('document_title', '')
            })
        
        print(f"    ✅ Created {len(self.federal_state_cross_ref_index)} federal-state cross-references")
    
    def load_qap_chunks_for_cross_reference(self) -> List[Dict]:
        """Load QAP chunks for cross-reference analysis (lightweight version)"""
        qap_chunks = []
        
        # Load master QAP index
        qap_master = self.load_existing_qap_master_index()
        states_processed = qap_master.get('states_processed', [])
        
        # Sample from each state (to avoid loading massive dataset)
        for state_code in states_processed[:10]:  # Limit to first 10 states for initial implementation
            state_file = self.qap_processed_dir / state_code / f"{state_code}_all_chunks.json"
            if state_file.exists():
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        chunks = json.load(f)
                        # Sample chunks for performance
                        sample_size = min(50, len(chunks))
                        qap_chunks.extend(chunks[:sample_size])
                except Exception as e:
                    print(f"    ⚠️  Error loading QAP chunks from {state_code}: {e}")
        
        return qap_chunks
    
    def create_enhanced_federal_indexes(self, chunks: List[Dict]):
        """Create enhanced versions of traditional indexes for federal content"""
        print("📊 Creating enhanced federal content indexes...")
        
        # Federal Content Index (similar to QAP but with federal-specific metadata)
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            
            self.federal_content_index[chunk_id] = {
                'content': chunk.get('content', ''),
                'source_type': chunk.get('source_type', ''),
                'authority_level': chunk.get('authority_level', ''),
                'section_reference': chunk.get('section_reference', ''),
                'document_title': chunk.get('document_title', ''),
                'effective_date': chunk.get('effective_date', ''),
                'superseded_by': chunk.get('superseded_by', ''),
                'content_type': chunk.get('content_type', ''),
                'chunk_size': chunk.get('chunk_size', 0),
                'entities': chunk.get('entities', []),
                'cross_references': chunk.get('cross_references', []),
                'state_applications': chunk.get('state_applications', [])
            }
        
        # Federal Entity Index
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            entities = chunk.get('entities', [])
            
            for entity in entities:
                if ':' in entity:
                    entity_type, entity_value = entity.split(':', 1)
                    self.federal_entity_index[entity_type].append({
                        'chunk_id': chunk_id,
                        'value': entity_value,
                        'source_type': chunk.get('source_type', ''),
                        'authority_level': chunk.get('authority_level', ''),
                        'section_reference': chunk.get('section_reference', '')
                    })
        
        # Federal Section Index  
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            section_ref = chunk.get('section_reference', 'Unknown')
            
            self.federal_section_index[section_ref].append({
                'chunk_id': chunk_id,
                'source_type': chunk.get('source_type', ''),
                'authority_level': chunk.get('authority_level', ''),
                'content_type': chunk.get('content_type', ''),
                'chunk_size': chunk.get('chunk_size', 0),
                'effective_date': chunk.get('effective_date', '')
            })
        
        print(f"    ✅ Enhanced federal indexes created")
    
    def create_unified_master_index(self, federal_chunks: List[Dict]):
        """Create unified master index combining federal and QAP systems"""
        print("🔄 Creating unified master index...")
        
        # Load existing QAP master index
        qap_master = self.load_existing_qap_master_index()
        
        # Create unified index structure
        self.unified_master_index = {
            'system_info': {
                'created_date': datetime.now().isoformat(),
                'federal_chunks_count': len(federal_chunks),
                'qap_chunks_count': qap_master.get('total_chunks', 0),
                'total_unified_chunks': len(federal_chunks) + qap_master.get('total_chunks', 0),
                'federal_sources_processed': len(set(chunk.get('source_type', '') for chunk in federal_chunks)),
                'qap_states_processed': len(qap_master.get('states_processed', [])),
                'index_types': {
                    'federal_specific': ['authority_index', 'effective_date_index', 'federal_state_cross_ref_index'],
                    'enhanced_traditional': ['federal_content_index', 'federal_entity_index', 'federal_section_index'],
                    'qap_existing': ['content_index', 'entity_index', 'section_index', 'program_index', 
                                   'state_index', 'keyword_index', 'similarity_index', 'search_index']
                }
            },
            'federal_sources': {
                source_type: {
                    'count': len([c for c in federal_chunks if c.get('source_type') == source_type]),
                    'authority_level': next((c.get('authority_level') for c in federal_chunks 
                                           if c.get('source_type') == source_type), 'unknown')
                } for source_type in set(chunk.get('source_type', '') for chunk in federal_chunks)
            },
            'authority_hierarchy': {
                'statutory': len([c for c in federal_chunks if c.get('authority_level') == 'statutory']),
                'regulatory': len([c for c in federal_chunks if c.get('authority_level') == 'regulatory']),
                'guidance': len([c for c in federal_chunks if c.get('authority_level') == 'guidance']),
                'interpretive': len([c for c in federal_chunks if c.get('authority_level') == 'interpretive'])
            },
            'integration_stats': {
                'federal_state_cross_references': len(self.federal_state_cross_ref_index),
                'effective_date_coverage': len(self.effective_date_index),
                'authority_levels_indexed': len(self.authority_index)
            }
        }
        
        print(f"    ✅ Unified master index created with {self.unified_master_index['system_info']['total_unified_chunks']} total chunks")
    
    def save_all_indexes(self):
        """Save all federal indexes to JSON files"""
        print("💾 Saving federal indexes...")
        
        indexes_to_save = {
            'authority_index.json': dict(self.authority_index),
            'effective_date_index.json': dict(self.effective_date_index),
            'federal_state_cross_ref_index.json': dict(self.federal_state_cross_ref_index),
            'federal_content_index.json': self.federal_content_index,
            'federal_entity_index.json': dict(self.federal_entity_index),
            'federal_section_index.json': dict(self.federal_section_index),
            'unified_master_index.json': self.unified_master_index
        }
        
        for filename, index_data in indexes_to_save.items():
            index_path = self.federal_index_dir / filename
            
            try:
                with open(index_path, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, indent=2, ensure_ascii=False, default=str)
                print(f"    ✅ Saved {filename} ({len(index_data)} entries)")
            except Exception as e:
                print(f"    ❌ Error saving {filename}: {e}")
    
    def build_all_federal_indexes(self):
        """Build comprehensive federal RAG indexes"""
        print("🇺🇸 Starting Federal RAG Index Build")
        print(f"📁 Federal source directory: {self.federal_processed_dir}")
        
        # Load federal chunks
        federal_chunks = self.load_federal_chunks()
        if not federal_chunks:
            print("❌ No federal chunks found to index")
            return
        
        print(f"📋 Processing {len(federal_chunks)} federal chunks")
        
        # Create federal-specific indexes
        self.create_authority_index(federal_chunks)
        self.create_effective_date_index(federal_chunks)
        self.create_federal_state_cross_reference_index(federal_chunks)
        
        # Create enhanced traditional indexes
        self.create_enhanced_federal_indexes(federal_chunks)
        
        # Create unified master index
        self.create_unified_master_index(federal_chunks)
        
        # Save all indexes
        self.save_all_indexes()
        
        print(f"\n✅ Federal RAG indexing complete!")
        print(f"📊 Authority levels: {len(self.authority_index)} types")
        print(f"📅 Date coverage: {len(self.effective_date_index)} time periods")
        print(f"🔗 Federal-state mappings: {len(self.federal_state_cross_ref_index)} cross-references")

def main():
    """Main execution function"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    indexer = FederalRAGIndexer(base_dir)
    indexer.build_all_federal_indexes()

if __name__ == "__main__":
    main()