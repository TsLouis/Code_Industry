"""
系统配置文件
"""

import os
from typing import Dict, Any

# OpenAI配置
OPENAI_API_KEY = "sk-WGQLphVmPxKMhgPu8L6ewi0jdV6D78ht1nBm2MJRQg7Tu6wg"  # API密钥
OPENAI_BASE_URL = "https://api.openai-proxy.org/v1"  # API基础URL

# LLM配置
LLM_CONFIG = {
    "model": "gpt-3.5-turbo",  # 默认模型
    "temperature": 0.7,        # 温度参数
    "max_tokens": 2000,        # 最大token数
    "timeout": 60,            # 超时时间(秒)
    "base_url": OPENAI_BASE_URL  # API基础URL
}

# Agent配置
AGENT_CONFIG = {
    "coordinator": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 1000
    },
    "product_manager": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1500
    },
    "developer": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 2000
    }
}

# 系统配置
SYSTEM_CONFIG = {
    "max_concurrent_tasks": 5,  # 最大并发任务数
    "task_timeout": 300,       # 任务超时时间(秒)
    "retry_attempts": 3,       # 重试次数
    "retry_delay": 1.0,        # 重试延迟(秒)
}

def get_openai_api_key() -> str:
    """获取OpenAI API密钥"""
    return OPENAI_API_KEY

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """获取指定Agent的配置"""
    if agent_type not in AGENT_CONFIG:
        raise ValueError(f"未知的Agent类型: {agent_type}")
    return AGENT_CONFIG[agent_type] 