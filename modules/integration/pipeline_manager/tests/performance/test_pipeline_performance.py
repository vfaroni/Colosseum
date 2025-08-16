#!/usr/bin/env python3
"""
Performance tests for pipeline manager
Roman Engineering Standard: Built for 2000+ year reliability

Performance benchmarks and load testing for the document processing
pipeline to ensure scalability and efficiency targets are met.
"""

import unittest
import sys
import time
import tempfile
import json
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.extraction_orchestrator import ExtractionOrchestrator
from core.document_processor import DocumentProcessor
from core.data_validator import DataValidator
from integrations.openai_client import OpenAIClient, OpenAIConfig


class TestPipelinePerformance(unittest.TestCase):
    """Performance tests for pipeline components"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create sample document content of various sizes
        self.small_content = "Basic offering memorandum content. " * 50  # ~2KB
        self.medium_content = "Detailed offering memorandum content. " * 500  # ~20KB
        self.large_content = "Comprehensive offering memorandum content. " * 2000  # ~80KB
        
        # Performance targets (based on README specifications)
        self.TARGET_PROCESSING_TIME = 60  # seconds per document
        self.TARGET_ACCURACY = 0.95  # 95% extraction accuracy
        self.TARGET_BATCH_CAPACITY = 100  # documents per hour
        self.TARGET_UPTIME = 0.999  # 99.9% availability
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_test_document(self, content: str, filename: str) -> str:
        """Create test document file"""
        file_path = self.test_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return str(file_path)
    
    @patch('integrations.openai_client.OpenAI')
    def test_single_document_processing_speed(self, mock_openai):
        """Test single document processing meets speed targets"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "property_details": {"name": "Test Property", "unit_count": 100},
            "financial_metrics": {"purchase_price": 10000000}
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1500
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Test different document sizes
        test_cases = [
            ("small", self.small_content),
            ("medium", self.medium_content),
            ("large", self.large_content)
        ]
        
        orchestrator = ExtractionOrchestrator()
        
        for size_name, content in test_cases:
            with self.subTest(document_size=size_name):
                # Create test document
                doc_path = self.create_test_document(content, f"test_{size_name}.txt")
                
                # Mock Excel manager to focus on processing speed
                with patch.object(orchestrator, 'excel_manager') as mock_excel:
                    mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
                    
                    # Measure processing time
                    start_time = time.time()
                    task = orchestrator.process_single_document(doc_path)
                    processing_time = time.time() - start_time
                    
                    # Verify speed target met
                    self.assertLess(processing_time, self.TARGET_PROCESSING_TIME,
                                  f"{size_name} document processing took {processing_time:.2f}s, target: {self.TARGET_PROCESSING_TIME}s")
                    
                    # Verify successful processing
                    self.assertTrue(task.extraction_result.success if task.extraction_result else False)
    
    @patch('integrations.openai_client.OpenAI')
    def test_batch_processing_throughput(self, mock_openai):
        """Test batch processing meets throughput targets"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "property_details": {"name": "Test Property", "unit_count": 100}
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1000
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Create batch of test documents
        batch_size = 10  # Scaled down for testing
        doc_paths = []
        
        for i in range(batch_size):
            doc_path = self.create_test_document(self.medium_content, f"batch_test_{i}.txt")
            doc_paths.append(doc_path)
        
        orchestrator = ExtractionOrchestrator()
        
        # Mock Excel manager
        with patch.object(orchestrator, 'excel_manager') as mock_excel:
            mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
            
            # Measure batch processing time
            start_time = time.time()
            batch_result = orchestrator.process_batch_documents(doc_paths)
            processing_time = time.time() - start_time
            
            # Calculate throughput (documents per hour)
            throughput = (batch_size / processing_time) * 3600
            
            # Verify throughput target
            self.assertGreaterEqual(throughput, self.TARGET_BATCH_CAPACITY,
                                  f"Batch throughput: {throughput:.1f} docs/hour, target: {self.TARGET_BATCH_CAPACITY}")
            
            # Verify success rate
            success_rate = batch_result.successful_tasks / batch_result.total_tasks
            self.assertGreaterEqual(success_rate, self.TARGET_ACCURACY)
    
    def test_data_validator_performance(self):
        """Test data validator performance with large datasets"""
        validator = DataValidator()
        
        # Create large test dataset
        large_dataset = {
            "property_details": {
                "name": "Performance Test Property",
                "address": "123 Performance Ave",
                "city": "Austin",
                "state": "TX",
                "unit_count": 500,
                "year_built": 2020
            },
            "financial_metrics": {
                "purchase_price": 75000000,
                "net_operating_income": 4500000,
                "cap_rate": 0.06,
                "occupancy_rate": 0.97
            },
            # Add many additional fields to test performance
            **{f"test_field_{i}": f"test_value_{i}" for i in range(100)}
        }
        
        # Measure validation time
        validation_times = []
        for _ in range(10):  # Run multiple times for average
            start_time = time.time()
            result = validator.validate_extraction(large_dataset)
            validation_time = time.time() - start_time
            validation_times.append(validation_time)
        
        # Verify validation performance
        avg_validation_time = statistics.mean(validation_times)
        self.assertLess(avg_validation_time, 1.0,  # Should validate in under 1 second
                       f"Average validation time: {avg_validation_time:.3f}s")
        
        # Verify validation accuracy
        self.assertTrue(result.is_valid)
        self.assertGreaterEqual(result.confidence_score, 0.8)
    
    @patch('integrations.openai_client.OpenAI')
    def test_concurrent_processing_performance(self, mock_openai):
        """Test performance under concurrent load"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "property_details": {"name": "Concurrent Test", "unit_count": 100}
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1000
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Create test documents
        num_documents = 20
        doc_paths = []
        for i in range(num_documents):
            doc_path = self.create_test_document(self.medium_content, f"concurrent_{i}.txt")
            doc_paths.append(doc_path)
        
        orchestrator = ExtractionOrchestrator()
        
        # Mock Excel manager
        with patch.object(orchestrator, 'excel_manager') as mock_excel:
            mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
            
            # Test concurrent processing
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(orchestrator.process_single_document, doc_path)
                    for doc_path in doc_paths
                ]
                
                results = []
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.fail(f"Concurrent processing failed: {e}")
            
            total_time = time.time() - start_time
            
            # Verify concurrent performance
            throughput = (num_documents / total_time) * 3600
            self.assertGreaterEqual(throughput, self.TARGET_BATCH_CAPACITY)
            
            # Verify all tasks completed successfully
            successful_tasks = sum(1 for r in results if r.extraction_result and r.extraction_result.success)
            success_rate = successful_tasks / num_documents
            self.assertGreaterEqual(success_rate, 0.95)
    
    def test_memory_usage_performance(self):
        """Test memory usage stays within reasonable bounds"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple documents to test memory accumulation
        orchestrator = ExtractionOrchestrator()
        validator = DataValidator()
        
        # Simulate processing without actual API calls
        for i in range(50):
            # Create test data
            test_data = {
                "property_details": {
                    "name": f"Memory Test Property {i}",
                    "unit_count": 100 + i,
                    "address": f"123 Memory St #{i}"
                },
                "financial_metrics": {
                    "purchase_price": 10000000 + (i * 100000)
                }
            }
            
            # Validate data (this exercises memory allocation)
            result = validator.validate_extraction(test_data)
            self.assertIsNotNone(result)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        self.assertLess(memory_increase, 100,
                       f"Memory increased by {memory_increase:.1f}MB during processing")
    
    def test_error_recovery_performance(self):
        """Test performance of error recovery mechanisms"""
        orchestrator = ExtractionOrchestrator()
        
        # Create mix of valid and invalid documents
        valid_doc = self.create_test_document(self.medium_content, "valid.txt")
        invalid_doc = self.create_test_document("Invalid content", "invalid.txt")
        nonexistent_doc = str(self.test_dir / "nonexistent.txt")
        
        doc_paths = [valid_doc, invalid_doc, nonexistent_doc] * 5  # 15 total
        
        # Measure error recovery performance
        start_time = time.time()
        
        with patch.object(orchestrator, 'document_processor') as mock_processor:
            # Simulate mixed success/failure responses
            def side_effect(file_path, doc_type=None):
                if "valid" in file_path:
                    return Mock(success=True, data={"test": "data"}, confidence_score=0.9)
                else:
                    raise Exception("Simulated processing error")
            
            mock_processor.process_document.side_effect = side_effect
            
            batch_result = orchestrator.process_batch_documents(doc_paths)
        
        processing_time = time.time() - start_time
        
        # Verify error recovery doesn't significantly impact performance
        self.assertLess(processing_time, 30,  # Should complete within 30 seconds
                       f"Error recovery took {processing_time:.2f}s")
        
        # Verify partial success
        self.assertGreater(batch_result.successful_tasks, 0)
        self.assertGreater(batch_result.failed_tasks, 0)
    
    def test_api_rate_limiting_performance(self):
        """Test performance with API rate limiting"""
        config = OpenAIConfig(
            rate_limit_rpm=60,  # 1 request per second
            rate_limit_tpm=1000
        )
        
        # Mock API key
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('integrations.openai_client.OpenAI') as mock_openai:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = '{"test": "data"}'
                mock_response.usage = Mock()
                mock_response.usage.total_tokens = 100
                mock_response.model = "gpt-4"
                
                mock_openai.return_value.chat.completions.create.return_value = mock_response
                
                client = OpenAIClient(config)
                
                # Test multiple requests to trigger rate limiting
                start_time = time.time()
                
                for i in range(5):
                    result = client.extract_with_prompt(f"Test content {i}", "Test prompt")
                    self.assertIsInstance(result, dict)
                
                total_time = time.time() - start_time
                
                # With rate limiting, should take at least 4 seconds (5 requests at 1/sec)
                self.assertGreaterEqual(total_time, 4.0,
                                      f"Rate limiting not working properly: {total_time:.2f}s")


class TestPipelineScalability(unittest.TestCase):
    """Test pipeline scalability under various loads"""
    
    def setUp(self):
        """Set up scalability test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('integrations.openai_client.OpenAI')
    def test_scaling_with_document_count(self, mock_openai):
        """Test how performance scales with increasing document count"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"test": "data"}'
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 500
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        orchestrator = ExtractionOrchestrator()
        
        # Test with increasing batch sizes
        batch_sizes = [1, 5, 10, 20]
        performance_data = {}
        
        for batch_size in batch_sizes:
            # Create test documents
            doc_paths = []
            for i in range(batch_size):
                doc_path = self.test_dir / f"scale_test_{batch_size}_{i}.txt"
                with open(doc_path, 'w') as f:
                    f.write(f"Test content for document {i}")
                doc_paths.append(str(doc_path))
            
            # Mock Excel manager
            with patch.object(orchestrator, 'excel_manager') as mock_excel:
                mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
                
                # Measure processing time
                start_time = time.time()
                batch_result = orchestrator.process_batch_documents(doc_paths)
                processing_time = time.time() - start_time
                
                # Calculate metrics
                throughput = batch_size / processing_time
                avg_time_per_doc = processing_time / batch_size
                
                performance_data[batch_size] = {
                    'total_time': processing_time,
                    'throughput': throughput,
                    'avg_time_per_doc': avg_time_per_doc,
                    'success_rate': batch_result.successful_tasks / batch_result.total_tasks
                }
        
        # Verify scalability characteristics
        for batch_size, metrics in performance_data.items():
            with self.subTest(batch_size=batch_size):
                # Average time per document should remain relatively constant
                self.assertLess(metrics['avg_time_per_doc'], 10,
                              f"Avg time per doc: {metrics['avg_time_per_doc']:.2f}s for batch size {batch_size}")
                
                # Success rate should remain high
                self.assertGreaterEqual(metrics['success_rate'], 0.95,
                                      f"Success rate: {metrics['success_rate']:.2f} for batch size {batch_size}")
    
    def test_memory_scaling(self):
        """Test memory usage scaling with data volume"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        validator = DataValidator()
        
        # Test with increasing data sizes
        data_sizes = [10, 50, 100, 200]  # Number of properties to validate
        memory_usage = {}
        
        for data_size in data_sizes:
            # Create large dataset
            test_data = {}
            for i in range(data_size):
                test_data[f"property_{i}"] = {
                    "property_details": {
                        "name": f"Property {i}",
                        "unit_count": 100 + i,
                        "address": f"123 Test St #{i}"
                    },
                    "financial_metrics": {
                        "purchase_price": 10000000 + (i * 100000)
                    }
                }
            
            # Measure memory before processing
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process data
            for property_data in test_data.values():
                result = validator.validate_extraction(property_data)
                self.assertIsNotNone(result)
            
            # Measure memory after processing
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            memory_usage[data_size] = memory_increase
        
        # Verify memory scaling is reasonable
        for data_size, memory_increase in memory_usage.items():
            with self.subTest(data_size=data_size):
                # Memory per property should be reasonable
                memory_per_property = memory_increase / data_size if data_size > 0 else 0
                self.assertLess(memory_per_property, 1,  # Less than 1MB per property
                              f"Memory per property: {memory_per_property:.2f}MB for {data_size} properties")


if __name__ == '__main__':
    # Run performance tests
    unittest.main(verbosity=2)