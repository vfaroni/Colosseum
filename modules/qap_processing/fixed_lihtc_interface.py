#!/usr/bin/env python3
"""
Fixed LIHTC Definition Interface - M4 Beast
Resolves ChromaDB telemetry issues and connection problems
"""

import json
import os
import sys
from pathlib import Path
import gradio as gr

# Disable ChromaDB telemetry completely
os.environ["ANONYMIZED_TELEMETRY"] = "False"

class FixedLIHTCInterface:
    """Fixed interface that bypasses ChromaDB issues"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        self.definitions_data = {}
        self.load_definitions_from_files()
    
    def load_definitions_from_files(self):
        """Load definitions directly from JSON files, bypassing ChromaDB"""
        
        print("🔍 Loading definitions from Phase 2E results...")
        
        # Load from all phases - focus on Phase 2E batch files
        phase_dirs = [
            "phase_2e_full_54_jurisdictions", 
            "phase_2e_final_5_results",
            "phase_2d_all_states_intelligent"
        ]
        
        total_definitions = 0
        
        for phase_dir in phase_dirs:
            phase_path = self.base_dir / phase_dir
            if phase_path.exists():
                print(f"  📁 Checking {phase_dir}...")
                for json_file in phase_path.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        print(f"    📄 Processing {json_file.name}...")
                        
                        # Handle Phase 2E batch structure (state -> definitions)
                        if isinstance(data, dict):
                            # Skip summary files
                            if 'processing_date' in data and 'total_jurisdictions' in data:
                                print(f"      ⏭️ Skipping summary file")
                                continue
                                
                            for state_code, state_data in data.items():
                                if isinstance(state_data, dict) and 'definitions' in state_data:
                                    definitions = state_data['definitions']
                                    defs_added = 0
                                    
                                    for definition in definitions:
                                        if isinstance(definition, dict) and 'term' in definition:
                                            # Normalize jurisdiction field
                                            jurisdiction = definition.get('state_code', definition.get('jurisdiction', state_code))
                                            definition['jurisdiction'] = jurisdiction
                                            
                                            key = f"{jurisdiction}_{definition['term']}_{total_definitions}"
                                            self.definitions_data[key] = definition
                                            total_definitions += 1
                                            defs_added += 1
                                    
                                    if defs_added > 0:
                                        print(f"        ✅ {state_code}: {defs_added} definitions")
                                
                                elif isinstance(state_data, list):
                                    # Direct list of definitions
                                    defs_added = 0
                                    for definition in state_data:
                                        if isinstance(definition, dict) and 'term' in definition:
                                            jurisdiction = definition.get('state_code', definition.get('jurisdiction', state_code))
                                            definition['jurisdiction'] = jurisdiction
                                            
                                            key = f"{jurisdiction}_{definition['term']}_{total_definitions}"
                                            self.definitions_data[key] = definition
                                            total_definitions += 1
                                            defs_added += 1
                                    
                                    if defs_added > 0:
                                        print(f"        ✅ {state_code}: {defs_added} definitions")
                        
                        print(f"      ✅ Added definitions from {json_file.name}")
                                
                    except Exception as e:
                        print(f"      ⚠️ Error loading {json_file}: {e}")
        
        print(f"✅ Loaded {total_definitions:,} definitions from files")
        
        # Show jurisdiction summary
        jurisdictions = set(d.get('jurisdiction', 'Unknown') for d in self.definitions_data.values())
        print(f"📍 Jurisdictions found: {', '.join(sorted(jurisdictions))}")
        
        return total_definitions > 0
    
    def search_definitions(self, query, relevance_filter="All", jurisdiction_filter="All", num_results=10):
        """Search definitions using simple text matching"""
        
        if not query.strip():
            return "Please enter a search query.", ""
        
        query_lower = query.lower()
        results = []
        
        # Search through all definitions
        for key, definition in self.definitions_data.items():
            term = definition.get('term', '').lower()
            def_text = definition.get('definition', '').lower()
            jurisdiction = definition.get('jurisdiction', 'Unknown')
            relevance = definition.get('lihtc_relevance', 'unknown')
            
            # Apply filters
            if relevance_filter != "All" and relevance != relevance_filter.lower():
                continue
            if jurisdiction_filter != "All" and jurisdiction != jurisdiction_filter:
                continue
            
            # Simple matching score
            score = 0
            if query_lower in term:
                score += 10
            if query_lower in def_text:
                score += 5
            
            # Check for word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in term:
                    score += 3
                if word in def_text:
                    score += 1
            
            if score > 0:
                results.append({
                    'definition': definition,
                    'score': score
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:int(num_results)]
        
        if not results:
            return "No definitions found matching your query.", ""
        
        # Format results
        search_text = f"**Found {len(results)} definitions for: '{query}'**\n\n"
        
        for i, result in enumerate(results):
            definition = result['definition']
            search_text += f"**{i+1}. {definition.get('term', 'Unknown Term')}** "
            search_text += f"({definition.get('jurisdiction', 'Unknown')} - {definition.get('lihtc_relevance', 'unknown')} relevance)\n"
            search_text += f"*Match Score: {result['score']}*\n\n"
            search_text += f"{definition.get('definition', 'No definition available')}\n\n"
            
            # Add cross-references if available
            if 'cross_references' in definition and definition['cross_references']:
                search_text += f"**Cross-references:** {len(definition['cross_references'])} locations\n"
            
            search_text += f"---\n\n"
        
        # Create summary
        jurisdictions = set(r['definition'].get('jurisdiction', 'Unknown') for r in results)
        relevance_counts = {}
        for result in results:
            rel = result['definition'].get('lihtc_relevance', 'unknown')
            relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
        
        summary_text = f"**Search Summary:**\n"
        summary_text += f"- Query: '{query}'\n"
        summary_text += f"- Results: {len(results)}\n"
        summary_text += f"- Jurisdictions: {', '.join(sorted(jurisdictions))}\n"
        summary_text += f"- Relevance breakdown: {dict(relevance_counts)}\n"
        
        return search_text, summary_text
    
    def get_system_stats(self):
        """Get system statistics from loaded data"""
        
        total_count = len(self.definitions_data)
        
        # Count jurisdictions and relevance
        jurisdictions = set()
        relevance_counts = {}
        
        for definition in self.definitions_data.values():
            jurisdictions.add(definition.get('jurisdiction', 'Unknown'))
            rel = definition.get('lihtc_relevance', 'unknown')
            relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
        
        stats_text = f"""**LIHTC Definition Intelligence System Status**

