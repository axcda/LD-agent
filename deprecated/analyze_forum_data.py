#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛帖子数据分析脚本
适配你提供的JSON数据结构
"""

import json
import sys
from api_client_demo import MultiModalAnalysisClient
from typing import Dict, Any, List


def parse_forum_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析论坛数据并转换为分析请求格式
    
    Args:
        data: 论坛帖子的JSON数据
        
    Returns:
        包含主题和所有回复的文本内容
    """
    # 提取主题信息
    topic_info = {
        "url": data.get("url", ""),
        "title": data.get("topicTitle", ""),
        "timestamp": data.get("timestamp", ""),
        "total_posts": data.get("totalPosts", 0)
    }
    
    # 提取所有帖子内容
    posts_content = []
    for post in data.get("posts", []):
        post_info = {
            "post_id": post.get("postId", ""),
            "username": post.get("username", ""),
            "time": post.get("time", ""),
            "content": post.get("content", {}).get("text", ""),
            "images": post.get("content", {}).get("images", []),
            "links": post.get("content", {}).get("links", [])
        }
        posts_content.append(post_info)
    
    return {
        "topic_info": topic_info,
        "posts": posts_content
    }


def create_analysis_content(parsed_data: Dict[str, Any]) -> str:
    """
    创建用于分析的文本内容
    
    Args:
        parsed_data: 解析后的论坛数据
        
    Returns:
        格式化的文本内容
    """
    topic_info = parsed_data["topic_info"]
    posts = parsed_data["posts"]
    
    # 构建主题内容
    content = f"论坛主题: {topic_info['title']}\n"
    content += f"帖子链接: {topic_info['url']}\n"
    content += f"发布时间: {topic_info['timestamp']}\n"
    content += f"总回复数: {topic_info['total_posts']}\n"
    content += "\n" + "="*50 + "\n"
    content += "帖子内容:\n\n"
    
    # 添加每个回复
    for i, post in enumerate(posts, 1):
        content += f"{i}. 用户: {post['username']}\n"
        content += f"   时间: {post['time']}\n"
        content += f"   内容: {post['content']}\n"
        
        # 如果有图片链接，添加图片信息
        if post['images']:
            content += f"   图片: {len(post['images'])}张\n"
            
        # 如果有链接，添加链接信息
        if post['links']:
            content += f"   链接: {len(post['links'])}个\n"
            
        content += "\n"
    
    return content


def analyze_forum_topic(client: MultiModalAnalysisClient, forum_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析论坛主题
    
    Args:
        client: API客户端
        forum_data: 论坛数据
        
    Returns:
        分析结果
    """
    # 解析数据
    parsed_data = parse_forum_data(forum_data)
    
    # 创建分析内容
    analysis_content = create_analysis_content(parsed_data)
    
    # 执行分析
    result = client.analyze_content(
        content=analysis_content,
        content_type="text",
        context=f"论坛帖子分析: {parsed_data['topic_info']['title']}"
    )
    
    return result


def analyze_forum_posts_individually(client: MultiModalAnalysisClient, forum_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分别分析每个论坛帖子
    
    Args:
        client: API客户端
        forum_data: 论坛数据
        
    Returns:
        批量分析结果
    """
    parsed_data = parse_forum_data(forum_data)
    posts = parsed_data["posts"]
    
    # 创建批量分析请求（限制在10个以内）
    batch_requests = []
    
    # 添加主题分析
    topic_content = f"主题: {parsed_data['topic_info']['title']}\n链接: {parsed_data['topic_info']['url']}"
    batch_requests.append({
        "content": topic_content,
        "content_type": "text",
        "context": "论坛主题概述"
    })
    
    # 添加前几个重要回复的分析（限制数量以符合API要求）
    for i, post in enumerate(posts[:9]):  # 只分析前9个帖子，留一个位置给主题
        post_content = f"用户 {post['username']} 说: {post['content']}"
        batch_requests.append({
            "content": post_content,
            "content_type": "text",
            "context": f"论坛回复 #{i+1}"
        })
    
    # 执行批量分析
    result = client.analyze_batch(batch_requests)
    
    return result


def main():
    """主函数"""
    # 创建API客户端
    client = MultiModalAnalysisClient("http://localhost:9980")
    
    # 读取JSON数据
    try:
        # 如果提供了文件路径参数，从文件读取
        if len(sys.argv) > 1:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                forum_data = json.load(f)
        else:
            # 从标准输入读取
            print("请输入JSON数据 (或按Ctrl+D结束输入):")
            input_data = sys.stdin.read()
            forum_data = json.loads(input_data)
        
        print("🚀 开始分析论坛帖子数据...")
        print("="*60)
        
        # 方法1: 整体分析
        print("\n1. 整体分析论坛帖子...")
        overall_result = analyze_forum_topic(client, forum_data)
        
        if overall_result.get('success'):
            print("✅ 整体分析完成")
            analysis = overall_result['data']['analysis']
            print(f"综合摘要: {analysis['summary'][:200]}...")
            print("关键点:")
            for i, point in enumerate(analysis['key_points'][:5], 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ 整体分析失败: {overall_result.get('error', {}).get('message')}")
        
        # 方法2: 单独分析
        print("\n2. 单独分析各个帖子...")
        individual_result = analyze_forum_posts_individually(client, forum_data)
        
        if individual_result.get('success'):
            print("✅ 单独分析完成")
            analysis = individual_result['data']['analysis']
            print(f"综合摘要: {analysis['summary'][:200]}...")
            print("关键点:")
            for i, point in enumerate(analysis['key_points'][:5], 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ 单独分析失败: {individual_result.get('error', {}).get('message')}")
            
        print("\n" + "="*60)
        print("🎉 分析完成!")
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {sys.argv[1]}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")


if __name__ == "__main__":
    main()