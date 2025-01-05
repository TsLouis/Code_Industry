"""
运行引擎模块测试的脚本
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # 设置pytest的asyncio模式
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "True"
    os.environ["PYTEST_ADDOPTS"] = "--asyncio-mode=strict"
    
    # 运行engine模块的测试
    pytest.main([
        "tests/core/engine/test_engine.py",
        "-v",
        "--capture=no",
        "--tb=short"
    ]) 