#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版论坛数据分析器
预处理数据后批量分析，避免每个帖子都调用大模型
"""

import json
import sys
import re
import requests
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse


class ForumDataPreprocessor:
    """论坛数据预处理器"""
    
    def __init__(self):
        self.image_patterns = [
            r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp)',
            r'!\[.*?\]\([^\)]+\)',  # markdown图片
        ]
        self.url_patterns = [
            r'https?://[^\s]+',
        ]
    
    def extract_links_and_images(self, text: str) -> Tuple[List[str], List[str]]:
        """从文本中提取链接和图片"""
        images = []
        links = []
        
        # 提取图片
        for pattern in self.image_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            images.extend(matches)
        
        # 提取链接
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 排除已经识别为图片的链接
                if not any(img_ext in match.lower() for img_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    links.append(match)
        
        return list(set(links)), list(set(images))
    
    def preprocess_forum_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理论坛数据"""
        processed_data = {
            "topic_info": {
                "title": data.get("topicTitle", ""),
                "url": data.get("url", ""),
                "timestamp": data.get("timestamp", ""),
                "total_posts": data.get("totalPosts", 0)
            },
            "content_summary": {
                "main_discussion": "",
                "key_users": set(),
                "all_links": [],
                "all_images": [],
                "post_count": 0
            },
            "structured_content": []
        }
        
        posts = data.get("posts", [])
        processed_data["content_summary"]["post_count"] = len(posts)
        
        # 处理每个帖子
        for i, post in enumerate(posts):
            username = post.get("username", "未知用户")
            text_content = post.get("content", {}).get("text", "")
            post_images = post.get("content", {}).get("images", [])
            post_links_data = post.get("content", {}).get("links", [])
            
            # 记录关键用户
            processed_data["content_summary"]["key_users"].add(username)
            
            # 处理链接数据（从字典格式提取href）
            post_links = []
            for link_item in post_links_data:
                if isinstance(link_item, dict) and "href" in link_item:
                    post_links.append(link_item["href"])
                elif isinstance(link_item, str):
                    post_links.append(link_item)
            
            # 提取额外的链接和图片
            extracted_links, extracted_images = self.extract_links_and_images(text_content)
            
            # 合并所有链接和图片
            all_post_links = list(set(post_links + extracted_links))
            all_post_images = list(set(post_images + extracted_images))
            
            processed_data["content_summary"]["all_links"].extend(all_post_links)
            processed_data["content_summary"]["all_images"].extend(all_post_images)
            
            # 构建结构化内容
            processed_post = {
                "index": i + 1,
                "username": username,
                "content": text_content,
                "has_media": len(all_post_images) > 0,
                "has_links": len(all_post_links) > 0,
                "media_count": len(all_post_images),
                "links_count": len(all_post_links)
            }
            processed_data["structured_content"].append(processed_post)
            
            # 构建主要讨论内容（限制长度）
            if len(processed_data["content_summary"]["main_discussion"]) < 2000:
                processed_data["content_summary"]["main_discussion"] += f"[{username}]: {text_content[:200]}...\n"
        
        # 去重和整理
        processed_data["content_summary"]["key_users"] = list(processed_data["content_summary"]["key_users"])
        processed_data["content_summary"]["all_links"] = list(set(processed_data["content_summary"]["all_links"]))
        processed_data["content_summary"]["all_images"] = list(set(processed_data["content_summary"]["all_images"]))
        
        return processed_data


class OptimizedForumAnalyzer:
    """优化版论坛分析器"""
    
    def __init__(self, api_base_url: str = "http://localhost:9980"):
        self.api_base_url = api_base_url
        self.preprocessor = ForumDataPreprocessor()
    
    def check_api_health(self) -> bool:
        """检查API健康状态"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_analysis_content(self, processed_data: Dict[str, Any]) -> str:
        """创建分析内容"""
        topic_info = processed_data["topic_info"]
        summary = processed_data["content_summary"]
        
        content = f"""论坛主题分析报告
