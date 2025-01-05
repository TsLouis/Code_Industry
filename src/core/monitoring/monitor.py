"""
监控模块
"""

import time
from typing import Any, Dict, Optional
from contextlib import contextmanager
from .logger import JsonLogger

class Monitor:
    """监控类"""
    
    def __init__(self):
        self.logger = JsonLogger("app")
        
    def log_operation(self, operation: str, status: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录操作日志"""
        self.logger.info(f"Operation {operation}: {status}", context=context, **kwargs)
        
    def log_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录错误日志"""
        self.logger.error(f"Error in {operation}: {str(error)}", context=context, exc_info=True, **kwargs)
        
    def log_metric(self, metric: str, value: Any, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录指标"""
        self.logger.info(f"Metric {metric}: {value}", context=context, **kwargs)
        
    def record_value(self, name: str, value: Any, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录值（与 log_metric 相同）"""
        self.log_metric(name, value, context, **kwargs)
        
    @contextmanager
    def measure_operation(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """测量操作执行时间的上下文管理器"""
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.log_metric(f"{operation}_duration", duration, context)
            self.log_operation(operation, "success", context)
        except Exception as e:
            duration = time.time() - start_time
            self.log_metric(f"{operation}_duration", duration, context)
            self.log_error(operation, e, context)
            raise

# 创建默认监控实例
monitor = Monitor() 