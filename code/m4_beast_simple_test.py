#!/usr/bin/env python3
"""
M4 BEAST DOCLING SIMPLE TEST - Imperial Power Verification
"""

import time
import os
import psutil
from datetime import datetime
from docling.document_converter import DocumentConverter

def test_m4_beast_processing():
    print("🦁 M4 BEAST DOCLING PROCESSING TEST")
    print("=" * 50)
    
    # System info
    ram_gb = round(psutil.virtual_memory().total / (1024**3))
    cpu_count = psutil.cpu_count()
    print(f"🖥️  M4 Beast: {ram_gb}GB RAM, {cpu_count} CPU cores")
    
    # Test file
    test_file = "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    print(f"📄 Test QAP: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    # Initialize converter
    print("🔧 Initializing Docling converter...")
    converter = DocumentConverter()
    print("✅ Converter ready!")
    
    # Process document
    print("🚀 Processing QAP document...")
    start_time = time.time()
    start_memory = psutil.virtual_memory().used / (1024**2)  # MB
    
    try:
        result = converter.convert(test_file)
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used / (1024**2)  # MB
        processing_time = end_time - start_time
        memory_delta = end_memory - start_memory
        
        # Extract document info
        document = result.document
        
        print("✅ PROCESSING COMPLETE!")
        print("=" * 30)
        print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
        print(f"💾 Memory Used: {memory_delta:.1f} MB")
        print(f"📄 Document Pages: {len(document.pages) if document.pages else 0}")
        print(f"📝 Text Length: {len(document.text or ''):,} characters")
        print(f"🏛️ M4 Beast Performance: {len(document.text or '') / processing_time:.0f} chars/sec")
        
        # Save a sample of extracted text
        if document.text:
            sample_text = document.text[:500] + "..." if len(document.text) > 500 else document.text
            print(f"\n📖 Sample Extracted Text:")
            print("-" * 30)
            print(sample_text)
        
        return {
            "success": True,
            "processing_time": processing_time,
            "memory_used": memory_delta,
            "pages": len(document.pages) if document.pages else 0,
            "text_length": len(document.text or ''),
            "performance_chars_per_sec": len(document.text or '') / processing_time if processing_time > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    test_m4_beast_processing()