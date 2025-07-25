from typing import TypedDict, List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = "text"
    URL = "url" 
    IMAGE = "image"
    CODE = "code"


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


class GraphState(TypedDict):
    """定义图的状态结构"""
    # 输入内容
    analysis_requests: List[AnalysisRequest]
    
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