📊 **Database Statistics:**
- Total Definitions: {total_count:,}
- Jurisdictions: {len(jurisdictions)}
- Data Source: Direct JSON files (ChromaDB bypassed)

🏛️ **Jurisdiction Coverage:**
{', '.join(sorted(list(jurisdictions)[:20]))}{"..." if len(jurisdictions) > 20 else ""}

📈 **LIHTC Relevance Distribution:**
"""
        
        for relevance, count in sorted(relevance_counts.items()):
            percentage = (count / total_count) * 100
            stats_text += f"- {relevance.capitalize()}: {count} ({percentage:.1f}%)\n"
        
        return stats_text
    
    def create_interface(self):
        """Create fixed Gradio interface"""
        
        # Get available filters from loaded data
        jurisdictions = sorted(set(d.get('jurisdiction', 'Unknown') for d in self.definitions_data.values()))
        relevance_options = ['All', 'Critical', 'High', 'Medium', 'Low', 'Minimal']
        
        with gr.Blocks(title="LIHTC Definition Search - M4 Beast (Fixed)") as interface:
            
            gr.Markdown(f"""
            # 🏛️ LIHTC Definition Intelligence System (Fixed)
            ## Search {len(self.definitions_data):,} definitions from {len(set(d.get('jurisdiction', 'Unknown') for d in self.definitions_data.values()))} US LIHTC jurisdictions
            ### ✅ Direct file access - ChromaDB bypassed for reliability
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
                            choices=["All"] + jurisdictions[:30],  # Limit to avoid UI issues
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
    """Launch fixed LIHTC interface"""
    
    print("🏛️ FIXED LIHTC DEFINITION INTERFACE - M4 BEAST")
    print("=" * 60)
    print("🔧 ChromaDB bypassed - Direct file access")
    
    try:
        # Initialize fixed interface
        interface_system = FixedLIHTCInterface()
        
        if not interface_system.definitions_data:
            print("❌ No definitions loaded - check file paths")
            return
        
        # Create and launch interface
        interface = interface_system.create_interface()
        
        print("🚀 Launching fixed interface...")
        print("📱 Access at: http://localhost:7860")
        print(f"🔍 Ready to search {len(interface_system.definitions_data):,} LIHTC definitions!")
        
        # Launch with basic settings
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            quiet=False,
            show_error=True,
            debug=False,
            inbrowser=True  # Auto-open browser
        )
        
    except Exception as e:
        print(f"❌ Failed to launch interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()