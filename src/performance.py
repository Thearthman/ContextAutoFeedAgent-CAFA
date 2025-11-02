#!/usr/bin/env python3
"""
Performance Monitoring Module
Provides performance metrics tracking and analysis
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricSnapshot:
    """Metric snapshot"""
    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMetrics:
    """Performance metrics tracker"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance metrics tracker
        
        Args:
            max_history: Number of historical records to keep
        """
        self.max_history = max_history
        self.metrics: Dict[str, deque] = {}
        self.lock = threading.Lock()
        
        # System resource monitoring
        self.system_metrics = {
            "cpu_percent": deque(maxlen=max_history),
            "memory_percent": deque(maxlen=max_history),
            "memory_used_mb": deque(maxlen=max_history),
        }
    
    def record(self, metric_name: str, value: float, metadata: Optional[Dict] = None) -> None:
        """
        Record performance metric
        
        Args:
            metric_name: Metric name
            value: Metric value
            metadata: Additional metadata
        """
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = deque(maxlen=self.max_history)
            
            snapshot = MetricSnapshot(
                timestamp=time.time(),
                value=value,
                metadata=metadata or {}
            )
            
            self.metrics[metric_name].append(snapshot)
    
    def get_stats(self, metric_name: str) -> Optional[Dict[str, float]]:
        """
        Get metric statistics
        
        Args:
            metric_name: Metric name
        
        Returns:
            Statistics (min, max, avg, latest, etc.)
        """
        with self.lock:
            if metric_name not in self.metrics or not self.metrics[metric_name]:
                return None
            
            values = [s.value for s in self.metrics[metric_name]]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1],
                "p50": self._percentile(values, 0.5),
                "p90": self._percentile(values, 0.9),
                "p95": self._percentile(values, 0.95),
                "p99": self._percentile(values, 0.99),
            }
    
    def get_recent(self, metric_name: str, count: int = 10) -> List[MetricSnapshot]:
        """
        Get recent metric records
        
        Args:
            metric_name: Metric name
            count: Number of records
        
        Returns:
            List of metric snapshots
        """
        with self.lock:
            if metric_name not in self.metrics:
                return []
            
            snapshots = list(self.metrics[metric_name])
            return snapshots[-count:]
    
    def record_system_metrics(self) -> None:
        """Record system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        with self.lock:
            self.system_metrics["cpu_percent"].append(
                MetricSnapshot(time.time(), cpu_percent)
            )
            self.system_metrics["memory_percent"].append(
                MetricSnapshot(time.time(), memory.percent)
            )
            self.system_metrics["memory_used_mb"].append(
                MetricSnapshot(time.time(), memory.used / 1024 / 1024)
            )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        with self.lock:
            stats = {}
            for metric_name, snapshots in self.system_metrics.items():
                if snapshots:
                    values = [s.value for s in snapshots]
                    stats[metric_name] = {
                        "current": values[-1],
                        "avg": sum(values) / len(values),
                        "max": max(values)
                    }
            
            return stats
    
    def clear(self, metric_name: Optional[str] = None) -> None:
        """
        Clear metric data
        
        Args:
            metric_name: Metric name (if None, clear all)
        """
        with self.lock:
            if metric_name:
                if metric_name in self.metrics:
                    self.metrics[metric_name].clear()
            else:
                self.metrics.clear()
                for deq in self.system_metrics.values():
                    deq.clear()
    
    def get_all_metrics(self) -> List[str]:
        """Get all metric names"""
        with self.lock:
            return list(self.metrics.keys())
    
    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]


