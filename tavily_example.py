#!/usr/bin/env python3
"""
Tavily使用示例脚本
演示如何在多模态框架中使用Tavily搜索功能
"""

import os
import sys
import logging

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """主函数 - 演示Tavily使用方法"""
    logger.info("🚀 Tavily使用示例开始")
    
    try:
        # 导入Tavily分析器
        from src.analyzers.tavily_analyzer import TavilyAnalyzer
        
        # 初始化分析器
        logger.info("🔧 初始化Tavily分析器...")
        tavily_analyzer = TavilyAnalyzer()
        
        # 检查分析器是否可用
        if not tavily_analyzer.is_available():
            logger.error("❌ Tavily分析器不可用，请检查API密钥配置")
            logger.info("💡 请在.env文件中设置有效的TAVILY_API_KEY")
            return
        
        logger.info("✅ Tavily分析器已就绪")
        
        # 示例1: 基本搜索
        logger.info("\n🔍 示例1: 基本搜索")
        query = "人工智能发展现状"
        logger.info(f"🔍 搜索查询: {query}")
        
        result = tavily_analyzer.search(query, max_results=3)
        
        if result["success"]:
            logger.info(f"✅ 搜索成功，返回 {len(result['results'])} 个结果")
            
            # 显示答案（如果有的话）
            if result.get("answer"):
                logger.info(f"🤖 答案: {result['answer']}")
            
            # 显示搜索结果
            for i, item in enumerate(result["results"], 1):
                logger.info(f"\n{i}. {item['title']}")
                logger.info(f"   URL: {item['url']}")
                logger.info(f"   内容: {item['content'][:100]}...")
        else:
            logger.error(f"❌ 搜索失败: {result.get('error')}")
        
        # 示例2: 问答搜索
        logger.info("\n❓ 示例2: 问答搜索")
        question = "什么是机器学习？"
        logger.info(f"❓ 问题: {question}")
        
        answer = tavily_analyzer.qna_search(question)
        logger.info(f"🤖 答案: {answer}")
        
        # 示例3: 获取上下文（用于RAG应用）
        logger.info("\n📄 示例3: 获取上下文")
        context_query = "Python Flask框架教程"
        logger.info(f"📄 查询: {context_query}")
        
        context = tavily_analyzer.get_context(context_query)
        logger.info(f"📄 上下文长度: {len(context)} 字符")
        logger.info(f"📄 上下文预览: {context[:200]}...")
        
        logger.info("\n🎉 Tavily使用示例完成")
        
    except Exception as e:
        logger.error(f"❌ 示例运行失败: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    main()