#!/usr/bin/env python3
"""Quick chunking comparison between GPT-OSS and Llama"""

import subprocess
import json
import time

# Sample QAP text for chunking test
sample_text = """
Section 10325(c)(5) Transit Amenities
The project is located where there is a bus rapid transit station, light rail station, 
commuter rail station, ferry terminal, bus station, or public bus stop within 1/3 mile 
from the site with service at least every 30 minutes during peak hours 7-9 AM and 4-6 PM.
Projects meeting this requirement receive 7 points if density exceeds 25 units per acre.

Section 10325(c)(6) Site Amenities
Amenities must be appropriate to the tenant population and at least one must be provided.
Community gardens, playground equipment, and computer learning centers are eligible.
"""

def test_chunking(model, text):
    """Test chunking with a model"""
    prompt = f"Break this LIHTC QAP text into 3 logical chunks for retrieval. Be concise:\n{text}"
    
    start = time.time()
    cmd = f'echo {json.dumps(prompt)} | timeout 20 ollama run {model} 2>/dev/null'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        elapsed = time.time() - start
        
        # Clean output
        output = result.stdout.strip()
        # Remove progress indicators
        clean_output = '\n'.join([line for line in output.split('\n') 
                                 if not line.startswith('[?') and line.strip()])
        
        return {"time": elapsed, "output": clean_output, "success": True}
    except subprocess.TimeoutExpired:
        return {"time": 20, "output": "Timeout", "success": False}
    except Exception as e:
        return {"time": time.time() - start, "output": str(e), "success": False}

print("🔬 Quick Chunking Test: GPT-OSS vs Llama")
print("="*60)
print(f"Test text: {len(sample_text)} characters")
print()

# Test GPT-OSS
print("📊 Testing GPT-OSS 20B...")
gpt_result = test_chunking("gpt-oss:20b", sample_text)
print(f"✅ Time: {gpt_result['time']:.2f}s")
if gpt_result['success']:
    print("Output preview:")
    print(gpt_result['output'][:300])
else:
    print(f"❌ Failed: {gpt_result['output']}")

print("\n" + "-"*60)

# Test Llama
print("📊 Testing Llama 3.3 70B...")
llama_result = test_chunking("llama3.3:70b", sample_text)
print(f"✅ Time: {llama_result['time']:.2f}s")
if llama_result['success']:
    print("Output preview:")
    print(llama_result['output'][:300])
else:
    print(f"❌ Failed: {llama_result['output']}")

print("\n" + "="*60)
print("🎯 COMPARISON RESULTS:")
print("="*60)

if gpt_result['success'] and llama_result['success']:
    speed_diff = abs(gpt_result['time'] - llama_result['time'])
    faster = "GPT-OSS" if gpt_result['time'] < llama_result['time'] else "Llama"
    print(f"⚡ {faster} is {speed_diff:.1f}s faster")
    
    print(f"\nGPT-OSS: {gpt_result['time']:.2f}s - Output length: {len(gpt_result['output'])} chars")
    print(f"Llama:   {llama_result['time']:.2f}s - Output length: {len(llama_result['output'])} chars")
    
    print("\n📝 RECOMMENDATION FOR CHUNKING:")
    print("-"*30)
    
    if gpt_result['time'] < 5 and gpt_result['time'] < llama_result['time']:
        print("✅ Use GPT-OSS 20B for chunking:")
        print("   • Faster response times")
        print("   • Shows reasoning process")
        print("   • More efficient (13GB vs 42GB)")
    elif llama_result['time'] < gpt_result['time']:
        print("✅ Use Llama 3.3 70B for chunking:")
        print("   • Better for detailed analysis")
        print("   • More comprehensive outputs")
    else:
        print("✅ Use hybrid approach:")
        print("   • GPT-OSS for quick semantic chunks")
        print("   • Llama for detailed regulatory chunks")
        print("   • Docling for PDF extraction (keep as-is)")
    
    print("\n💡 With 128GB RAM, you can run both models simultaneously")
    print("   for A/B testing and quality comparison.")
else:
    print("⚠️ One or both models failed the test")
    
print()