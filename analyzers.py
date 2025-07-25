from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io
import re
from config import config
from graph.state import GraphState, AnalysisResult, ContentType
import dashscope
from dashscope import MultiModalConversation


class ContentAnalyzer:
    """内容分析器基类"""
    
    def __init__(self):
        self.config = config
    
    def analyze_with_openai(self, prompt: str, content: str = None) -> str:
        """使用OpenAI进行分析"""
        try:
            client = self.config.get_openai_client()
            messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model="gpt-4.1-2025-04-14",
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI分析失败: {str(e)}"
    
    def analyze_with_gemini(self, prompt: str) -> str:
        """使用Gemini进行分析"""
        try:
            model = self.config.get_gemini_model()
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini分析失败: {str(e)}"
    
    def analyze_with_alibaba(self, prompt: str, image_url: str = None) -> str:
        """使用阿里百炼进行分析"""
        try:
            messages = [{'role': 'user', 'content': prompt}]
            
            if image_url:
                messages[0]['content'] = [
                    {'text': prompt},
                    {'image': image_url}
                ]
            
            response = MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=messages
            )
            
            if response.status_code == 200:
                return response.output.choices[0]['message']['content'][0]['text']
            else:
                return f"阿里百炼分析失败: {response.message}"
        except Exception as e:
            return f"阿里百炼分析失败: {str(e)}"


class URLAnalyzer(ContentAnalyzer):
    """URL内容分析器"""
    
    def analyze_url(self, url: str) -> AnalysisResult:
        """分析URL内容"""
        try:
            # 获取网页内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取文本内容
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text()
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 限制内容长度
            if len(clean_text) > 3000:
                clean_text = clean_text[:3000] + "..."
            
            # 构造分析提示
            prompt = f"""
            请分析以下网页内容，并提供结构化的总结：

            标题：{title_text}
            URL：{url}
            内容：{clean_text}

            请提供：
            1. 内容主题和核心观点
            2. 关键信息点（3-5个）
            3. 内容类型和质量评估
            4. 实用性和价值评估
            """
            
            # 使用多个API进行分析
            analysis = self.analyze_with_openai(prompt)
            if "失败" in analysis:
                analysis = self.analyze_with_gemini(prompt)
            
            # 提取关键点
            key_points = self._extract_key_points(analysis)
            
            return {
                "content_type": ContentType.URL,
                "original_content": f"URL: {url}\n标题: {title_text}",
                "analysis": analysis,
                "summary": self._extract_summary(analysis),
                "key_points": key_points,
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "content_type": ContentType.URL,
                "original_content": url,
                "analysis": f"URL分析失败: {str(e)}",
                "summary": "无法获取URL内容",
                "key_points": [],
                "confidence": 0.0
            }
    
    def _extract_key_points(self, analysis: str) -> List[str]:
        """从分析结果中提取关键点"""
        lines = analysis.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('•'):
                key_points.append(line)
                if len(key_points) >= 5:
                    break
        
        return key_points[:5]
    
    def _extract_summary(self, analysis: str) -> str:
        """提取摘要"""
        lines = analysis.split('\n')
        summary_lines = []
        
        for line in lines[:3]:
            if line.strip() and not re.match(r'^\d+\.', line.strip()):
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines)[:200] + "..." if summary_lines else "无可用摘要"


