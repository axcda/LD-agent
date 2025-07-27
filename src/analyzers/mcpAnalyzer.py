from typing import Dict, Any, Optional
from .base import ContentAnalyzer
from src.graph.state import AnalysisResult, ContentType
import logging

logger = logging.getLogger(__name__)

class MCPAnalyzer(ContentAnalyzer):
    """MCP工具分析器"""
    
    def __init__(self):
        super().__init__()
    
    def analyze_content(self, content: str, content_type: ContentType = ContentType.TEXT) -> AnalysisResult:
        """
        使用MCP工具分析内容
        
        Args:
            content: 要分析的内容
            content_type: 内容类型
            
        Returns:
            分析结果
        """
        try:
            # 根据内容类型选择合适的MCP工具
            if content_type == ContentType.TEXT:
                return self._analyze_text_content(content)
            elif content_type == ContentType.CODE:
                return self._analyze_code_content(content)
            elif content_type == ContentType.URL:
                return self._analyze_url_content(content)
            else:
                # 默认使用文本分析
                return self._analyze_text_content(content)
                
        except Exception as e:
            logger.error(f"MCP分析器执行失败: {str(e)}", exc_info=True)
            return AnalysisResult(
                content=content,
                content_type=content_type,
                analysis=f"MCP分析失败: {str(e)}",
                key_points=[],
                metadata={"error": str(e)}
            )
    
    def _analyze_text_content(self, content: str) -> AnalysisResult:
        """分析文本内容"""
        # 示例：使用Smithery的文本分析工具
        # 注意：这里使用的是假设的工具名称，实际使用时需要根据具体的Smithery工具进行调整
        arguments = {
            "text": content,
            "analysisType": "comprehensive"
        }
        
        # 尝试使用Smithery MCP工具进行分析
        result = self.analyzeWithSmitheryMcp("text-analyzer", arguments)
        
        if result:
            analysis = result.get("analysis", "未提供分析结果")
            key_points = result.get("keyPoints", [])
            metadata = result.get("metadata", {})
        else:
            # 如果MCP工具不可用，回退到OpenAI分析
            logger.info("MCP工具不可用，回退到OpenAI分析")
            analysis = self.analyzeWithOpenai(
                f"请对以下文本内容进行分析：\n\n{content}",
                content
            )
            key_points = self.extractKeyPoints(analysis)
            metadata = {"fallback": "openai"}
        
        return AnalysisResult(
            content=content,
            content_type=ContentType.TEXT,
            analysis=analysis,
            key_points=key_points,
            metadata=metadata
        )
    
    def _analyze_code_content(self, content: str) -> AnalysisResult:
        """分析代码内容"""
        # 示例：使用Smithery的代码分析工具
        arguments = {
            "code": content,
            "language": "auto-detect"
        }
        
        # 尝试使用Smithery MCP工具进行分析
        result = self.analyzeWithSmitheryMcp("code-analyzer", arguments)
        
        if result:
            analysis = result.get("analysis", "未提供分析结果")
            key_points = result.get("keyPoints", [])
            metadata = result.get("metadata", {})
        else:
            # 如果MCP工具不可用，回退到OpenAI分析
            logger.info("MCP工具不可用，回退到OpenAI分析")
            analysis = self.analyzeWithOpenai(
                f"请对以下代码进行分析：\n\n{content}",
                content
            )
            key_points = self.extractKeyPoints(analysis)
            metadata = {"fallback": "openai"}
        
        return AnalysisResult(
            content=content,
            content_type=ContentType.CODE,
            analysis=analysis,
            key_points=key_points,
            metadata=metadata
        )
    
    def _analyze_url_content(self, content: str) -> AnalysisResult:
        """分析URL内容"""
        # 示例：使用Smithery的URL分析工具
        arguments = {
            "url": content
        }
        
        # 尝试使用Smithery MCP工具进行分析
        result = self.analyzeWithSmitheryMcp("url-analyzer", arguments)
        
        if result:
            analysis = result.get("analysis", "未提供分析结果")
            key_points = result.get("keyPoints", [])
            metadata = result.get("metadata", {})
        else:
            # 如果MCP工具不可用，回退到OpenAI分析
            logger.info("MCP工具不可用，回退到OpenAI分析")
            analysis = self.analyzeWithOpenai(
                f"请分析以下URL的内容：{content}",
                content
            )
            key_points = self.extractKeyPoints(analysis)
            metadata = {"fallback": "openai"}
        
        return AnalysisResult(
            content=content,
            content_type=ContentType.URL,
            analysis=analysis,
            key_points=key_points,
            metadata=metadata
        )