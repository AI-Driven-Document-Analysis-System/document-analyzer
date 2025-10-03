"""
System Resource Monitor
Monitors CPU, Memory, Disk, and Network during tests
"""

import psutil
import time
import json
from datetime import datetime
import threading

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.start_time = None
        self.monitor_thread = None
        
    def start_monitoring(self, interval=1):
        """Start monitoring system resources"""
        self.monitoring = True
        self.start_time = datetime.now()
        self.metrics = []
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"✓ System monitoring started at {self.start_time.strftime('%H:%M:%S')}")
    
    def _monitor_loop(self, interval):
        """Background monitoring loop"""
        while self.monitoring:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / (1024 * 1024),
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "network_sent_mb": psutil.net_io_counters().bytes_sent / (1024 * 1024),
                "network_recv_mb": psutil.net_io_counters().bytes_recv / (1024 * 1024)
            }
            self.metrics.append(metric)
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring and return results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"✓ System monitoring stopped at {end_time.strftime('%H:%M:%S')}")
        print(f"✓ Monitoring duration: {duration:.2f} seconds")
        
        return self.get_summary()
    
    def get_summary(self):
        """Get monitoring summary statistics"""
        if not self.metrics:
            return {}
        
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_percent'] for m in self.metrics]
        
        summary = {
            "duration_seconds": len(self.metrics),
            "cpu": {
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "average": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "samples_collected": len(self.metrics)
        }
        
        return summary
    
    def save_metrics(self, filename='system_metrics.json'):
        """Save metrics to file"""
        data = {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "metrics": self.metrics,
            "summary": self.get_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self):
        """Print monitoring summary"""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("SYSTEM RESOURCE SUMMARY")
        print("=" * 60)
        print(f"Monitoring Duration: {summary.get('duration_seconds', 0)} seconds")
        print(f"Samples Collected: {summary.get('samples_collected', 0)}")
        print("\nCPU Usage:")
        print(f"  Average: {summary.get('cpu', {}).get('average', 0):.2f}%")
        print(f"  Maximum: {summary.get('cpu', {}).get('max', 0):.2f}%")
        print(f"  Minimum: {summary.get('cpu', {}).get('min', 0):.2f}%")
        print("\nMemory Usage:")
        print(f"  Average: {summary.get('memory', {}).get('average', 0):.2f}%")
        print(f"  Maximum: {summary.get('memory', {}).get('max', 0):.2f}%")
        print(f"  Minimum: {summary.get('memory', {}).get('min', 0):.2f}%")
        print("=" * 60)

if __name__ == "__main__":
    monitor = SystemMonitor()
    
    print("Testing System Monitor...")
    monitor.start_monitoring(interval=1)
    
    # Simulate some work
    print("Simulating system activity for 10 seconds...")
    time.sleep(10)
    
    monitor.stop_monitoring()
    monitor.print_summary()
    monitor.save_metrics('test_metrics.json')
    print("\n✓ Metrics saved to test_metrics.json")