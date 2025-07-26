#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自定义OpenAI URL配置的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import config


def test_custom_openai_url():
    """测试自定义OpenAI URL配置"""
    print("🧪 测试自定义OpenAI URL配置")
    print("=" * 50)
    
    print(f"✅ OpenAI API密钥配置: {'已配置' if config.openai_api_key else '未配置'}")
    print(f"🌐 OpenAI基础URL: {config.openai_base_url}")
    
    # 测试获取OpenAI客户端
    try:
        client = config.get_openai_client()
        print(f"✅ OpenAI客户端创建成功")
        print(f"🌐 客户端基础URL: {client.base_url}")
    except Exception as e:
        print(f"❌ OpenAI客户端创建失败: {e}")
        return
    
    # 如果配置了自定义URL，检查是否与默认不同
    if config.openai_base_url != "https://api.openai.com/v1":
        print(f"🔄 使用自定义OpenAI URL: {config.openai_base_url}")
    else:
        print(f"🔄 使用默认OpenAI URL")


if __name__ == "__main__":
    test_custom_openai_url()