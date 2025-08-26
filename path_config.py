"""
模块路径配置文件
遵循"模块路径配置最佳实践"规范
通过统一的配置文件管理多路径导入
"""

import os
import sys

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 定义需要添加到Python路径的目录列表
PATHS_TO_ADD = [
    PROJECT_ROOT,  # 项目根目录
    os.path.join(PROJECT_ROOT, 'Data_Analysis'),  # Data_Analysis包目录
]

def setup_python_path():
    """
    设置Python模块搜索路径
    支持IDE跳转和代码提示
    """
    # 一次性添加所有路径
    for path in PATHS_TO_ADD:
        if path not in sys.path:
            sys.path.insert(0, path)
            print(f"✅ 已添加路径到Python path: {path}")

def get_project_root():
    """获取项目根目录"""
    return PROJECT_ROOT

def get_data_analysis_path():
    """获取Data_Analysis包的路径"""
    return os.path.join(PROJECT_ROOT, 'Data_Analysis')

if __name__ == "__main__":
    print("🔧 Python路径配置")
    print("=" * 40)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"要添加的路径:")
    for i, path in enumerate(PATHS_TO_ADD, 1):
        print(f"  {i}. {path}")
    
    setup_python_path()
    print("\n✅ 路径配置完成")