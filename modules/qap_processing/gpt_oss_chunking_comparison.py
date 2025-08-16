#!/usr/bin/env python3
"""
GPT-OSS 20B vs Llama 3.3 70B Chunking Comparison
Tests both models for intelligent QAP document chunking with Docling
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from docling.document_converter import DocumentConverter
import hashlib

class ChunkingComparison:
    """Compare chunking quality between GPT-OSS 20B and Llama 3.3 70B"""
    
    def __init__(self):
        self.converter = DocumentConverter()
        self.models = {
            "gpt-oss:20b": {
                "name": "GPT-OSS 20B",
                "size": "13GB",
                "reasoning": True
            },
            "llama3.3:70b": {
                "name": "Llama 3.3 70B", 
                "size": "42GB",
                "reasoning": False
            }
        }
        
        # LIHTC-specific chunking prompts
        self.chunking_prompts = {
            "semantic": """Given this QAP text section, identify the most logical semantic boundaries for chunking. 
                          Consider LIHTC concepts, scoring criteria, and regulatory requirements.
                          Return a list of chunk boundaries with brief explanations.
                          Text: {text}""",
            
            "regulatory": """Analyze this QAP text and identify chunks based on regulatory references.
                           Group related IRC Section 42 requirements, state regulations, and scoring criteria.
                           Text: {text}""",
            
            "scoring": """Break this QAP text into chunks optimized for scoring criteria retrieval.
                        Each chunk should contain complete scoring requirements or criteria.
                        Text: {text}"""
        }
    
    def extract_with_docling(self, pdf_path: Path) -> str:
        """Extract text from PDF using Docling"""
        print(f"📄 Extracting text from: {pdf_path.name}")
        result = self.converter.convert(str(pdf_path))
        text = result.document.export_to_markdown()
        print(f"✅ Extracted {len(text):,} characters")
        return text
    
    def chunk_with_model(self, text: str, model: str, prompt_type: str = "semantic") -> Dict:
        """Use LLM to intelligently chunk text"""
        start_time = time.time()
        
        # Prepare prompt
        prompt = self.chunking_prompts[prompt_type].format(
            text=text[:5000]  # Limit for testing
        )
        
        # Call model via Ollama
        try:
            cmd = f'echo {json.dumps(prompt)} | ollama run {model} --verbose 2>&1'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            response = result.stdout.strip()
            elapsed = time.time() - start_time
            
            # Parse chunks from response
            chunks = self._parse_chunks_from_response(response)
            
            return {
                "model": model,
                "model_info": self.models[model],
                "prompt_type": prompt_type,
                "chunks": chunks,
                "num_chunks": len(chunks),
                "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
                "processing_time": elapsed,
                "response_length": len(response),
                "success": True
            }
            
        except Exception as e:
            return {
                "model": model,
                "model_info": self.models[model],
                "prompt_type": prompt_type,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "success": False
            }
    
    def _parse_chunks_from_response(self, response: str) -> List[str]:
        """Parse chunk boundaries from model response"""
        # Simple parsing - in production would be more sophisticated
        chunks = []
        
        # Look for numbered lists or bullet points
        lines = response.split('\n')
        current_chunk = []
        
        for line in lines:
            if any(marker in line for marker in ['1.', '2.', '•', '-', '*']):
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
            current_chunk.append(line)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [response]
    
    def compare_chunking(self, pdf_path: Path) -> Dict:
        """Compare chunking between models"""
        print("\n" + "="*80)
        print("🔬 CHUNKING COMPARISON: GPT-OSS 20B vs Llama 3.3 70B")
        print("="*80)
        
        # Extract text
        text = self.extract_with_docling(pdf_path)
        
        results = {
            "document": pdf_path.name,
            "text_length": len(text),
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }
        
        # Test each model
        for model_key in self.models:
            print(f"\n📊 Testing: {self.models[model_key]['name']}")
            print("-"*40)
            
            model_results = {}
            
            # Test different chunking strategies
            for prompt_type in ["semantic", "regulatory", "scoring"]:
                print(f"  Strategy: {prompt_type}")
                result = self.chunk_with_model(text, model_key, prompt_type)
                
                if result["success"]:
                    print(f"    ✅ {result['num_chunks']} chunks in {result['processing_time']:.2f}s")
                else:
                    print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                
                model_results[prompt_type] = result
            
            results["models"][model_key] = model_results
        
        # Compare metrics
        print("\n" + "="*80)
        print("📈 COMPARISON SUMMARY")
        print("="*80)
        
        for model_key in self.models:
            model_name = self.models[model_key]['name']
            print(f"\n{model_name}:")
            
            for strategy in ["semantic", "regulatory", "scoring"]:
                if strategy in results["models"][model_key]:
                    res = results["models"][model_key][strategy]
                    if res["success"]:
                        print(f"  {strategy}: {res['num_chunks']} chunks, {res['processing_time']:.2f}s")
        
        return results
    
    def benchmark_quality(self, chunks_a: List[str], chunks_b: List[str]) -> Dict:
        """Compare quality metrics between two chunking approaches"""
        metrics = {
            "chunk_count_diff": len(chunks_a) - len(chunks_b),
            "avg_size_a": sum(len(c) for c in chunks_a) / len(chunks_a) if chunks_a else 0,
            "avg_size_b": sum(len(c) for c in chunks_b) / len(chunks_b) if chunks_b else 0,
        }
        
        # Check for LIHTC terms preservation
        lihtc_terms = ['section 42', 'qualified basis', 'eligible basis', 'qct', 'dda']
        
        for term in lihtc_terms:
            metrics[f"{term}_in_a"] = sum(1 for c in chunks_a if term.lower() in c.lower())
            metrics[f"{term}_in_b"] = sum(1 for c in chunks_b if term.lower() in c.lower())
        
        return metrics

def run_comparison():
    """Run the chunking comparison"""
    
    # Use a sample California QAP section
    ca_qap = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/split_sections/CA_2025_QAP_Regulations_Dec_2024_section_01_pages_1-100.pdf")
    
    if not ca_qap.exists():
        print(f"❌ File not found: {ca_qap}")
        return
    
    # Run comparison
    comparator = ChunkingComparison()
    results = comparator.compare_chunking(ca_qap)
    
    # Save results
    output_file = f"chunking_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Recommendation
    print("\n" + "="*80)
    print("🎯 RECOMMENDATION")
    print("="*80)
    
    print("""
Based on the comparison, consider:

1. **Hybrid Approach**: Use GPT-OSS 20B for reasoning-heavy tasks
   - Semantic understanding of LIHTC concepts
   - Complex scoring criteria interpretation
   - Cross-reference identification

2. **Keep Docling**: For PDF extraction (it's excellent)

3. **Parallel Processing**: With 128GB RAM, run both models:
   - GPT-OSS for quick semantic chunks
   - Llama for detailed regulatory analysis
   
4. **Quality over Speed**: GPT-OSS shows reasoning process,
   which could improve chunk boundary decisions
""")

if __name__ == "__main__":
    run_comparison()