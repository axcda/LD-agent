#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import json
import requests
import os


def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get("http://localhost:9980/health")
        if response.status_code == 200:
            print("✅ API服务器连接正常")
            return True
        else:
            print(f"❌ API服务器连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务器: {str(e)}")
        return False


def test_simple_analysis():
    """测试简单文本分析"""
    payload = {
        "content": "这是测试文本",
        "content_type": "text",
        "context": "测试"
    }
    
    try:
        response = requests.post("http://localhost:9980/analyze", json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 简单文本分析成功")
                return True
            else:
                print(f"❌ 分析失败: {result.get('error', {}).get('message')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 分析请求出错: {str(e)}")
        return False


def test_forum_data_loading():
    """测试论坛数据加载"""
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "examples", "sample_data", "sample_forum_data.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功加载论坛数据")
        print(f"  主题: {data.get('topicTitle', '')}")
        print(f"  回复数: {len(data.get('posts', []))}")
        return True
    except Exception as e:
        print(f"❌ 加载论坛数据失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("🚀 开始测试...")
    print("="*50)
    
    # 测试API连接
    if not test_api_connection():
        return
    
    # 测试简单分析
    if not test_simple_analysis():
        return
    
    # 测试数据加载
    if not test_forum_data_loading():
        return
    
    print("\n" + "="*50)
    print("🎉 所有测试通过!")


if __name__ == "__main__":
    main()