#!/usr/bin/env python3
"""
Simple LIHTC Definition Interface - M4 Beast
Quick test interface for 2,283 definitions from all 54 jurisdictions
"""

import json
import time
from pathlib import Path
import gradio as gr
import pandas as pd

# Vector database
import chromadb
from chromadb.config import Settings

class SimpleLIHTCInterface:
    """Simple, reliable interface for LIHTC definitions"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        self.chroma_db_path = str(self.base_dir / "lihtc_definitions_chromadb")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        self.collection = self.chroma_client.get_collection("lihtc_definitions_54_jurisdictions")
        
        print(f"✅ Connected to ChromaDB with {self.collection.count()} definitions")
    
    def search_definitions(self, query, relevance_filter="All", jurisdiction_filter="All", num_results=10):
        """Search definitions with filters"""
        
        if not query.strip():
            return "Please enter a search query.", ""
        
        try:
            # Build where filter
            where_filter = {}
            if relevance_filter != "All":
                where_filter["lihtc_relevance"] = relevance_filter.lower()
            if jurisdiction_filter != "All":
                where_filter["jurisdiction"] = jurisdiction_filter
            
            # Search
            results = self.collection.query(
                query_texts=[query],
                n_results=int(num_results),
                where=where_filter if where_filter else None
            )
            
            # Format results
            if not results['documents'] or not results['documents'][0]:
                return "No definitions found.", ""
            
            # Create search results text
            search_text = f"**Found {len(results['documents'][0])} definitions for: '{query}'**\n\n"
            
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if results.get('distances') else 0
                similarity = round((1 - distance) * 100, 1)
                
                search_text += f"**{i+1}. {metadata.get('term', 'Unknown Term')}** "
                search_text += f"({metadata.get('jurisdiction', 'Unknown')} - {metadata.get('lihtc_relevance', 'unknown')} relevance)\n"
                search_text += f"*Similarity: {similarity}%*\n\n"
                search_text += f"{metadata.get('definition', 'No definition available')}\n\n"
                search_text += f"---\n\n"
            
            # Create summary
            jurisdictions = set(results['metadatas'][0][i].get('jurisdiction', 'Unknown') for i in range(len(results['metadatas'][0])))
            relevance_counts = {}
            for metadata in results['metadatas'][0]:
                rel = metadata.get('lihtc_relevance', 'unknown')
                relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
            
            summary_text = f"**Search Summary:**\n"
            summary_text += f"- Query: '{query}'\n"
            summary_text += f"- Results: {len(results['documents'][0])}\n"
            summary_text += f"- Jurisdictions: {', '.join(sorted(jurisdictions))}\n"
            summary_text += f"- Relevance breakdown: {dict(relevance_counts)}\n"
            
            return search_text, summary_text
            
        except Exception as e:
            return f"Search error: {str(e)}", ""
    
    def get_system_stats(self):
        """Get system statistics"""
        
        try:
            total_count = self.collection.count()
            
            # Sample some data to get stats
            sample = self.collection.get(limit=min(1000, total_count))
            
            # Count jurisdictions
            jurisdictions = set()
            relevance_counts = {}
            
            for metadata in sample['metadatas']:
                jurisdictions.add(metadata.get('jurisdiction', 'Unknown'))
                rel = metadata.get('lihtc_relevance', 'unknown')
                relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
            
            stats_text = f"""**LIHTC Definition Intelligence System Status**

📊 **Database Statistics:**
- Total Definitions: {total_count:,}
- Jurisdictions Loaded: {len(jurisdictions)}
- Sample Size: {len(sample['metadatas'])}

🏛️ **Jurisdiction Coverage:**
{', '.join(sorted(jurisdictions))}

📈 **LIHTC Relevance (Sample):**
"""
            
            for relevance, count in sorted(relevance_counts.items()):
                percentage = (count / len(sample['metadatas'])) * 100
                stats_text += f"- {relevance.capitalize()}: {count} ({percentage:.1f}%)\n"
            
            return stats_text
            
        except Exception as e:
            return f"Error getting stats: {str(e)}"
    
    def create_interface(self):
        """Create simple Gradio interface"""
        
        # Get available filters
        sample = self.collection.get(limit=1000)
        jurisdictions = sorted(set(m.get('jurisdiction', 'Unknown') for m in sample['metadatas']))
        relevance_options = ['All', 'Critical', 'High', 'Medium', 'Low', 'Minimal']
        
        with gr.Blocks(title="LIHTC Definition Search - M4 Beast") as interface:
            
            gr.Markdown("""
            # 🏛️ LIHTC Definition Intelligence System
            ## Search 2,283+ definitions from all 54 US LIHTC jurisdictions
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Search LIHTC Definitions",
                        placeholder="e.g., qualified basis, AMI limits, compliance period",
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
                    
                    search_btn = gr.Button("🔍 Search Definitions", variant="primary")
                
                with gr.Column(scale=1):
                    system_stats = gr.Textbox(
                        label="System Status",
                        value=self.get_system_stats(),
                        lines=20,
                        interactive=False
                    )
            
            with gr.Row():
                search_results = gr.Textbox(
                    label="Search Results",
                    lines=20,
                    interactive=False
                )
                
                search_summary = gr.Textbox(
                    label="Search Summary",
                    lines=20,
                    interactive=False
                )
            
            # Example queries
            gr.Markdown("""
            ## 🔍 Try These Example Queries:
            - **Basic Terms**: "qualified basis", "AMI limits", "compliance period"
            - **Geographic**: "difficult development area", "QCT", "rural"
            - **Process**: "tax credit allocation", "carryover", "placed in service"
            - **Cross-Jurisdictional**: "income limits" (compare across states)
            """)
            
            # Connect search function
            search_btn.click(
                fn=self.search_definitions,
                inputs=[query_input, relevance_filter, jurisdiction_filter, num_results],
                outputs=[search_results, search_summary]
            )
        
        return interface

def main():
    """Launch simple LIHTC interface"""
    
    print("🏛️ SIMPLE LIHTC DEFINITION INTERFACE - M4 BEAST")
    print("=" * 60)
    
    try:
        # Initialize interface
        interface_system = SimpleLIHTCInterface()
        
        # Create and launch Gradio interface
        interface = interface_system.create_interface()
        
        print("🚀 Launching interface...")
        print("📱 Access at: http://localhost:7860")
        print("🔍 Ready to search 2,283+ LIHTC definitions!")
        
        # Launch with simple settings
        interface.launch(
            server_name="127.0.0.1",  # localhost only
            server_port=7860,
            share=False,
            quiet=False,
            show_error=True,
            debug=False
        )
        
    except Exception as e:
        print(f"❌ Failed to launch interface: {e}")
        print("💡 Try running the test script first: python3 test_m4_beast_system.py")

if __name__ == "__main__":
    main()