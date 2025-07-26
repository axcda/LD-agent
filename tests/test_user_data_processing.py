#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据处理测试
测试适配器处理用户提供的完整JSON数据
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


def test_user_provided_data():
    """测试处理用户提供的完整JSON数据"""
    # 用户提供的完整JSON数据
    user_data = {
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
            },
            {
                "postId": "post_6",
                "username": "ion",
                "time": "2 天",
                "content": {
                    "text": "出站口常开没问题，不刷就是最高票价，大家都会主动刷",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_7",
                "username": "6gdfg",
                "time": "2 天",
                "content": {
                    "text": "20米助跑能直接过吗",
                    "images": [
                        "https://linux.do/images/emoji/twemoji/laughing.png?v=14"
                    ],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_8",
                "username": "介似怎么肥四",
                "time": "2 天",
                "content": {
                    "text": "感觉就是刷卡已经成下意识的习惯了，看样子不刷应该能直接过吧，不然提升的效率在哪？就省去开门那一瞬间，人犹豫那1秒吗，并且真的想逃票了，是不是还挺危险的，被闸机夹住咋办？",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_9",
                "username": "lw不錄了",
                "time": "2 天",
                "content": {
                    "text": "腿会剧痛并且一堆人看着你发出尖叫然后你众目睽睽之下刷卡然后过去",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_10",
                "username": "lw不錄了",
                "time": "2 天",
                "content": {
                    "text": "会被罚两次吧",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_11",
                "username": "介似怎么肥四",
                "time": "2 天",
                "content": {
                    "text": "你是不是被闸机夹住过了？",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_12",
                "username": "lw不錄了",
                "time": "2 天",
                "content": {
                    "text": "有日韩的朋友跟我哭诉",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_13",
                "username": "介似怎么肥四",
                "time": "2 天",
                "content": {
                    "text": "好家伙，他们是想硬闯闸吗？还是歪果仁猛",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_14",
                "username": "systemctl",
                "time": "2 天",
                "content": {
                    "text": "介似怎么肥四:\n\n提升的效率\n\n\n效率提升在不需要关门了，如果都是正常付费的人\n没付费走过去有红外会提前关门的，不会夹到",
                    "images": [
                        "https://linux.do/user_avatar/linux.do/c293943/48/572040_2.png"
                    ],
                    "codeBlocks": [],
                    "links": [
                        {
                            "text": "",
                            "href": "/t/topic/802519/8"
                        }
                    ]
                }
            },
            {
                "postId": "post_15",
                "username": "lw不錄了",
                "time": "2 天",
                "content": {
                    "text": "不是的，有时候可能没刷到但自己以为刷到了，那个门发现没刷卡就砰的一下打过去",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_16",
                "username": "阳青",
                "time": "2 天",
                "content": {
                    "text": "不刷怎么扣钱",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_17",
                "username": "fablia",
                "time": "2 天",
                "content": {
                    "text": "日本好像也是这样的闸机",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_18",
                "username": "jrerrq",
                "time": "2 天",
                "content": {
                    "text": "终于支持visa master了, 另外上海能不能搞个nfc教育, 特么老有人二维码站那里卡半天",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_19",
                "username": "魔力鸽",
                "time": "2 天",
                "content": {
                    "text": "每次过这种闸机总是很怕被夹到",
                    "images": [
                        "https://linux.do/uploads/default/original/3X/9/4/949d4d71290d75c51e81e4fc70d23246e4a9214c.png?v=14"
                    ],
                    "codeBlocks": [],
                    "links": []
                }
            },
            {
                "postId": "post_20",
                "username": "背包",
                "time": "2 天",
                "content": {
                    "text": "因为节奏很快。别人都是眼睛不看一扫直接过，如果自己停下等确认就会打乱节奏。但如果刚好自己没刷上就会被夹+尴尬",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            }
        ]
    }
    
    print("🎯 测试处理用户提供的完整JSON数据")
    print("=" * 50)
    
    # 1. 验证数据格式
    print("\n1. 验证数据格式...")
    is_valid = ForumDataAdapter.validate_user_data(user_data)
    if is_valid:
        print("✅ 数据格式正确")
    else:
        print("❌ 数据格式不正确")
        return False
    
    # 2. 转换数据格式
    print("\n2. 转换数据格式...")
    try:
        forum_data = convert_user_forum_data(user_data)
        print("✅ 数据转换成功")
        print(f"   主题: {forum_data['topic_title']}")
        print(f"   帖子数: {forum_data['total_posts']}")
        print(f"   实际帖子数: {len(forum_data['posts'])}")
    except Exception as e:
        print(f"❌ 数据转换失败: {str(e)}")
        return False
    
    # 3. 保存到文件
    print("\n3. 保存到文件...")
    try:
        ForumDataAdapter.save_forum_data_to_json(forum_data, "test_user_data_output.json")
        print("✅ 数据保存成功")
    except Exception as e:
        print(f"❌ 数据保存失败: {str(e)}")
        return False
    
    # 4. 使用论坛分析器分析
    print("\n4. 使用论坛分析器分析...")
    try:
        analyzer = ForumAnalyzer()
        result = analyzer.analyze_forum(forum_data)
        print("✅ 论坛分析成功")
        print(f"   分析结果长度: {len(result.get('analysis', ''))} 字符")
        print(f"   置信度: {result.get('confidence', 0)}")
        print(f"   关键点数: {len(result.get('key_points', []))}")
    except Exception as e:
        print(f"❌ 论坛分析失败: {str(e)}")
        return False
    
    # 5. 清理测试文件
    print("\n5. 清理测试文件...")
    try:
        if os.path.exists("test_user_data_output.json"):
            os.remove("test_user_data_output.json")
        print("✅ 测试文件清理完成")
    except Exception as e:
        print(f"⚠️  文件清理失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！适配器能够正确处理用户提供的完整JSON数据")
    return True


if __name__ == "__main__":
    success = test_user_provided_data()
    sys.exit(0 if success else 1)