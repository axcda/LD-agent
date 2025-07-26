#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛数据适配器使用示例
展示如何使用ForumDataAdapter处理用户提供的JSON格式数据
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.forum_data_adapter import (
    ForumDataAdapter,
    convert_user_forum_data,
    load_forum_data_from_json
)
from src.graph.state import ForumData
from src.analyzers.forum_analyzer import ForumAnalyzer


def create_sample_user_data() -> dict:
    """创建示例用户数据"""
    return {
        "url": "https://linux.do/t/topic/802519",
        "timestamp": "2025-07-22T14:14:27.271Z",
        "topicTitle": "大门敞开！上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过",
        "replyInfo": "",
        "totalPosts": 20,
        "posts": [
            {
                "postId": "post_1",
                "username": "雪梨纽西兰希思露甘奶迪",
                "time": "2 天",
                "content": {
                    "text": "据“浦东发布”官方消息，为进一步提高车站闸机的客流通行能力，从 7 月 19 日开始，上海地铁在现有 32 座车站试点的基础上，新增 91 座车站试点“闸机常开门”模式。至此，全网有 19 条线路累计 123 座车站试点采用“闸机常开门”模式。\n756×714 108 KB\n与日常闸机的常闭模式相反，“闸机常开门”模式是在常态时，车站闸机扇门默认保持开启状态，乘客刷卡或扫码后，经确认闸机屏幕显示“绿色通行”箭头，可直接通行。这一模式理论上可以减少乘客在闸机处等待扇门开闭动作的时间，提高客流连续正常通行的效率。\n1080×809 225 KB\n需要提醒乘客注意的是：当闸机接受到无效车票或无票通过时，闸机扇门将自动合拢，阻挡通道，乘客须重新刷卡、扫码或寻求工作人员协助票务处置；同时，排队进出站时，当前面的乘客通过后，后面的乘客无须等待闸门关闭后再刷卡或扫码，而是可以直接刷卡或扫码通行。\n\n  \n\n      finance.sina.com.cn – 20 Jul 25\n  \n\n  \n    \n\n上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过\n\n  上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过",
                    "images": [
                        "https://linux.do/uploads/default/optimized/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f_2_529x499.jpeg",
                        "https://linux.do/uploads/default/optimized/4X/2/3/2/232c6eca41c21ede791db7bc2a9773aa76a937ac_2_667x500.jpeg",
                        "https://linux.do/uploads/default/optimized/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f_2_529x499.jpeg"
                    ],
                    "codeBlocks": [],
                    "links": [
                        {
                            "text": "756×714 108 KB",
                            "href": "https://linux.do/uploads/default/original/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f.jpeg"
                        },
                        {
                            "text": "1080×809 225 KB",
                            "href": "https://linux.do/uploads/default/original/4X/2/3/2/232c6eca41c21ede791db7bc2a9773aa76a937ac.jpeg"
                        },
                        {
                            "text": "finance.sina.com.cn – 20 Jul 25",
                            "href": "https://finance.sina.com.cn/tech/digi/2025-07-20/doc-infharny4341371.shtml"
                        },
                        {
                            "text": "上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过",
                            "href": "https://finance.sina.com.cn/tech/digi/2025-07-20/doc-infharny4341371.shtml"
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
            }
        ]
    }


def demo_data_conversion():
    """演示数据转换功能"""
    print("🎯 论坛数据适配器使用示例")
    print("=" * 50)
    
    # 1. 创建示例用户数据
    print("\n1. 创建示例用户数据...")
    user_data = create_sample_user_data()
    print(f"✅ 创建了包含 {len(user_data['posts'])} 个帖子的示例数据")
    
    # 2. 验证用户数据格式
    print("\n2. 验证用户数据格式...")
    if ForumDataAdapter.validate_user_data(user_data):
        print("✅ 用户数据格式正确")
    else:
        print("❌ 用户数据格式不正确")
        return
    
    # 3. 转换数据格式
    print("\n3. 转换数据格式...")
    try:
        forum_data = convert_user_forum_data(user_data)
        print("✅ 数据转换成功")
        print(f"   主题: {forum_data['topic_title']}")
        print(f"   帖子数: {forum_data['total_posts']}")
        print(f"   URL: {forum_data['url']}")
    except Exception as e:
        print(f"❌ 数据转换失败: {str(e)}")
        return
    
    # 4. 保存转换后的数据到文件
    print("\n4. 保存转换后的数据到文件...")
    try:
        output_file = "converted_forum_data.json"
        ForumDataAdapter.save_forum_data_to_json(forum_data, output_file)
        print(f"✅ 数据已保存到 {output_file}")
    except Exception as e:
        print(f"❌ 数据保存失败: {str(e)}")
    
    # 5. 从文件加载数据
    print("\n5. 从文件加载数据...")
    try:
        loaded_forum_data = load_forum_data_from_json(output_file)
        print("✅ 从文件加载数据成功")
        print(f"   主题: {loaded_forum_data['topic_title']}")
        print(f"   帖子数: {loaded_forum_data['total_posts']}")
    except Exception as e:
        print(f"❌ 从文件加载数据失败: {str(e)}")
    
    # 6. 使用论坛分析器分析数据
    print("\n6. 使用论坛分析器分析数据...")
    try:
        analyzer = ForumAnalyzer()
        analysis_result = analyzer.analyze_forum(forum_data)
        print("✅ 论坛分析完成")
        print(f"   分析结果长度: {len(analysis_result.get('analysis', ''))} 字符")
        print(f"   置信度: {analysis_result.get('confidence', 0)}")
    except Exception as e:
        print(f"❌ 论坛分析失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 示例演示完成")


def demo_file_processing(json_file_path: str):
    """演示文件处理功能"""
    print(f"📂 处理文件: {json_file_path}")
    
    if not os.path.exists(json_file_path):
        print(f"❌ 文件不存在: {json_file_path}")
        return
    
    try:
        # 从文件加载并转换数据
        forum_data = load_forum_data_from_json(json_file_path)
        print("✅ 文件加载和转换成功")
        print(f"   主题: {forum_data['topic_title']}")
        print(f"   帖子数: {forum_data['total_posts']}")
        
        # 使用论坛分析器分析数据
        analyzer = ForumAnalyzer()
        analysis_result = analyzer.analyze_forum(forum_data)
        print("✅ 论坛分析完成")
        
        # 输出分析结果摘要
        summary = analysis_result.get('summary', '无摘要')
        print(f"   摘要: {summary[:100]}...")
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")


if __name__ == "__main__":
    print("🚀 论坛数据适配器演示程序")
    
    # 如果提供了命令行参数，则处理指定的JSON文件
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
        demo_file_processing(json_file_path)
    else:
        # 运行完整的演示
        demo_data_conversion()
        
        # 创建示例JSON文件供测试
        print("\n💾 创建示例JSON文件...")
        sample_data = create_sample_user_data()
        with open("sample_user_forum_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        print("✅ 示例JSON文件已创建: sample_user_forum_data.json")
        print("💡 您可以使用以下命令处理该文件:")
        print("   python examples/forum_data_adapter_example.py sample_user_forum_data.json")