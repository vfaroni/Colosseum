#!/usr/bin/env python3
"""
Granite Model Benchmark for LIHTC Address Extraction
Test Granite against our failing address cases
"""

import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time

class GraniteLIHTCBenchmark:
    
    def __init__(self, model_path="ibm-granite/granite-3.1-8b-instruct"):
        print(f"🔥 Loading Granite model: {model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Test cases from TDHCA benchmark (our failing cases)
        self.test_cases = [
            {
                "id": "tdhca_fail_001",
                "input": "Development Site: Located at 9012 North Elm Street, Suite 100 in the city of Austin, Travis County, Texas",
                "expected": "9012 North Elm Street, Suite 100",
                "difficulty": "hard"
            },
            {
                "id": "tdhca_fail_002", 
                "input": """Property Information:
Address Line 1: 3456 Technology Drive
Address Line 2: Building A
City: San Antonio
County: Bexar
State: Texas""",
                "expected": "3456 Technology Drive, Building A",
                "difficulty": "very_hard"
            },
            {
                "id": "tdhca_fail_003",
                "input": "Developer office located at 1111 Business Blvd. Project site address: 7890 Innovation Way, Fort Worth, TX.",
                "expected": "7890 Innovation Way",
                "difficulty": "hard"
            }
        ]
    
    def extract_address(self, text: str) -> str:
        """Extract address using Granite model"""
        
        prompt = f"""Extract the street address of the development project from this text. Return ONLY the street address.

Text: {text}

Street Address:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the generated part
        generated = response[len(prompt):].strip()
        return generated
    
    def run_benchmark(self):
        """Run benchmark against failing TDHCA cases"""
        
        print("🎯 Granite LIHTC Address Extraction Benchmark")
        print("=" * 60)
        
        results = []
        
        for test_case in self.test_cases:
            print(f"\n📝 Test: {test_case['id']} ({test_case['difficulty']})")
            
            start_time = time.time()
            extracted = self.extract_address(test_case['input'])
            processing_time = time.time() - start_time
            
            # Simple validation
            expected_clean = test_case['expected'].lower().replace(',', '').replace('.', '')
            extracted_clean = extracted.lower().replace(',', '').replace('.', '')
            
            success = expected_clean in extracted_clean or extracted_clean in expected_clean
            
            result = {
                'test_id': test_case['id'],
                'expected': test_case['expected'],
                'extracted': extracted,
                'success': success,
                'processing_time': processing_time,
                'difficulty': test_case['difficulty']
            }
            
            results.append(result)
            
            status = "✅" if success else "❌"
            print(f"  {status} Expected: {test_case['expected']}")
            print(f"     Extracted: {extracted}")
            print(f"     Time: {processing_time:.2f}s")
        
        # Calculate summary
        success_count = sum(1 for r in results if r['success'])
        accuracy = (success_count / len(results)) * 100
        avg_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"\n📊 Granite Results Summary:")
        print(f"Accuracy: {accuracy:.1f}% ({success_count}/{len(results)})")
        print(f"Avg Time: {avg_time:.2f}s")
        print(f"vs Current System: {accuracy:.1f}% vs 26.9% (+{accuracy-26.9:.1f} points)")
        
        # Save results
        with open('granite_benchmark_results.json', 'w') as f:
            json.dump({
                'model': 'granite-3.1-8b-instruct',
                'accuracy': accuracy,
                'avg_processing_time': avg_time,
                'improvement_over_current': accuracy - 26.9,
                'detailed_results': results
            }, f, indent=2)
        
        print("💾 Results saved to granite_benchmark_results.json")
        
        return results

if __name__ == "__main__":
    try:
        benchmark = GraniteLIHTCBenchmark()
        benchmark.run_benchmark()
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        print("Make sure Granite model is installed first!")
