from typing import Dict, Any
import requests
import base64
from PIL import Image
import io
from src.analyzers.base import ContentAnalyzer
from src.graph.state import AnalysisResult, ContentType


class ImageAnalyzer(ContentAnalyzer):
    """图片内容分析器"""
    
    def __init__(self):
        super().__init__()
    
    def download_image(self, image_url: str) -> str:
        """下载图片并转换为base64"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # 转换为base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{image_base64}"
            
        except Exception as e:
            return f"图片下载失败: {str(e)}"
    
    def analyze_image(self, image_url: str) -> AnalysisResult:
        """分析图片内容"""
        print(f"🖼️ 开始分析图片: {image_url}")
        
        # 首先尝试下载图片
        image_data = self.download_image(image_url)
        
        # 创建分析提示
        prompt = f"""
        请分析这张图片：
        
        图片URL: {image_url}
        
        请提供：
        1. 图片主要内容和场景描述
        2. 图片中的关键元素和细节
        3. 图片的用途和背景分析
        4. 图片质量和技术特点
        
        请详细描述你在图片中看到的内容。
        """
        
        # 尝试使用阿里百炼分析图片（传递实际图片数据）
        if not image_data.startswith("图片下载失败"):
            # 如果图片下载成功，传递base64数据给阿里百炼
            analysis = self.analyze_with_alibaba(prompt, image_data)
        else:
            # 如果下载失败，仍然使用URL进行分析
            analysis = self.analyze_with_alibaba(prompt, image_url)
        
        # 如果阿里百炼失败，提供更好的错误处理
        if "失败" in analysis:
            # 提供更友好的错误信息
            if image_data.startswith("图片下载失败"):
                analysis = f"图片分析: {image_url}\n无法下载或访问此图片，可能是因为网络问题或图片不存在。"
            else:
                analysis = f"图片分析: {image_url}\n虽然图片已下载，但无法进行详细分析。这可能是一张相关的图片，但需要更多上下文来理解其内容。"
        
        # 提取关键点
        key_points = self.extractKeyPoints(analysis)
        
        # 评估置信度
        confidence = 0.7 if "失败" not in analysis else 0.3
        
        return {
            "content_type": ContentType.IMAGE,
            "original_content": image_url,
            "analysis": analysis,
            "summary": analysis[:300] + "..." if len(analysis) > 300 else analysis,
            "key_points": key_points,
            "confidence": confidence
        }