from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from src.analyzers.base import ContentAnalyzer
from src.graph.state import AnalysisResult, ContentType


class URLAnalyzer(ContentAnalyzer):
    """URL内容分析器"""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_url_content(self, url: str) -> str:
        """获取URL内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取主要文本内容
            title = soup.find('title')
            title_text = title.get_text() if title else "无标题"
            
            # 提取正文内容
            content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'main'])
            content_text = '\n'.join([tag.get_text().strip() for tag in content_tags if tag.get_text().strip()])
            
            return f"标题: {title_text}\n\n内容: {content_text[:2000]}..."
            
        except Exception as e:
            return f"无法获取URL内容: {str(e)}"
    
    def analyze_url(self, url: str) -> AnalysisResult:
        """分析URL内容"""
        print(f"📥 开始分析URL: {url}")
        
        # 获取网页内容
        web_content = self.fetch_url_content(url)
        
        # 创建分析提示
        prompt = f"""
        请分析以下网页内容：
        
        URL: {url}
        内容: {web_content}
        
        请提供：
        1. 网页主题和核心内容总结
        2. 关键信息和要点
        3. 内容的可信度和价值评估
        4. 对读者的实用性建议
        
        请用简洁明了的语言总结，突出最重要的信息。
        """
        
        # 使用AI分析
        analysis = self.analyze_with_openai(prompt)
        
        if "失败" in analysis:
            analysis = self.analyze_with_gemini(prompt)
        
        # 提取关键点
        key_points = self._extract_key_points(analysis)
        
        # 评估置信度
        confidence = 0.8 if "失败" not in analysis else 0.3
        if "无法获取" in web_content:
            confidence = 0.1
        
        return {
            "content_type": ContentType.URL,
            "original_content": url,
            "analysis": analysis,
            "summary": analysis[:300] + "..." if len(analysis) > 300 else analysis,
            "key_points": key_points,
            "confidence": confidence
        }