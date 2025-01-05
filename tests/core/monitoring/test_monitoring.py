"""
监控系统测试用例
"""

import pytest
import time
from datetime import datetime, timedelta
from src.core.monitoring.logger import Logger
from src.core.monitoring.metrics import MetricsCollector, Metric
from src.core.monitoring.monitor import Monitor

# 测试配置
TEST_CONFIG = {
    "collection_interval": 0.1,  # 100ms
    "retention_period": 1,
    "alert_check_interval": 0.1,  # 100ms
    "thresholds": {
        "latency_ms": 100,
        "error_rate": 0.1,
        "queue_size": 10
    }
}

@pytest.fixture
def metrics_collector():
    """创建MetricsCollector实例"""
    collector = MetricsCollector(TEST_CONFIG)
    yield collector
    collector.shutdown()  # 清理资源

def test_logger():
    """测试日志记录器"""
    config = {
        "level": "DEBUG",
        "file": {
            "path": "test_logs/",
            "max_size": "10MB",
            "backup_count": 3
        }
    }
    logger = Logger("test", config)
    
    # 测试不同级别的日志记录
    logger.debug("Debug message", context={"test": True})
    logger.info("Info message", extra_field="value")
    logger.warning("Warning message")
    logger.error("Error message", context={"error_code": 500})
    
    # 测试异常记录
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception("Exception occurred", context={"error_type": "ValueError"})

def test_metrics_collector(metrics_collector):
    """测试指标收集器"""
    # 测试指标记录
    metrics_collector.record_metric("test_metric", 42.0)
    metrics_collector.record_metric("latency", 150.0)  # 应该触发告警
    metrics_collector.record_metric("queue_size", 15)  # 应该触发告警
    
    # 测试错误率计算
    metrics_collector.record_metric("request_count", 1)
    metrics_collector.record_metric("error_count", 1)
    assert metrics_collector.calculate_error_rate() > 0
    
    # 等待告警检查
    time.sleep(0.2)
    
    # 验证告警生成
    assert len(metrics_collector.alerts) > 0

def test_monitor():
    """测试监控接口"""
    monitor = Monitor()
    
    # 测试操作日志和指标记录
    monitor.log_operation(
        "test_operation",
        "success",
        context={"test": True}
    )
    
    # 测试错误记录
    try:
        raise ValueError("Test error")
    except Exception as e:
        monitor.log_error("test_operation", e, context={"error_type": "ValueError"})
    
    # 测试操作时间测量
    with monitor.measure_operation("timed_operation", context={"test": True}):
        time.sleep(0.1)
    
    # 测试自定义指标记录
    monitor.record_value("custom_metric", 42.0)
    
    # 验证指标摘要
    summary = monitor.get_metrics_summary()
    assert "timed_operation_latency" in summary
    assert "custom_metric" in summary
    
    # 验证告警
    alerts = monitor.get_recent_alerts()
    assert isinstance(alerts, list)

def test_integration():
    """集成测试"""
    monitor = Monitor()
    
    # 模拟一系列操作
    for i in range(10):
        # 记录成功操作
        monitor.log_operation(
            "batch_process",
            "success",
            context={"batch_id": i}
        )
        
        # 记录一些指标
        monitor.record_value("queue_size", i * 10)
        
        # 模拟一些耗时操作
        with monitor.measure_operation("process_item", context={"item_id": i}):
            time.sleep(0.01)
            
        # 随机模拟一些错误
        if i % 3 == 0:
            try:
                raise ValueError(f"Test error {i}")
            except Exception as e:
                monitor.log_error("batch_process", e, context={"batch_id": i})
    
    # 验证结果
    summary = monitor.get_metrics_summary()
    assert "process_item_latency" in summary
    assert "queue_size" in summary
    assert "error_count" in summary
    
    # 验证告警
    alerts = monitor.get_recent_alerts()
    assert len(alerts) > 0

if __name__ == "__main__":
    pytest.main([__file__]) 