#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云DashScope API客户端
提供对DashScope API的访问接口，包括天气查询和联网搜索功能
"""

import requests
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


class DashScopeClient:
    """阿里云DashScope API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化DashScope客户端
        
        Args:
            api_key: DashScope API密钥，如果未提供则从环境变量DASHSCOPE_API_KEY获取
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DashScope API密钥未配置，请设置DASHSCOPE_API_KEY环境变量")
        
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def chat_completion(self, model: str, messages: list, 
                       enable_search: bool = False, 
                       search_options: Optional[Dict[str, Any]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        聊天完成接口
        
        Args:
            model: 模型名称
            messages: 消息列表
            enable_search: 是否启用搜索
            search_options: 搜索选项
            **kwargs: 其他参数
            
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        if enable_search:
            data["enable_search"] = True
            if search_options:
                data["search_options"] = search_options
        
        try:
            logger.debug(f"🔗 请求端点: {url}")
            logger.debug(f"📋 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            response = self.session.post(
                url,
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"✅ 响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_message = f"DashScope API请求失败: {str(e)}"
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message += f"\n响应内容: {json.dumps(error_details, indent=2, ensure_ascii=False)}"
                except json.JSONDecodeError:
                    error_message += f"\n响应内容 (非JSON): {e.response.text}"
            logger.error(error_message)
            raise Exception(error_message)
    
    def get_weather(self, location: str, date: str = "tomorrow") -> str:
        """
        获取天气信息
        
        Args:
            location: 地点
            date: 日期（默认为"tomorrow"表示明天）
            
        Returns:
            天气信息
        """
        prompt = f"请提供{date}{location}的天气信息"
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self.chat_completion(
                model="Moonshot-Kimi-K2-Instruct",
                messages=messages,
                enable_search=True,
                search_options={
                    "forced_search": True
                }
            )
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                return "无法获取天气信息"
                
        except Exception as e:
            logger.error(f"获取天气信息失败: {str(e)}")
            return f"获取天气信息失败: {str(e)}"
    
    def search_and_summarize(self, query: str) -> Dict[str, Any]:
        """
        联网搜索并总结
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果和总结
        """
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        try:
            response = self.chat_completion(
                model="Moonshot-Kimi-K2-Instruct",
                messages=messages,
                enable_search=True,
                search_options={
                    "forced_search": True
                }
            )
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "query": query,
                    "result": content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": "无法获取搜索结果",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"联网搜索失败: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": f"联网搜索失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


def demo_usage():
    """演示DashScope客户端使用方法"""
    try:
        # 创建客户端实例
        client = DashScopeClient()
        
        print("🤖 阿里云DashScope API客户端演示")
        print("=" * 50)
        
        # 1. 天气查询示例
        print("1. 天气查询示例")
        weather_info = client.get_weather("杭州")
        print(f"明天杭州的天气: {weather_info}")
        
        print("\n" + "-" * 30)
        
        # 2. 联网搜索示例
        print("2. 联网搜索示例")
        search_result = client.search_and_summarize("人工智能的最新发展")
        if search_result["success"]:
            print(f"搜索查询: {search_result['query']}")
            print(f"搜索结果: {search_result['result'][:200]}...")
        else:
            print(f"搜索失败: {search_result['error']}")
        
        print("\n" + "=" * 50)
        print("✅ 演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")


if __name__ == "__main__":
    demo_usage()