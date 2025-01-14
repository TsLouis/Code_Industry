"""
Developer agent implementation
"""

from typing import Dict, Optional, Any, List
from ..base import BaseAgent, AgentConfig, AgentResponse, Message, AgentRole
from ..utils.llm import LLMTool
from pypinyin import lazy_pinyin
from src.core.monitoring.agent_monitor import monitor_agent_action, monitor_conversation
from datetime import datetime


class DeveloperAgent(BaseAgent):
    """
    Developer agent that implements technical solutions.
    Responsible for:
    - Code analysis and implementation
    - Testing and debugging
    - Code review and optimization
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # 初始化LLM工具
        self.llm_tool = LLMTool(config.llm_config["adapter"])

    @monitor_agent_action("process")
    @monitor_conversation()
    async def process(self, message: str) -> AgentResponse:
        """处理开发任务"""
        if not message:
            raise ValueError("Message cannot be empty")
            
        # 分析代码需求
        analysis = await self._analyze_code(message)
        
        # 实现解决方案
        implementation = await self._implement_solution(analysis)
        
        # 生成测试代码
        tests = await self._test_implementation(implementation)
        
        # 代码审查
        review = await self._review_code(implementation)
        
        # 保存生成的代码
        output_dir = await self._save_generated_code(implementation, tests)
        
        return AgentResponse(
            response=f"代码已生成并保存到 {output_dir}",
            metadata={
                "analysis": analysis,
                "implementation": implementation,
                "tests": tests,
                "review": review,
                "output_dir": output_dir
            }
        )
        
    async def _save_generated_code(self, implementation: str, tests: str) -> str:
        """保存生成的代码"""
        from pathlib import Path
        import os
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output/generated_code") / f"snake_game_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存主要实现
        main_file = output_dir / "snake_game.py"
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(implementation)
            
        # 保存测试代码
        test_file = output_dir / "test_snake_game.py"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(tests)
            
        # 生成requirements.txt
        requirements = self._extract_requirements(implementation)
        req_file = output_dir / "requirements.txt"
        with open(req_file, "w", encoding="utf-8") as f:
            f.write(requirements)
            
        # 生成README.md
        readme = f"""# 贪吃蛇游戏

## 简介
这是一个使用Python和Pygame实现的贪吃蛇游戏。

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行游戏
```bash
python snake_game.py
```

## 游戏控制
- 方向键控制蛇的移动
- ESC键退出游戏
"""
        readme_file = output_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme)
            
        return str(output_dir)

    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Create a development plan"""
        if not task:
            raise ValueError("Task cannot be empty")

        try:
            # 分析代码
            code_analysis = await self._analyze_code(task)
            # 实现解决方案
            implementation = await self._implement_solution(code_analysis)
            # 测试实现
            test_results = await self._test_implementation(implementation)

            return AgentResponse(
                response="Development plan created",
                metadata={
                    "code_analysis": code_analysis,
                    "implementation": implementation,
                    "test_results": test_results
                }
            )
        except Exception as e:
            return AgentResponse(
                response="Error occurred during planning",
                error=str(e)
            )

    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute the development plan"""
        if not plan:
            raise ValueError("Plan cannot be empty")

        try:
            # 代码审查
            review = await self._review_code({"plan": plan})

            return AgentResponse(
                response="Development started",
                metadata={
                    "review": review,
                    "status": "in_progress"
                }
            )
        except Exception as e:
            return AgentResponse(
                response="Error occurred during execution",
                error=str(e)
            )

    @monitor_agent_action("analyze_code")
    async def _analyze_code(self, task: str) -> Dict[str, Any]:
        """分析任务并创建代码分析"""
        prompt = f"""
        作为一个Python游戏开发专家，请分析以下游戏开发任务并提供详细的技术方案：
        任务：{task}
        
        请提供：
        1. 游戏核心功能
        2. 游戏机制
        3. 用户界面
        4. 控制方式
        5. 游戏逻辑
        6. 性能考虑
        
        以JSON格式返回分析结果。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("implement_solution")
    async def _implement_solution(self, analysis: Dict[str, Any]) -> str:
        """基于分析实现游戏代码"""
        prompt = f"""
        基于以下技术分析，请实现一个完整的Python游戏：
        
        技术分析：{analysis}
        
        要求：
        1. 代码完整可运行
        2. 包含必要的注释
        3. 遵循PEP 8规范
        4. 包含错误处理
        5. 包含所有必要的import语句
        6. 使用Pygame库实现图形界面
        7. 包含游戏主循环
        8. 实现用户输入处理
        9. 实现游戏状态管理
        10. 添加基本的音效和图形效果
        
        请直接返回代码，不需要其他解释。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("test_implementation")
    async def _test_implementation(self, implementation: str) -> str:
        """生成游戏测试代码"""
        prompt = f"""
        为以下游戏代码实现编写完整的单元测试：
        
        {implementation}
        
        要求：
        1. 使用pytest框架
        2. 测试游戏核心逻辑
        3. 测试碰撞检测
        4. 测试游戏状态
        5. 测试用户输入
        6. 包含边界条件测试
        7. 包含异常测试
        
        请直接返回测试代码，不需要其他解释。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("review_code")
    async def _review_code(self, implementation: str) -> Dict[str, Any]:
        """代码审查"""
        prompt = f"""
        请对以下代码进行全面的代码审查：
        
        {implementation}
        
        关注点：
        1. 代码质量
        2. 性能优化
        3. 安全性
        4. 可维护性
        5. 最佳实践
        
        以JSON格式返回审查结果。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    def _integrate_code(self, implementation: str, tests: str) -> str:
        """整合实现代码和测试代码"""
        return f"""
# 主要实现
{implementation}

# 单元测试
{tests}
""" 

    def _extract_requirements(self, code: str) -> str:
        """从代码中提取依赖项"""
        requirements = set()
        import_lines = [line for line in code.split("\n") if line.startswith("import ") or line.startswith("from ")]
        
        for line in import_lines:
            package = line.split()[1].split(".")[0]
            if package not in ("os", "sys", "typing", "pathlib", "unittest", "pytest"):
                requirements.add(f"{package}")
                if package == "pygame":
                    requirements.add("pygame==2.5.2")  # 使用稳定版本
                    
        return "\n".join(sorted(requirements)) 

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符，将中文转换为英文名称"""
        name_map = {
            "贪吃蛇": "snake",
            "坦克大战": "tank",
            "俄罗斯方块": "tetris",
            "飞机大战": "plane",
            "五子棋": "gomoku"
        }
        
        # 检查是否有预定义的英文名称
        for cn, en in name_map.items():
            if cn in filename:
                return en
                
        # 如果没有预定义名称，则使用拼音
        from pypinyin import lazy_pinyin
        pinyin_list = lazy_pinyin(filename)
        pinyin_name = "".join(pinyin_list)
        
        # 清理其他非法字符
        return "".join(c for c in pinyin_name if c.isalnum() or c in (' ', '-', '_')).strip()

    def _create_readme(self, task_name: str, code: str) -> str:
        """创建README文件"""
        return f"""# {task_name}

## 项目说明
这是由AI助手生成的代码实现。

## 目录结构
- main.py: 主要实现代码
- test_main.py: 单元测试代码
- requirements.txt: 项目依赖

## 如何运行
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行主程序：
```bash
python main.py
```

3. 运行测试：
```bash
pytest test_main.py
```
""" 