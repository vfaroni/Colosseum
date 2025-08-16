#!/usr/bin/env python3
"""
LIHTC QAP RAG Demo for Vitor
Interactive demonstration of cross-jurisdictional LIHTC research system
"""

from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery
import time

def demo_banner():
    print("=" * 60)
    print("🏛️  LIHTC QAP RAG SYSTEM - LIVE DEMO")
    print("=" * 60)
    print("📊 Coverage: 54 US Jurisdictions (50 states + DC + territories)")
    print("🔍 Documents: 27,344+ knowledge chunks")
    print("⚡ Technology: ChromaDB vector search with MPS acceleration")
    print("💰 Value: $10,000+ savings vs commercial databases per property")
    print("=" * 60)

def run_preset_demos(query_system):
    """Run impressive preset demos"""
    demos = [
        {
            'title': 'California Construction Standards',
            'query': 'minimum construction standards accessibility requirements',
            'states': ['CA'],
            'description': 'Find specific CTCAC construction requirements'
        },
        {
            'title': 'Cross-State Tie-Breaker Comparison', 
            'query': 'tie breaker scoring criteria',
            'states': ['CA', 'TX', 'FL', 'NY'],
            'description': 'Compare how 4 major states handle tie-breakers'
        },
        {
            'title': 'Income Verification Procedures',
            'query': 'income verification tenant certification procedures',
            'states': ['CA', 'TX'],
            'description': 'Find income verification requirements'
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n🎯 DEMO {i}: {demo['title']}")
        print(f"📝 Query: \"{demo['query']}\"")
        print(f"🗺️ States: {demo['states']}")
        print(f"💡 Purpose: {demo['description']}")
        
        start_time = time.time()
        results = query_system.semantic_search_unified(
            demo['query'],
            search_namespace='state',
            states=demo['states'],
            limit=6
        )
        search_time = time.time() - start_time
        
        print(f"⚡ Results: {len(results)} found in {search_time*1000:.0f}ms")
        
        # Group by state
        by_state = {}
        for result in results:
            state = result['state_code'] or 'Unknown'
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(result)
        
        for state, state_results in by_state.items():
            if state_results:
                best = state_results[0]
                print(f"   🏛️ {state}: {best['section_title']} (Score: {best['score']:.3f})")
                print(f"      {best['content'][:120]}...")
        
        input("\n⏸️  Press Enter to continue...")

def interactive_mode(query_system):
    """Let Vitor ask his own questions"""
    print("\n🎤 INTERACTIVE MODE - Ask Your Own Questions!")
    print("💭 Try: 'affordable housing scoring', 'construction timeline', 'income limits'")
    print("🗺️ States: CA, TX, FL, NY, WA, IL, etc. (or leave blank for all)")
    print("❌ Type 'quit' to exit")
    
    while True:
        print("\n" + "-" * 50)
        query = input("📝 Your LIHTC question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q', '']:
            break
            
        states_input = input("🗺️ Specific states (CA,TX,FL) or Enter for all: ").strip()
        states = [s.strip().upper() for s in states_input.split(',')] if states_input else None
        
        print(f"\n🔍 Searching: \"{query}\"")
        if states:
            print(f"🗺️ States: {states}")
        
        start_time = time.time()
        results = query_system.semantic_search_unified(
            query,
            search_namespace='state',
            states=states,
            limit=5
        )
        search_time = time.time() - start_time
        
        print(f"⚡ Found {len(results)} results in {search_time*1000:.0f}ms")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. {result['state_code']} - {result['section_title']}")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Content: {result['content'][:200]}...")

def main():
    demo_banner()
    
    print("\n🚀 Initializing system...")
    start_time = time.time()
    
    base_dir = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets'
    query_system = UnifiedLIHTCRAGQuery(base_dir)
    
    init_time = time.time() - start_time
    print(f"✅ System loaded in {init_time:.1f} seconds")
    
    print("\n🎬 Choose demo mode:")
    print("1. Preset Demos (recommended for first viewing)")
    print("2. Interactive Mode (let Vitor ask questions)")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == '1':
        run_preset_demos(query_system)
        
        # Offer interactive mode after presets
        continue_interactive = input("\n🎤 Continue with interactive mode? (y/n): ").strip().lower()
        if continue_interactive in ['y', 'yes']:
            interactive_mode(query_system)
    else:
        interactive_mode(query_system)
    
    print("\n🎉 Demo complete! Thank you for exploring the LIHTC QAP RAG system.")
    print("💼 Business impact: Industry-first 54 jurisdiction coverage")
    print("🚀 Next steps: API deployment and premium service development")

if __name__ == "__main__":
    main()