from typing import Dict, Any
import re
from src.analyzers.base import ContentAnalyzer
from src.graph.state import AnalysisResult, ContentType


class CodeAnalyzer(ContentAnalyzer):
    """代码分析器"""
    
    def __init__(self):
        super().__init__()
        
        # 支持的编程语言
        self.language_keywords = {
            'python': ['def', 'class', 'import', 'from', 'if __name__'],
            'javascript': ['function', 'const', 'let', 'var', '=>'],
            'java': ['public class', 'private', 'public', 'static'],
            'cpp': ['#include', 'using namespace', 'int main'],
            'go': ['package', 'func', 'import'],
            'rust': ['fn', 'let', 'pub', 'use'],
        }
    
    def detect_language(self, code: str) -> str:
        """检测代码语言"""
        code_lower = code.lower()
        
        # 计算每种语言的匹配度
        language_scores = {}
        for lang, keywords in self.language_keywords.items():
            score = sum(1 for keyword in keywords if keyword in code_lower)
            if score > 0:
                language_scores[lang] = score
        
        # 返回得分最高的语言
        if language_scores:
            return max(language_scores, key=language_scores.get)
        else:
            return "unknown"
    
    def extract_code_structure(self, code: str) -> Dict[str, Any]:
        """提取代码结构信息"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "lines": len(code.split('\n')),
            "complexity": "simple"
        }
        
        lines = code.split('\n')
        
        # 提取函数定义
        for line in lines:
            line = line.strip()
            if re.match(r'^(def|function|func)\s+\w+', line):
                structure["functions"].append(line)
            elif re.match(r'^class\s+\w+', line):
                structure["classes"].append(line)
            elif line.startswith(('import', 'from', 'using', '#include')):
                structure["imports"].append(line)
        
        # 简单的复杂度评估
        if structure["lines"] > 100 or len(structure["functions"]) > 10:
            structure["complexity"] = "complex"
        elif structure["lines"] > 50 or len(structure["functions"]) > 5:
            structure["complexity"] = "medium"
        
        return structure
    
    def analyze_code(self, code: str, language: str = None) -> AnalysisResult:
        """分析代码内容"""
        print(f"💻 开始分析代码 ({language or '自动检测'})")
        
        # 检测编程语言
        if not language or language == "Unknown":
            detected_language = self.detect_language(code)
        else:
            detected_language = language.lower()
        
        # 提取代码结构
        structure = self.extract_code_structure(code)
        
        # 创建分析提示
        prompt = f"""
        请分析以下{detected_language}代码：
        
        代码：
        {code[:1000]}{"..." if len(code) > 1000 else ""}
        
        代码结构信息：
        - 行数: {structure['lines']}
        - 函数: {len(structure['functions'])}个
        - 类: {len(structure['classes'])}个
        - 导入: {len(structure['imports'])}个
        - 复杂度: {structure['complexity']}
        
        请提供：
        1. 代码功能和用途分析
        2. 代码质量和设计模式评估
        3. 潜在的改进建议
        4. 代码的技术特点和亮点
        
        请从技术角度进行专业分析。
        """
        
        # 使用AI分析
        analysis = self.analyze_with_openai(prompt)
        
        if "失败" in analysis:
            analysis = self.analyze_with_gemini(prompt)
        
        # 提取关键点
        key_points = self._extract_key_points(analysis)
        
        # 添加结构化信息到关键点
        key_points.insert(0, f"编程语言: {detected_language}")
        key_points.insert(1, f"代码行数: {structure['lines']}, 复杂度: {structure['complexity']}")
        
        # 评估置信度
        confidence = 0.9 if "失败" not in analysis else 0.4
        
        return {
            "content_type": ContentType.CODE,
            "original_content": code[:200] + "..." if len(code) > 200 else code,
            "analysis": analysis,
            "summary": analysis[:300] + "..." if len(analysis) > 300 else analysis,
            "key_points": key_points[:10],
            "confidence": confidence,
            "metadata": {
                "language": detected_language,
                "structure": structure
            }
        }