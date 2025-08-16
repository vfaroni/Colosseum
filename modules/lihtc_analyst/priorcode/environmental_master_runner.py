#!/usr/bin/env python3
"""
Environmental Database Master Runner
Production system with comprehensive status updates, intelligent retry logic, and bandwidth management

Status: Production Ready with Advanced Monitoring
Author: Structured Consultants LLC
Date: July 23, 2025
"""

import os
import sys
import json
import time
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
from dataclasses import dataclass, asdict
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our collectors
from environmental_database_orchestrator import EnvironmentalDatabaseOrchestrator
from epa_envirofacts_collector import EPAEnvirofactsCollector
from echo_exporter_downloader import ECHOExporterDownloader
from california_environmental_collector import CaliforniaEnvironmentalCollector
from texas_environmental_collector import TexasEnvironmentalCollector

@dataclass
class CollectionStatus:
    """Real-time collection status tracking"""
    task_name: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'retrying'
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    progress_percent: float
    current_step: str
    records_collected: int
    data_size_mb: float
    error_message: Optional[str]
    retry_count: int
    estimated_completion: Optional[datetime]

class EnvironmentalMasterRunner:
    """Master runner with comprehensive status monitoring and intelligent retry logic"""
    
    # Connection retry configuration
    RETRY_CONFIG = {
        'max_retries': 5,
        'base_delay': 2.0,  # seconds
        'max_delay': 300.0,  # 5 minutes max delay
        'backoff_multiplier': 2.0,
        'jitter_range': 0.1,  # ±10% random jitter
        'timeout_escalation': [30, 60, 120, 300, 600],  # Progressive timeout increases
        'status_update_interval': 30,  # seconds
        'connection_test_urls': [
            'https://data.epa.gov/efservice/',
            'https://data.ca.gov/api/3/action/datastore_search',
            'https://httpbin.org/status/200'  # Fallback connectivity test
        ]
    }
    
    def __init__(self, base_data_path: str, bandwidth_profile: str = 'normal'):
        self.base_data_path = Path(base_data_path)
        self.bandwidth_profile = bandwidth_profile
        self.setup_logging()
        
        # Status tracking
        self.collection_status: Dict[str, CollectionStatus] = {}
        self.overall_start_time = None
        self.status_lock = threading.Lock()
        self.should_stop = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize collectors
        self.orchestrator = EnvironmentalDatabaseOrchestrator(str(base_data_path))
        self.epa_collector = EPAEnvirofactsCollector(str(base_data_path))
        self.echo_downloader = ECHOExporterDownloader(str(base_data_path), bandwidth_profile)
        self.ca_collector = CaliforniaEnvironmentalCollector(str(base_data_path))
        self.tx_collector = TexasEnvironmentalCollector(str(base_data_path))
        
        # Status monitoring thread
        self.status_thread = None
        self.start_status_monitoring()
        
    def setup_logging(self):
        """Setup comprehensive logging with multiple handlers"""
        log_dir = self.base_data_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Setup root logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"environmental_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for status updates
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Status file handler for real-time monitoring
        status_handler = logging.FileHandler(log_dir / "status_updates.log")
        status_handler.setLevel(logging.INFO)
        status_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(status_handler)
        
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.should_stop = True
        
    def start_status_monitoring(self):
        """Start background status monitoring thread"""
        def status_monitor():
            while not self.should_stop:
                self._print_status_update()
                time.sleep(self.RETRY_CONFIG['status_update_interval'])
        
        self.status_thread = threading.Thread(target=status_monitor, daemon=True)
        self.status_thread.start()
        
    def _print_status_update(self):
        """Print comprehensive status update"""
        if not self.collection_status:
            return
            
        with self.status_lock:
            print("\n" + "="*80)
            print(f"🔄 ENVIRONMENTAL DATA COLLECTION STATUS - {datetime.now().strftime('%H:%M:%S')}")
            print("="*80)
            
            # Overall progress
            total_tasks = len(self.collection_status)
            completed_tasks = sum(1 for status in self.collection_status.values() 
                                if status.status == 'completed')
            failed_tasks = sum(1 for status in self.collection_status.values() 
                             if status.status == 'failed')
            running_tasks = sum(1 for status in self.collection_status.values() 
                              if status.status == 'running')
            
            print(f"📊 Overall Progress: {completed_tasks}/{total_tasks} completed, "
                  f"{running_tasks} running, {failed_tasks} failed")
            
            if self.overall_start_time:
                elapsed = datetime.now() - self.overall_start_time
                print(f"⏱️  Total Runtime: {self._format_duration(elapsed)}")
            
            # Individual task status
            for task_name, status in self.collection_status.items():
                status_icon = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌',
                    'retrying': '🔁'
                }.get(status.status, '❓')
                
                duration_str = ""
                if status.start_time:
                    if status.end_time:
                        duration = status.end_time - status.start_time
                        duration_str = f"({self._format_duration(duration)})"
                    else:
                        duration = datetime.now() - status.start_time
                        duration_str = f"({self._format_duration(duration)} elapsed)"
                
                print(f"{status_icon} {task_name:25} | {status.status:10} | {status.current_step:30} {duration_str}")
                
                if status.progress_percent > 0:
                    print(f"   Progress: {status.progress_percent:5.1f}% | "
                          f"Records: {status.records_collected:,} | "
                          f"Size: {status.data_size_mb:.1f} MB")
                
                if status.retry_count > 0:
                    print(f"   🔁 Retries: {status.retry_count}")
                
                if status.error_message:
                    print(f"   ⚠️  Error: {status.error_message[:50]}...")
            
            print("="*80)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable format"""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def update_task_status(self, task_name: str, **kwargs):
        """Update task status with thread safety"""
        with self.status_lock:
            if task_name not in self.collection_status:
                self.collection_status[task_name] = CollectionStatus(
                    task_name=task_name,
                    status='pending',
                    start_time=None,
                    end_time=None,
                    progress_percent=0.0,
                    current_step='Initializing',
                    records_collected=0,
                    data_size_mb=0.0,
                    error_message=None,
                    retry_count=0,
                    estimated_completion=None
                )
            
            # Update provided fields
            for key, value in kwargs.items():
                if hasattr(self.collection_status[task_name], key):
                    setattr(self.collection_status[task_name], key, value)
    
    def test_connectivity(self) -> Tuple[bool, List[str]]:
        """Test connectivity to key endpoints with detailed reporting"""
        self.logger.info("🔍 Testing connectivity to environmental data sources...")
        
        connectivity_results = []
        overall_success = True
        
        for i, url in enumerate(self.RETRY_CONFIG['connection_test_urls']):
            try:
                self.logger.info(f"   Testing {url}...")
                
                response = requests.get(
                    url,
                    timeout=10,
                    headers={'User-Agent': 'LIHTC-Environmental-Analysis/1.0 (Connectivity Test)'}
                )
                
                if response.status_code == 200:
                    connectivity_results.append(f"✅ {url} - OK ({response.elapsed.total_seconds():.2f}s)")
                    self.logger.info(f"   ✅ Success: {response.status_code} in {response.elapsed.total_seconds():.2f}s")
                else:
                    connectivity_results.append(f"⚠️  {url} - HTTP {response.status_code}")
                    self.logger.warning(f"   ⚠️  HTTP {response.status_code}: {url}")
                    
            except requests.exceptions.Timeout:
                connectivity_results.append(f"⏱️  {url} - Timeout")
                self.logger.warning(f"   ⏱️  Timeout: {url}")
                overall_success = False
                
            except requests.exceptions.ConnectionError as e:
                connectivity_results.append(f"❌ {url} - Connection Error")
                self.logger.error(f"   ❌ Connection Error: {url} - {str(e)}")
                overall_success = False
                
            except Exception as e:
                connectivity_results.append(f"❌ {url} - Error: {str(e)[:30]}...")
                self.logger.error(f"   ❌ Error: {url} - {str(e)}")
                overall_success = False
        
        if overall_success:
            self.logger.info("🌐 Connectivity test passed - all endpoints accessible")
        else:
            self.logger.warning("⚠️  Connectivity issues detected - some endpoints unreachable")
        
        return overall_success, connectivity_results
    
    def execute_with_retry(self, task_name: str, func, *args, **kwargs) -> Dict:
        """Execute function with intelligent retry logic and status updates"""
        
        self.update_task_status(
            task_name,
            status='running',
            start_time=datetime.now(),
            current_step='Starting execution'
        )
        
        last_exception = None
        
        for retry_attempt in range(self.RETRY_CONFIG['max_retries'] + 1):
            if self.should_stop:
                self.logger.info(f"⏹️  Stopping {task_name} due to shutdown signal")
                break
                
            try:
                if retry_attempt > 0:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        self.RETRY_CONFIG['base_delay'] * (self.RETRY_CONFIG['backoff_multiplier'] ** retry_attempt),
                        self.RETRY_CONFIG['max_delay']
                    )
                    
                    # Add random jitter
                    import random
                    jitter = delay * self.RETRY_CONFIG['jitter_range'] * (2 * random.random() - 1)
                    actual_delay = delay + jitter
                    
                    self.update_task_status(
                        task_name,
                        status='retrying',
                        retry_count=retry_attempt,
                        current_step=f'Waiting {actual_delay:.1f}s before retry {retry_attempt}'
                    )
                    
                    self.logger.info(f"🔁 {task_name}: Retry {retry_attempt} in {actual_delay:.1f} seconds...")
                    time.sleep(actual_delay)
                    
                    # Test connectivity before retry
                    connectivity_ok, _ = self.test_connectivity()
                    if not connectivity_ok:
                        self.logger.warning(f"⚠️  {task_name}: Connectivity issues detected, extending delay...")
                        time.sleep(30)  # Additional delay for connectivity issues
                
                self.update_task_status(
                    task_name,
                    status='running',
                    current_step=f'Executing (attempt {retry_attempt + 1})',
                    retry_count=retry_attempt
                )
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Check if result indicates success
                if isinstance(result, dict) and result.get('success', True):
                    self.update_task_status(
                        task_name,
                        status='completed',
                        end_time=datetime.now(),
                        current_step='Completed successfully',
                        records_collected=result.get('records_count', result.get('records_collected', 0)),
                        data_size_mb=result.get('file_size_mb', result.get('data_size_mb', 0)),
                        progress_percent=100.0
                    )
                    
                    self.logger.info(f"✅ {task_name}: Completed successfully!")
                    return result
                else:
                    # Function completed but indicated failure
                    error_msg = result.get('error', result.get('message', 'Unknown error'))
                    raise Exception(f"Function completed with error: {error_msg}")
                    
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                self.logger.warning(f"🌐 {task_name}: Connection error on attempt {retry_attempt + 1}: {str(e)}")
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                self.logger.warning(f"⏱️  {task_name}: Timeout on attempt {retry_attempt + 1}: {str(e)}")
                
            except requests.exceptions.HTTPError as e:
                last_exception = e
                self.logger.warning(f"🌐 {task_name}: HTTP error on attempt {retry_attempt + 1}: {str(e)}")
                
            except Exception as e:
                last_exception = e
                self.logger.error(f"❌ {task_name}: Unexpected error on attempt {retry_attempt + 1}: {str(e)}")
                
                # For non-network errors, don't retry as aggressively
                if retry_attempt >= 2:
                    break
        
        # All retries exhausted
        self.update_task_status(
            task_name,
            status='failed',
            end_time=datetime.now(),
            current_step='Failed after all retries',
            error_message=str(last_exception) if last_exception else 'Unknown error'
        )
        
        self.logger.error(f"❌ {task_name}: Failed after {self.RETRY_CONFIG['max_retries']} retries")
        
        return {
            'success': False,
            'error': str(last_exception) if last_exception else 'Unknown error',
            'retry_count': retry_attempt
        }
    
    def run_comprehensive_collection(self, priority_level: int = 2) -> Dict:
        """Run comprehensive environmental data collection with full monitoring"""
        
        self.overall_start_time = datetime.now()
        self.logger.info("🚀 Starting comprehensive environmental data collection...")
        self.logger.info(f"📊 Priority Level: {priority_level} (1=Critical, 2=High, 3=Medium, 4=All)")
        self.logger.info(f"🌐 Bandwidth Profile: {self.bandwidth_profile}")
        
        # Test connectivity first
        connectivity_ok, connectivity_results = self.test_connectivity()
        for result in connectivity_results:
            self.logger.info(f"   {result}")
        
        if not connectivity_ok:
            self.logger.warning("⚠️  Connectivity issues detected - proceeding with caution")
        
        collection_results = {}
        
        # Define collection tasks based on priority
        if priority_level <= 1:  # Critical only
            tasks = [
                ('EPA_Envirofacts_Superfund', lambda: self.epa_collector.collect_system_data('superfund')),
                ('California_EnviroStor', lambda: self.ca_collector.collect_envirostor_data()),
            ]
        elif priority_level <= 2:  # High priority
            tasks = [
                ('EPA_Envirofacts_Priority', lambda: self.epa_collector.collect_all_systems(['superfund', 'rcrainfo', 'tri'])),
                ('ECHO_Exporter', lambda: self.echo_downloader.download_with_resume()),
                ('California_All', lambda: self.ca_collector.collect_all_california_databases()),
                ('Texas_Analysis', lambda: self.tx_collector.analyze_existing_tceq_data()),
            ]
        else:  # Comprehensive collection
            tasks = [
                ('EPA_Envirofacts_Complete', lambda: self.epa_collector.collect_all_systems()),
                ('ECHO_Exporter', lambda: self.echo_downloader.download_with_resume()),
                ('California_Complete', lambda: self.ca_collector.collect_all_california_databases()),
                ('Texas_Complete', lambda: self.tx_collector.collect_all_additional_texas_data()),
            ]
        
        # Initialize all task statuses
        for task_name, _ in tasks:
            self.update_task_status(task_name, status='pending')
        
        # Execute tasks with monitoring
        for task_name, task_func in tasks:
            if self.should_stop:
                self.logger.info("⏹️  Collection stopped by user request")
                break
                
            self.logger.info(f"🎯 Starting: {task_name}")
            result = self.execute_with_retry(task_name, task_func)
            collection_results[task_name] = result
            
            # Brief pause between major tasks
            if not self.should_stop:
                time.sleep(5)
        
        # Generate final report
        self._generate_final_report(collection_results)
        
        total_duration = datetime.now() - self.overall_start_time
        self.logger.info(f"🏁 Collection completed in {self._format_duration(total_duration)}")
        
        return collection_results
    
    def _generate_final_report(self, results: Dict):
        """Generate comprehensive final collection report"""
        
        report_time = datetime.now()
        successful_tasks = [k for k, v in results.items() if v.get('success', False)]
        failed_tasks = [k for k, v in results.items() if not v.get('success', False)]
        
        report = f"""# Environmental Database Collection Final Report

