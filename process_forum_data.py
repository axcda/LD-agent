#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版论坛帖子数据处理脚本
专门处理你提供的JSON数据结构
"""

import json
import sys
import requests
from typing import Dict, Any, List


def process_forum_data(json_file_path: str):
    """
    处理论坛数据并发送到API进行分析
    
    Args:
        json_file_path: JSON文件路径
    """
    # 读取JSON数据
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取主题信息
    topic_title = data.get("topicTitle", "")
    posts = data.get("posts", [])
    
    print(f"📝 主题: {topic_title}")
    print(f"💬 回复数: {len(posts)}")
    print("="*50)
    
    # 创建整体分析内容
    overall_content = f"主题: {topic_title}\n\n论坛讨论内容:\n"
    
    for i, post in enumerate(posts, 1):
        username = post.get("username", "未知用户")
        content_text = post.get("content", {}).get("text", "")
        overall_content += f"{i}. {username}: {content_text}\n\n"
    
    # 发送到API进行分析
    api_url = "http://localhost:9980/analyze"
    
    # 整体分析
    print("🔍 正在进行整体分析...")
    overall_payload = {
        "content": overall_content,
        "content_type": "text",
        "context": f"论坛帖子分析: {topic_title}"
    }
    
    try:
        response = requests.post(api_url, json=overall_payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis = result["data"]["analysis"]
                print("✅ 整体分析完成")
                print(f"摘要: {analysis['summary'][:150]}...")
                print("关键点:")
                for point in analysis["key_points"][:3]:
                    print(f"  - {point}")
            else:
                print(f"❌ 分析失败: {result.get('error', {}).get('message')}")
        else:
            print(f"❌ API请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求出错: {str(e)}")
    
    # 选择性分析前几个重要帖子
    print("\n" + "="*50)
    print("🔍 正在进行重点帖子分析...")
    
    batch_payload = {
        "requests": []
    }
    
    # 添加主题概述
    topic_overview = f"主题: {topic_title}"
    batch_payload["requests"].append({
        "content": topic_overview,
        "content_type": "text",
        "context": "论坛主题概述"
    })
    
    # 添加前5个帖子（避免超过限制）
    for i, post in enumerate(posts[:5]):
        username = post.get("username", "未知用户")
        content_text = post.get("content", {}).get("text", "")
        post_content = f"用户 {username} 说: {content_text}"
        
        batch_payload["requests"].append({
            "content": post_content,
            "content_type": "text",
            "context": f"论坛回复 #{i+1}"
        })
    
    # 发送批量分析请求
    batch_api_url = "http://localhost:9980/analyze/batch"
    
    try:
        response = requests.post(batch_api_url, json=batch_payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis = result["data"]["analysis"]
                print("✅ 重点帖子分析完成")
                print(f"综合摘要: {analysis['summary'][:150]}...")
                print("关键点:")
                for point in analysis["key_points"][:3]:
                    print(f"  - {point}")
            else:
                print(f"❌ 批量分析失败: {result.get('error', {}).get('message')}")
        else:
            print(f"❌ 批量API请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 批量请求出错: {str(e)}")
    
    print("\n" + "="*50)
    print("🎉 分析完成!")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python process_forum_data.py <json文件路径>")
        print("示例: python process_forum_data.py sample_forum_data.json")
        return
    
    json_file_path = sys.argv[1]
    process_forum_data(json_file_path)


if __name__ == "__main__":
    main()