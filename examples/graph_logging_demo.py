#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph日志演示脚本
展示Graph层的日志消息
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.multimodal_agent import run_multimodal_analysis, analyze_url, analyze_text
from src.graph.state import ContentType
from src.core.multimodal_agent import create_analysis_request

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def demo_graph_logging():
    """演示Graph日志功能"""
    print("🚀 Graph日志演示")
    print("=" * 50)
    
    # 示例1: 运行多模态分析
    print("\n📝 示例1: 多模态分析")
    print("-" * 30)
    result = run_multimodal_analysis()
    
    if result:
        print("✅ 多模态分析完成")
        print(f"📊 最终总结: {result.get('final_summary', '')[:100]}...")
    
    # 示例2: 分析单个URL
    print("\n📝 示例2: URL分析")
    print("-" * 30)
    url_result = analyze_url(
        "https://www.python.org/about/",
        "Python官网介绍页面"
    )
    
    if url_result:
        print("✅ URL分析完成")
    
    # 示例3: 分析文本
    print("\n📝 示例3: 文本分析")
    print("-" * 30)
    text_result = analyze_text(
        "人工智能技术正在快速发展，特别是大语言模型的出现，为各行各业带来了新的机遇和挑战。"
    )
    
    if text_result:
        print("✅ 文本分析完成")


if __name__ == "__main__":
    demo_graph_logging()