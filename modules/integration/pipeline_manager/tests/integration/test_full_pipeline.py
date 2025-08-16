#!/usr/bin/env python3
"""
Integration tests for full pipeline workflow
Roman Engineering Standard: Built for 2000+ year reliability

End-to-end integration tests covering the complete document processing
pipeline from document input to Excel output.
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.extraction_orchestrator import ExtractionOrchestrator, ProcessingTask, ProcessingStatus
from core.document_processor import DocumentProcessor, ExtractionResult, DocumentType
from core.data_validator import DataValidator, ValidationResult
from core.excel_manager import ExcelManager, ExcelConfig
from integrations.openai_client import OpenAIClient, OpenAIConfig
from integrations.pipeline_connector import PipelineConnector


class TestFullPipelineIntegration(unittest.TestCase):
    """Integration tests for complete pipeline workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_excel_file = self.test_dir / "test_pipeline.xlsx"
        
        # Create test document content
        self.test_om_content = """
        OFFERING MEMORANDUM
        
        Property Name: Test Apartments
        Address: 123 Main Street, Austin, TX 78701
        Total Units: 100
        Year Built: 1995
        
        Purchase Price: $12,500,000
        Net Operating Income: $825,000
        Cap Rate: 6.6%
        Occupancy Rate: 95%
        
        Average Rent: $1,150
        
        Listing Broker: John Smith
        Broker Company: ABC Realty
        """
        
        self.test_document_path = self.test_dir / "test_om.txt"
        with open(self.test_document_path, 'w') as f:
            f.write(self.test_om_content)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('integrations.openai_client.OpenAI')
    def test_full_pipeline_workflow(self, mock_openai):
        """Test complete pipeline workflow from document to Excel"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "property_details": {
                "name": "Test Apartments",
                "address": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78701",
                "unit_count": 100,
                "year_built": 1995
            },
            "financial_metrics": {
                "purchase_price": 12500000,
                "net_operating_income": 825000,
                "cap_rate": 0.066,
                "occupancy_rate": 0.95
            },
            "rent_information": {
                "average_rent": 1150
            },
            "transaction_details": {
                "listing_broker": "John Smith",
                "broker_company": "ABC Realty"
            }
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1500
        mock_response.usage.prompt_tokens = 1000
        mock_response.usage.completion_tokens = 500
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Initialize orchestrator with test configuration
        orchestrator = ExtractionOrchestrator()
        
        # Mock the Excel manager to avoid file operations
        with patch.object(orchestrator, 'excel_manager') as mock_excel:
            mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
            
            # Process single document
            task = orchestrator.process_single_document(str(self.test_document_path))
            
            # Verify task completion
            self.assertEqual(task.status, ProcessingStatus.COMPLETED)
            self.assertIsNotNone(task.extraction_result)
            self.assertTrue(task.extraction_result.success)
            self.assertIsNotNone(task.validation_result)
            self.assertEqual(task.excel_row, 2)
            
            # Verify extracted data
            extracted_data = task.extraction_result.data
            self.assertEqual(extracted_data["property_details"]["name"], "Test Apartments")
            self.assertEqual(extracted_data["property_details"]["unit_count"], 100)
            self.assertEqual(extracted_data["financial_metrics"]["purchase_price"], 12500000)
    
    @patch('integrations.openai_client.OpenAI')
    def test_batch_processing_workflow(self, mock_openai):
        """Test batch processing of multiple documents"""
        # Create additional test documents
        test_files = []
        for i in range(3):
            test_file = self.test_dir / f"test_om_{i}.txt"
            with open(test_file, 'w') as f:
                f.write(self.test_om_content.replace("Test Apartments", f"Test Apartments {i}"))
            test_files.append(str(test_file))
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "property_details": {"name": "Test Apartments", "unit_count": 100},
            "financial_metrics": {"purchase_price": 12500000}
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1000
        mock_response.model = "gpt-4"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Initialize orchestrator
        orchestrator = ExtractionOrchestrator()
        
        # Mock Excel manager
        with patch.object(orchestrator, 'excel_manager') as mock_excel:
            mock_excel.add_extraction_to_pipeline.return_value = (True, 2)
            
            # Process batch
            batch_result = orchestrator.process_batch_documents(test_files)
            
            # Verify batch results
            self.assertEqual(batch_result.total_tasks, 3)
            self.assertEqual(batch_result.successful_tasks, 3)
            self.assertEqual(batch_result.failed_tasks, 0)
            self.assertGreater(len(batch_result.summary_report), 0)
    
    def test_validation_integration(self):
        """Test integration between extraction and validation"""
        # Create test extraction result
        extraction_result = ExtractionResult(
            success=True,
            data={
                "property_details": {
                    "name": "Test Property",
                    "address": "123 Test St",
                    "city": "Austin",
                    "state": "TX",
                    "unit_count": 50
                },
                "financial_metrics": {
                    "purchase_price": 8000000,
                    "cap_rate": 0.065
                }
            },
            confidence_score=0.92,
            processing_time=45.0,
            errors=[],
            warnings=[],
            document_type=DocumentType.OFFERING_MEMORANDUM,
            extraction_timestamp="2025-01-31T12:00:00"
        )
        
        # Validate extracted data
        validator = DataValidator()
        validation_result = validator.validate_extraction(extraction_result.data)
        
        # Verify validation results
        self.assertIsInstance(validation_result, ValidationResult)
        self.assertTrue(validation_result.is_valid)
        self.assertGreaterEqual(validation_result.confidence_score, 0.8)
    
    def test_excel_integration(self):
        """Test integration with Excel output"""
        # Create Excel configuration
        excel_config = ExcelConfig(
            file_path=str(self.test_excel_file),
            sheet_name="Test Pipeline",
            backup_enabled=False
        )
        
        # Initialize Excel manager
        excel_manager = ExcelManager(excel_config)
        
        # Create test extraction result
        extraction_result = ExtractionResult(
            success=True,
            data={
                "property_details": {
                    "name": "Excel Test Property",
                    "address": "456 Excel Ave",
                    "city": "Dallas",
                    "state": "TX",
                    "unit_count": 75
                },
                "financial_metrics": {
                    "purchase_price": 10000000,
                    "net_operating_income": 650000,
                    "cap_rate": 0.065
                }
            },
            confidence_score=0.90,
            processing_time=30.0,
            errors=[],
            warnings=[],
            document_type=DocumentType.OFFERING_MEMORANDUM,
            extraction_timestamp="2025-01-31T12:00:00"
        )
        
        # Add extraction to pipeline
        success, row_number = excel_manager.add_extraction_to_pipeline(
            extraction_result, str(self.test_document_path)
        )
        
        # Verify Excel integration
        self.assertTrue(success)
        self.assertGreater(row_number, 1)
        self.assertTrue(self.test_excel_file.exists())
    
    def test_error_handling_integration(self):
        """Test error handling across pipeline components"""
        # Test with invalid document path
        orchestrator = ExtractionOrchestrator()
        
        task = orchestrator.process_single_document("nonexistent_file.pdf")
        
        # Verify error handling
        self.assertEqual(task.status, ProcessingStatus.FAILED)
        self.assertIsNotNone(task.error_message)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_openai_client_integration(self):
        """Test OpenAI client integration with mocked API"""
        with patch('integrations.openai_client.OpenAI') as mock_openai_class:
            # Mock the client instance
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            # Mock the API response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"test": "data"}'
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 100
            mock_response.model = "gpt-4"
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Test OpenAI client
            config = OpenAIConfig(api_key='test-key')
            client = OpenAIClient(config)
            
            result = client.extract_with_prompt("Test content", "Test prompt")
            
            # Verify integration
            self.assertIsInstance(result, dict)
            self.assertEqual(result["test"], "data")
    
    def test_pipeline_connector_integration(self):
        """Test pipeline connector integration"""
        # Initialize connector
        connector = PipelineConnector()
        
        # Test integration status
        status = connector.get_integration_status()
        
        # Verify status structure
        self.assertIn("timestamp", status)
        self.assertIn("systems", status)
        self.assertIn("config", status)
    
    def test_performance_metrics_collection(self):
        """Test performance metrics collection across pipeline"""
        orchestrator = ExtractionOrchestrator()
        
        # Get initial metrics
        initial_stats = orchestrator.get_processing_status()
        
        # Verify metrics structure
        self.assertIn("active_tasks", initial_stats)
        self.assertIn("completed_tasks", initial_stats)
        self.assertIn("performance_metrics", initial_stats)
    
    def test_configuration_integration(self):
        """Test configuration system integration"""
        # Test with custom configuration
        config_data = {
            "max_concurrent_tasks": 2,
            "timeout_seconds": 120,
            "excel": {
                "backup_enabled": False
            }
        }
        
        config_file = self.test_dir / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Initialize with custom config
        orchestrator = ExtractionOrchestrator(str(config_file))
        
        # Verify configuration applied
        self.assertEqual(orchestrator.config["max_concurrent_tasks"], 2)
        self.assertEqual(orchestrator.config["timeout_seconds"], 120)


class TestPipelineRobustness(unittest.TestCase):
    """Test pipeline robustness and error recovery"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_malformed_document_handling(self):
        """Test handling of malformed or corrupted documents"""
        # Create malformed document
        malformed_file = self.test_dir / "malformed.txt"
        with open(malformed_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')  # Binary garbage
        
        orchestrator = ExtractionOrchestrator()
        task = orchestrator.process_single_document(str(malformed_file))
        
        # Should handle gracefully without crashing
        self.assertIn(task.status, [ProcessingStatus.FAILED, ProcessingStatus.COMPLETED])
    
    @patch('integrations.openai_client.OpenAI')
    def test_api_failure_recovery(self, mock_openai):
        """Test recovery from API failures"""
        # Mock API failure
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        orchestrator = ExtractionOrchestrator()
        
        test_file = self.test_dir / "test.txt"
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        task = orchestrator.process_single_document(str(test_file))
        
        # Should fail gracefully
        self.assertEqual(task.status, ProcessingStatus.FAILED)
        self.assertIsNotNone(task.error_message)
    
    def test_concurrent_processing_stability(self):
        """Test stability under concurrent processing load"""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = self.test_dir / f"concurrent_test_{i}.txt"
            with open(test_file, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(str(test_file))
        
        orchestrator = ExtractionOrchestrator()
        
        # Mock processing to avoid API calls
        with patch.object(orchestrator, 'document_processor'):
            with patch.object(orchestrator, 'excel_manager'):
                batch_result = orchestrator.process_batch_documents(test_files)
                
                # Verify no crashes or deadlocks
                self.assertEqual(batch_result.total_tasks, 5)


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)