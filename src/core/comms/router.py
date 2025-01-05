"""
消息路由器模块
"""

from typing import Any, Dict, List, Optional, Pattern
import re
from .types import Message
from ..monitoring.decorators import monitor_router, trace_message

class Router:
    """消息路由器"""
    
    @monitor_router("router_init")
    def __init__(self):
        self.routes: Dict[Pattern, Any] = {}
        
    @monitor_router("router_register")
    def register_route(self, pattern: str, handler: Any) -> None:
        """注册路由规则"""
        self.routes[re.compile(pattern)] = handler
        
    @monitor_router("router_remove")
    def remove_route(self, pattern: str) -> bool:
        """移除路由规则"""
        pattern_obj = re.compile(pattern)
        if pattern_obj in self.routes:
            del self.routes[pattern_obj]
            return True
        return False
        
    @monitor_router("router_route")
    @trace_message("message_route")
    async def route(self, message: Message) -> List[Any]:
        """路由消息到匹配的处理器"""
        handlers = []
        for pattern, handler in self.routes.items():
            if pattern.match(message.type):
                handlers.append(handler)
        return handlers
        
    @monitor_router("router_find_handler")
    async def find_handler(self, message_type: str) -> Optional[Any]:
        """查找消息类型对应的处理器"""
        for pattern, handler in self.routes.items():
            if pattern.match(message_type):
                return handler
        return None 