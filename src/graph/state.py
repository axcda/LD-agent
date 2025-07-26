from typing import TypedDict, List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = "text"
    URL = "url" 
    IMAGE = "image"
    CODE = "code"
    FORUM = "forum"


class AnalysisRequest(TypedDict):
    """分析请求结构"""
    content: str
    content_type: ContentType
    context: Optional[str]


class AnalysisResult(TypedDict):
    """分析结果结构"""
    content_type: ContentType
    original_content: str
    analysis: str
    summary: str
    key_points: List[str]
    confidence: float


class ForumData(TypedDict):
    """论坛数据结构"""
    url: str
    timestamp: str
    topic_title: str
    total_posts: int
    posts: List[Dict[str, Any]]


class ProcessedForumData(TypedDict):
    """预处理后的论坛数据"""
    topic_info: Dict[str, Any]
    content_summary: Dict[str, Any]
    structured_content: List[Dict[str, Any]]


class GraphState(TypedDict):
    """定义图的状态结构"""
    # 输入内容
    analysis_requests: List[AnalysisRequest]
    
    # 论坛专用字段
    forum_data: Optional[ForumData]
    processed_forum_data: Optional[ProcessedForumData]
    
    # 处理结果
    analysis_results: List[AnalysisResult]
    
    # 最终输出
    final_summary: Optional[str]
    consolidated_key_points: List[str]
    
    # 流程控制
    current_step: str
    messages: List[str]
    
    # 元数据
    metadata: Dict[str, Any]