#!/usr/bin/env python3
"""
Quick Docling vs Llama 8B Test - Single QAP
Accuracy > Speed > Resources
"""

import time
import psutil
import ollama
from docling.document_converter import DocumentConverter

def test_docling_extraction():
    """Test Docling on CA QAP"""
    print("🏛️ DOCLING CHAMPION - Testing CA QAP")
    print("="*40)
    
    qap_file = "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    start_time = time.time()
    start_memory = psutil.virtual_memory().used / (1024**2)
    
    try:
        converter = DocumentConverter()
        result = converter.convert(qap_file)
        text_content = result.document.export_to_markdown()
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used / (1024**2)
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        pages = len(result.document.pages) if result.document.pages else 0
        
        # LIHTC accuracy test
        lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                      'scoring', 'threshold', 'compliance', 'affordability', 'income',
                      'basis', 'rent', 'AMI', 'HUD', 'section 42']
        
        terms_found = sum(1 for term in lihtc_terms if term.lower() in text_content.lower())
        accuracy_score = (terms_found / len(lihtc_terms)) * 100
        
        print(f"✅ DOCLING RESULTS:")
        print(f"   ⏱️  Time: {processing_time:.2f}s")
        print(f"   💾 Memory: {memory_used:.1f}MB")
        print(f"   📄 Pages: {pages}")
        print(f"   📝 Text: {len(text_content):,} chars")
        print(f"   🎯 LIHTC Accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
        print(f"   ⚡ Speed: {pages/processing_time:.2f} pages/sec")
        
        return {
            "time": processing_time,
            "memory": memory_used,
            "pages": pages,
            "text_length": len(text_content),
            "accuracy": accuracy_score,
            "terms_found": terms_found
        }
        
    except Exception as e:
        print(f"❌ Docling failed: {e}")
        return None

def test_llama_8b():
    """Test Llama 8B analysis"""
    print("\n🦙 LLAMA 8B SWIFT - Testing Analysis")
    print("="*40)
    
    # Simple prompt to test basic LIHTC knowledge
    test_prompt = """
What are the key components of a LIHTC QAP (Qualified Allocation Plan)? 
List the main categories that typically receive points in LIHTC tax credit allocation.
Keep response under 200 words.
"""
    
    start_time = time.time()
    start_memory = psutil.virtual_memory().used / (1024**2)
    
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": test_prompt}]
        )
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used / (1024**2)
        
        analysis_time = end_time - start_time
        memory_used = end_memory - start_memory
        response_text = response['message']['content']
        
        # LIHTC accuracy test
        lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                      'scoring', 'threshold', 'compliance', 'affordability', 'income',
                      'basis', 'rent', 'AMI', 'HUD', 'section 42']
        
        terms_found = sum(1 for term in lihtc_terms if term.lower() in response_text.lower())
        accuracy_score = (terms_found / len(lihtc_terms)) * 100
        
        print(f"✅ LLAMA 8B RESULTS:")
        print(f"   ⏱️  Time: {analysis_time:.2f}s")
        print(f"   💾 Memory: {memory_used:.1f}MB")
        print(f"   📝 Response: {len(response_text)} chars")
        print(f"   🎯 LIHTC Accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
        print(f"   ⚡ Speed: {len(response_text.split())/analysis_time:.1f} words/sec")
        print(f"\n📖 Sample Response:")
        print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
        
        return {
            "time": analysis_time,
            "memory": memory_used,
            "response_length": len(response_text),
            "accuracy": accuracy_score,
            "terms_found": terms_found
        }
        
    except Exception as e:
        print(f"❌ Llama 8B failed: {e}")
        return None

def compare_results(docling_result, llama_result):
    """Compare the two approaches"""
    print("\n🏛️ EMPEROR'S JUDGMENT")
    print("="*40)
    
    if not docling_result or not llama_result:
        print("❌ Insufficient results for comparison")
        return
    
    print("🎯 ACCURACY COMPARISON (Primary):")
    print(f"   Docling: {docling_result['accuracy']:.1f}% ({docling_result['terms_found']}/15)")
    print(f"   Llama 8B: {llama_result['accuracy']:.1f}% ({llama_result['terms_found']}/15)")
    accuracy_winner = "Docling" if docling_result['accuracy'] > llama_result['accuracy'] else "Llama 8B"
    print(f"   🏆 Winner: {accuracy_winner}")
    
    print("\n⚡ SPEED COMPARISON (Secondary):")
    print(f"   Docling: {docling_result['time']:.2f}s")
    print(f"   Llama 8B: {llama_result['time']:.2f}s")
    speed_winner = "Docling" if docling_result['time'] < llama_result['time'] else "Llama 8B"
    print(f"   🏆 Winner: {speed_winner}")
    
    print("\n💾 RESOURCE USAGE (Tertiary):")
    print(f"   Docling: {docling_result['memory']:.1f}MB")
    print(f"   Llama 8B: {llama_result['memory']:.1f}MB")
    resource_winner = "Docling" if docling_result['memory'] < llama_result['memory'] else "Llama 8B"
    print(f"   🏆 Winner: {resource_winner}")
    
    # Overall winner based on priorities
    accuracy_points = 3 if accuracy_winner == "Docling" else 0
    speed_points = 2 if speed_winner == "Docling" else 0  
    resource_points = 1 if resource_winner == "Docling" else 0
    
    docling_total = accuracy_points + speed_points + resource_points
    llama_total = 6 - docling_total
    
    overall_winner = "Docling" if docling_total > llama_total else "Llama 8B"
    
    print(f"\n👑 OVERALL PRODUCTION CHAMPION: {overall_winner}")
    print(f"   Docling: {docling_total}/6 points")
    print(f"   Llama 8B: {llama_total}/6 points")
    print(f"   (Accuracy: 3pts, Speed: 2pts, Resources: 1pt)")

if __name__ == "__main__":
    print("🏛️ QUICK DOCLING vs LLAMA 8B BATTLE")
    print("Priority: Accuracy > Speed > Resources")
    print("="*60)
    
    docling_result = test_docling_extraction()
    llama_result = test_llama_8b()
    
    compare_results(docling_result, llama_result)