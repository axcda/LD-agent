#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据处理示例
展示如何在代码中使用论坛数据适配器处理用户提供的JSON数据
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.forum_data_adapter import (
    ForumDataAdapter,
    convert_user_forum_data,
    load_forum_data_from_json
)
from src.analyzers.forum_analyzer import ForumAnalyzer


def main():
    """主函数"""
    print("🎯 用户数据处理示例")
    print("=" * 50)
    
    # 用户提供的JSON数据（可以来自文件、API等）
    user_data = {
        "url": "https://linux.do/t/topic/802519",
        "timestamp": "2025-07-22T14:14:27.271Z",
        "topicTitle": "大门敞开！上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过",
        "replyInfo": "",
        "totalPosts": 5,  # 简化为5个帖子用于示例
        "posts": [
            {
                "postId": "post_1",
                "username": "雪梨纽西兰希思露甘奶迪",
                "time": "2 天",
                "content": {
                    "text": "据“浦东发布”官方消息，为进一步提高车站闸机的客流通行能力，从 7 月 19 日开始，上海地铁在现有 32 座车站试点的基础上，新增 91 座车站试点“闸机常开门”模式。",
                    "images": [
                        "https://linux.do/uploads/default/optimized/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f_2_529x499.jpeg"
                    ],
                    "codeBlocks": [],
                    "links": [
                        {
                            "text": "756×714 108 KB",
                            "href": "https://linux.do/uploads/default/original/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f.jpeg"
                        }
                    ]
                }
            },
            {
                "postId": "post_2",
                "username": "Crixs",
                "time": "2 天",
                "content": {
                    "text": "不刷直接过怎么破",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_3",
                "username": "PHP 码农",
                "time": "2 天",
                "content": {
                    "text": "雪梨纽西兰希思露甘奶迪:\n\n当闸机接受到无效车票或无票通过时，闸机扇门将自动合拢\n\n\n是这么说的，会自动关闭",
                    "images": [
                        "https://linux.do/user_avatar/linux.do/sydneynewzealand/48/830676_2.png"
                    ],
                    "codeBlocks": [],
                    "links": [
                        {
                            "text": "",
                            "href": "/t/topic/802519/1"
                        }
                    ]
                }
            },
            {
                "postId": "post_4",
                "username": "雪梨纽西兰希思露甘奶迪",
                "time": "2 天",
                "content": {
                    "text": "会关门",
                    "images": [
                        "https://linux.do/images/emoji/twemoji/see_no_evil_monkey.png?v=14"
                    ],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_5",
                "username": "coconut",
                "time": "2 天",
                "content": {
                    "text": "建议码直接放在安检处，反正早高峰都是排两次队，不如整成一次",
                    "images": [
                        "https://linux.do/uploads/default/original/3X/3/3/3339b15ea7c025039809fab82a3b3e4d31f80b80.png?v=14"
                    ],
                    "codeBlocks": [],
                    "links": []
                }
            }
        ]
    }
    
    # 1. 验证用户数据格式
    print("\n1. 验证用户数据格式...")
    if ForumDataAdapter.validate_user_data(user_data):
        print("✅ 用户数据格式正确")
    else:
        print("❌ 用户数据格式不正确")
        return
    
    # 2. 转换数据格式
    print("\n2. 转换数据格式...")
    try:
        forum_data = convert_user_forum_data(user_data)
        print("✅ 数据转换成功")
        print(f"   主题: {forum_data['topic_title']}")
        print(f"   帖子数: {forum_data['total_posts']}")
    except Exception as e:
        print(f"❌ 数据转换失败: {str(e)}")
        return
    
    # 3. 保存转换后的数据到文件
    print("\n3. 保存转换后的数据到文件...")
    try:
        output_file = "example_converted_forum_data.json"
        ForumDataAdapter.save_forum_data_to_json(forum_data, output_file)
        print(f"✅ 数据已保存到 {output_file}")
    except Exception as e:
        print(f"❌ 数据保存失败: {str(e)}")
    
    # 4. 使用论坛分析器分析数据
    print("\n4. 使用论坛分析器分析数据...")
    try:
        analyzer = ForumAnalyzer()
        analysis_result = analyzer.analyze_forum(forum_data)
        
        if analysis_result.get('confidence', 0) > 0.5:
            print("✅ 论坛分析完成")
            print(f"   置信度: {analysis_result['confidence']}")
            print(f"   摘要: {analysis_result.get('summary', '')}")
            
            # 显示关键点
            key_points = analysis_result.get('key_points', [])
            if key_points:
                print("   关键点:")
                for i, point in enumerate(key_points[:5], 1):  # 只显示前5个
                    print(f"     {i}. {point}")
        else:
            print("❌ 论坛分析失败")
            print(f"   错误信息: {analysis_result.get('analysis', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 论坛分析失败: {str(e)}")
    
    # 5. 清理示例文件
    print("\n5. 清理示例文件...")
    try:
        if os.path.exists(output_file):
            os.remove(output_file)
        print("✅ 示例文件清理完成")
    except Exception as e:
        print(f"⚠️  文件清理失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 示例演示完成")


if __name__ == "__main__":
    main()