#!/usr/bin/env python3
"""
LIHTC Definition Intelligence System - M4 Beast Optimized
Complete test interface with ChromaDB + LLAMA 34B + Docling Intelligence
2,159 definitions across all 54 US LIHTC jurisdictions
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Vector database and embeddings
import chromadb
from chromadb.config import Settings
import numpy as np

# LLAMA model integration
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("⚠️ llama-cpp-python not available. Install with: pip install llama-cpp-python")

# Alternative embedding models
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not available. Install with: pip install sentence-transformers")

# Web interface
import gradio as gr
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LIHTCDefinitionIntelligenceSystem:
    """
    Complete LIHTC Definition Intelligence System
    Optimized for M4 Beast with 128GB unified memory
    """
    
    def __init__(self, 
                 data_dir: str = None,
                 model_path: str = None,
                 chroma_db_path: str = None):
        """Initialize the complete intelligence system"""
        
        # Paths
        self.base_dir = Path(data_dir or "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_dir = self.base_dir / "modules" / "qap_processing"
        self.chroma_db_path = chroma_db_path or str(self.data_dir / "lihtc_definitions_chromadb")
        
        # Model configuration for M4 Beast
        self.model_path = model_path
        self.llama_model = None
        self.embedding_model = None
        
        # ChromaDB setup
        self.chroma_client = None
        self.collection = None
        
        # Definition database
        self.all_definitions = []
        self.jurisdiction_stats = {}
        
        # System stats
        self.system_stats = {
            'total_definitions': 0,
            'total_jurisdictions': 0,
            'total_cross_references': 0,
            'relevance_distribution': {},
            'load_time': 0
        }
        
        logger.info("🏛️ LIHTC Definition Intelligence System initialized")
        logger.info(f"📂 Data directory: {self.data_dir}")
        logger.info(f"🗄️ ChromaDB path: {self.chroma_db_path}")
    
    def load_all_definitions(self) -> Dict[str, Any]:
        """Load all 2,159 definitions from Phase 2D/2E results"""
        
        start_time = time.time()
        logger.info("📚 Loading all definitions from 54 jurisdictions...")
        
        all_definitions = []
        jurisdiction_stats = {}
        total_cross_references = 0
        relevance_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'minimal': 0}
        
        # Load Phase 2D results (11 jurisdictions)
        phase_2d_dir = self.data_dir / "phase_2d_all_states_intelligent"
        if phase_2d_dir.exists():
            for json_file in phase_2d_dir.glob("*_intelligent_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        jurisdiction = data.get('state_code', 'Unknown')
                        definitions = data.get('definitions', [])
                        cross_refs = data.get('cross_references', [])
                        
                        # Add jurisdiction metadata to each definition
                        for defn in definitions:
                            defn['data_source'] = 'phase_2d'
                            defn['jurisdiction'] = jurisdiction
                            all_definitions.append(defn)
                            
                            # Track relevance
                            relevance = defn.get('lihtc_relevance', 'unknown')
                            if relevance in relevance_counts:
                                relevance_counts[relevance] += 1
                        
                        # Track jurisdiction stats
                        jurisdiction_stats[jurisdiction] = {
                            'definitions_count': len(definitions),
                            'cross_references_count': len(cross_refs),
                            'data_source': 'phase_2d'
                        }
                        
                        total_cross_references += len(cross_refs)
                        logger.info(f"✅ {jurisdiction}: {len(definitions)} definitions")
                        
                except Exception as e:
                    logger.error(f"Failed to load {json_file}: {e}")
        
        # Load Phase 2E results (remaining jurisdictions)
        phase_2e_dir = self.data_dir / "phase_2e_full_54_jurisdictions"
        if phase_2e_dir.exists():
            # Load main Phase 2E results
            for json_file in phase_2e_dir.glob("PHASE_2E_FULL_54_JURISDICTIONS_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        jurisdiction_results = data.get('jurisdiction_results', {})
                        
                        for jurisdiction, result in jurisdiction_results.items():
                            if result.get('success', True) and jurisdiction not in jurisdiction_stats:
                                definitions = result.get('definitions', [])
                                cross_refs = result.get('cross_references', [])
                                
                                # Add jurisdiction metadata
                                for defn in definitions:
                                    defn['data_source'] = 'phase_2e'
                                    defn['jurisdiction'] = jurisdiction
                                    all_definitions.append(defn)
                                    
                                    # Track relevance
                                    relevance = defn.get('lihtc_relevance', 'unknown')
                                    if relevance in relevance_counts:
                                        relevance_counts[relevance] += 1
                                
                                # Track jurisdiction stats
                                jurisdiction_stats[jurisdiction] = {
                                    'definitions_count': len(definitions),
                                    'cross_references_count': len(cross_refs),
                                    'data_source': 'phase_2e'
                                }
                                
                                total_cross_references += len(cross_refs)
                                logger.info(f"✅ {jurisdiction}: {len(definitions)} definitions")
                        
                        break  # Only need the most recent file
                        
                except Exception as e:
                    logger.error(f"Failed to load {json_file}: {e}")
        
        # Load Phase 2E Final 5 results
        final_5_dir = self.data_dir / "phase_2e_final_5_results"
        if final_5_dir.exists():
            for json_file in final_5_dir.glob("*_final_result.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        jurisdiction = data.get('state_code', 'Unknown')
                        
                        if data.get('success', True) and jurisdiction not in jurisdiction_stats:
                            definitions = data.get('definitions', [])
                            cross_refs = data.get('cross_references', [])
                            
                            # Add jurisdiction metadata
                            for defn in definitions:
                                defn['data_source'] = 'phase_2e_final_5'
                                defn['jurisdiction'] = jurisdiction
                                all_definitions.append(defn)
                                
                                # Track relevance
                                relevance = defn.get('lihtc_relevance', 'unknown')
                                if relevance in relevance_counts:
                                    relevance_counts[relevance] += 1
                            
                            # Track jurisdiction stats
                            jurisdiction_stats[jurisdiction] = {
                                'definitions_count': len(definitions),
                                'cross_references_count': len(cross_refs),
                                'data_source': 'phase_2e_final_5'
                            }
                            
                            total_cross_references += len(cross_refs)
                            logger.info(f"✅ {jurisdiction}: {len(definitions)} definitions")
                    
                except Exception as e:
                    logger.error(f"Failed to load {json_file}: {e}")
        
        # Update system stats
        load_time = time.time() - start_time
        self.system_stats = {
            'total_definitions': len(all_definitions),
            'total_jurisdictions': len(jurisdiction_stats),
            'total_cross_references': total_cross_references,
            'relevance_distribution': relevance_counts,
            'load_time': load_time
        }
        
        self.all_definitions = all_definitions
        self.jurisdiction_stats = jurisdiction_stats
        
        logger.info(f"🏆 DEFINITIONS LOADED SUCCESSFULLY!")
        logger.info(f"📖 Total definitions: {len(all_definitions):,}")
        logger.info(f"🏛️ Total jurisdictions: {len(jurisdiction_stats)}")
        logger.info(f"🔗 Total cross-references: {total_cross_references:,}")
        logger.info(f"⏱️ Load time: {load_time:.1f} seconds")
        
        return self.system_stats
    
    def initialize_chromadb(self) -> bool:
        """Initialize ChromaDB with LIHTC-optimized indexing"""
        
        logger.info("🗄️ Initializing ChromaDB...")
        
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection with LIHTC metadata
            collection_name = "lihtc_definitions_54_jurisdictions"
            
            try:
                # Try to get existing collection
                self.collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"📚 Using existing collection: {collection_name}")
                
                # Check if we need to rebuild
                collection_count = self.collection.count()
                if collection_count != len(self.all_definitions):
                    logger.info(f"🔄 Collection size mismatch ({collection_count} vs {len(self.all_definitions)}), rebuilding...")
                    self.chroma_client.delete_collection(collection_name)
                    raise Exception("Force rebuild")
                    
            except:
                # Create new collection
                logger.info(f"🆕 Creating new collection: {collection_name}")
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={
                        "description": "LIHTC definitions with intelligence from all 54 US jurisdictions",
                        "total_definitions": len(self.all_definitions),
                        "total_jurisdictions": len(self.jurisdiction_stats),
                        "created_date": datetime.now().isoformat()
                    }
                )
                
                # Add all definitions to ChromaDB
                self._populate_chromadb()
            
            logger.info("✅ ChromaDB initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            return False
    
    def _populate_chromadb(self):
        """Populate ChromaDB with all definitions and metadata"""
        
        logger.info("📚 Populating ChromaDB with all definitions...")
        
        # Prepare batch data
        documents = []
        metadatas = []
        ids = []
        
        for i, defn in enumerate(self.all_definitions):
            # Create searchable document text
            document_text = f"Term: {defn.get('term', '')}\nDefinition: {defn.get('definition', '')}"
            documents.append(document_text)
            
            # Create comprehensive metadata
            metadata = {
                'jurisdiction': defn.get('jurisdiction', 'Unknown'),
                'term': defn.get('term', ''),
                'definition': defn.get('definition', ''),
                'lihtc_relevance': defn.get('lihtc_relevance', 'unknown'),
                'category': defn.get('category', 'general'),
                'definition_type': defn.get('definition_type', 'descriptive'),
                'section_reference': defn.get('section_reference', ''),
                'data_source': defn.get('data_source', 'unknown'),
                'definition_id': defn.get('definition_id', f'unknown_{i}')
            }
            metadatas.append(metadata)
            
            # Create unique ID
            ids.append(f"{defn.get('jurisdiction', 'unknown')}_{i:04d}")
        
        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            
            self.collection.add(
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )
            
            if (i // batch_size + 1) % 10 == 0:
                logger.info(f"📚 Added {batch_end:,}/{len(documents):,} definitions to ChromaDB")
        
        logger.info(f"✅ ChromaDB population complete: {len(documents):,} definitions indexed")
    
    def initialize_llama_model(self) -> bool:
        """Initialize LLAMA 34B model optimized for M4 Beast"""
        
        if not LLAMA_AVAILABLE:
            logger.error("❌ llama-cpp-python not available")
            return False
        
        logger.info("🦙 Initializing LLAMA 34B model for M4 Beast...")
        
        try:
            # M4 Beast optimized configuration
            self.llama_model = Llama(
                model_path=self.model_path,
                n_ctx=8192,  # Large context for LIHTC definitions
                n_batch=512,  # Optimized for M4 Beast
                n_threads=8,  # Use 8 CPU cores
                n_gpu_layers=0,  # Use CPU for now (can enable GPU later)
                verbose=False,
                chat_format="llama-2"  # Use appropriate chat format
            )
            
            logger.info("✅ LLAMA 34B model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ LLAMA model initialization failed: {e}")
            return False
    
    def query_definitions(self, 
                         query: str, 
                         limit: int = 10,
                         relevance_filter: str = None,
                         jurisdiction_filter: str = None) -> List[Dict[str, Any]]:
        """Query the definition database with filters"""
        
        if not self.collection:
            logger.error("❌ ChromaDB not initialized")
            return []
        
        try:
            # Build where filter
            where_filter = {}
            if relevance_filter and relevance_filter != "All":
                where_filter["lihtc_relevance"] = relevance_filter.lower()
            if jurisdiction_filter and jurisdiction_filter != "All":
                where_filter["jurisdiction"] = jurisdiction_filter
            
            # Perform vector search
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter if where_filter else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    
                    formatted_results.append({
                        'term': metadata.get('term', ''),
                        'definition': metadata.get('definition', ''),
                        'jurisdiction': metadata.get('jurisdiction', ''),
                        'lihtc_relevance': metadata.get('lihtc_relevance', ''),
                        'category': metadata.get('category', ''),
                        'section_reference': metadata.get('section_reference', ''),
                        'similarity_score': 1 - distance,  # Convert distance to similarity
                        'definition_id': metadata.get('definition_id', '')
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return []
    
    def ask_llama_about_definitions(self, 
                                   question: str, 
                                   context_definitions: List[Dict[str, Any]]) -> str:
        """Ask LLAMA model about definitions with context"""
        
        if not self.llama_model:
            return "❌ LLAMA model not available. Please initialize the model first."
        
        try:
            # Prepare context from definitions
            context_text = "LIHTC Definitions Context:\n\n"
            for i, defn in enumerate(context_definitions[:5], 1):  # Limit to top 5
                context_text += f"{i}. **{defn['term']}** ({defn['jurisdiction']}, {defn['lihtc_relevance']} relevance)\n"
                context_text += f"   Definition: {defn['definition'][:200]}...\n\n"
            
            # Create prompt
            prompt = f"""You are an expert LIHTC (Low-Income Housing Tax Credit) consultant with access to definitions from all 54 US jurisdictions. Answer the question using the provided context.