================
主题: {topic_info['title']}
链接: {topic_info['url']}
发布时间: {topic_info['timestamp']}
总回复数: {summary['post_count']}

参与用户: {', '.join(summary['key_users'][:10])}{'...' if len(summary['key_users']) > 10 else ''}
媒体内容: {len(summary['all_images'])}张图片, {len(summary['all_links'])}个链接

主要讨论内容:
{summary['main_discussion']}

需要进一步分析的媒体内容:
"""
        
        # 添加需要分析的链接
        if summary['all_links']:
            content += f"\n外部链接({len(summary['all_links'])}个):\n"
            for i, link in enumerate(summary['all_links'][:5]):  # 只列出前5个
                content += f"  {i+1}. {link}\n"
            if len(summary['all_links']) > 5:
                content += f"  ... 还有{len(summary['all_links'])-5}个链接\n"
        
        # 添加需要分析的图片
        if summary['all_images']:
            content += f"\n图片内容({len(summary['all_images'])}张):\n"
            for i, img in enumerate(summary['all_images'][:3]):  # 只列出前3个
                content += f"  {i+1}. {img}\n"
            if len(summary['all_images']) > 3:
                content += f"  ... 还有{len(summary['all_images'])-3}张图片\n"
        
        return content
    
    def analyze_media_content(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析媒体内容，使用对应的workflow"""
        analysis_requests = []
        summary = processed_data["content_summary"]
        
        # 分析重要链接 - 使用URL workflow
        for i, link in enumerate(summary['all_links'][:3]):  # 只分析前3个链接
            # 验证链接格式
            if self._is_valid_url(link):
                analysis_requests.append({
                    "content": link,
                    "content_type": "url",
                    "context": f"论坛讨论中的外部链接 #{i+1}: {processed_data['topic_info']['title']}"
                })
        
        # 分析重要图片 - 使用Image workflow  
        for i, img_url in enumerate(summary['all_images'][:2]):  # 只分析前2张图片
            # 验证图片链接格式
            if self._is_valid_image_url(img_url):
                analysis_requests.append({
                    "content": img_url,
                    "content_type": "image", 
                    "context": f"论坛讨论中的图片 #{i+1}: {processed_data['topic_info']['title']}"
                })
        
        return analysis_requests
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_valid_image_url(self, url: str) -> bool:
        """验证图片URL格式"""
        if not self._is_valid_url(url):
            return False
        
        # 检查是否为图片扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        url_lower = url.lower()
        
        # 直接包含图片扩展名
        if any(ext in url_lower for ext in image_extensions):
            return True
            
        # 或者是图片服务域名 (如uploads.linux.do等)
        image_domains = ['uploads.', 'images.', 'img.', 'cdn.']
        if any(domain in url_lower for domain in image_domains):
            return True
            
        return False
    
    def perform_analysis(self, forum_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行优化的分析流程"""
        print("🔄 预处理论坛数据...")
        processed_data = self.preprocessor.preprocess_forum_data(forum_data)
        
        print(f"✅ 预处理完成:")
        print(f"  - 主题: {processed_data['topic_info']['title']}")
        print(f"  - 帖子数: {processed_data['content_summary']['post_count']}")
        print(f"  - 参与用户: {len(processed_data['content_summary']['key_users'])}人")
        print(f"  - 链接: {len(processed_data['content_summary']['all_links'])}个")
        print(f"  - 图片: {len(processed_data['content_summary']['all_images'])}张")
        
        # 1. 主要内容分析
        print("\n🔍 分析主要讨论内容...")
        main_content = self.create_analysis_content(processed_data)
        
        main_analysis_payload = {
            "content": main_content,
            "content_type": "text",
            "context": f"论坛主题分析: {processed_data['topic_info']['title']}"
        }
        
        try:
            response = requests.post(f"{self.api_base_url}/analyze", json=main_analysis_payload, timeout=30)
            if response.status_code == 200:
                main_result = response.json()
                if main_result.get("success"):
                    print("✅ 主要内容分析完成")
                    analysis = main_result["data"]["analysis"]
                    print(f"摘要: {analysis['summary'][:150]}...")
                    print("关键点:")
                    for i, point in enumerate(analysis["key_points"][:3], 1):
                        print(f"  {i}. {point}")
                else:
                    print(f"❌ 主要内容分析失败: {main_result.get('error', {}).get('message')}")
                    return main_result
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return {"success": False, "error": {"message": f"HTTP {response.status_code}"}}
        except Exception as e:
            print(f"❌ 请求出错: {str(e)}")
            return {"success": False, "error": {"message": str(e)}}
        
        # 2. 媒体内容分析（如果有的话）
        media_requests = self.analyze_media_content(processed_data)
        if media_requests:
            print(f"\n🖼️ 分析媒体内容({len(media_requests)}项)...")
            
            batch_payload = {"requests": media_requests}
            
            try:
                response = requests.post(f"{self.api_base_url}/analyze/batch", json=batch_payload, timeout=60)
                if response.status_code == 200:
                    media_result = response.json()
                    if media_result.get("success"):
                        print("✅ 媒体内容分析完成")
                        media_analysis = media_result["data"]["analysis"]
                        print(f"媒体分析摘要: {media_analysis['summary'][:150]}...")
                        
                        # 合并分析结果
                        combined_summary = f"{analysis['summary']}\n\n媒体内容补充: {media_analysis['summary']}"
                        combined_key_points = analysis["key_points"] + media_analysis["key_points"]
                        
                        return {
                            "success": True,
                            "data": {
                                "analysis": {
                                    "summary": combined_summary,
                                    "key_points": combined_key_points[:10],  # 限制关键点数量
                                    "processed_info": {
                                        "total_posts": processed_data['content_summary']['post_count'],
                                        "users_count": len(processed_data['content_summary']['key_users']),
                                        "links_count": len(processed_data['content_summary']['all_links']),
                                        "images_count": len(processed_data['content_summary']['all_images'])
                                    }
                                }
                            }
                        }
                    else:
                        print(f"⚠️ 媒体内容分析失败，仅返回主要内容分析")
                else:
                    print(f"⚠️ 媒体分析API请求失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 媒体分析请求出错: {str(e)}")
        
        # 返回主要分析结果
        return main_result


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python optimized_forum_analyzer.py <json文件路径>")
        print("示例: python optimized_forum_analyzer.py sample_forum_data.json")
        return
    
    # 创建分析器
    analyzer = OptimizedForumAnalyzer()
    
    # 检查API状态
    if not analyzer.check_api_health():
        print("❌ 无法连接到API服务器，请确保服务器正在运行")
        return
    
    print("✅ 连接到API服务器")
    
    # 加载数据
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            forum_data = json.load(f)
        print(f"✅ 加载数据成功: {forum_data.get('topicTitle', '')}")
    except Exception as e:
        print(f"❌ 加载数据失败: {str(e)}")
        return
    
    # 执行分析
    print("\n" + "="*60)
    print("🚀 开始优化分析...")
    
    result = analyzer.perform_analysis(forum_data)
    
    print("\n" + "="*60)
    if result.get("success"):
        print("🎉 分析完成!")
        if "processed_info" in result["data"]["analysis"]:
            info = result["data"]["analysis"]["processed_info"]
            print(f"\n📊 处理统计:")
            print(f"  - 总帖子数: {info['total_posts']}")
            print(f"  - 参与用户: {info['users_count']}人")
            print(f"  - 外部链接: {info['links_count']}个")
            print(f"  - 图片内容: {info['images_count']}张")
    else:
        print("❌ 分析失败")


if __name__ == "__main__":
    main()