class ImageAnalyzer(ContentAnalyzer):
    """图片内容分析器"""
    
    def analyze_image(self, image_path: str) -> AnalysisResult:
        """分析图片内容"""
        try:
            # 检查是否为URL
            if image_path.startswith(('http://', 'https://')):
                return self._analyze_image_url(image_path)
            else:
                return self._analyze_image_file(image_path)
                
        except Exception as e:
            return {
                "content_type": ContentType.IMAGE,
                "original_content": image_path,
                "analysis": f"图片分析失败: {str(e)}",
                "summary": "无法分析图片内容",
                "key_points": [],
                "confidence": 0.0
            }
    
    def _analyze_image_url(self, image_url: str) -> AnalysisResult:
        """分析网络图片"""
        prompt = """
        请详细分析这张图片，包括：
        1. 图片内容描述（场景、对象、人物等）
        2. 图片主题和意图
        3. 重要的视觉元素
        4. 可能的用途或含义
        5. 技术特征（如果适用）
        """
        
        # 优先使用阿里百炼的多模态能力
        analysis = self.analyze_with_alibaba(prompt, image_url)
        
        if "失败" in analysis:
            # 降级到文本分析
            analysis = f"无法直接分析图片 {image_url}，建议手动查看图片内容"
        
        key_points = self._extract_key_points(analysis)
        
        return {
            "content_type": ContentType.IMAGE,
            "original_content": f"图片URL: {image_url}",
            "analysis": analysis,
            "summary": self._extract_summary(analysis),
            "key_points": key_points,
            "confidence": 0.7
        }
    
    def _analyze_image_file(self, image_path: str) -> AnalysisResult:
        """分析本地图片文件"""
        try:
            # 读取并处理图片
            with Image.open(image_path) as img:
                # 获取图片基本信息
                width, height = img.size
                format_info = img.format
                mode = img.mode
                
                # 转换为RGB如果需要
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 转换为base64用于API调用
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                prompt = f"""
                请分析这张图片（尺寸: {width}x{height}, 格式: {format_info}）：
                1. 详细描述图片内容
                2. 识别主要对象和场景
                3. 分析图片的用途和含义
                4. 提取关键信息点
                """
                
                # 使用OpenAI Vision API
                analysis = self._analyze_with_openai_vision(prompt, img_base64)
                
                if "失败" in analysis:
                    analysis = f"图片基本信息: 尺寸{width}x{height}, 格式{format_info}, 模式{mode}"
                
                key_points = self._extract_key_points(analysis)
                
                return {
                    "content_type": ContentType.IMAGE,
                    "original_content": f"图片文件: {image_path} ({width}x{height})",
                    "analysis": analysis,
                    "summary": self._extract_summary(analysis),
                    "key_points": key_points,
                    "confidence": 0.8
                }
                
        except Exception as e:
            return {
                "content_type": ContentType.IMAGE,
                "original_content": image_path,
                "analysis": f"本地图片分析失败: {str(e)}",
                "summary": "无法读取或分析图片文件",
                "key_points": [],
                "confidence": 0.0
            }
    
    def _analyze_with_openai_vision(self, prompt: str, image_base64: str) -> str:
        """使用OpenAI Vision API分析图片"""
        try:
            client = self.config.get_openai_client()
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"OpenAI Vision分析失败: {str(e)}"


class CodeAnalyzer(ContentAnalyzer):
    """代码块分析器"""
    
    def analyze_code(self, code: str, language: str = None) -> AnalysisResult:
        """分析代码块"""
        try:
            # 检测编程语言
            if not language:
                language = self._detect_language(code)
            
            prompt = f"""
            请分析以下{language}代码，提供详细的技术分析：

            代码内容：
            ```{language}
            {code}
            ```

            请提供：
            1. 代码功能和用途描述
            2. 主要算法和逻辑分析
            3. 代码结构和设计模式
            4. 潜在的问题或改进建议
            5. 关键技术点总结
            """
            
            # 使用OpenAI进行代码分析
            analysis = self.analyze_with_openai(prompt)
            
            if "失败" in analysis:
                analysis = self.analyze_with_gemini(prompt)
            
            key_points = self._extract_key_points(analysis)
            
            return {
                "content_type": ContentType.CODE,
                "original_content": f"语言: {language}\n代码长度: {len(code)}字符",
                "analysis": analysis,
                "summary": self._extract_summary(analysis),
                "key_points": key_points,
                "confidence": 0.9
            }
            
        except Exception as e:
            return {
                "content_type": ContentType.CODE,
                "original_content": f"代码块 ({language})",
                "analysis": f"代码分析失败: {str(e)}",
                "summary": "无法分析代码块",
                "key_points": [],
                "confidence": 0.0
            }
    
    def _detect_language(self, code: str) -> str:
        """检测编程语言"""
        code_lower = code.lower()
        
        # 简单的语言检测逻辑
        if 'def ' in code and 'import ' in code:
            return 'Python'
        elif 'function' in code_lower and '{' in code:
            return 'JavaScript'
        elif 'public class' in code or 'import java' in code:
            return 'Java'
        elif '#include' in code or 'int main' in code:
            return 'C/C++'
        elif 'func ' in code and 'package ' in code:
            return 'Go'
        else:
            return 'Unknown'