{context_text}

Question: {question}

Please provide a comprehensive answer that:
1. References specific definitions when relevant
2. Notes any jurisdictional differences
3. Explains LIHTC relevance and implications
4. Uses the exact terminology from the definitions

Answer:"""
            
            # Generate response
            response = self.llama_model(
                prompt,
                max_tokens=1000,
                temperature=0.1,
                top_p=0.9,
                stop=["Question:", "Context:"]
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            logger.error(f"❌ LLAMA query failed: {e}")
            return f"❌ Error generating response: {str(e)}"
    
    def create_gradio_interface(self) -> gr.Interface:
        """Create Gradio web interface for testing"""
        
        def search_and_ask(question, relevance_filter, jurisdiction_filter, num_results):
            """Combined search and LLAMA query function"""
            
            # Search for relevant definitions
            search_results = self.query_definitions(
                query=question,
                limit=int(num_results),
                relevance_filter=relevance_filter,
                jurisdiction_filter=jurisdiction_filter
            )
            
            if not search_results:
                return "No definitions found matching your query.", ""
            
            # Format search results
            search_output = f"**Found {len(search_results)} relevant definitions:**\n\n"
            for i, result in enumerate(search_results, 1):
                search_output += f"**{i}. {result['term']}** ({result['jurisdiction']}, {result['lihtc_relevance']} relevance)\n"
                search_output += f"*Score: {result['similarity_score']:.3f}*\n"
                search_output += f"{result['definition'][:300]}...\n\n"
            
            # Generate LLAMA response if model is available
            if self.llama_model:
                llama_response = self.ask_llama_about_definitions(question, search_results)
            else:
                llama_response = "LLAMA model not initialized. Only showing search results."
            
            return search_output, llama_response
        
        def get_system_stats():
            """Get current system statistics"""
            stats_text = f"""**LIHTC Definition Intelligence System Status:**

