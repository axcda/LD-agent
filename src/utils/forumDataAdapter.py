#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛数据适配器
将用户提供的JSON格式转换为项目内部使用的ForumData格式
"""

from typing import Dict, Any, List
from src.graph.state import ForumData


class ForumDataAdapter:
    """论坛数据适配器类"""
    
    @staticmethod
    def convert_user_data_to_forum_data(user_data: Dict[str, Any]) -> ForumData:
        """
        将用户提供的JSON格式数据转换为项目内部的ForumData格式
        
        Args:
            user_data: 用户提供的JSON格式数据
            
        Returns:
            ForumData: 项目内部使用的论坛数据格式
        """
        # 检查是否是用户提供的新格式
        if "meta" in user_data and "data" in user_data:
            # 转换用户提供的格式为期望格式
            converted_data = ForumDataAdapter._convert_new_format_to_expected(user_data)
            return ForumDataAdapter._convert_expected_format_to_forum_data(converted_data)
        else:
            # 原始格式
            return ForumDataAdapter._convert_expected_format_to_forum_data(user_data)
    
    @staticmethod
    def _convert_new_format_to_expected(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将用户提供的新格式转换为期望格式
        
        Args:
            user_data: 用户提供的新格式数据
            
        Returns:
            Dict[str, Any]: 期望格式的数据
        """
        # 从第一个帖子获取URL和主题标题
        first_post = user_data["data"][0] if user_data["data"] else {}
        url = first_post.get("url", "")
        topic_title = first_post.get("title", "")
        
        # 计算总帖子数（主帖+回复）
        total_posts = len(user_data["data"])
        for post in user_data["data"]:
            total_posts += len(post.get("replies", []))
        
        # 转换帖子格式
        posts = []
        post_id_counter = 1
        
        for post in user_data["data"]:
            # 主帖
            main_post = {
                "postId": f"post_{post_id_counter}",
                "username": post.get("author", ""),
                "time": post.get("timestamp", ""),
                "content": {
                    "text": post.get("content", ""),
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            }
            posts.append(main_post)
            post_id_counter += 1
            
            # 回复
            for reply in post.get("replies", []):
                reply_post = {
                    "postId": f"post_{post_id_counter}",
                    "username": reply.get("author", ""),
                    "time": reply.get("timestamp", ""),
                    "content": {
                        "text": reply.get("content", ""),
                        "images": [],
                        "codeBlocks": [],
                        "links": []
                    }
                }
                posts.append(reply_post)
                post_id_counter += 1
        
        # 构建期望格式的数据
        expected_data = {
            "url": url,
            "timestamp": user_data["meta"].get("exported_at", ""),
            "topicTitle": topic_title,
            "totalPosts": total_posts,
            "posts": posts
        }
        
        return expected_data
    
    @staticmethod
    def _convert_expected_format_to_forum_data(user_data: Dict[str, Any]) -> ForumData:
        """
        将期望格式转换为项目内部的ForumData格式
        
        Args:
            user_data: 期望格式的数据
            
        Returns:
            ForumData: 项目内部使用的论坛数据格式
        """
        # 转换字段名
        forum_data: ForumData = {
            "url": user_data.get("url", ""),
            "timestamp": user_data.get("timestamp", ""),
            "topic_title": user_data.get("topicTitle", ""),  # topicTitle -> topic_title
            "total_posts": user_data.get("totalPosts", 0),   # totalPosts -> total_posts
            "posts": user_data.get("posts", [])
        }
        
        # 处理帖子内容中的字段名转换
        converted_posts = []
        for post in forum_data["posts"]:
            converted_post = post.copy()
            
            # 确保content字段存在
            if "content" not in converted_post:
                converted_post["content"] = {
                    "text": "",
                    "images": [],
                    "codeBlocks": [],
                    "links": []
                }
            
            # 转换content内部的字段名（如果需要）
            content = converted_post["content"]
            if isinstance(content, dict):
                # 确保所有必要的字段都存在
                content.setdefault("text", "")
                content.setdefault("images", [])
                content.setdefault("codeBlocks", [])
                content.setdefault("links", [])
            
            converted_posts.append(converted_post)
        
        forum_data["posts"] = converted_posts
        
        return forum_data
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> bool:
        """
        验证用户提供的数据格式是否正确
        
        Args:
            user_data: 用户提供的JSON格式数据
            
        Returns:
            bool: 数据格式是否正确
        """
        required_fields = ["url", "timestamp", "topicTitle", "totalPosts", "posts"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in user_data:
                print(f"缺少必需字段: {field}")
                return False
        
        # 检查posts是否为列表
        if not isinstance(user_data["posts"], list):
            print("posts字段必须是列表")
            return False
        
        # 检查每个帖子的必需字段
        for i, post in enumerate(user_data["posts"]):
            if not isinstance(post, dict):
                print(f"第{i+1}个帖子必须是字典格式")
                return False
            
            required_post_fields = ["postId", "username", "time", "content"]
            for field in required_post_fields:
                if field not in post:
                    print(f"第{i+1}个帖子缺少必需字段: {field}")
                    return False
        
        return True
    
    @staticmethod
    def load_from_json_file(file_path: str) -> ForumData:
        """
        从JSON文件加载用户数据并转换为ForumData格式
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            ForumData: 项目内部使用的论坛数据格式
        """
        import json
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            if ForumDataAdapter.validate_user_data(user_data):
                return ForumDataAdapter.convert_user_data_to_forum_data(user_data)
            else:
                raise ValueError("JSON文件格式不正确")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {str(e)}")
    
    @staticmethod
    def save_forum_data_to_json(forum_data: ForumData, file_path: str):
        """
        将ForumData保存为用户格式的JSON文件
        
        Args:
            forum_data: 项目内部的ForumData格式数据
            file_path: 保存的JSON文件路径
        """
        import json
        
        # 转换回用户格式
        user_data = {
            "url": forum_data.get("url", ""),
            "timestamp": forum_data.get("timestamp", ""),
            "topicTitle": forum_data.get("topic_title", ""),
            "totalPosts": forum_data.get("total_posts", 0),
            "posts": forum_data.get("posts", [])
        }
        
        # 处理帖子内容
        converted_posts = []
        for post in user_data["posts"]:
            converted_post = post.copy()
            converted_posts.append(converted_post)
        
        user_data["posts"] = converted_posts
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)


# 便捷函数
def convert_user_forum_data(user_data: Dict[str, Any]) -> ForumData:
    """
    便捷函数：将用户提供的JSON格式数据转换为项目内部的ForumData格式
    
    Args:
        user_data: 用户提供的JSON格式数据
        
    Returns:
        ForumData: 项目内部使用的论坛数据格式
    """
    return ForumDataAdapter.convert_user_data_to_forum_data(user_data)


def load_forum_data_from_json(file_path: str) -> ForumData:
    """
    便捷函数：从JSON文件加载用户数据并转换为ForumData格式
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        ForumData: 项目内部使用的论坛数据格式
    """
    return ForumDataAdapter.load_from_json_file(file_path)


# 示例使用
if __name__ == "__main__":
    # 示例用户数据
    sample_user_data = {
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
            }
        ]
    }
    
    # 验证数据
    if ForumDataAdapter.validate_user_data(sample_user_data):
        print("✅ 用户数据格式正确")
        
        # 转换数据
        forum_data = convert_user_forum_data(sample_user_data)
        print("✅ 数据转换成功")
        print(f"转换后的数据: {forum_data['topic_title']}")
    else:
        print("❌ 用户数据格式不正确")