#!/usr/bin/env python3
"""
Enhanced Regulatory Search System for LIHTC QAP Content
Fixes embedded content search issues and adds regulatory section detection
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import gradio as gr
import pandas as pd

# Vector database
import chromadb
from chromadb.config import Settings

class EnhancedRegulatorySearch:
    """Enhanced search system for LIHTC content with regulatory section detection"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        self.chroma_db_path = str(self.base_dir / "lihtc_definitions_chromadb")
        
        # Load Phase 2E data for enhanced search
        self.phase_2e_data = self.load_phase_2e_data()
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        self.collection = self.chroma_client.get_collection("lihtc_definitions_54_jurisdictions")
        
        # Initialize regulatory section patterns
        self.regulatory_patterns = self.init_regulatory_patterns()
        
        print(f"✅ Enhanced search initialized with {self.collection.count()} definitions")
        print(f"✅ Phase 2E data loaded: {len(self.phase_2e_data)} jurisdictions")
    
    def load_phase_2e_data(self) -> Dict[str, Any]:
        """Load all Phase 2E data for enhanced searching"""
        phase_2e_dir = self.base_dir / "phase_2e_full_54_jurisdictions"
        data = {}
        
        # Load all batch files
        for batch_file in phase_2e_dir.glob("phase_2e_incremental_batch_*.json"):
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    data.update(batch_data)
                    print(f"   Loaded {batch_file.name}: {len(batch_data)} jurisdictions")
            except Exception as e:
                print(f"   Error loading {batch_file.name}: {e}")
        
        # Load final 5 results
        final_5_dir = self.base_dir / "phase_2e_final_5_results"
        for final_file in final_5_dir.glob("*_final_result.json"):
            try:
                with open(final_file, 'r', encoding='utf-8') as f:
                    final_data = json.load(f)
                    if isinstance(final_data, dict) and len(final_data) == 1:
                        # Extract state code and data
                        state_code = list(final_data.keys())[0]
                        data[state_code] = final_data[state_code]
                        print(f"   Loaded {final_file.name}: {state_code}")
            except Exception as e:
                print(f"   Error loading {final_file.name}: {e}")
        
        return data
    
    def init_regulatory_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting regulatory sections"""
        return {
            'construction_standards': [
                r'design\s+and\s+construction\s+standards',
                r'minimum\s+construction\s+standards?',
                r'construction\s+requirements',
                r'building\s+standards?',
                r'design\s+standards?',
                r'construction\s+specifications'
            ],
            'income_limits': [
                r'income\s+limits?',
                r'ami\s+limits?',
                r'area\s+median\s+income',
                r'household\s+income\s+limits?',
                r'income\s+requirements?'
            ],
            'scoring_criteria': [
                r'scoring\s+criteria',
                r'point\s+system',
                r'competitive\s+scoring',
                r'selection\s+criteria',
                r'ranking\s+system'
            ],
            'compliance_monitoring': [
                r'compliance\s+monitoring',
                r'monitoring\s+requirements?',
                r'compliance\s+procedures?',
                r'ongoing\s+compliance',
                r'compliance\s+period'
            ]
        }
    
    def enhanced_text_search(self, query: str, content: str) -> Tuple[bool, List[str], float]:
        """Enhanced text search that handles embedded content"""
        if not query.strip() or not content:
            return False, [], 0.0
        
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Direct match
        if query_lower in content_lower:
            # Find context around the match
            contexts = []
            start_idx = 0
            while True:
                idx = content_lower.find(query_lower, start_idx)
                if idx == -1:
                    break
                
                # Extract context (150 chars before and after)
                context_start = max(0, idx - 150)
                context_end = min(len(content), idx + len(query) + 150)
                context = content[context_start:context_end].strip()
                contexts.append(f"...{context}...")
                start_idx = idx + 1
            
            # Calculate relevance score
            matches = content_lower.count(query_lower)
            content_length = len(content)
            relevance = min(1.0, (matches * len(query)) / (content_length * 0.01))
            
            return True, contexts, relevance
        
        # Word-based fuzzy matching
        query_words = query_lower.split()
        if len(query_words) > 1:
            word_matches = 0
            total_words = len(query_words)
            
            for word in query_words:
                if len(word) > 2 and word in content_lower:
                    word_matches += 1
            
            if word_matches >= max(1, total_words * 0.6):  # At least 60% word match
                # Find best context
                contexts = []
                for word in query_words:
                    if word in content_lower:
                        idx = content_lower.find(word)
                        context_start = max(0, idx - 100)
                        context_end = min(len(content), idx + len(word) + 100)
                        context = content[context_start:context_end].strip()
                        contexts.append(f"...{context}...")
                        break
                
                relevance = (word_matches / total_words) * 0.8  # Lower than exact match
                return True, contexts, relevance
        
        return False, [], 0.0
    
    def detect_regulatory_sections(self, content: str) -> List[Dict[str, Any]]:
        """Detect regulatory sections in content"""
        sections = []
        
        for section_type, patterns in self.regulatory_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract context around the match
                    start_idx = max(0, match.start() - 200)
                    end_idx = min(len(content), match.end() + 500)
                    section_content = content[start_idx:end_idx].strip()
                    
                    sections.append({
                        'type': section_type,
                        'pattern': pattern,
                        'match_text': match.group(),
                        'content': section_content,
                        'position': match.start()
                    })
        
        return sections
    
    def comprehensive_search(self, query: str, relevance_filter="All", jurisdiction_filter="All", num_results=10):
        """Comprehensive search combining ChromaDB and direct content search"""
        
        if not query.strip():
            return "Please enter a search query.", ""
        
        try:
            # First, do ChromaDB search
            where_filter = {}
            if relevance_filter != "All":
                where_filter["lihtc_relevance"] = relevance_filter.lower()
            if jurisdiction_filter != "All":
                where_filter["jurisdiction"] = jurisdiction_filter
            
            chroma_results = self.collection.query(
                query_texts=[query],
                n_results=max(50, int(num_results) * 2),  # Get more for filtering
                where=where_filter if where_filter else None
            )
            
            # Enhanced direct search through Phase 2E data
            direct_matches = []
            
            for state_code, state_data in self.phase_2e_data.items():
                if jurisdiction_filter != "All" and jurisdiction_filter != state_code:
                    continue
                
                if 'definitions' in state_data:
                    for definition in state_data['definitions']:
                        # Check if relevance filter matches
                        if relevance_filter != "All" and definition.get('lihtc_relevance', '').lower() != relevance_filter.lower():
                            continue
                        
                        # Search in definition text
                        definition_text = definition.get('definition', '')
                        term = definition.get('term', '')
                        
                        # Enhanced search in definition
                        found, contexts, relevance = self.enhanced_text_search(query, definition_text)
                        if found:
                            direct_matches.append({
                                'definition': definition,
                                'contexts': contexts,
                                'relevance': relevance,
                                'search_type': 'definition_content'
                            })
                        
                        # Also search in term
                        if query.lower() in term.lower():
                            direct_matches.append({
                                'definition': definition,
                                'contexts': [term],
                                'relevance': 0.9,
                                'search_type': 'term_match'
                            })
            
            # Detect regulatory sections
            regulatory_sections = []
            for state_code, state_data in self.phase_2e_data.items():
                if jurisdiction_filter != "All" and jurisdiction_filter != state_code:
                    continue
                    
                # Check if this state has content relevant to the query
                full_text = ""
                if 'definitions' in state_data:
                    for definition in state_data['definitions']:
                        full_text += f"{definition.get('term', '')} {definition.get('definition', '')} "
                
                if full_text:
                    sections = self.detect_regulatory_sections(full_text)
                    for section in sections:
                        found, contexts, relevance = self.enhanced_text_search(query, section['content'])
                        if found:
                            regulatory_sections.append({
                                'state': state_code,
                                'section': section,
                                'contexts': contexts,
                                'relevance': relevance
                            })
            
            # Combine and rank results
            all_results = []
            
            # Add ChromaDB results
            if chroma_results['documents'] and chroma_results['documents'][0]:
                for i, doc in enumerate(chroma_results['documents'][0]):
                    metadata = chroma_results['metadatas'][0][i]
                    distance = chroma_results['distances'][0][i] if chroma_results.get('distances') else 0
                    all_results.append({
                        'type': 'chroma',
                        'relevance': 1 - distance,
                        'term': metadata.get('term', 'Unknown Term'),
                        'definition': metadata.get('definition', 'No definition available'),
                        'jurisdiction': metadata.get('jurisdiction', 'Unknown'),
                        'lihtc_relevance': metadata.get('lihtc_relevance', 'unknown'),
                        'contexts': []
                    })
            
            # Add direct matches
            for match in direct_matches:
                definition = match['definition']
                all_results.append({
                    'type': 'direct',
                    'relevance': match['relevance'],
                    'term': definition.get('term', 'Unknown Term'),
                    'definition': definition.get('definition', 'No definition available'),
                    'jurisdiction': definition.get('state_code', 'Unknown'),
                    'lihtc_relevance': definition.get('lihtc_relevance', 'unknown'),
                    'contexts': match['contexts'],
                    'search_type': match['search_type']
                })
            
            # Add regulatory sections
            for reg_match in regulatory_sections:
                all_results.append({
                    'type': 'regulatory',
                    'relevance': reg_match['relevance'],
                    'term': f"Regulatory Section: {reg_match['section']['type'].replace('_', ' ').title()}",
                    'definition': reg_match['section']['content'],
                    'jurisdiction': reg_match['state'],
                    'lihtc_relevance': 'high',
                    'contexts': reg_match['contexts'],
                    'section_type': reg_match['section']['type']
                })
            
            # Remove duplicates and sort by relevance
            seen = set()
            unique_results = []
            for result in all_results:
                key = (result['jurisdiction'], result['term'], result['definition'][:100])
                if key not in seen:
                    seen.add(key)
                    unique_results.append(result)
            
            # Sort by relevance
            unique_results.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Limit results
            final_results = unique_results[:int(num_results)]
            
            if not final_results:
                return "No definitions found.", ""
            
            # Format results
            search_text = f"**Found {len(final_results)} definitions for: '{query}'**\n\n"
            
            for i, result in enumerate(final_results):
                search_text += f"**{i+1}. {result['term']}** "
                search_text += f"({result['jurisdiction']} - {result['lihtc_relevance']} relevance)\n"
                search_text += f"*{result['type'].title()} Search - Relevance: {result['relevance']:.3f}*\n\n"
                
                # Add definition
                definition = result['definition']
                if len(definition) > 1000:
                    definition = definition[:1000] + "..."
                search_text += f"{definition}\n\n"
                
                # Add contexts if available
                if result.get('contexts'):
                    search_text += f"**Relevant Context:**\n"
                    for context in result['contexts'][:2]:  # Limit contexts
                        search_text += f"• {context}\n"
                    search_text += "\n"
                
                search_text += f"---\n\n"
            
            # Create summary
            jurisdictions = set(result['jurisdiction'] for result in final_results)
            relevance_counts = {}
            search_types = {}
            
            for result in final_results:
                rel = result['lihtc_relevance']
                relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
                
                search_type = result['type']
                search_types[search_type] = search_types.get(search_type, 0) + 1
            
            summary_text = f"**Enhanced Search Summary:**\n"
            summary_text += f"- Query: '{query}'\n"
            summary_text += f"- Results: {len(final_results)}\n"
            summary_text += f"- Jurisdictions: {', '.join(sorted(jurisdictions))}\n"
            summary_text += f"- Search methods: {dict(search_types)}\n"
            summary_text += f"- Relevance breakdown: {dict(relevance_counts)}\n"
            
            return search_text, summary_text
            
        except Exception as e:
            return f"Enhanced search error: {str(e)}", ""
    
    def create_interface(self):
        """Create enhanced Gradio interface"""
        
        # Get available filters
        sample = self.collection.get(limit=1000)
        jurisdictions = sorted(set(m.get('jurisdiction', 'Unknown') for m in sample['metadatas']))
        relevance_options = ['All', 'Critical', 'High', 'Medium', 'Low', 'Minimal']
        
        with gr.Blocks(title="Enhanced LIHTC Regulatory Search - M4 Beast") as interface:
            
            gr.Markdown("""
            # 🔍 Enhanced LIHTC Regulatory Search System
            ## Advanced search with regulatory section detection and embedded content analysis
            ### Fixes search issues with "minimum construction standards" and similar complex terms
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Search LIHTC Content",
                        placeholder="e.g., minimum construction standards, design requirements, AMI limits",
                        lines=2
                    )
                    
                    with gr.Row():
                        relevance_filter = gr.Dropdown(
                            label="LIHTC Relevance",
                            choices=relevance_options,
                            value="All"
                        )
                        
                        jurisdiction_filter = gr.Dropdown(
                            label="Jurisdiction",
                            choices=["All"] + jurisdictions,
                            value="All"
                        )
                        
                        num_results = gr.Slider(
                            label="Results",
                            minimum=5, maximum=25, value=10, step=5
                        )
                    
                    search_btn = gr.Button("🔍 Enhanced Search", variant="primary")
                
                with gr.Column(scale=1):
                    system_info = gr.Textbox(
                        label="Enhanced Search Features",
                        value="""**Enhanced Capabilities:**

🔍 **Multi-Method Search:**
- ChromaDB vector search
- Direct content analysis
- Regulatory section detection

📋 **Pattern Recognition:**
- Construction standards
- Income limits
- Scoring criteria
- Compliance monitoring

🎯 **Content Analysis:**
- Embedded text detection
- Context extraction
- Relevance scoring
- Duplicate removal

💡 **Improved Results:**
- Better term matching
- Regulatory context
- Cross-jurisdictional coverage""",
                        lines=20,
                        interactive=False
                    )
            
            with gr.Row():
                search_results = gr.Textbox(
                    label="Enhanced Search Results",
                    lines=25,
                    interactive=False
                )
                
                search_summary = gr.Textbox(
                    label="Search Analysis",
                    lines=25,
                    interactive=False
                )
            
            # Example queries specifically for testing
            gr.Markdown("""
            ## 🧪 Test These Previously Problematic Queries:
            - **"minimum construction standards"** (should now find CA QAP content)
            - **"design and construction standards"** (regulatory section detection)
            - **"construction requirements"** (embedded content search)
            - **"building standards"** (cross-jurisdictional comparison)
            """)
            
            # Connect enhanced search function
            search_btn.click(
                fn=self.comprehensive_search,
                inputs=[query_input, relevance_filter, jurisdiction_filter, num_results],
                outputs=[search_results, search_summary]
            )
        
        return interface

def main():
    """Launch enhanced regulatory search system"""
    
    print("🔍 ENHANCED LIHTC REGULATORY SEARCH SYSTEM - M4 BEAST")
    print("=" * 60)
    print("🎯 Fixing embedded content search issues")
    print("📋 Adding regulatory section detection")
    print("🔧 Multi-method search approach")
    print("")
    
    try:
        # Initialize enhanced search system
        search_system = EnhancedRegulatorySearch()
        
        # Create and launch Gradio interface
        interface = search_system.create_interface()
        
        print("🚀 Launching enhanced search interface...")
        print("📱 Access at: http://localhost:7861")
        print("🔍 Testing 'minimum construction standards' search capability!")
        
        # Launch with different port to avoid conflicts
        interface.launch(
            server_name="127.0.0.1",
            server_port=7861,
            share=False,
            quiet=False,
            show_error=True,
            debug=False
        )
        
    except Exception as e:
        print(f"❌ Failed to launch enhanced search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()