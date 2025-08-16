#!/usr/bin/env python3
"""
Quick Codellama 34B Test for Three-Way Comparison
"""

import time
import psutil
import ollama

def test_codellama_34b():
    """Test Codellama 34B LIHTC analysis"""
    print("🦙 CODELLAMA 34B THE MIGHTY - LIHTC Analysis")
    print("="*45)
    
    test_prompt = """
Analyze LIHTC (Low-Income Housing Tax Credit) QAP requirements. Provide:

1. KEY ALLOCATION CRITERIA: Main scoring categories for tax credit allocation
2. COMPLIANCE REQUIREMENTS: Critical federal and state requirements  
3. INCOME LIMITS: AMI restrictions and tenant qualification rules
4. DEADLINES: Application and compliance timeline requirements
5. BASIS CALCULATION: Qualified basis and eligible costs overview

Keep response comprehensive but under 400 words.
"""
    
    start_time = time.time()
    start_memory = psutil.virtual_memory().used / (1024**2)
    
    try:
        response = ollama.chat(
            model="codellama:34b",
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
        
        # Analysis quality - specific LIHTC concepts
        quality_terms = ['allocation plan', 'scoring criteria', 'set aside', 'compliance period',
                       'placed in service', 'qualified census tract', 'difficult development area',
                       'maximum rent', 'income certification', 'recapture']
        quality_found = sum(1 for term in quality_terms if term.lower() in response_text.lower())
        quality_score = (quality_found / len(quality_terms)) * 100
        
        print(f"✅ CODELLAMA 34B RESULTS:")
        print(f"   ⏱️  Time: {analysis_time:.2f}s") 
        print(f"   💾 Memory: {memory_used:.1f}MB")
        print(f"   📝 Response: {len(response_text)} chars")
        print(f"   🎯 LIHTC Accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
        print(f"   📊 Quality Score: {quality_found}/{len(quality_terms)} ({quality_score:.1f}%)")
        print(f"   ⚡ Speed: {len(response_text.split())/analysis_time:.1f} words/sec")
        
        # Show sample response
        print(f"\n📖 Sample Response:")
        sample = response_text[:300] + "..." if len(response_text) > 300 else response_text
        print(sample)
        
        return {
            "time": analysis_time,
            "memory": memory_used,
            "response_length": len(response_text),
            "accuracy": accuracy_score,
            "quality": quality_score,
            "terms_found": terms_found,
            "quality_found": quality_found,
            "words_per_sec": len(response_text.split()) / analysis_time,
            "response_sample": response_text
        }
        
    except Exception as e:
        print(f"❌ Codellama 34B failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    test_codellama_34b()