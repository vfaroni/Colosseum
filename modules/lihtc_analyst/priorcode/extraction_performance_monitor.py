#!/usr/bin/env python3
"""
Extraction Performance Monitor
Real-time performance tracking for WINGMAN CTCAC extraction
WINGMAN-01 Mission Implementation
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass
class RealTimeMetrics:
    """Real-time performance metrics"""
    timestamp: datetime
    files_processed: int
    current_file: str
    processing_rate: float  # files per minute
    memory_usage_mb: float
    cpu_usage_percent: float
    estimated_completion: Optional[datetime] = None

class ExtractionPerformanceMonitor:
    """
    Real-time performance monitoring for WINGMAN extraction operations
    Tracks processing speed, memory usage, and provides estimates
    """
    
    def __init__(self, target_processing_time: float = 5.0, target_memory_mb: float = 200.0):
        """
        Initialize performance monitor
        
        Args:
            target_processing_time: Target processing time per file in seconds
            target_memory_mb: Target memory usage per file in MB
        """
        self.target_processing_time = target_processing_time
        self.target_memory_mb = target_memory_mb
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.start_time = None
        self.metrics_history: List[RealTimeMetrics] = []
        
        # Current session data
        self.total_files_to_process = 0
        self.files_processed = 0
        self.current_file = ""
        self.processing_errors = 0
        
        # Performance tracking
        self.file_processing_times: List[float] = []
        self.memory_usage_history: List[float] = []
        self.peak_memory_usage = 0.0
        
        # Alerts and notifications
        self.performance_alerts: List[str] = []
        self.alert_thresholds = {
            "slow_processing": target_processing_time * 2,  # 2x target time
            "high_memory": target_memory_mb * 1.5,         # 1.5x target memory
            "cpu_spike": 90.0,                             # 90% CPU usage
            "low_success_rate": 0.8                        # 80% success rate
        }
        
        print(f"📊 Performance Monitor initialized")
        print(f"   🎯 Target processing time: {target_processing_time}s per file")
        print(f"   💾 Target memory usage: {target_memory_mb}MB per file")
    
    def start_monitoring(self, total_files: int):
        """Start real-time monitoring"""
        
        self.total_files_to_process = total_files
        self.files_processed = 0
        self.start_time = datetime.now()
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"🚀 Performance monitoring started")
        print(f"   📁 Total files to process: {total_files}")
        print(f"   ⏰ Started at: {self.start_time.strftime('%H:%M:%S')}")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        
        print(f"🏁 Performance monitoring stopped")
        self._generate_final_report()
    
    def update_current_file(self, filename: str):
        """Update currently processing file"""
        self.current_file = filename
    
    def record_file_completion(self, filename: str, processing_time: float, 
                              memory_used: float, success: bool):
        """Record completion of file processing"""
        
        self.files_processed += 1
        
        if success:
            self.file_processing_times.append(processing_time)
            self.memory_usage_history.append(memory_used)
            self.peak_memory_usage = max(self.peak_memory_usage, memory_used)
        else:
            self.processing_errors += 1
        
        # Check for performance alerts
        self._check_performance_alerts(processing_time, memory_used, success)
        
        # Progress update
        progress = (self.files_processed / self.total_files_to_process) * 100 if self.total_files_to_process > 0 else 0
        avg_time = sum(self.file_processing_times) / len(self.file_processing_times) if self.file_processing_times else 0
        
        status_icon = "✅" if success else "❌"
        time_icon = "🚀" if processing_time <= self.target_processing_time else "⚠️"
        memory_icon = "💾" if memory_used <= self.target_memory_mb else "⚠️"
        
        print(f"{status_icon} {filename}: {processing_time:.2f}s {time_icon}, {memory_used:.1f}MB {memory_icon} ({progress:.1f}% complete)")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        
        while self.monitoring_active:
            try:
                # Collect current metrics
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                cpu_percent = process.cpu_percent()
                
                # Calculate processing rate
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
                processing_rate = (self.files_processed / elapsed_time * 60) if elapsed_time > 0 else 0
                
                # Estimate completion time
                remaining_files = self.total_files_to_process - self.files_processed
                if processing_rate > 0:
                    remaining_minutes = remaining_files / processing_rate
                    estimated_completion = datetime.now() + timedelta(minutes=remaining_minutes)
                else:
                    estimated_completion = None
                
                # Store metrics
                metrics = RealTimeMetrics(
                    timestamp=datetime.now(),
                    files_processed=self.files_processed,
                    current_file=self.current_file,
                    processing_rate=processing_rate,
                    memory_usage_mb=memory_mb,
                    cpu_usage_percent=cpu_percent,
                    estimated_completion=estimated_completion
                )
                
                self.metrics_history.append(metrics)
                
                # Keep only last 100 metrics for memory efficiency
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                # Real-time status every 30 seconds
                if len(self.metrics_history) % 6 == 0:  # Every 30 seconds (5s intervals)
                    self._print_realtime_status(metrics)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _print_realtime_status(self, metrics: RealTimeMetrics):
        """Print real-time status update"""
        
        progress = (metrics.files_processed / self.total_files_to_process) * 100 if self.total_files_to_process > 0 else 0
        
        print(f"\n📊 REAL-TIME STATUS [{metrics.timestamp.strftime('%H:%M:%S')}]")
        print(f"   Progress: {metrics.files_processed}/{self.total_files_to_process} ({progress:.1f}%)")
        print(f"   Rate: {metrics.processing_rate:.1f} files/minute")
        print(f"   Memory: {metrics.memory_usage_mb:.1f} MB")
        print(f"   CPU: {metrics.cpu_usage_percent:.1f}%")
        
        if metrics.estimated_completion:
            print(f"   ETA: {metrics.estimated_completion.strftime('%H:%M:%S')}")
        
        if self.current_file:
            print(f"   Current: {self.current_file}")
        
        # Performance indicators
        avg_time = sum(self.file_processing_times) / len(self.file_processing_times) if self.file_processing_times else 0
        time_status = "🚀 ON TARGET" if avg_time <= self.target_processing_time else "⚠️ SLOW"
        memory_status = "💾 EFFICIENT" if metrics.memory_usage_mb <= self.target_memory_mb else "⚠️ HIGH"
        
        print(f"   Performance: {time_status}, {memory_status}")
    
    def _check_performance_alerts(self, processing_time: float, memory_used: float, success: bool):
        """Check for performance alerts and add to alert list"""
        
        # Slow processing alert
        if processing_time > self.alert_thresholds["slow_processing"]:
            alert = f"SLOW PROCESSING: {processing_time:.2f}s (target: {self.target_processing_time}s)"
            if alert not in self.performance_alerts:
                self.performance_alerts.append(alert)
                print(f"⚠️ {alert}")
        
        # High memory alert
        if memory_used > self.alert_thresholds["high_memory"]:
            alert = f"HIGH MEMORY: {memory_used:.1f}MB (target: {self.target_memory_mb}MB)"
            if alert not in self.performance_alerts:
                self.performance_alerts.append(alert)
                print(f"⚠️ {alert}")
        
        # Success rate alert
        if self.files_processed >= 5:  # Only check after processing at least 5 files
            success_rate = (self.files_processed - self.processing_errors) / self.files_processed
            if success_rate < self.alert_thresholds["low_success_rate"]:
                alert = f"LOW SUCCESS RATE: {success_rate:.1%} (target: {self.alert_thresholds['low_success_rate']:.1%})"
                if alert not in self.performance_alerts:
                    self.performance_alerts.append(alert)
                    print(f"⚠️ {alert}")
    
    def _generate_final_report(self):
        """Generate final performance report"""
        
        if not self.start_time:
            return
        
        total_elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n📋 WINGMAN PERFORMANCE REPORT")
        print("=" * 50)
        
        # Basic metrics
        print(f"⏱️ Total Time: {total_elapsed:.2f}s ({total_elapsed/60:.1f} minutes)")
        print(f"📁 Files Processed: {self.files_processed}/{self.total_files_to_process}")
        print(f"❌ Processing Errors: {self.processing_errors}")
        
        # Success rate
        success_rate = ((self.files_processed - self.processing_errors) / self.files_processed * 100 
                       if self.files_processed > 0 else 0)
        print(f"✅ Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        if self.file_processing_times:
            avg_processing_time = sum(self.file_processing_times) / len(self.file_processing_times)
            min_time = min(self.file_processing_times)
            max_time = max(self.file_processing_times)
            
            print(f"\n⚡ PROCESSING TIMES")
            print(f"   Average: {avg_processing_time:.2f}s")
            print(f"   Minimum: {min_time:.2f}s")
            print(f"   Maximum: {max_time:.2f}s")
            print(f"   Target: {self.target_processing_time:.2f}s")
            
            target_met = avg_processing_time <= self.target_processing_time
            print(f"   Status: {'✅ TARGET MET' if target_met else '❌ TARGET MISSED'}")
        
        # Memory metrics
        if self.memory_usage_history:
            avg_memory = sum(self.memory_usage_history) / len(self.memory_usage_history)
            
            print(f"\n💾 MEMORY USAGE")
            print(f"   Average: {avg_memory:.1f} MB")
            print(f"   Peak: {self.peak_memory_usage:.1f} MB")
            print(f"   Target: {self.target_memory_mb:.1f} MB")
            
            memory_target_met = avg_memory <= self.target_memory_mb
            print(f"   Status: {'✅ TARGET MET' if memory_target_met else '❌ TARGET MISSED'}")
        
        # Throughput metrics
        overall_rate = (self.files_processed / total_elapsed * 60) if total_elapsed > 0 else 0
        print(f"\n🚀 THROUGHPUT")
        print(f"   Overall Rate: {overall_rate:.1f} files/minute")
        
        # Estimated M4 Beast vs baseline comparison
        m1_baseline_rate = 2.0  # files/minute
        improvement_factor = overall_rate / m1_baseline_rate if m1_baseline_rate > 0 else 0
        print(f"   vs M1 Baseline: {improvement_factor:.1f}x improvement")
        
        # Mission targets assessment
        print(f"\n🎯 MISSION TARGETS")
        processing_target = avg_processing_time <= self.target_processing_time if self.file_processing_times else False
        memory_target = avg_memory <= self.target_memory_mb if self.memory_usage_history else False
        success_target = success_rate >= 95.0
        
        print(f"   Processing Time <{self.target_processing_time}s: {'✅ MET' if processing_target else '❌ MISSED'}")
        print(f"   Memory Usage <{self.target_memory_mb}MB: {'✅ MET' if memory_target else '❌ MISSED'}")
        print(f"   Success Rate >95%: {'✅ MET' if success_target else '❌ MISSED'}")
        
        overall_mission_success = processing_target and memory_target and success_target
        print(f"\n🏆 MISSION STATUS: {'✅ SUCCESS' if overall_mission_success else '❌ NEEDS IMPROVEMENT'}")
        
        # Performance alerts summary
        if self.performance_alerts:
            print(f"\n⚠️ PERFORMANCE ALERTS ({len(self.performance_alerts)})")
            for alert in self.performance_alerts:
                print(f"   • {alert}")
        else:
            print(f"\n✅ NO PERFORMANCE ALERTS")
    
    def export_metrics(self, output_path: Path):
        """Export performance metrics to JSON file"""
        
        if not self.metrics_history:
            print("No metrics to export")
            return
        
        export_data = {
            "session_info": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": datetime.now().isoformat(),
                "total_files": self.total_files_to_process,
                "files_processed": self.files_processed,
                "processing_errors": self.processing_errors,
                "target_processing_time": self.target_processing_time,
                "target_memory_mb": self.target_memory_mb
            },
            "performance_summary": {
                "avg_processing_time": (sum(self.file_processing_times) / len(self.file_processing_times) 
                                       if self.file_processing_times else 0),
                "avg_memory_usage": (sum(self.memory_usage_history) / len(self.memory_usage_history) 
                                    if self.memory_usage_history else 0),
                "peak_memory_usage": self.peak_memory_usage,
                "success_rate": ((self.files_processed - self.processing_errors) / self.files_processed 
                                if self.files_processed > 0 else 0)
            },
            "metrics_history": [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "files_processed": metric.files_processed,
                    "current_file": metric.current_file,
                    "processing_rate": metric.processing_rate,
                    "memory_usage_mb": metric.memory_usage_mb,
                    "cpu_usage_percent": metric.cpu_usage_percent,
                    "estimated_completion": (metric.estimated_completion.isoformat() 
                                           if metric.estimated_completion else None)
                }
                for metric in self.metrics_history
            ],
            "performance_alerts": self.performance_alerts,
            "file_processing_times": self.file_processing_times,
            "memory_usage_history": self.memory_usage_history
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = output_path / f"wingman_performance_metrics_{timestamp}.json"
        
        with open(metrics_file, "w") as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📊 Performance metrics exported to: {metrics_file}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        
        if not self.metrics_history:
            return {"status": "not_started"}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            "status": "active" if self.monitoring_active else "stopped",
            "files_processed": self.files_processed,
            "total_files": self.total_files_to_process,
            "progress_percent": (self.files_processed / self.total_files_to_process * 100 
                               if self.total_files_to_process > 0 else 0),
            "current_file": self.current_file,
            "processing_rate": latest_metrics.processing_rate,
            "memory_usage_mb": latest_metrics.memory_usage_mb,
            "cpu_usage_percent": latest_metrics.cpu_usage_percent,
            "estimated_completion": (latest_metrics.estimated_completion.isoformat() 
                                   if latest_metrics.estimated_completion else None),
            "performance_alerts_count": len(self.performance_alerts),
            "avg_processing_time": (sum(self.file_processing_times) / len(self.file_processing_times) 
                                   if self.file_processing_times else 0),
            "targets_met": {
                "processing_time": (sum(self.file_processing_times) / len(self.file_processing_times) 
                                   <= self.target_processing_time if self.file_processing_times else False),
                "memory_usage": latest_metrics.memory_usage_mb <= self.target_memory_mb,
                "success_rate": ((self.files_processed - self.processing_errors) / self.files_processed >= 0.95 
                               if self.files_processed > 0 else False)
            }
        }

def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    
    print("📊 WINGMAN Performance Monitor Demo")
    print("=" * 40)
    
    # Simulate extraction session
    monitor = ExtractionPerformanceMonitor(target_processing_time=5.0, target_memory_mb=200.0)
    
    # Start monitoring
    total_files = 5
    monitor.start_monitoring(total_files)
    
    # Simulate file processing
    import random
    for i in range(total_files):
        filename = f"CTCAC_Application_{i+1:03d}.xlsx"
        monitor.update_current_file(filename)
        
        # Simulate processing time
        processing_time = random.uniform(2.0, 7.0)  # 2-7 seconds
        memory_used = random.uniform(150.0, 250.0)  # 150-250 MB
        success = random.random() > 0.1  # 90% success rate
        
        time.sleep(1)  # Simulate actual processing
        
        monitor.record_file_completion(filename, processing_time, memory_used, success)
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Export metrics
    output_path = Path("/tmp")
    monitor.export_metrics(output_path)
    
    return monitor

if __name__ == "__main__":
    demo_performance_monitoring()