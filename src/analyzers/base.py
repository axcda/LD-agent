from typing import Dict, Any, List
import re
import logging
from src.config import config
from src.graph.state import AnalysisResult, ContentType

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """内容分析器基类"""

    def __init__(self):
        self.config = config

    def analyze_with_openai(self, prompt: str, content: str = None) -> str:
        """使用OpenAI进行分析"""
        try:
            client = self.config.get_openai_client()
            
            # 调试日志，记录使用的base_url
            logger.info(f"--- OpenAI API 调用 ---")
            logger.info(f"使用 Base URL: {client.base_url}")
            logger.info(f"模型: gpt-4.1-mini-2025-04-14")
            logger.info(f"----------------------")

            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI分析失败: {str(e)}", exc_info=True)
            return f"OpenAI分析失败: {str(e)}"
    
    def analyze_with_gemini(self, prompt: str) -> str:
        """使用Gemini进行分析"""
        try:
            model = self.config.get_gemini_model()
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini分析失败: {str(e)}"
    
    def analyze_with_alibaba(self, prompt: str, image_data: str = None) -> str:
        """使用阿里百炼进行分析"""
        try:
            import dashscope
            from dashscope import MultiModalConversation
            
            messages = [{'role': 'user', 'content': prompt}]
            
            if image_data:
                # 检查是否为base64数据
                if image_data.startswith("data:image"):
                    messages[0]['content'] = [
                        {'text': prompt},
                        {'image': image_data}  # base64数据
                    ]
                else:
                    # 假设是URL
                    messages[0]['content'] = [
                        {'text': prompt},
                        {'image': image_data}  # URL
                    ]
            
            response = MultiModalConversation.call(
                model='Moonshot-Kimi-K2-Instruct',
                messages=messages
            )
            
            if response.status_code == 200:
                return response.output.choices[0]['message']['content']
            else:
                return f"阿里百炼分析失败: {response.message}"
                
        except Exception as e:
            return f"阿里百炼分析失败: {str(e)}"
    
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