#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛数据适配器测试
测试ForumDataAdapter的功能
"""

import sys
import os
import json
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.forum_data_adapter import (
    ForumDataAdapter,
    convert_user_forum_data,
    load_forum_data_from_json
)
from src.graph.state import ForumData


class TestForumDataAdapter(unittest.TestCase):
    """论坛数据适配器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.sample_user_data = {
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
                        "text": "据“浦东发布”官方消息，为进一步提高车站闸机的客流通行能力...",
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
                }
            ]
        }
    
    def test_validate_user_data_valid(self):
        """测试验证有效的用户数据"""
        result = ForumDataAdapter.validate_user_data(self.sample_user_data)
        self.assertTrue(result)
    
    def test_validate_user_data_missing_fields(self):
        """测试验证缺少字段的用户数据"""
        # 缺少必需字段
        invalid_data = self.sample_user_data.copy()
        del invalid_data["url"]
        
        result = ForumDataAdapter.validate_user_data(invalid_data)
        self.assertFalse(result)
    
    def test_convert_user_data_to_forum_data(self):
        """测试将用户数据转换为论坛数据"""
        forum_data = ForumDataAdapter.convert_user_data_to_forum_data(self.sample_user_data)
        
        # 检查字段转换
        self.assertEqual(forum_data["url"], self.sample_user_data["url"])
        self.assertEqual(forum_data["timestamp"], self.sample_user_data["timestamp"])
        self.assertEqual(forum_data["topic_title"], self.sample_user_data["topicTitle"])
        self.assertEqual(forum_data["total_posts"], self.sample_user_data["totalPosts"])
        self.assertEqual(len(forum_data["posts"]), len(self.sample_user_data["posts"]))
    
    def test_convert_user_data_content_structure(self):
        """测试转换后的内容结构"""
        forum_data = ForumDataAdapter.convert_user_data_to_forum_data(self.sample_user_data)
        
        # 检查第一个帖子
        first_post = forum_data["posts"][0]
        self.assertIn("postId", first_post)
        self.assertIn("username", first_post)
        self.assertIn("time", first_post)
        self.assertIn("content", first_post)
        
        # 检查内容结构
        content = first_post["content"]
        self.assertIsInstance(content, dict)
        self.assertIn("text", content)
        self.assertIn("images", content)
        self.assertIn("codeBlocks", content)
        self.assertIn("links", content)
    
    def test_load_from_json_file(self):
        """测试从JSON文件加载数据"""
        # 创建临时JSON文件
        temp_file = "temp_test_forum_data.json"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.sample_user_data, f, ensure_ascii=False, indent=2)
            
            # 加载数据
            forum_data = ForumDataAdapter.load_from_json_file(temp_file)
            
            # 验证数据
            self.assertEqual(forum_data["topic_title"], self.sample_user_data["topicTitle"])
            self.assertEqual(forum_data["total_posts"], self.sample_user_data["totalPosts"])
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_save_forum_data_to_json(self):
        """测试将论坛数据保存为JSON"""
        # 转换数据
        forum_data = ForumDataAdapter.convert_user_data_to_forum_data(self.sample_user_data)
        
        # 保存到临时文件
        temp_file = "temp_saved_forum_data.json"
        try:
            ForumDataAdapter.save_forum_data_to_json(forum_data, temp_file)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))
            
            # 重新加载并验证
            with open(temp_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data["topicTitle"], forum_data["topic_title"])
            self.assertEqual(loaded_data["totalPosts"], forum_data["total_posts"])
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试convert_user_forum_data函数
        forum_data = convert_user_forum_data(self.sample_user_data)
        self.assertEqual(forum_data["topic_title"], self.sample_user_data["topicTitle"])
        
        # 创建临时文件测试load_forum_data_from_json函数
        temp_file = "temp_convenience_test.json"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.sample_user_data, f, ensure_ascii=False, indent=2)
            
            forum_data = load_forum_data_from_json(temp_file)
            self.assertEqual(forum_data["topic_title"], self.sample_user_data["topicTitle"])
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def run_tests():
    """运行所有测试"""
    print("🧪 运行论坛数据适配器测试...")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestForumDataAdapter)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"测试运行完成:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  失败数: {len(result.failures)}")
    print(f"  错误数: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)