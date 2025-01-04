from pathlib import Path
from typing import Dict, Tuple, List
from .comms.message import MessageType

class TaskProcessor:
    @staticmethod
    async def process_developer_response(implementation: str, version_dir: Path) -> Tuple[bool, Dict[str, bool]]:
        """处理开发者的响应，保存文件并检查完整性"""
        current_file = None
        current_content = []
        has_files = False
        required_files = {
            'app.py': False,
            'models.py': False,
            'static/js/main.js': False,
            'static/css/style.css': False,
            'templates/index.html': False,
            'requirements.txt': False
        }
        
        # 解析并保存代码文件
        for line in implementation.split('\n'):
            if line.startswith('```'):
                if current_file and current_content:
                    # 保存当前文件
                    current_file.parent.mkdir(parents=True, exist_ok=True)
                    file_content = '\n'.join(current_content)
                    current_file.write_text(file_content, encoding='utf-8')
                    has_files = True
                    
                    # 检查文件是否为空或只包含注释
                    is_empty = all(l.strip().startswith('//') or l.strip().startswith('/*') or not l.strip() 
                                 for l in current_content)
                    if not is_empty:
                        file_path = str(current_file.relative_to(version_dir))
                        if file_path in required_files:
                            required_files[file_path] = True
                
                if ':' in line:
                    # 开始新文件
                    file_path = line.split(':', 1)[1].strip()
                    current_file = version_dir / file_path
                    current_content = []
                else:
                    current_file = None
                    current_content = []
            elif current_file and not line.startswith('```'):
                current_content.append(line)
        
        # 保存最后一个文件
        if current_file and current_content:
            current_file.parent.mkdir(parents=True, exist_ok=True)
            file_content = '\n'.join(current_content)
            current_file.write_text(file_content, encoding='utf-8')
            has_files = True
            
            is_empty = all(l.strip().startswith('//') or l.strip().startswith('/*') or not l.strip() 
                          for l in current_content)
            if not is_empty:
                file_path = str(current_file.relative_to(version_dir))
                if file_path in required_files:
                    required_files[file_path] = True
        
        return has_files, required_files

    @staticmethod
    def get_missing_files(required_files: Dict[str, bool]) -> List[str]:
        """获取未实现的文件列表"""
        return [f for f, implemented in required_files.items() if not implemented]

    @staticmethod
    def get_initial_task() -> str:
        """获取初始任务描述"""
        return """请实现一个基于Flask和SQLite的待办事项应用，要求：

技术要求：
1. 后端使用Flask框架
2. 数据库使用SQLite
3. 前端使用HTML + JavaScript
4. 所有代码必须分文件保存，不要都写在一个文件里

功能要求：
1. 实现待办事项的创建、编辑、删除功能
2. 支持待办事项状态管理（未完成、已完成）
3. 实现美观的用户界面
4. 良好的交互体验

请提供以下文件的完整实现：
1. app.py: Flask应用主文件
2. models.py: 数据库模型定义
3. static/js/main.js: 前端JavaScript代码（实现与后端API的交互）
4. static/css/style.css: 样式文件（提供美观的界面）
5. templates/index.html: 主页面模板
6. requirements.txt: 项目依赖

每个文件都必须使用 ```python:文件路径 或 ```html:文件路径 等格式标注。
代码必须完整可运行，包含所有必要的导入语句和配置。""" 