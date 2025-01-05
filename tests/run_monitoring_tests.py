"""
监控系统测试运行脚本
"""

import pytest
import asyncio
import json
from datetime import datetime
from pathlib import Path

def format_test_results(result):
    """格式化测试结果"""
    return {
        "total": result.total,
        "passed": result.passed,
        "failed": result.failed,
        "skipped": result.skipped,
        "error": result.error,
        "duration": result.duration
    }

def save_test_results(results, output_file):
    """保存测试结果到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    """运行所有监控系统测试"""
    # 创建结果目录
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    # 运行测试
    test_files = [
        "core/monitoring/test_monitoring.py",
        "core/monitoring/test_agent_monitoring.py"
    ]
    
    results = {}
    for test_file in test_files:
        print(f"\n运行测试: {test_file}")
        result = pytest.main([
            f"tests/{test_file}",
            "-v",
            "--asyncio-mode=auto"
        ])
        
        results[test_file] = {
            "status": "passed" if result == 0 else "failed",
            "timestamp": datetime.now().isoformat()
        }
    
    # 保存结果
    output_file = results_dir / f"monitoring_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_test_results(results, output_file)
    
    print(f"\n测试结果已保存到: {output_file}")

if __name__ == "__main__":
    main() 