from typing import Dict, Any, List
from tavily import TavilyClient
from src.config import config
import logging
import os

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

class TavilyAnalyzer:
    """Tavily搜索分析器"""
    
    def __init__(self):
        """初始化Tavily分析器"""
        logger.debug("🔧 初始化Tavily分析器...")
        
        # 从配置中获取Tavily API密钥
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        logger.debug(f"🔑 Tavily API密钥配置状态: {'已配置' if self.tavily_api_key else '未配置'}")
        
        if not self.tavily_api_key:
            logger.warning("⚠️ Tavily API密钥未配置，Tavily分析器将不可用")
            self.client = None
        else:
            try:
                self.client = TavilyClient(api_key=self.tavily_api_key)
                logger.info("✅ Tavily客户端初始化成功")
            except Exception as e:
                logger.error(f"❌ Tavily客户端初始化失败: {str(e)}")
                self.client = None
    
    def is_available(self) -> bool:
        """检查Tavily分析器是否可用"""
        return self.client is not None
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        执行Tavily搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            包含搜索结果的字典
        """
        if not self.is_available():
            logger.warning("⚠️ Tavily分析器不可用，无法执行搜索")
            return {
                "success": False,
                "error": "Tavily分析器不可用",
                "results": []
            }
        
        try:
            logger.info(f"🔍 执行Tavily搜索: {query}")
            logger.debug(f"📊 最大结果数: {max_results}")
            
            # 执行搜索
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_answer=True,
                include_raw_content=True
            )
            
            logger.debug(f"📥 Tavily搜索响应: {response}")
            
            # 处理结果
            results = []
            if "results" in response:
                for item in response["results"]:
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "raw_content": item.get("raw_content", ""),
                        "score": item.get("score", 0)
                    }
                    results.append(result)
            
            logger.info(f"✅ Tavily搜索完成，返回 {len(results)} 个结果")
            
            return {
                "success": True,
                "query": query,
                "answer": response.get("answer", ""),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Tavily搜索失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_context(self, query: str) -> str:
        """
        获取搜索上下文用于RAG应用
        
        Args:
            query: 查询语句
            
        Returns:
            上下文字符串
        """
        if not self.is_available():
            logger.warning("⚠️ Tavily分析器不可用，无法获取上下文")
            return "Tavily分析器不可用"
        
        try:
            logger.info(f"🔍 获取Tavily上下文: {query}")
            
            # 获取上下文
            context = self.client.get_search_context(query=query)
            
            logger.info("✅ Tavily上下文获取完成")
            return context
            
        except Exception as e:
            logger.error(f"❌ Tavily上下文获取失败: {str(e)}")
            return f"上下文获取失败: {str(e)}"
    
    def qna_search(self, query: str) -> str:
        """
        执行问答搜索
        
        Args:
            query: 问题
            
        Returns:
            答案字符串
        """
        if not self.is_available():
            logger.warning("⚠️ Tavily分析器不可用，无法执行问答搜索")
            return "Tavily分析器不可用"
        
        try:
            logger.info(f"🔍 执行Tavily问答搜索: {query}")
            
            # 执行问答搜索
            answer = self.client.qna_search(query=query)
            
            logger.info("✅ Tavily问答搜索完成")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Tavily问答搜索失败: {str(e)}")
            return f"问答搜索失败: {str(e)}"

# 全局Tavily分析器实例
tavily_analyzer = TavilyAnalyzer()