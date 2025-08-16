#!/usr/bin/env python3
"""
IBM Granite vs Llama 3 Benchmark Framework for LIHTC Applications
Focuses specifically on the challenging street_address extraction problem
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
import re

@dataclass
class ExtractionResult:
    """Results from model extraction"""
    model_name: str
    field_name: str
    extracted_value: Optional[str]
    confidence: float
    processing_time: float
    raw_response: str = ""
    validation_flags: List[str] = None
    
    def __post_init__(self):
        if self.validation_flags is None:
            self.validation_flags = []

@dataclass
class BenchmarkTest:
    """Individual benchmark test case"""
    test_id: str
    field_name: str
    expected_value: Optional[str]
    input_text: str
    difficulty_level: str  # easy, medium, hard
    failure_reason: Optional[str] = None

class GraniteVsLlamaBenchmark:
    """Compare IBM Granite and Llama 3 models for LIHTC extraction"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        
        # Models to test
        self.models = {
            'llama_8b': 'llama3.1:8b',
            'llama_70b': 'llama3.1:70b',
            'granite_3b': 'granite-3b-code-instruct',
            'granite_8b': 'granite-8b-code-instruct',
            'granite_20b': 'granite-20b-code-instruct'
        }
        
        # Test cases based on TDHCA benchmark findings
        self.test_cases = self._create_address_test_cases()
        
        self.results = []
    
    def _create_address_test_cases(self) -> List[BenchmarkTest]:
        """Create test cases for the problematic street_address field (26.9% success)"""
        
        test_cases = [
            # Easy cases (should work for all models)
            BenchmarkTest(
                test_id="addr_001",
                field_name="street_address",
                expected_value="1234 Main Street",
                input_text="Project Address: 1234 Main Street, Dallas, TX 75201",
                difficulty_level="easy"
            ),
            
            # Medium cases (formatting challenges)
            BenchmarkTest(
                test_id="addr_002", 
                field_name="street_address",
                expected_value="5678 Oak Park Boulevard",
                input_text="Site Location:\n5678 Oak Park Boulevard\nHouston, Texas 77019",
                difficulty_level="medium"
            ),
            
            # Hard cases (complex formatting, current system fails)
            BenchmarkTest(
                test_id="addr_003",
                field_name="street_address", 
                expected_value="9012 North Elm Street, Suite 100",
                input_text="Development Site: Located at 9012 North Elm Street, Suite 100 in the city of Austin, Travis County, Texas",
                difficulty_level="hard"
            ),
            
            # Very hard (table format, why current system fails)
            BenchmarkTest(
                test_id="addr_004",
                field_name="street_address",
                expected_value="3456 Technology Drive",
                input_text="""
Property Information:
Address Line 1: 3456 Technology Drive
Address Line 2: Building A
City: San Antonio
County: Bexar
State: Texas
Zip: 78249
""",
                difficulty_level="hard"
            ),
            
            # Edge case (multiple addresses in text)
            BenchmarkTest(
                test_id="addr_005",
                field_name="street_address",
                expected_value="7890 Innovation Way",
                input_text="Developer office located at 1111 Business Blvd. Project site address: 7890 Innovation Way, Fort Worth, TX.",
                difficulty_level="hard"
            )
        ]
        
        return test_cases
    
    def _create_extraction_prompt(self, field_name: str, text: str) -> str:
        """Create optimized prompt for each model type"""
        
        if field_name == "street_address":
            return f"""Extract the street address of the development project from the following text.
Return ONLY the street address (street number and name), not the full address.

Examples:
- Input: "Located at 1234 Main Street, Dallas, TX" → Output: "1234 Main Street"
- Input: "Project site: 5678 Oak Avenue, Building B" → Output: "5678 Oak Avenue, Building B"

Text to analyze:
{text}

Street Address:"""
        
        return f"Extract the {field_name} from this text: {text}"
    
    def _call_ollama_model(self, model: str, prompt: str) -> Dict[str, Any]:
        """Call Ollama model with prompt"""
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistency
                        "top_p": 0.9,
                        "num_predict": 100   # Limit response length
                    }
                },
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result.get('response', '').strip(),
                    'processing_time': processing_time
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'processing_time': processing_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def _validate_extraction(self, extracted: str, expected: str) -> tuple[bool, float]:
        """Validate extraction and calculate confidence"""
        
        if not extracted or not expected:
            return False, 0.0
        
        # Clean both strings for comparison
        extracted_clean = re.sub(r'[^\w\s]', '', extracted.lower().strip())
        expected_clean = re.sub(r'[^\w\s]', '', expected.lower().strip())
        
        # Exact match
        if extracted_clean == expected_clean:
            return True, 1.0
        
        # Partial match (contains expected)
        if expected_clean in extracted_clean:
            return True, 0.8
        
        # Word overlap
        extracted_words = set(extracted_clean.split())
        expected_words = set(expected_clean.split())
        
        if expected_words and extracted_words:
            overlap = len(expected_words.intersection(extracted_words))
            total = len(expected_words)
            overlap_score = overlap / total
            
            if overlap_score >= 0.6:
                return True, overlap_score
        
        return False, 0.0
    
    def run_model_comparison(self, test_case: BenchmarkTest, model_name: str) -> ExtractionResult:
        """Run a single test case against a model"""
        
        model_id = self.models.get(model_name)
        if not model_id:
            return ExtractionResult(
                model_name=model_name,
                field_name=test_case.field_name,
                extracted_value=None,
                confidence=0.0,
                processing_time=0.0,
                validation_flags=["Model not available"]
            )
        
        # Create prompt
        prompt = self._create_extraction_prompt(test_case.field_name, test_case.input_text)
        
        # Call model
        result = self._call_ollama_model(model_id, prompt)
        
        if not result['success']:
            return ExtractionResult(
                model_name=model_name,
                field_name=test_case.field_name,
                extracted_value=None,
                confidence=0.0,
                processing_time=result['processing_time'],
                validation_flags=[f"Model error: {result['error']}"]
            )
        
        # Validate result
        extracted = result['response']
        is_correct, confidence = self._validate_extraction(extracted, test_case.expected_value)
        
        return ExtractionResult(
            model_name=model_name,
            field_name=test_case.field_name,
            extracted_value=extracted,
            confidence=confidence,
            processing_time=result['processing_time'],
            raw_response=extracted,
            validation_flags=["Correct" if is_correct else "Incorrect"]
        )
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark across all models and test cases"""
        
        print("🚀 Starting Granite vs Llama Benchmark")
        print("=" * 60)
        print(f"Test Cases: {len(self.test_cases)}")
        print(f"Models: {list(self.models.keys())}")
        print()
        
        benchmark_results = {
            'benchmark_start': time.time(),
            'model_performance': {},
            'test_case_results': {},
            'summary_stats': {}
        }
        
        # Run each test case against each model
        for test_case in self.test_cases:
            print(f"📝 Running test: {test_case.test_id} ({test_case.difficulty_level})")
            
            test_results = {}
            
            for model_name in self.models.keys():
                print(f"  Testing {model_name}...", end="")
                
                result = self.run_model_comparison(test_case, model_name)
                test_results[model_name] = result
                
                status = "✅" if result.confidence > 0.6 else "❌"
                print(f" {status} ({result.confidence:.2f})")
            
            benchmark_results['test_case_results'][test_case.test_id] = test_results
            print()
        
        # Calculate summary statistics
        model_stats = {}
        for model_name in self.models.keys():
            correct_count = 0
            total_time = 0
            total_confidence = 0
            
            for test_id, test_results in benchmark_results['test_case_results'].items():
                result = test_results[model_name]
                if result.confidence > 0.6:  # Consider >0.6 as correct
                    correct_count += 1
                total_time += result.processing_time
                total_confidence += result.confidence
            
            model_stats[model_name] = {
                'accuracy': (correct_count / len(self.test_cases)) * 100,
                'avg_processing_time': total_time / len(self.test_cases),
                'avg_confidence': total_confidence / len(self.test_cases)
            }
        
        benchmark_results['model_performance'] = model_stats
        benchmark_results['benchmark_duration'] = time.time() - benchmark_results['benchmark_start']
        
        return benchmark_results
    
    def print_benchmark_summary(self, results: Dict[str, Any]):
        """Print formatted benchmark results"""
        
        print("\n📊 Benchmark Results Summary")
        print("=" * 60)
        
        # Model performance ranking
        model_perf = results['model_performance']
        sorted_models = sorted(model_perf.items(), key=lambda x: x[1]['accuracy'], reverse=True)
        
        print("\n🏆 Model Rankings (by accuracy):")
        for i, (model, stats) in enumerate(sorted_models, 1):
            print(f"{i}. {model.upper()}")
            print(f"   Accuracy: {stats['accuracy']:.1f}%")
            print(f"   Avg Time: {stats['avg_processing_time']:.2f}s")
            print(f"   Confidence: {stats['avg_confidence']:.2f}")
            print()
        
        # Best model analysis
        best_model = sorted_models[0]
        print(f"🥇 Best Performer: {best_model[0].upper()}")
        print(f"   Improvement over current system: +{best_model[1]['accuracy'] - 26.9:.1f}% points")
        
        # Recommendations
        print("\n💡 Recommendations for M4 Beast:")
        if 'granite' in best_model[0]:
            print("   ✅ IBM Granite shows superior performance")
            print("   ✅ Deploy Granite for address extraction")
        else:
            print("   ✅ Llama maintains competitive performance")
            print("   ✅ Consider cost vs performance trade-offs")
        
        # Save results
        output_path = Path(__file__).parent / 'granite_vs_llama_benchmark.json'
        with open(output_path, 'w') as f:
            # Convert dataclasses to dicts for JSON serialization
            json_results = self._convert_results_for_json(results)
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_path}")
    
    def _convert_results_for_json(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Convert results to JSON-serializable format"""
        
        json_results = results.copy()
        
        # Convert test case results
        json_test_results = {}
        for test_id, test_results in results['test_case_results'].items():
            json_test_results[test_id] = {}
            for model_name, result in test_results.items():
                json_test_results[test_id][model_name] = {
                    'model_name': result.model_name,
                    'field_name': result.field_name,
                    'extracted_value': result.extracted_value,
                    'confidence': result.confidence,
                    'processing_time': result.processing_time,
                    'validation_flags': result.validation_flags
                }
        
        json_results['test_case_results'] = json_test_results
        
        return json_results

def main():
    """Run the complete Granite vs Llama benchmark"""
    
    benchmark = GraniteVsLlamaBenchmark()
    
    print("🎯 Focus Area: Street Address Extraction")
    print("Current System Performance: 26.9% accuracy")
    print("Target: Improve to >90% accuracy")
    print()
    
    # Run benchmark
    results = benchmark.run_full_benchmark()
    
    # Print summary
    benchmark.print_benchmark_summary(results)
    
    print("\n🎯 Next Steps:")
    print("1. Deploy winning model on M4 Beast")
    print("2. Test with full TDHCA dataset")
    print("3. Integrate with production system")

if __name__ == "__main__":
    main()