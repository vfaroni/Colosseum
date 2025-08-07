#!/usr/bin/env python3
"""
M4 BEAST DOCLING HYBRID BENCHMARK
Imperial-Scale LIHTC QAP Processing Performance Test
"""

import time
import json
import platform
import os
import psutil
from datetime import datetime
from pathlib import Path
from docling.document_converter import DocumentConverter

class M4BeastBenchmark:
    def __init__(self):
        self.base_path = Path(".")
        self.qap_paths = {
            "CA": "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf",
            "TX": "data_sets/QAP/TX/current/TX_2025_QAP.pdf", 
            "OR": "data_sets/QAP/OR/current/2025-qap-final.pdf"
        }
        self.results = {}
        
    def get_system_info(self):
        """Get M4 Beast system information"""
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3)),
            "cpu_count": psutil.cpu_count(),
            "python_version": platform.python_version(),
            "test_time": datetime.now().isoformat()
        }
    
    def benchmark_docling_processing(self, state, pdf_path):
        """Benchmark Docling processing for a single QAP"""
        print(f"\n🚀 Processing {state} QAP: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return None
            
        # Initialize Docling converter
        converter = DocumentConverter()
        
        # Start timing and monitoring
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        start_cpu = psutil.cpu_percent()
        
        try:
            # Process the QAP with Docling
            result = converter.convert(pdf_path)
            
            # Stop timing
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            processing_time = end_time - start_time
            memory_used = (end_memory - start_memory) / (1024**2)  # MB
            
            # Extract metrics
            document = result.document
            
            metrics = {
                "state": state,
                "file_path": pdf_path,
                "processing_time_seconds": round(processing_time, 2),
                "memory_used_mb": round(memory_used, 2),
                "pages_processed": len(document.pages) if document.pages else 0,
                "tables_extracted": len([item for page in document.pages or [] for item in page.cells or [] if item.type == "table"]),
                "text_length": len(document.text or ""),
                "success": True
            }
            
            print(f"✅ {state} processed in {processing_time:.2f}s")
            print(f"   📄 Pages: {metrics['pages_processed']}")
            print(f"   💾 Memory: {memory_used:.1f}MB")
            print(f"   📝 Text length: {metrics['text_length']:,} chars")
            
            return metrics
            
        except Exception as e:
            error_metrics = {
                "state": state,
                "file_path": pdf_path,
                "processing_time_seconds": time.time() - start_time,
                "error": str(e),
                "success": False
            }
            print(f"❌ {state} processing failed: {e}")
            return error_metrics
    
    def run_full_benchmark(self):
        """Run complete M4 Beast benchmark suite"""
        print("🦁 M4 BEAST DOCLING HYBRID BENCHMARK")
        print("=" * 50)
        
        # Get system info
        system_info = self.get_system_info()
        print(f"🖥️  System: {system_info['machine']} - {system_info['ram_gb']}GB RAM")
        print(f"🧠 CPU Cores: {system_info['cpu_count']}")
        print(f"🐍 Python: {system_info['python_version']}")
        
        benchmark_results = {
            "system_info": system_info,
            "qap_results": {},
            "summary": {}
        }
        
        total_start_time = time.time()
        successful_processings = 0
        total_pages = 0
        total_text = 0
        
        # Process each test QAP
        for state, pdf_path in self.qap_paths.items():
            result = self.benchmark_docling_processing(state, pdf_path)
            benchmark_results["qap_results"][state] = result
            
            if result and result.get("success"):
                successful_processings += 1
                total_pages += result.get("pages_processed", 0)
                total_text += result.get("text_length", 0)
        
        total_time = time.time() - total_start_time
        
        # Calculate summary metrics
        benchmark_results["summary"] = {
            "total_processing_time": round(total_time, 2),
            "successful_processings": successful_processings,
            "total_qaps_attempted": len(self.qap_paths),
            "total_pages_processed": total_pages,
            "total_text_extracted": total_text,
            "average_processing_time": round(total_time / len(self.qap_paths), 2),
            "pages_per_second": round(total_pages / total_time, 2) if total_time > 0 else 0,
            "success_rate": round((successful_processings / len(self.qap_paths)) * 100, 1)
        }
        
        # Save results
        results_file = f"m4_beast_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        # Print summary
        print("\n🏛️ M4 BEAST BENCHMARK COMPLETE!")
        print("=" * 50)
        print(f"✅ Success Rate: {benchmark_results['summary']['success_rate']}%")
        print(f"⏱️  Total Time: {benchmark_results['summary']['total_processing_time']}s")
        print(f"📄 Pages Processed: {benchmark_results['summary']['total_pages_processed']}")
        print(f"🚀 Processing Speed: {benchmark_results['summary']['pages_per_second']:.2f} pages/sec")
        print(f"📊 Results saved: {results_file}")
        
        return benchmark_results

if __name__ == "__main__":
    benchmark = M4BeastBenchmark()
    results = benchmark.run_full_benchmark()