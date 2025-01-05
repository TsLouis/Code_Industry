"""
指标收集模块
"""

import time
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
from .logger import JsonLogger

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, collection_interval: float = 60.0, alert_threshold: float = 300.0):
        """初始化指标收集器
        
        Args:
            collection_interval: 指标收集间隔(秒)
            alert_threshold: 告警阈值(秒)
        """
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.collection_interval = collection_interval
        self.alert_threshold = alert_threshold
        self.logger = JsonLogger("metrics")
        self._lock = threading.Lock()
        self._running = False
        self._collection_thread = None
        self._alert_thread = None
        
    def start(self):
        """启动指标收集"""
        if not self._running:
            self._running = True
            self._collection_thread = threading.Thread(target=self._collect_metrics)
            self._alert_thread = threading.Thread(target=self._check_alerts)
            self._collection_thread.daemon = True
            self._alert_thread.daemon = True
            self._collection_thread.start()
            self._alert_thread.start()
            
    def stop(self):
        """停止指标收集"""
        self._running = False
        if self._collection_thread:
            self._collection_thread.join()
        if self._alert_thread:
            self._alert_thread.join()
            
    def record_metric(self, name: str, value: float):
        """记录指标值"""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(value)
            
    def get_metric(self, name: str) -> Optional[List[float]]:
        """获取指标值"""
        with self._lock:
            return self.metrics.get(name)
            
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            summary = {}
            for name, values in self.metrics.items():
                if values:
                    summary[name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
            return summary
            
    def _collect_metrics(self):
        """收集指标"""
        while self._running:
            time.sleep(self.collection_interval)
            summary = self.get_metrics_summary()
            self.logger.info("Metrics collected", context={"metrics": summary})
            
    def _check_alerts(self):
        """检查告警"""
        while self._running:
            time.sleep(self.collection_interval)
            with self._lock:
                for name, values in self.metrics.items():
                    if values:
                        avg_value = sum(values) / len(values)
                        if avg_value > self.alert_threshold:
                            alert = {
                                "metric": name,
                                "value": avg_value,
                                "threshold": self.alert_threshold,
                                "timestamp": datetime.now()
                            }
                            self.alerts.append(alert)
                            self.logger.warning(
                                f"Alert: {name} exceeded threshold",
                                context=alert
                            )

@contextmanager
def measure_time(operation: str):
    """测量操作执行时间的上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics.record_metric(f"{operation}_duration", duration)

# 创建默认指标收集器实例
metrics = MetricsCollector() 