"""
Message protocol implementation
"""
from typing import Optional, Callable, Awaitable
import asyncio
from datetime import datetime

from .types import Message, MessageStatus, RetryStrategy

class ProtocolError(Exception):
    """协议错误基类"""
    pass

class RetryableError(ProtocolError):
    """可重试的错误"""
    pass

class MaxRetriesExceededError(ProtocolError):
    """超过最大重试次数"""
    pass

class TimeoutError(ProtocolError):
    """消息处理超时"""
    pass

class MessageHandler:
    """消息处理器基类"""
    async def handle(self, message: Message) -> Optional[Message]:
        """处理消息
        
        Args:
            message: 要处理的消息
            
        Returns:
            Optional[Message]: 处理结果消息，如果没有则返回None
            
        Raises:
            RetryableError: 可重试的错误
            ProtocolError: 其他协议错误
        """
        raise NotImplementedError

class Protocol:
    """消息协议基类"""
    def __init__(self, retry_strategy: Optional[RetryStrategy] = None):
        self.retry_strategy = retry_strategy or RetryStrategy()
        
    async def execute(self, 
                     handler: Callable[[], Awaitable[Optional[Message]]], 
                     timeout: Optional[float] = None) -> Optional[Message]:
        """执行消息处理
        
        Args:
            handler: 消息处理函数
            timeout: 超时时间(秒)
            
        Returns:
            Optional[Message]: 处理结果消息
            
        Raises:
            TimeoutError: 处理超时
            MaxRetriesExceededError: 超过最大重试次数
            ProtocolError: 其他协议错误
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= self.retry_strategy.max_retries:
            try:
                if timeout:
                    return await asyncio.wait_for(handler(), timeout)
                return await handler()
                
            except asyncio.TimeoutError:
                raise TimeoutError("Message handling timed out")
                
            except RetryableError as e:
                last_error = e
                retry_count += 1
                if retry_count > self.retry_strategy.max_retries:
                    break
                    
                delay = self.retry_strategy.get_delay(retry_count)
                await asyncio.sleep(delay)
                continue
                
            except Exception as e:
                raise ProtocolError(f"Unexpected error: {str(e)}")
                
        raise MaxRetriesExceededError(
            f"Max retries exceeded ({self.retry_strategy.max_retries}), "
            f"last error: {str(last_error)}"
        ) 