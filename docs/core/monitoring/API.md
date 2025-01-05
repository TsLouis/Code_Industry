# 监控系统 API 参考文档

## 1. MetricsCollector

### 类定义
```python
class MetricsCollector:
    def __init__(self, config: Dict[str, Any])
```

### 配置参数
- `collection_interval`: 采集间隔（秒）
- `retention_period`: 数据保留期（天）
- `alert_check_interval`: 告警检查间隔（秒）
- `thresholds`: 告警阈值配置
  - `latency_ms`: 延迟阈值（毫秒）
  - `error_rate`: 错误率阈值
  - `queue_size`: 队列大小阈值

### 主要方法

#### record_metric
```python
def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None)
```
记录一个指标值。

参数：
- `name`: 指标名称
- `value`: 指标值
- `labels`: 可选的标签字典

#### get_recent_metrics
```python
def get_recent_metrics(self, name: str, minutes: int = 5) -> List[Metric]
```
获取最近一段时间的指标数据。

参数：
- `name`: 指标名称
- `minutes`: 时间范围（分钟）

返回：
- 指标列表

#### calculate_error_rate
```python
def calculate_error_rate(self) -> float
```
计算当前错误率。

返回：
- 错误率（0-1之间的浮点数）

#### get_metrics_summary
```python
def get_metrics_summary(self) -> Dict[str, Any]
```
获取指标摘要信息。

返回：
- 包含各指标统计信息的字典

#### shutdown
```python
def shutdown(self)
```
关闭指标收集器，停止后台任务。

## 2. Logger

### 类定义
```python
class Logger:
    def __init__(self, name: str, config: Dict[str, Any])
```

### 配置参数
- `level`: 日志级别
- `file`: 文件配置
  - `path`: 日志文件路径
  - `max_size`: 最大文件大小
  - `backup_count`: 备份文件数量

### 日志方法

#### debug
```python
def debug(self, message: str, context: Dict[str, Any] = None)
```
记录调试级别日志。

#### info
```python
def info(self, message: str, context: Dict[str, Any] = None)
```
记录信息级别日志。

#### warning
```python
def warning(self, message: str, context: Dict[str, Any] = None)
```
记录警告级别日志。

#### error
```python
def error(self, message: str, context: Dict[str, Any] = None)
```
记录错误级别日志。

#### exception
```python
def exception(self, message: str, context: Dict[str, Any] = None)
```
记录异常信息，包含堆栈跟踪。

## 3. Monitor

### 类定义
```python
class Monitor:
    def __init__(self)
```

### 主要方法

#### log_operation
```python
def log_operation(self, operation: str, status: str, context: Dict[str, Any] = None)
```
记录操作日志。

参数：
- `operation`: 操作名称
- `status`: 操作状态
- `context`: 上下文信息

#### log_error
```python
def log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None)
```
记录错误信息。

参数：
- `operation`: 操作名称
- `error`: 异常对象
- `context`: 上下文信息

#### measure_operation
```python
@contextmanager
def measure_operation(self, operation: str, context: Dict[str, Any] = None)
```
测量操作执行时间的上下文管理器。

参数：
- `operation`: 操作名称
- `context`: 上下文信息

#### record_value
```python
def record_value(self, name: str, value: float)
```
记录自定义指标值。

参数：
- `name`: 指标名称
- `value`: 指标值

## 4. 装饰器

### monitor_agent_action
```python
def monitor_agent_action(action_type: str)
```
监控Agent行为的装饰器。

参数：
- `action_type`: 行为类型

用法：
```python
@monitor_agent_action("analyze_requirement")
async def analyze_requirement(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
    pass
```

### measure_time
```python
def measure_time(operation: str)
```
测量操作执行时间的装饰器。

参数：
- `operation`: 操作名称

用法：
```python
@measure_time("process_task")
def process_task(self):
    pass
```

## 5. 数据类型

### Metric
```python
@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    labels: Optional[Dict[str, str]] = None
```

### Alert
```python
@dataclass
class Alert:
    name: str
    message: str
    level: str
    timestamp: datetime
    metric: Metric
```

## 6. 使用示例

### 基础监控
```python
from src.core.monitoring import metrics, monitor, logger

# 记录指标
metrics.record_metric("api_latency", 150.0)

# 记录日志
logger.info("API call completed", context={"endpoint": "/api/v1/users"})

# 测量操作时间
with monitor.measure_operation("data_processing"):
    process_data()
```

### Agent监控
```python
from src.core.monitoring import agent_monitor

@agent_monitor.monitor_agent_action("process_task")
async def process_task(self, task_data):
    # 处理任务
    pass
```

### 告警处理
```python
# 配置告警阈值
config = {
    "thresholds": {
        "latency_ms": 1000,
        "error_rate": 0.01,
        "queue_size": 1000
    }
}

# 创建监控器
collector = metrics.MetricsCollector(config)

# 记录可能触发告警的指标
collector.record_metric("latency", 1500.0)  # 将触发延迟告警
``` 