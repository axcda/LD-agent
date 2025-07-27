#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛分析器 - 符合LangGraph项目结构
集成到现有的多模态内容分析框架中
"""

import re
import requests
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from src.graph.state import ForumData, ProcessedForumData, ContentType
from src.analyzers.base import ContentAnalyzer
from src.analyzers.urlAnalyzer import URLAnalyzer


class ForumDataPreprocessor:
    """论坛数据预处理器"""
    
    def __init__(self):
        self.image_patterns = [
            r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp|bmp)',
            r'!\[.*?\]\([^\)]+\)',  # markdown图片
        ]
        self.url_patterns = [
            r'https?://[^\s]+',
        ]
    
    def extract_links_and_images(self, text: str) -> Tuple[List[str], List[str]]:
        """从文本中提取链接和图片"""
        images = []
        links = []
        
        # 提取图片URL
        for pattern in self.image_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    images.append(match)
                elif isinstance(match, tuple):
                    # 对于正则表达式返回的元组，取完整匹配
                    full_match = re.search(pattern, text, re.IGNORECASE)
                    if full_match:
                        images.append(full_match.group(0))
        
        # 提取链接
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 排除已经识别为图片的链接
                if not any(img_ext in match.lower() for img_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
                    links.append(match)
        
        return list(set(links)), list(set(images))
    
    def preprocess_forum_data(self, forum_data: ForumData) -> ProcessedForumData:
        """预处理论坛数据"""
        processed_data: ProcessedForumData = {
            "topic_info": {
                "title": forum_data.get("topic_title", ""),
                "url": forum_data.get("url", ""),
                "timestamp": forum_data.get("timestamp", ""),
                "total_posts": forum_data.get("total_posts", 0)
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
        
        posts = forum_data.get("posts", [])
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


class ForumAnalyzer(ContentAnalyzer):
    """论坛内容分析器"""
    
    def __init__(self):
        super().__init__()
        self.preprocessor = ForumDataPreprocessor()
        self.url_analyzer = URLAnalyzer()
    
    def create_analysis_content(self, processed_data: ProcessedForumData) -> str:
        """创建用于分析的综合内容"""
        topic_info = processed_data["topic_info"]
        summary = processed_data["content_summary"]
        
        content = f"""论坛主题分析
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
    
    def analyze_link_content(self, url: str) -> Dict[str, Any]:
        """分析链接内容 - 联网搜索功能"""
        try:
            # 使用URL分析器获取网页内容
            result = self.url_analyzer.analyze_url(url)
            return result
        except Exception as e:
            return {
                "content_type": ContentType.URL,
                "original_content": url,
                "analysis": f"链接分析失败: {str(e)}",
                "summary": "无法分析链接内容",
                "key_points": [],
                "confidence": 0.0
            }
    
    def create_media_analysis_requests(self, processed_data: ProcessedForumData) -> List[Dict[str, Any]]:
        """创建媒体内容分析请求"""
        analysis_requests = []
        summary = processed_data["content_summary"]
        topic_title = processed_data["topic_info"]["title"]
        
        # 分析重要链接 - 使用URL workflow
        for i, link in enumerate(summary['all_links'][:3]):  # 只分析前3个链接
            if self._is_valid_url(link):
                analysis_requests.append({
                    "content": link,
                    "content_type": ContentType.URL,
                    "context": f"论坛讨论中的外部链接 #{i+1}: {topic_title}"
                })
        
        # 分析重要图片 - 使用Image workflow  
        for i, img_url in enumerate(summary['all_images'][:2]):  # 只分析前2张图片
            if self._is_valid_image_url(img_url):
                analysis_requests.append({
                    "content": img_url,
                    "content_type": ContentType.IMAGE, 
                    "context": f"论坛讨论中的图片 #{i+1}: {topic_title}"
                })
        
        return analysis_requests
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
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
    
    def analyze_forum(self, forum_data: ForumData) -> Dict[str, Any]:
        """分析论坛内容的主入口"""
        try:
            # 1. 预处理数据
            processed_data = self.preprocessor.preprocess_forum_data(forum_data)
            
            # 2. 创建主要内容分析
            main_content = self.create_analysis_content(processed_data)
            
            # 3. 分析主要讨论内容
            prompt = f"""
            请分析这个论坛主题的讨论内容：
            
            {main_content}
            
            请提供：
            1. 整体主题和核心观点
            2. 主要讨论点和用户观点
            3. 关键信息和数据
            4. 讨论趋势和用户情绪
            5. 实用性和价值评估
            
            请用简洁明了的语言总结，突出最重要的讨论要点。
            """
            
            analysis = self.analyzeWithOpenai(prompt)
            
            if "失败" in analysis:
                analysis = self.analyzeWithGemini(prompt)
            
            # 4. 提取关键点
            key_points = self.extractKeyPoints(analysis)
            
            # 5. 创建媒体分析请求（供后续使用）
            media_requests = self.create_media_analysis_requests(processed_data)
            
            # 6. 对重要链接进行联网搜索分析
            link_analyses = []
            for i, link in enumerate(processed_data["content_summary"]["all_links"][:3]):  # 分析前3个链接
                if self._is_valid_url(link):
                    link_analysis = self.analyze_link_content(link)
                    link_analyses.append({
                        "url": link,
                        "analysis": link_analysis
                    })
            
            return {
                "content_type": ContentType.FORUM,
                "original_content": f"论坛主题: {processed_data['topic_info']['title']}",
                "analysis": analysis,
                "summary": analysis[:300] + "..." if len(analysis) > 300 else analysis,
                "key_points": key_points,
                "confidence": 0.9 if "失败" not in analysis else 0.3,
                "processed_data": processed_data,
                "media_requests": media_requests,
                "link_analyses": link_analyses,  # 添加链接分析结果
                "metadata": {
                    "total_posts": processed_data['content_summary']['post_count'],
                    "users_count": len(processed_data['content_summary']['key_users']),
                    "links_count": len(processed_data['content_summary']['all_links']),
                    "images_count": len(processed_data['content_summary']['all_images'])
                }
            }
            
        except Exception as e:
            return {
                "content_type": ContentType.FORUM,
                "original_content": forum_data.get("topic_title", "未知论坛主题"),
                "analysis": f"论坛分析失败: {str(e)}",
                "summary": "分析过程中出现错误",
                "key_points": [],
                "confidence": 0.0,
                "processed_data": None,
                "media_requests": [],
                "link_analyses": [],  # 添加链接分析结果
                "metadata": {"error": str(e)}
            }
    
    def _extract_key_points(self, analysis: str) -> List[str]:
        """从分析结果中提取关键点"""
        key_points = []
        
        # 查找列表项或编号项
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            # 匹配各种列表格式
            if (line.startswith('-') or line.startswith('•') or 
                line.startswith('*') or re.match(r'^\d+\.', line)):
                clean_point = re.sub(r'^[-•*\d\.\s]+', '', line).strip()
                if clean_point and len(clean_point) > 10:
                    key_points.append(clean_point)
        
        # 如果没有找到列表格式，尝试按句号分割
        if not key_points:
            sentences = re.split(r'[。！？]', analysis)
            for sentence in sentences[:8]:  # 最多取8个句子
                sentence = sentence.strip()
                if len(sentence) > 20:
                    key_points.append(sentence)
        
        return key_points[:10]  # 限制关键点数量