#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.multimodal_agent import (
    run_multimodal_analysis, 
    analyze_url, 
    analyze_image, 
    analyze_code, 
    analyze_text
)


def demo_basic_workflow():
    """演示基本工作流"""
    print("🎯 运行基本多模态分析演示")
    return run_multimodal_analysis()


def demo_url_analysis():
    """演示URL分析"""
    print("🔗 URL分析示例")
    url = "https://github.com/langchain-ai/langgraph"
    result = analyze_url(url, "LangGraph项目页面")
    return result


def demo_code_analysis():
    """演示代码分析"""
    print("💻 代码分析示例")
    code = """
class MultiModalAgent:
    def __init__(self, config):
        self.config = config
        self.analyzers = {
            'url': URLAnalyzer(),
            'image': ImageAnalyzer(), 
            'code': CodeAnalyzer()
        }
    
    def analyze(self, content, content_type):
        analyzer = self.analyzers.get(content_type)
        return analyzer.analyze(content)
    """
    result = analyze_code(code, "Python")
    return result


def demo_text_analysis():
    """演示文本分析"""
    print("📝 文本分析示例")
    text = """
    LangGraph是一个用于构建多代理和多步应用的框架，基于LangChain构建。
    它提供了状态图的概念，允许开发者定义复杂的工作流程，包括循环、条件分支等。
    主要特点包括：状态持久化、错误恢复、人工干预、流式处理等。
    """
    result = analyze_text(text, "LangGraph技术介绍")
    return result


def main():
    """主函数"""
    print("🤖 多模态内容分析示例")
    print("=" * 50)
    
    # 运行基本演示
    demo_basic_workflow()
    
    print("\n" + "=" * 50)
    print("✅ 示例运行完成")


if __name__ == "__main__":
    main()