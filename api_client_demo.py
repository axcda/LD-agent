import requests
import json
from typing import Dict, Any, List, Optional


class MultiModalAnalysisClient:
    """多模态内容分析API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_config_status(self) -> Dict[str, Any]:
        """获取API配置状态"""
        response = self.session.get(f"{self.base_url}/config/status")
        return response.json()
    
    def analyze_content(self, content: str, content_type: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        分析单个内容
        
        Args:
            content: 要分析的内容
            content_type: 内容类型 (url/image/code/text)
            context: 可选的上下文信息
            
        Returns:
            分析结果
        """
        data = {
            "content": content,
            "content_type": content_type,
            "context": context
        }
        
        response = self.session.post(f"{self.base_url}/analyze", json=data)
        return response.json()
    
    def analyze_batch(self, requests_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量分析多个内容
        
        Args:
            requests_data: 分析请求列表，每个请求包含content, content_type, context字段
            
        Returns:
            批量分析结果
        """
        data = {"requests": requests_data}
        
        response = self.session.post(f"{self.base_url}/analyze/batch", json=data)
        return response.json()
    
    def analyze_url(self, url: str, context: Optional[str] = None) -> Dict[str, Any]:
        """分析URL内容"""
        return self.analyze_content(url, "url", context)
    
    def analyze_image(self, image_path: str, context: Optional[str] = None) -> Dict[str, Any]:
        """分析图片内容"""
        return self.analyze_content(image_path, "image", context)
    
    def analyze_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """分析代码内容"""
        return self.analyze_content(code, "code", language)
    
    def analyze_text(self, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """分析文本内容"""
        return self.analyze_content(text, "text", context)


def demo_api_usage():
    """演示API使用方法"""
    client = MultiModalAnalysisClient()
    
    print("🤖 多模态内容分析API客户端演示")
    print("=" * 50)
    
    # 健康检查
    print("1. 健康检查")
    try:
        health = client.health_check()
        print(f"✅ 服务状态: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return
    
    # 配置状态检查
    print("\n2. 配置状态检查") 
    try:
        config_status = client.get_config_status()
        if config_status.get('success'):
            apis = config_status['data']['configured_apis']
            print(f"✅ 已配置API: {', '.join(apis)}")
        else:
            print("❌ 配置检查失败")
            return
    except Exception as e:
        print(f"❌ 配置检查失败: {str(e)}")
        return
    
    # 单个内容分析示例
    print("\n3. 单个内容分析示例")
    
    # 分析代码
    print("\n📝 分析Python代码:")
    code_example = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
    """
    
    try:
        result = client.analyze_code(code_example, "Python")
        if result.get('success'):
            analysis = result['data']['analysis']
            print(f"摘要: {analysis['summary'][:100]}...")
            print("关键点:")
            for i, point in enumerate(analysis['key_points'][:3], 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ 分析失败: {result.get('error', {}).get('message')}")
    except Exception as e:
        print(f"❌ 代码分析失败: {str(e)}")
    
    # 分析文本
    print("\n📄 分析文本内容:")
    text_example = """
    LangGraph是一个基于LangChain构建的框架，用于创建有状态的多代理应用程序。
    它允许开发者定义复杂的工作流，包括循环、条件分支和并行处理。
    主要特点包括状态持久化、错误恢复、人工干预点和流式处理能力。
    """
    
    try:
        result = client.analyze_text(text_example, "LangGraph技术介绍")
        if result.get('success'):
            analysis = result['data']['analysis']
            print(f"摘要: {analysis['summary'][:100]}...")
            print("关键点:")
            for i, point in enumerate(analysis['key_points'][:3], 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ 分析失败: {result.get('error', {}).get('message')}")
    except Exception as e:
        print(f"❌ 文本分析失败: {str(e)}")
    
    # 批量分析示例
    print("\n4. 批量分析示例")
    batch_requests = [
        {
            "content": "https://www.python.org/about/",
            "content_type": "url",
            "context": "Python官网介绍页面"
        },
        {
            "content": "import numpy as np\ndef matrix_multiply(a, b):\n    return np.dot(a, b)",
            "content_type": "code",
            "context": "Python"
        },
        {
            "content": "机器学习是人工智能的一个重要分支，通过算法让计算机从数据中学习patterns。",
            "content_type": "text",
            "context": "机器学习概念"
        }
    ]
    
    try:
        result = client.analyze_batch(batch_requests)
        if result.get('success'):
            analysis = result['data']['analysis']
            print(f"批量分析完成，共处理 {result['data']['input']['total_requests']} 个内容")
            print(f"综合摘要: {analysis['summary'][:150]}...")
            print("综合关键点:")
            for i, point in enumerate(analysis['key_points'][:3], 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ 批量分析失败: {result.get('error', {}).get('message')}")
    except Exception as e:
        print(f"❌ 批量分析失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ API演示完成")


if __name__ == "__main__":
    demo_api_usage()