**Collection Date**: {report_time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Runtime**: {self._format_duration(report_time - self.overall_start_time)}
**Bandwidth Profile**: {self.bandwidth_profile}
**Tasks Completed**: {len(successful_tasks)}/{len(results)}

## Successful Collections

"""
        
        total_records = 0
        total_size_mb = 0
        
        for task_name in successful_tasks:
            result = results[task_name]
            records = result.get('records_count', result.get('records_collected', 0))
            size_mb = result.get('file_size_mb', result.get('data_size_mb', 0))
            
            total_records += records
            total_size_mb += size_mb
            
            report += f"### ✅ {task_name}\n"
            report += f"- **Records**: {records:,}\n"
            report += f"- **Size**: {size_mb:.1f} MB\n"
            
            if 'collection_duration_seconds' in result:
                duration = timedelta(seconds=result['collection_duration_seconds'])
                report += f"- **Duration**: {self._format_duration(duration)}\n"
            
            report += "\n"
        
        if failed_tasks:
            report += "## Failed Collections\n\n"
            for task_name in failed_tasks:
                result = results[task_name]
                report += f"### ❌ {task_name}\n"
                report += f"- **Error**: {result.get('error', 'Unknown error')}\n"
                report += f"- **Retries**: {result.get('retry_count', 0)}\n\n"
        
        report += f"""## Summary Statistics

- **Total Records Collected**: {total_records:,}
- **Total Data Size**: {total_size_mb:.1f} MB
- **Success Rate**: {len(successful_tasks)/len(results)*100:.1f}%
- **Average Task Duration**: {self._format_duration((report_time - self.overall_start_time) / len(results))}

## Data Integration Ready

The collected environmental databases are now ready for:

1. **LIHTC Property Screening**: Automated proximity analysis for contaminated sites
2. **Risk Assessment**: Comprehensive environmental due diligence
3. **Regulatory Compliance**: Phase I Environmental Site Assessment support
4. **Portfolio Analysis**: Batch screening for multiple properties

## Next Steps

1. **Geocoding Validation**: Verify coordinate accuracy for spatial analysis
2. **Database Integration**: Cross-reference federal and state databases
3. **Automation Setup**: Schedule regular updates for time-sensitive data
4. **LIHTC Integration**: Connect with property analysis workflows
"""
        
        # Save report
        report_file = self.base_data_path / "logs" / f"final_collection_report_{report_time.strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"📄 Final report saved: {report_file.name}")
        
        # Print summary to console
        print("\n" + "="*80)
        print("🏁 COLLECTION COMPLETED")
        print("="*80)
        print(f"✅ Successful: {len(successful_tasks)}/{len(results)} tasks")
        print(f"📊 Total Records: {total_records:,}")
        print(f"💾 Total Size: {total_size_mb:.1f} MB")
        print(f"⏱️  Total Time: {self._format_duration(report_time - self.overall_start_time)}")
        print(f"📄 Report: {report_file.name}")
        print("="*80)

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Environmental Database Collection System')
    parser.add_argument('--priority', type=int, choices=[1, 2, 3, 4], default=2,
                       help='Priority level: 1=Critical, 2=High, 3=Medium, 4=All (default: 2)')
    parser.add_argument('--bandwidth', choices=['travel', 'normal', 'high_speed'], default='normal',
                       help='Bandwidth profile (default: normal)')
    parser.add_argument('--data-path', type=str, 
                       default='/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets',
                       help='Base data storage path')
    
    args = parser.parse_args()
    
    print("🌍 Environmental Database Collection System")
    print("=" * 60)
    print(f"📁 Data Path: {args.data_path}")
    print(f"🎯 Priority Level: {args.priority}")
    print(f"🌐 Bandwidth Profile: {args.bandwidth}")
    print("=" * 60)
    print()
    
    # Initialize and run
    runner = EnvironmentalMasterRunner(args.data_path, args.bandwidth)
    
    try:
        results = runner.run_comprehensive_collection(args.priority)
        
        # Keep status monitoring active briefly for final updates
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n⏹️  Collection interrupted by user")
    except Exception as e:
        print(f"\n❌ Collection failed with error: {str(e)}")
    finally:
        runner.should_stop = True

if __name__ == "__main__":
    main()