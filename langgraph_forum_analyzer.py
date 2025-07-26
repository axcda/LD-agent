#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
基于LangGraph的论坛分析器
使用优化的预处理和批量分析流程
"""

import json
import sys
from typing import Dict, Any
from graph.workflow import compile_multimodal_workflow
from graph.state import ContentType


def load_forum_data(file_path: str) -> Dict[str, Any]:
    """加载论坛数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_forum_with_langgraph(forum_json_data: Dict[str, Any]) -> Dict[str, Any]:
    """使用LangGraph分析论坛数据"""
    
    # 编译工作流
    workflow = compile_multimodal_workflow()
    
    # 准备初始状态
    initial_state = {
        "analysis_requests": [],  # 论坛分析主要通过forum_data处理
        "forum_data": forum_json_data,  # 直接传入论坛数据
        "analysis_results": [],
        "final_summary": None,
        "consolidated_key_points": [],
        "current_step": "ready",
        "messages": [],
        "metadata": {
            "workflow_type": "forum_analysis",
            "source": "langgraph_forum_analyzer"
        }
    }
    
    print("🚀 启动LangGraph论坛分析工作流...")
    print("="*60)
    
    try:
        # 执行工作流
        result = workflow.invoke(initial_state)
        
        print("\n" + "="*60)
        print("🎉 LangGraph工作流执行完成!")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 工作流执行失败: {str(e)}")
        return {"error": str(e), "success": False}


def print_workflow_results(result: Dict[str, Any]):
    """打印工作流结果"""
    if result.get("error"):
        print(f"❌ 分析失败: {result['error']}")
        return
    
    print("\n📋 工作流执行摘要:")
    print(f"  - 当前步骤: {result.get('current_step', 'unknown')}")
    print(f"  - 处理消息: {len(result.get('messages', []))}")
    print(f"  - 分析结果: {len(result.get('analysis_results', []))}")
    
    # 显示论坛分析特定信息
    analysis_results = result.get("analysis_results", [])
    forum_results = [r for r in analysis_results if r.get("content_type") == ContentType.FORUM]
    
    if forum_results:
        forum_result = forum_results[0]
        metadata = forum_result.get("metadata", {})
        print(f"\n📊 论坛分析统计:")
        print(f"  - 总帖子数: {metadata.get('total_posts', 0)}")
        print(f"  - 参与用户: {metadata.get('users_count', 0)}人")
        print(f"  - 外部链接: {metadata.get('links_count', 0)}个")
        print(f"  - 图片内容: {metadata.get('images_count', 0)}张")
        print(f"  - 分析置信度: {forum_result.get('confidence', 0):.2f}")
        
        # 显示媒体分析结果
        media_results = [r for r in analysis_results if r.get("content_type") in [ContentType.URL, ContentType.IMAGE]]
        if media_results:
            print(f"  - 媒体内容分析: {len(media_results)}项")
    
    # 如果有最终报告，显示它
    if result.get("final_report"):
        print("\n" + result["final_report"])


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python langgraph_forum_analyzer.py <json文件路径>")
        print("示例: python langgraph_forum_analyzer.py sample_forum_data.json")
        return
    
    file_path = sys.argv[1]
    
    try:
        # 加载论坛数据
        print(f"📂 加载论坛数据: {file_path}")
        forum_data = load_forum_data(file_path)
        print(f"✅ 数据加载成功: {forum_data.get('topicTitle', '')}")
        
        # 使用LangGraph分析
        result = analyze_forum_with_langgraph(forum_data)
        
        # 显示结果
        print_workflow_results(result)
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")


if __name__ == "__main__":
    main()