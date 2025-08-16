#!/usr/bin/env python3
"""
Minimal test to identify ChromaDB/Gradio connection issues
"""

import os
import sys
from pathlib import Path

def test_chromadb_connection():
    """Test basic ChromaDB connection"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        chroma_db_path = str(base_dir / "lihtc_definitions_chromadb")
        
        print(f"🔍 Testing ChromaDB at: {chroma_db_path}")
        
        # Test with minimal settings to avoid telemetry issues
        client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False,
                is_persistent=True
            )
        )
        
        # Try to get collection
        collection = client.get_collection("lihtc_definitions_54_jurisdictions")
        count = collection.count()
        
        print(f"✅ ChromaDB connected successfully")
        print(f"📚 Collection size: {count:,} definitions")
        
        return True, client, collection
        
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False, None, None

def test_simple_search(collection):
    """Test basic search functionality"""
    try:
        results = collection.query(
            query_texts=["qualified basis"],
            n_results=3
        )
        
        print(f"✅ Search test successful")
        print(f"📄 Found {len(results['documents'][0])} results")
        
        # Show first result
        if results['documents'][0]:
            first_meta = results['metadatas'][0][0]
            print(f"   Term: {first_meta.get('term', 'Unknown')}")
            print(f"   Jurisdiction: {first_meta.get('jurisdiction', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_gradio_minimal():
    """Test minimal Gradio interface"""
    try:
        import gradio as gr
        
        def simple_search(query):
            return f"Search query: {query}"
        
        # Create minimal interface
        interface = gr.Interface(
            fn=simple_search,
            inputs=gr.Textbox(label="Test Query"),
            outputs=gr.Textbox(label="Result"),
            title="Minimal Test Interface"
        )
        
        print(f"✅ Gradio interface created")
        print(f"🚀 Launching on localhost:7860...")
        
        # Launch with basic settings
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            quiet=True,
            show_error=True,
            inbrowser=False
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Gradio test failed: {e}")
        return False

def main():
    """Run minimal tests"""
    
    print("🧪 MINIMAL LIHTC SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: ChromaDB Connection
    print("\n1️⃣ Testing ChromaDB Connection...")
    chromadb_success, client, collection = test_chromadb_connection()
    
    if not chromadb_success:
        print("❌ Cannot proceed without ChromaDB")
        return
    
    # Test 2: Basic Search
    print("\n2️⃣ Testing Search Functionality...")
    search_success = test_simple_search(collection)
    
    # Test 3: Gradio Interface
    print("\n3️⃣ Testing Gradio Interface...")
    gradio_success = test_gradio_minimal()
    
    print(f"\n🏁 RESULTS:")
    print(f"   ChromaDB: {'✅' if chromadb_success else '❌'}")
    print(f"   Search: {'✅' if search_success else '❌'}")
    print(f"   Gradio: {'✅' if gradio_success else '❌'}")

if __name__ == "__main__":
    main()