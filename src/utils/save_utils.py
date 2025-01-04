import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def save_conversation(conversation_id: str, messages: List[Dict[str, Any]]) -> None:
    """保存对话记录到文件"""
    # 创建保存目录
    save_dir = Path("data/conversations")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    filename = save_dir / f"{datetime.now().strftime('%Y%m%d')}_{conversation_id}.json"
    
    # 保存对话记录
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2) 