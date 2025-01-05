"""
日志模块
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

class JsonFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 基础日志数据
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # 添加上下文数据
        if hasattr(record, "context"):
            # 处理上下文中的 datetime 对象
            context = record.context.copy()
            for key, value in context.items():
                if isinstance(value, datetime):
                    context[key] = value.isoformat()
            log_data["context"] = context
            
        # 添加异常信息
        if record.exc_info:
            log_data["extra"] = {"exc_info": True}
            
        return json.dumps(log_data)
        
    def formatTime(self, record: logging.LogRecord) -> str:
        """格式化时间戳"""
        dt = datetime.fromtimestamp(record.created)
        return dt.isoformat()

class JsonLogger:
    """JSON日志记录器"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)
        
        # 创建文件处理器
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"{name}.log"),
            encoding="utf-8"
        )
        file_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(file_handler)
        
    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录日志"""
        extra = {"context": context or {}}
        self.logger.log(level, message, extra=extra)
        
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录调试日志"""
        self._log(logging.DEBUG, message, context, **kwargs)
        
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录信息日志"""
        self._log(logging.INFO, message, context, **kwargs)
        
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录警告日志"""
        self._log(logging.WARNING, message, context, **kwargs)
        
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录错误日志"""
        self._log(logging.ERROR, message, context, **kwargs)
        
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """记录严重错误日志"""
        self._log(logging.CRITICAL, message, context, **kwargs) 