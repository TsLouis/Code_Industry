"""
监控装饰器模块
提供用于通信模块的监控装饰器
"""

import functools
from typing import Any, Callable, Dict, Optional
from .monitor import monitor

def trace_message(operation: str):
    """
    跟踪消息处理的装饰器
    用于监控消息处理的性能和状态
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 提取消息信息
            message = args[1] if len(args) > 1 else kwargs.get('message')
            context = {
                "message_id": getattr(message, "id", None),
                "sender": getattr(message, "sender", None),
                "receiver": getattr(message, "receiver", None),
                "message_type": getattr(message, "type", None)
            }
            
            try:
                # 使用监控上下文管理器
                with monitor.measure_operation(operation, context=context):
                    result = await func(*args, **kwargs)
                    
                # 记录成功指标
                monitor.record_value(f"{operation}_success", 1)
                return result
                
            except Exception as e:
                # 记录错误
                monitor.log_error(operation, e, context=context)
                # 重新抛出异常
                raise
                
        return wrapper
    return decorator

def monitor_broker(operation: str):
    """
    监控消息代理操作的装饰器
    用于监控代理的性能和状态
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            broker = args[0]
            context = {
                "broker_id": id(broker),
                "queue_size": len(getattr(broker, "queue", [])),
                "active_handlers": len(getattr(broker, "handlers", {}))
            }
            
            try:
                with monitor.measure_operation(operation, context=context):
                    result = await func(*args, **kwargs)
                    
                # 记录队列状态
                monitor.record_value("broker_queue_size", context["queue_size"])
                monitor.record_value("broker_active_handlers", context["active_handlers"])
                
                return result
                
            except Exception as e:
                monitor.log_error(operation, e, context=context)
                raise
                
        return wrapper
    return decorator

def monitor_router(operation: str):
    """
    监控消息路由的装饰器
    用于监控路由性能和状态
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            router = args[0]
            message = args[1] if len(args) > 1 else kwargs.get('message')
            context = {
                "router_id": id(router),
                "route_patterns": len(getattr(router, "routes", {})),
                "message_type": getattr(message, "type", None)
            }
            
            try:
                with monitor.measure_operation(operation, context=context):
                    result = await func(*args, **kwargs)
                    
                # 记录路由状态
                monitor.record_value("router_patterns", context["route_patterns"])
                
                return result
                
            except Exception as e:
                monitor.log_error(operation, e, context=context)
                raise
                
        return wrapper
    return decorator

def monitor_filter(operation: str):
    """
    监控消息过滤器的装饰器
    用于监控过滤器性能和状态
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            filter_obj = args[0]
            message = args[1] if len(args) > 1 else kwargs.get('message')
            context = {
                "filter_id": id(filter_obj),
                "filter_type": filter_obj.__class__.__name__,
                "message_type": getattr(message, "type", None)
            }
            
            try:
                with monitor.measure_operation(operation, context=context):
                    result = await func(*args, **kwargs)
                    
                # 记录过滤结果
                monitor.record_value(
                    f"filter_{context['filter_type']}_{'accepted' if result else 'rejected'}", 
                    1
                )
                
                return result
                
            except Exception as e:
                monitor.log_error(operation, e, context=context)
                raise
                
        return wrapper
    return decorator

def monitor_serializer(operation: str):
    """
    监控序列化器的装饰器
    用于监控序列化性能和状态
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            serializer = args[0]
            data = args[1] if len(args) > 1 else kwargs.get('data')
            context = {
                "serializer_id": id(serializer),
                "serializer_type": serializer.__class__.__name__,
                "data_size": len(str(data)) if data else 0
            }
            
            try:
                with monitor.measure_operation(operation, context=context):
                    result = await func(*args, **kwargs)
                    
                # 记录序列化状态
                monitor.record_value(
                    f"serializer_{operation}_size", 
                    len(str(result)) if result else 0
                )
                
                return result
                
            except Exception as e:
                monitor.log_error(operation, e, context=context)
                raise
                
        return wrapper 
    return decorator