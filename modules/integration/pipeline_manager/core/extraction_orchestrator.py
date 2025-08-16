#!/usr/bin/env python3
"""
Pipeline Manager - Extraction Orchestrator
Roman Engineering Standard: Built for 2000+ year reliability

Central orchestration engine for document processing workflow with error handling,
retry logic, and performance monitoring for systematic pipeline excellence.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

# Internal imports
from .document_processor import DocumentProcessor, ExtractionResult, DocumentType
from .excel_manager import ExcelManager, ExcelConfig
from .data_validator import DataValidator, ValidationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATING = "validating"
    INTEGRATING = "integrating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class ProcessingTask:
    """Individual document processing task"""
    task_id: str
    file_path: str
    document_type: Optional[DocumentType]
    status: ProcessingStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    processing_time: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    extraction_result: Optional[ExtractionResult] = None
    validation_result: Optional[ValidationResult] = None
    excel_row: Optional[int] = None

@dataclass
class BatchProcessingResult:
    """Results from batch processing operation"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    processing_time: float
    tasks: List[ProcessingTask]
    performance_metrics: Dict[str, Any]
    summary_report: str

class ExtractionOrchestrator:
    """Central orchestration engine for document processing workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize extraction orchestrator with configuration"""
        self.config = self._load_configuration(config_path)
        
        # Initialize components
        self.document_processor = DocumentProcessor(config_path)
        self.data_validator = DataValidator(self.config.get('validation'))
        self.excel_manager = self._initialize_excel_manager()
        
        # Processing state
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: List[ProcessingTask] = []
        self.performance_metrics = {
            "total_documents_processed": 0,
            "average_processing_time": 0.0,
            "success_rate": 0.0,
            "total_processing_time": 0.0
        }
        
        logger.info("ExtractionOrchestrator initialized with full workflow orchestration")
    
    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            "max_concurrent_tasks": 4,
            "max_retry_attempts": 3,
            "retry_delay_seconds": 5,
            "timeout_seconds": 300,
            "batch_size": 10,
            "excel": {
                "file_path": "pipeline.xlsx",
                "sheet_name": "Deal Pipeline",
                "backup_enabled": True,
                "preserve_formatting": True
            },
            "validation": {
                "strict_mode": False,
                "auto_correct": True,
                "confidence_threshold": 0.85
            },
            "performance": {
                "enable_metrics": True,
                "log_processing_details": True,
                "save_performance_data": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                self._deep_update(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary with nested values"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _initialize_excel_manager(self) -> ExcelManager:
        """Initialize Excel manager with configuration"""
        excel_config = ExcelConfig(**self.config['excel'])
        return ExcelManager(excel_config)
    
    def process_single_document(self, file_path: str, 
                               document_type: Optional[DocumentType] = None) -> ProcessingTask:
        """Process a single document through the complete workflow"""
        task_id = self._generate_task_id(file_path)
        
        task = ProcessingTask(
            task_id=task_id,
            file_path=file_path,
            document_type=document_type,
            status=ProcessingStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.active_tasks[task_id] = task
        
        try:
            return self._execute_processing_task(task)
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now().isoformat()
            self._move_to_completed(task)
            return task
    
    def process_batch_documents(self, file_paths: List[str], 
                               document_types: Optional[List[DocumentType]] = None) -> BatchProcessingResult:
        """Process multiple documents in batch with concurrent execution"""
        start_time = time.time()
        
        # Create processing tasks
        tasks = []
        for i, file_path in enumerate(file_paths):
            doc_type = document_types[i] if document_types and i < len(document_types) else None
            task_id = self._generate_task_id(file_path)
            
            task = ProcessingTask(
                task_id=task_id,
                file_path=file_path,
                document_type=doc_type,
                status=ProcessingStatus.PENDING,
                created_at=datetime.now().isoformat()
            )
            tasks.append(task)
            self.active_tasks[task_id] = task
        
        # Execute tasks concurrently
        completed_tasks = []
        with ThreadPoolExecutor(max_workers=self.config['max_concurrent_tasks']) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_processing_task, task): task 
                for task in tasks
            }
            
            # Collect results
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    completed_task = future.result()
                    completed_tasks.append(completed_task)
                except Exception as e:
                    logger.error(f"Task {task.task_id} failed in executor: {str(e)}")
                    task.status = ProcessingStatus.FAILED
                    task.error_message = str(e)
                    task.completed_at = datetime.now().isoformat()
                    completed_tasks.append(task)
        
        # Calculate results
        processing_time = time.time() - start_time
        successful_tasks = len([t for t in completed_tasks if t.status == ProcessingStatus.COMPLETED])
        failed_tasks = len(completed_tasks) - successful_tasks
        
        # Update performance metrics
        self._update_performance_metrics(completed_tasks, processing_time)
        
        # Generate summary report
        summary_report = self._generate_batch_summary(completed_tasks, processing_time)
        
        return BatchProcessingResult(
            total_tasks=len(completed_tasks),
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            processing_time=processing_time,
            tasks=completed_tasks,
            performance_metrics=self.performance_metrics.copy(),
            summary_report=summary_report
        )
    
    def _execute_processing_task(self, task: ProcessingTask) -> ProcessingTask:
        """Execute complete processing workflow for a single task"""
        task.started_at = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            # Step 1: Document Processing
            task.status = ProcessingStatus.PROCESSING
            logger.info(f"Processing document: {task.file_path}")
            
            extraction_result = self.document_processor.process_document(
                task.file_path, task.document_type
            )
            task.extraction_result = extraction_result
            
            if not extraction_result.success:
                raise Exception(f"Document processing failed: {', '.join(extraction_result.errors)}")
            
            # Step 2: Data Validation
            task.status = ProcessingStatus.VALIDATING
            logger.info(f"Validating extracted data for: {task.file_path}")
            
            validation_result = self.data_validator.validate_extraction(extraction_result.data)
            task.validation_result = validation_result
            
            # Check if validation passed
            if not validation_result.is_valid and self.config['validation']['strict_mode']:
                critical_issues = validation_result.critical_issues
                if critical_issues:
                    raise Exception(f"Critical validation issues: {[issue.message for issue in critical_issues]}")
            
            # Step 3: Excel Integration
            task.status = ProcessingStatus.INTEGRATING
            logger.info(f"Integrating to Excel pipeline: {task.file_path}")
            
            # Use corrected data if validation made corrections
            final_data = validation_result.corrected_data if validation_result.corrected_data else extraction_result.data
            
            # Create updated extraction result with corrected data
            corrected_extraction = ExtractionResult(
                success=True,
                data=final_data,
                confidence_score=min(extraction_result.confidence_score, validation_result.confidence_score),
                processing_time=extraction_result.processing_time,
                errors=extraction_result.errors + [issue.message for issue in validation_result.critical_issues],
                warnings=extraction_result.warnings + [issue.message for issue in validation_result.warning_issues],
                document_type=extraction_result.document_type,
                extraction_timestamp=extraction_result.extraction_timestamp
            )
            
            success, excel_row = self.excel_manager.add_extraction_to_pipeline(
                corrected_extraction, task.file_path
            )
            
            if not success:
                raise Exception("Failed to integrate data to Excel pipeline")
            
            task.excel_row = excel_row
            
            # Step 4: Complete Task
            task.status = ProcessingStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.processing_time = time.time() - start_time
            
            logger.info(f"Task completed successfully: {task.task_id} (Row {excel_row})")
            
        except Exception as e:
            # Handle task failure with retry logic
            task.retry_count += 1
            
            if task.retry_count <= self.config['max_retry_attempts']:
                task.status = ProcessingStatus.RETRYING
                task.error_message = str(e)
                
                logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{self.config['max_retry_attempts']})")
                
                # Wait before retry
                time.sleep(self.config['retry_delay_seconds'] * task.retry_count)
                
                # Retry the task
                return self._execute_processing_task(task)
            else:
                task.status = ProcessingStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now().isoformat()
                task.processing_time = time.time() - start_time
                
                logger.error(f"Task {task.task_id} failed after {task.retry_count} attempts: {str(e)}")
        
        finally:
            # Move task to completed
            self._move_to_completed(task)
        
        return task
    
    def _move_to_completed(self, task: ProcessingTask):
        """Move task from active to completed"""
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.completed_tasks.append(task)
    
    def _generate_task_id(self, file_path: str) -> str:
        """Generate unique task ID from file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(file_path).stem
        return f"{file_name}_{timestamp}_{hash(file_path) % 10000:04d}"
    
    def _update_performance_metrics(self, tasks: List[ProcessingTask], total_time: float):
        """Update performance metrics based on completed tasks"""
        successful_tasks = [t for t in tasks if t.status == ProcessingStatus.COMPLETED]
        
        self.performance_metrics['total_documents_processed'] += len(tasks)
        self.performance_metrics['total_processing_time'] += total_time
        
        if successful_tasks:
            avg_time = sum(t.processing_time for t in successful_tasks if t.processing_time) / len(successful_tasks)
            self.performance_metrics['average_processing_time'] = avg_time
        
        total_processed = self.performance_metrics['total_documents_processed']
        if total_processed > 0:
            success_count = len([t for t in self.completed_tasks if t.status == ProcessingStatus.COMPLETED])
            self.performance_metrics['success_rate'] = success_count / total_processed
    
    def _generate_batch_summary(self, tasks: List[ProcessingTask], processing_time: float) -> str:
        """Generate batch processing summary report"""
        successful = [t for t in tasks if t.status == ProcessingStatus.COMPLETED]
        failed = [t for t in tasks if t.status == ProcessingStatus.FAILED]
        
        report = []
        report.append("=" * 60)
        report.append("BATCH PROCESSING SUMMARY")
        report.append("=" * 60)
        report.append(f"Total Documents: {len(tasks)}")
        report.append(f"Successful: {len(successful)}")
        report.append(f"Failed: {len(failed)}")
        report.append(f"Success Rate: {len(successful)/len(tasks)*100:.1f}%")
        report.append(f"Total Processing Time: {processing_time:.2f} seconds")
        
        if successful:
            avg_time = sum(t.processing_time for t in successful if t.processing_time) / len(successful)
            report.append(f"Average Processing Time: {avg_time:.2f} seconds")
            report.append(f"Processing Rate: {len(successful)/processing_time:.1f} documents/second")
        
        if failed:
            report.append("")
            report.append("FAILED DOCUMENTS:")
            report.append("-" * 30)
            for task in failed:
                report.append(f"  {Path(task.file_path).name}: {task.error_message}")
        
        # Performance insights
        if successful:
            report.append("")
            report.append("PERFORMANCE INSIGHTS:")
            report.append("-" * 30)
            processing_times = [t.processing_time for t in successful if t.processing_time]
            if processing_times:
                report.append(f"  Fastest Processing: {min(processing_times):.2f}s")
                report.append(f"  Slowest Processing: {max(processing_times):.2f}s")
                
                # Document type breakdown
                type_counts = {}
                for task in successful:
                    if task.extraction_result:
                        doc_type = task.extraction_result.document_type.value
                        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                
                if type_counts:
                    report.append("  Document Type Distribution:")
                    for doc_type, count in type_counts.items():
                        report.append(f"    {doc_type}: {count}")
        
        return "\n".join(report)
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics.copy(),
            "active_task_details": [
                {
                    "task_id": task.task_id,
                    "file_name": Path(task.file_path).name,
                    "status": task.status.value,
                    "started_at": task.started_at
                }
                for task in self.active_tasks.values()
            ]
        }
    
    def export_processing_history(self, output_path: str) -> bool:
        """Export processing history to JSON file"""
        try:
            history_data = {
                "export_timestamp": datetime.now().isoformat(),
                "performance_metrics": self.performance_metrics,
                "completed_tasks": [asdict(task) for task in self.completed_tasks],
                "active_tasks": [asdict(task) for task in self.active_tasks.values()]
            }
            
            with open(output_path, 'w') as f:
                json.dump(history_data, f, indent=2, default=str)
            
            logger.info(f"Processing history exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export processing history: {str(e)}")
            return False
    
    def cleanup_completed_tasks(self, max_history: int = 1000):
        """Clean up old completed tasks to manage memory"""
        if len(self.completed_tasks) > max_history:
            # Keep most recent tasks
            self.completed_tasks = self.completed_tasks[-max_history:]
            logger.info(f"Cleaned up completed tasks, keeping {max_history} most recent")

# Example usage and testing
if __name__ == "__main__":
    # Initialize orchestrator
    orchestrator = ExtractionOrchestrator()
    
    # Example single document processing
    # task = orchestrator.process_single_document("path/to/offering_memorandum.pdf")
    # print(f"Task Status: {task.status.value}")
    
    # Example batch processing
    # file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    # batch_result = orchestrator.process_batch_documents(file_paths)
    # print(batch_result.summary_report)
    
    logger.info("ExtractionOrchestrator ready for document processing")