class RequestTimer:
    """Request timer (context manager)"""
    
    def __init__(self, metrics: PerformanceMetrics, metric_name: str, metadata: Optional[Dict] = None):
        """
        Initialize timer
        
        Args:
            metrics: Performance metrics tracker
            metric_name: Metric name
            metadata: Additional metadata
        """
        self.metrics = metrics
        self.metric_name = metric_name
        self.metadata = metadata or {}
        self.start_time = None
        self.duration_ms = None
    
    def __enter__(self):
        """Enter context"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        if self.start_time:
            end_time = time.time()
            self.duration_ms = (end_time - self.start_time) * 1000
            self.metrics.record(self.metric_name, self.duration_ms, self.metadata)
        return False


class PerformanceMonitor:
    """Performance monitor (global singleton)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.metrics = PerformanceMetrics()
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self._initialized = True
        
        # Start background system monitoring (optional)
        self.monitoring = False
    
    def record_request(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """
        Record HTTP request
        
        Args:
            endpoint: Endpoint
            duration_ms: Duration (milliseconds)
            status_code: Status code
        """
        self.request_count += 1
        
        if status_code >= 400:
            self.error_count += 1
        
        self.metrics.record(
            f"request.{endpoint}",
            duration_ms,
            {"status_code": status_code}
        )
        
        self.metrics.record("request.all", duration_ms)
    
    def record_llm_call(
        self,
        provider: str,
        model: str,
        duration_s: float,
        tokens: int,
        success: bool = True
    ) -> None:
        """
        Record LLM call
        
        Args:
            provider: Provider
            model: Model
            duration_s: Duration (seconds)
            tokens: Number of tokens generated
            success: Success status
        """
        duration_ms = duration_s * 1000
        
        self.metrics.record(
            f"llm.{provider}.{model}",
            duration_ms,
            {"tokens": tokens, "success": success}
        )
        
        # Calculate tokens/s
        tokens_per_second = tokens / duration_s if duration_s > 0 else 0
        self.metrics.record(
            f"llm.{provider}.tokens_per_second",
            tokens_per_second
        )
    
    def record_memory_operation(
        self,
        operation: str,
        duration_ms: float,
        count: int = 1
    ) -> None:
        """
        Record memory operation
        
        Args:
            operation: Operation type (store, recall, decay)
            duration_ms: Duration (milliseconds)
            count: Number of operations
        """
        self.metrics.record(
            f"memory.{operation}",
            duration_ms,
            {"count": count}
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
            "metrics": {
                name: self.metrics.get_stats(name)
                for name in self.metrics.get_all_metrics()
            },
            "system": self.metrics.get_system_stats()
        }
    
    def start_system_monitoring(self, interval: float = 5.0) -> None:
        """
        Start system monitoring
        
        Args:
            interval: Monitoring interval (seconds)
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                self.metrics.record_system_metrics()
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def stop_system_monitoring(self) -> None:
        """Stop system monitoring"""
        self.monitoring = False


# Global performance monitor
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _monitor


# Usage example
if __name__ == "__main__":
    print("📊 Performance Monitoring Module Test")
    print("=" * 70)
    
    # Get monitor
    monitor = get_monitor()
    
    # Simulate some requests
    print("\n1️⃣ Simulate requests:")
    for i in range(5):
        with RequestTimer(monitor.metrics, "test.endpoint"):
            time.sleep(0.01 * (i + 1))  # Simulate different processing times
    
    # Get statistics
    print("\n2️⃣ Request statistics:")
    stats = monitor.metrics.get_stats("test.endpoint")
    if stats:
        print(f"  Request count: {stats['count']}")
        print(f"  Average time: {stats['avg']:.2f}ms")
        print(f"  Min time: {stats['min']:.2f}ms")
        print(f"  Max time: {stats['max']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
    
    # Simulate LLM calls
    print("\n3️⃣ Simulate LLM calls:")
    monitor.record_llm_call("openai", "gpt-3.5-turbo", 1.5, 150)
    monitor.record_llm_call("openai", "gpt-3.5-turbo", 2.0, 200)
    
    llm_stats = monitor.metrics.get_stats("llm.openai.gpt-3.5-turbo")
    if llm_stats:
        print(f"  LLM call count: {llm_stats['count']}")
        print(f"  Average time: {llm_stats['avg']:.2f}ms")
    
    # System resource monitoring
    print("\n4️⃣ System resources:")
    monitor.metrics.record_system_metrics()
    system_stats = monitor.metrics.get_system_stats()
    
    if "cpu_percent" in system_stats:
        print(f"  CPU usage: {system_stats['cpu_percent']['current']:.1f}%")
    
    if "memory_percent" in system_stats:
        print(f"  Memory usage: {system_stats['memory_percent']['current']:.1f}%")
    
    # Get complete summary
    print("\n5️⃣ Performance summary:")
    summary = monitor.get_summary()
    print(f"  Uptime: {summary['uptime_seconds']:.1f}s")
    print(f"  Total requests: {summary['total_requests']}")
    
    print("\n" + "=" * 70)
