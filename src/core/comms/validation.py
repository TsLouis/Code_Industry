"""
Message validation implementation
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .types import Message, Error, ErrorSeverity


class ValidationError(Exception):
    """验证错误"""
    
    def __init__(self, message: str, errors: List[Error]):
        super().__init__(message)
        self.errors = errors


class MessageValidator(ABC):
    """消息验证器接口"""
    
    @abstractmethod
    def validate(self, message: Message) -> List[Error]:
        """验证消息
        
        Args:
            message: 要验证的消息
            
        Returns:
            List[Error]: 错误列表，空列表表示验证通过
        """
        pass


class BasicValidator(MessageValidator):
    """基本验证器"""
    
    def validate(self, message: Message) -> List[Error]:
        errors = []
        
        # 验证必填字段
        if not message.id:
            errors.append(Error(
                code="MISSING_ID",
                message="Message ID is required",
                severity=ErrorSeverity.ERROR
            ))
            
        if not message.type:
            errors.append(Error(
                code="MISSING_TYPE",
                message="Message type is required",
                severity=ErrorSeverity.ERROR
            ))
            
        if not message.sender:
            errors.append(Error(
                code="MISSING_SENDER",
                message="Message sender is required",
                severity=ErrorSeverity.ERROR
            ))
            
        if not message.receiver:
            errors.append(Error(
                code="MISSING_RECEIVER",
                message="Message receiver is required",
                severity=ErrorSeverity.ERROR
            ))
            
        # 验证时间戳
        if not message.timestamp:
            errors.append(Error(
                code="MISSING_TIMESTAMP",
                message="Message timestamp is required",
                severity=ErrorSeverity.ERROR
            ))
        elif message.timestamp > datetime.utcnow():
            errors.append(Error(
                code="FUTURE_TIMESTAMP",
                message="Message timestamp cannot be in the future",
                severity=ErrorSeverity.ERROR
            ))
            
        # 验证超时时间
        if message.timeout <= 0:
            errors.append(Error(
                code="INVALID_TIMEOUT",
                message="Message timeout must be positive",
                severity=ErrorSeverity.ERROR
            ))
            
        return errors


class ContentValidator(MessageValidator):
    """内容验证器"""
    
    def __init__(self, required_fields: Optional[Dict[str, type]] = None):
        self.required_fields = required_fields or {}
    
    def validate(self, message: Message) -> List[Error]:
        errors = []
        
        # 验证内容是否存在
        if not message.content:
            if self.required_fields:
                errors.append(Error(
                    code="MISSING_CONTENT",
                    message="Message content is required",
                    severity=ErrorSeverity.ERROR
                ))
            return errors
            
        # 验证必填字段
        for field, field_type in self.required_fields.items():
            if field not in message.content:
                errors.append(Error(
                    code="MISSING_FIELD",
                    message=f"Required field '{field}' is missing in content",
                    severity=ErrorSeverity.ERROR
                ))
            elif not isinstance(message.content[field], field_type):
                errors.append(Error(
                    code="INVALID_FIELD_TYPE",
                    message=f"Field '{field}' must be of type {field_type.__name__}",
                    severity=ErrorSeverity.ERROR
                ))
                
        return errors


class CompositeValidator(MessageValidator):
    """组合验证器"""
    
    def __init__(self, validators: List[MessageValidator]):
        self.validators = validators
    
    def validate(self, message: Message) -> List[Error]:
        errors = []
        
        for validator in self.validators:
            errors.extend(validator.validate(message))
            
        return errors


class ValidationChain:
    """验证链"""
    
    def __init__(self, validators: List[MessageValidator]):
        self.validators = validators
    
    def validate(self, message: Message) -> None:
        """验证消息
        
        Args:
            message: 要验证的消息
            
        Raises:
            ValidationError: 验证失败
        """
        errors = []
        
        for validator in self.validators:
            errors.extend(validator.validate(message))
            
        if errors:
            raise ValidationError(
                f"Message validation failed with {len(errors)} errors",
                errors
            ) 