📖 **Total Definitions:** {self.system_stats['total_definitions']:,}
🏛️ **Total Jurisdictions:** {self.system_stats['total_jurisdictions']}/54
🔗 **Total Cross-references:** {self.system_stats['total_cross_references']:,}
⏱️ **Load Time:** {self.system_stats['load_time']:.1f} seconds

**LIHTC Relevance Distribution:**
- Critical: {self.system_stats['relevance_distribution'].get('critical', 0)} definitions
- High: {self.system_stats['relevance_distribution'].get('high', 0)} definitions  
- Medium: {self.system_stats['relevance_distribution'].get('medium', 0)} definitions
- Low: {self.system_stats['relevance_distribution'].get('low', 0)} definitions
- Minimal: {self.system_stats['relevance_distribution'].get('minimal', 0)} definitions

**Model Status:**
- ChromaDB: {'✅ Ready' if self.collection else '❌ Not initialized'}
- LLAMA 34B: {'✅ Ready' if self.llama_model else '❌ Not initialized'}
"""
            return stats_text
        
        # Create interface
        with gr.Blocks(title="LIHTC Definition Intelligence System - M4 Beast") as interface:
            gr.Markdown("""
            # 🏛️ LIHTC Definition Intelligence System
            ## Complete coverage of all 54 US LIHTC jurisdictions with 2,159+ definitions
            ### Optimized for M4 Beast with LLAMA 34B + ChromaDB + Docling Intelligence
            """)
            
            with gr.Tab("🔍 Definition Search & Analysis"):
                with gr.Row():
                    with gr.Column(scale=3):
                        question_input = gr.Textbox(
                            label="Ask about LIHTC definitions",
                            placeholder="e.g., What is qualified basis? How do states define AMI limits?",
                            lines=2
                        )
                        
                        with gr.Row():
                            relevance_filter = gr.Dropdown(
                                label="LIHTC Relevance Filter",
                                choices=["All", "Critical", "High", "Medium", "Low", "Minimal"],
                                value="All"
                            )
                            
                            jurisdiction_filter = gr.Dropdown(
                                label="Jurisdiction Filter", 
                                choices=["All"] + sorted(list(self.jurisdiction_stats.keys())),
                                value="All"
                            )
                            
                            num_results = gr.Slider(
                                label="Number of Results",
                                minimum=5, maximum=50, value=10, step=5
                            )
                        
                        search_button = gr.Button("🔍 Search Definitions", variant="primary")
                    
                    with gr.Column(scale=1):
                        system_stats = gr.Textbox(
                            label="System Status",
                            value=get_system_stats(),
                            lines=15,
                            interactive=False
                        )
                
                with gr.Row():
                    search_results = gr.Textbox(
                        label="Search Results",
                        lines=15,
                        interactive=False
                    )
                    
                    llama_analysis = gr.Textbox(
                        label="LLAMA 34B Analysis",
                        lines=15,
                        interactive=False
                    )
                
                search_button.click(
                    fn=search_and_ask,
                    inputs=[question_input, relevance_filter, jurisdiction_filter, num_results],
                    outputs=[search_results, llama_analysis]
                )
            
            with gr.Tab("📊 System Statistics"):
                gr.Markdown("### Jurisdiction Coverage")
                
                # Create jurisdiction stats DataFrame
                jurisdictions_data = []
                for jurisdiction, stats in self.jurisdiction_stats.items():
                    jurisdictions_data.append({
                        'Jurisdiction': jurisdiction,
                        'Definitions': stats['definitions_count'],
                        'Cross-References': stats['cross_references_count'],
                        'Data Source': stats['data_source']
                    })
                
                jurisdictions_df = pd.DataFrame(jurisdictions_data).sort_values('Definitions', ascending=False)
                
                gr.DataFrame(
                    value=jurisdictions_df,
                    label="All 54 Jurisdictions - Definition Coverage"
                )
        
        return interface
    
    def run_test_queries(self):
        """Run test queries to validate the system"""
        
        logger.info("🧪 Running test queries...")
        
        test_queries = [
            "What is qualified basis?",
            "How do states define AMI limits?", 
            "What are the requirements for tax credit allocation?",
            "Define compliance period",
            "What is a difficult development area?"
        ]
        
        for query in test_queries:
            logger.info(f"\n🔍 Test Query: {query}")
            results = self.query_definitions(query, limit=3)
            
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. {result['term']} ({result['jurisdiction']}) - {result['similarity_score']:.3f}")

def main():
    """Main function to initialize and run the system"""
    
    print("🏛️ LIHTC DEFINITION INTELLIGENCE SYSTEM - M4 BEAST")
    print("=" * 80)
    print("🎯 Loading 2,159+ definitions from all 54 US LIHTC jurisdictions")
    print("🦙 LLAMA 34B + ChromaDB + Docling Intelligence Integration")
    
    # Initialize system
    system = LIHTCDefinitionIntelligenceSystem()
    
    # Load all definitions
    stats = system.load_all_definitions()
    print(f"\n📊 System loaded: {stats['total_definitions']:,} definitions from {stats['total_jurisdictions']} jurisdictions")
    
    # Initialize ChromaDB
    if system.initialize_chromadb():
        print("✅ ChromaDB initialized successfully")
    else:
        print("❌ ChromaDB initialization failed")
        return
    
    # Initialize LLAMA model (optional - comment out if model not available)
    # model_path = "/path/to/your/llama-34b-model.gguf"  # Update this path
    # if system.initialize_llama_model():
    #     print("✅ LLAMA 34B model loaded")
    # else:
    #     print("⚠️ LLAMA model not loaded - search-only mode")
    
    # Run test queries
    system.run_test_queries()
    
    # Launch Gradio interface
    print(f"\n🚀 Launching Gradio interface...")
    interface = system.create_gradio_interface()
    
    # Launch with M4 Beast optimized settings
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True for public link
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()