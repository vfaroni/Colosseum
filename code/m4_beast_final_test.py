#!/usr/bin/env python3
"""
M4 BEAST DOCLING FINAL TEST - Imperial Power Unleashed!
"""

import time
import os
import psutil
from datetime import datetime
from docling.document_converter import DocumentConverter

def test_m4_beast_final():
    print("🦁 M4 BEAST DOCLING FINAL TEST - IMPERIAL POWER!")
    print("=" * 60)
    
    # System info
    ram_gb = round(psutil.virtual_memory().total / (1024**3))
    cpu_count = psutil.cpu_count()
    print(f"🖥️  M4 Beast: {ram_gb}GB RAM, {cpu_count} CPU cores")
    
    # Test files
    test_files = {
        "CA": "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf",
        "TX": "data_sets/QAP/TX/current/TX_2025_QAP.pdf",
        "OR": "data_sets/QAP/OR/current/2025-qap-final.pdf"
    }
    
    # Initialize converter once
    print("🔧 Initializing Docling converter...")
    converter = DocumentConverter()
    print("✅ Converter ready for imperial-scale processing!")
    
    total_start = time.time()
    results = {}
    
    for state, file_path in test_files.items():
        print(f"\n🚀 Processing {state} QAP...")
        print(f"📄 File: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        # Process document
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)  # MB
        
        try:
            result = converter.convert(file_path)
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / (1024**2)  # MB
            processing_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Extract document info using correct API
            document = result.document
            pages_count = len(document.pages) if hasattr(document, 'pages') and document.pages else 0
            
            # Get text content using export_to_markdown
            try:
                text_content = document.export_to_markdown()
                text_length = len(text_content)
                sample_text = text_content[:300] + "..." if len(text_content) > 300 else text_content
            except Exception as text_error:
                print(f"   ⚠️  Text extraction issue: {text_error}")
                text_length = 0
                sample_text = "Text extraction not available"
            
            # Store results
            results[state] = {
                "processing_time": processing_time,
                "memory_used": memory_delta,
                "pages": pages_count,
                "text_length": text_length,
                "chars_per_sec": text_length / processing_time if processing_time > 0 else 0,
                "pages_per_sec": pages_count / processing_time if processing_time > 0 else 0
            }
            
            print(f"✅ {state} COMPLETE!")
            print(f"   ⏱️  Time: {processing_time:.2f}s")
            print(f"   💾 Memory: {memory_delta:.1f}MB") 
            print(f"   📄 Pages: {pages_count}")
            print(f"   📝 Text: {text_length:,} chars")
            print(f"   🚀 Speed: {pages_count/processing_time:.2f} pages/sec")
            
            if sample_text and text_length > 0:
                print(f"   📖 Sample: {sample_text[:100]}...")
            
        except Exception as e:
            print(f"❌ {state} processing failed: {e}")
            results[state] = {"error": str(e)}
    
    total_time = time.time() - total_start
    
    # Summary
    print("\n🏛️ M4 BEAST IMPERIAL PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"🕒 Total Processing Time: {total_time:.2f} seconds")
    
    successful = [state for state, result in results.items() if "error" not in result]
    total_pages = sum(results[state].get("pages", 0) for state in successful)
    total_chars = sum(results[state].get("text_length", 0) for state in successful)
    
    if successful:
        avg_time = sum(results[state].get("processing_time", 0) for state in successful) / len(successful)
        print(f"✅ Successful: {len(successful)}/{len(test_files)} QAPs")
        print(f"📄 Total Pages: {total_pages}")
        print(f"📝 Total Text: {total_chars:,} characters")
        print(f"⚡ Average Processing: {avg_time:.2f}s per QAP")
        print(f"🚀 Overall Speed: {total_pages/total_time:.2f} pages/sec")
        print(f"🏛️ M4 Beast Performance: IMPERIAL DOMINANCE ACHIEVED!")
    else:
        print("❌ No successful processings")
    
    return results

if __name__ == "__main__":
    test_m4_beast_final()