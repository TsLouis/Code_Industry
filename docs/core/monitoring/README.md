# 监控系统模块

## 1. 模块概述

监控系统模块(`monitoring`)是一个全面的系统监控解决方案，提供了对Agent行为、系统性能、错误处理和资源使用的实时监控能力。该模块设计用于多智能体系统中，可以跟踪和分析各个Agent的行为和性能指标。

### 1.1 主要功能

- **Agent行为监控**：跟踪Agent的操作、决策过程和交互行为
- **性能指标收集**：收集和分析系统性能数据
- **告警机制**：基于阈值的自动告警系统
- **日志管理**：结构化的日志记录和管理
- **错误追踪**：详细的错误信息收集和分析

### 1.2 核心组件

- `metrics.py`: 指标收集和处理
- `monitor.py`: 监控核心功能
- `logger.py`: 日志记录系统
- `agent_monitor.py`: Agent专用监控
- `decorators.py`: 监控相关装饰器

## 2. 快速开始

### 2.1 基础配置

```python
from src.core.monitoring import metrics, monitor, logger

# 配置监控系统
config = {
    "collection_interval": 60,  # 秒
    "retention_period": 7,      # 天
    "alert_check_interval": 300,  # 秒
    "thresholds": {
        "latency_ms": 1000,
        "error_rate": 0.01,
        "queue_size": 1000
    }
}

# 创建监控器实例
metrics_collector = metrics.MetricsCollector(config)
```

### 2.2 使用示例

```python
# 记录指标
metrics_collector.record_metric("api_latency", 150.0)

# 使用上下文管理器测量操作时间
with metrics.measure_time("process_task"):
    # 执行任务
    process_task()

# 记录日志
logger.info("Task completed", context={"task_id": "123"})
```

## 3. 核心功能说明

### 3.1 指标收集

指标收集器支持多种类型的指标：
- 数值指标（如延迟、队列大小）
- 计数器（如请求数、错误数）
- 比率（如错误率、成功率）

### 3.2 告警机制

系统支持基于阈值的告警：
- 性能告警（延迟超限）
- 错误率告警
- 资源使用告警
- 自定义告警规则

### 3.3 日志系统

提供多级别的日志记录：
- DEBUG：调试信息
- INFO：一般信息
- WARNING：警告信息
- ERROR：错误信息
- CRITICAL：严重错误

### 3.4 Agent监控

专门的Agent监控功能：
- 行为跟踪
- 决策过程记录
- 交互历史
- 性能分析

## 4. 最佳实践

### 4.1 性能优化

- 合理设置采样间隔
- 适当配置数据保留期
- 使用标签优化查询
- 定期清理历史数据

### 4.2 告警配置

- 根据实际情况设置阈值
- 避免过于频繁的告警
- 设置合适的检查间隔
- 分级处理告警信息

### 4.3 日志管理

- 使用结构化日志
- 添加合适的上下文信息
- 设置适当的日志级别
- 实现日志轮转

## 5. 注意事项

1. **资源使用**
   - 监控数据会占用内存
   - 需要定期清理过期数据
   - 合理配置采样频率

2. **线程安全**
   - 所有操作都是线程安全的
   - 使用锁保护共享资源
   - 注意避免死锁

3. **错误处理**
   - 监控系统本身的错误不应影响主系统
   - 实现了优雅的降级机制
   - 提供错误恢复能力

## 6. 常见问题

1. Q: 如何调整告警阈值？
   A: 通过配置文件修改 thresholds 参数

2. Q: 如何处理历史数据？
   A: 系统会自动根据 retention_period 清理过期数据

3. Q: 如何添加自定义指标？
   A: 使用 record_metric 方法记录自定义指标

4. Q: 如何实现自定义告警？
   A: 扩展 _process_alerts 方法添加新的告警规则 