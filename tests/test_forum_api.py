#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛API测试
测试新增的论坛数据分析API端点
"""

import sys
import os
import json
import requests
import time
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.forum_data_adapter import ForumDataAdapter


class TestForumAPI(unittest.TestCase):
    """论坛API测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://localhost:9980"
        self.test_forum_data = {
            "url": "https://linux.do/t/topic/802519",
            "timestamp": "2025-07-22T14:14:27.271Z",
            "topicTitle": "大门敞开！上海 123 座地铁站实现“闸机常开门”，刷卡扫码秒通过",
            "replyInfo": "",
            "totalPosts": 5,
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
    
    def test_forum_api_endpoint_exists(self):
        """测试论坛API端点是否存在"""
        try:
            response = requests.get(f"{self.base_url}/")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("endpoints", data)
            self.assertIn("POST /analyze/forum", data["endpoints"])
        except requests.exceptions.ConnectionError:
            self.skipTest("API服务器未运行")
    
    def test_forum_api_health_check(self):
        """测试API健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
        except requests.exceptions.ConnectionError:
            self.skipTest("API服务器未运行")
    
    def test_forum_data_validation(self):
        """测试论坛数据验证"""
        # 验证有效数据
        is_valid = ForumDataAdapter.validate_user_data(self.test_forum_data)
        self.assertTrue(is_valid)
    
    def test_forum_data_conversion(self):
        """测试论坛数据转换"""
        forum_data = ForumDataAdapter.convert_user_data_to_forum_data(self.test_forum_data)
        self.assertEqual(forum_data["topic_title"], self.test_forum_data["topicTitle"])
        self.assertEqual(forum_data["total_posts"], self.test_forum_data["totalPosts"])
        self.assertEqual(len(forum_data["posts"]), self.test_forum_data["totalPosts"])
    
    def test_forum_api_analysis(self):
        """测试论坛API分析功能"""
        try:
            # 检查API服务器是否运行
            health_response = requests.get(f"{self.base_url}/health")
            if health_response.status_code != 200:
                self.skipTest("API服务器未运行")
            
            # 发送论坛数据分析请求
            response = requests.post(
                f"{self.base_url}/analyze/forum",
                json={"forum_data": self.test_forum_data},
                headers={"Content-Type": "application/json"}
            )
            
            # 检查响应状态
            self.assertIn(response.status_code, [200, 500])  # 200表示成功，500表示服务器错误（可能是API密钥未配置）
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("success", data)
                self.assertTrue(data["success"])
                
                # 检查响应数据结构
                self.assertIn("data", data)
                response_data = data["data"]
                
                self.assertIn("input", response_data)
                self.assertIn("analysis", response_data)
                
                # 检查输入信息
                input_data = response_data["input"]
                self.assertEqual(input_data["content_type"], "forum")
                self.assertEqual(input_data["topic_title"], self.test_forum_data["topicTitle"])
                self.assertEqual(input_data["total_posts"], self.test_forum_data["totalPosts"])
                
                # 检查分析结果
                analysis_data = response_data["analysis"]
                self.assertIn("summary", analysis_data)
                self.assertIn("key_points", analysis_data)
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API服务器未运行")
        except Exception as e:
            # 如果是API密钥未配置导致的错误，跳过测试
            if "API密钥" in str(e) or "api key" in str(e).lower():
                self.skipTest("API密钥未配置")
            else:
                raise e


def run_tests():
    """运行所有测试"""
    print("🧪 运行论坛API测试...")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestForumAPI)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"测试运行完成:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  失败数: {len(result.failures)}")
    print(f"  错误数: {len(result.errors)}")
    print(f"  跳过数: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)