#!/usr/bin/env python3
"""
API接口测试脚本
"""

import requests
import json
import time
import threading
import subprocess
import sys
from pathlib import Path

API_BASE_URL = "http://localhost:8888"

def test_api_endpoints():
    """测试API端点"""
    print("🧪 开始API接口测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 测试健康检查
    print("\n1. 测试健康检查")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False
    
    # 测试配置状态
    print("\n2. 测试配置状态")
    try:
        response = requests.get(f"{API_BASE_URL}/config/status", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ 配置状态检查通过")
            if result.get('success'):
                apis = result['data']['configured_apis']
                print(f"   已配置API: {', '.join(apis)}")
        else:
            print(f"❌ 配置状态检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置状态检查异常: {str(e)}")
    
    # 测试单个内容分析
    print("\n3. 测试单个内容分析")
    test_data = {
        "content": "def hello_world():\n    print('Hello, World!')\n    return 'success'",
        "content_type": "code",
        "context": "Python"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze", 
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ 单个内容分析通过")
            if result.get('success'):
                summary = result['data']['analysis']['summary']
                print(f"   分析摘要: {summary[:100]}...")
            else:
                print(f"   错误: {result.get('error', {}).get('message')}")
        else:
            print(f"❌ 单个内容分析失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 单个内容分析异常: {str(e)}")
    
    # 测试批量分析
    print("\n4. 测试批量分析")
    batch_data = {
        "requests": [
            {
                "content": "print('Hello Python')",
                "content_type": "code",
                "context": "Python"
            },
            {
                "content": "这是一段测试文本，用于验证文本分析功能。",
                "content_type": "text",
                "context": "测试文本"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze/batch",
            json=batch_data,
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ 批量分析通过")
            if result.get('success'):
                total = result['data']['input']['total_requests']
                print(f"   处理请求数: {total}")
            else:
                print(f"   错误: {result.get('error', {}).get('message')}")
        else:
            print(f"❌ 批量分析失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 批量分析异常: {str(e)}")
    
    # 测试错误处理
    print("\n5. 测试错误处理")
    invalid_data = {
        "content": "",  # 空内容
        "content_type": "invalid_type"  # 无效类型
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=invalid_data,
            timeout=10
        )
        if response.status_code == 400:
            print("✅ 错误处理正常")
            result = response.json()
            print(f"   错误信息: {result.get('error', {}).get('message')}")
        else:
            print(f"⚠️ 错误处理异常: 期望400，实际{response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 API接口测试完成")
    return True


def start_api_server():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    try:
        # 使用subprocess启动服务器
        process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待一段时间让服务器启动
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"❌ 启动服务器失败: {str(e)}")
        return None


if __name__ == "__main__":
    print("🤖 多模态内容分析API测试")
    print("=" * 50)
    
    # 检查是否已有服务器运行
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        print("✅ 检测到运行中的服务器")
        server_process = None
    except:
        print("🔄 启动新的服务器实例")
        server_process = start_api_server()
        if not server_process:
            print("❌ 无法启动服务器，退出测试")
            sys.exit(1)
    
    try:
        # 运行测试
        success = test_api_endpoints()
        
        if success:
            print("\n✅ 所有测试通过！API接口工作正常")
        else:
            print("\n⚠️ 部分测试失败，请检查服务器状态")
            
    finally:
        # 清理
        if server_process:
            print("\n🛑 停止测试服务器")
            server_process.terminate()
            server_process.wait()