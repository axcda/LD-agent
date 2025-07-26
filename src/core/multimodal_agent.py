from src.graph.workflow import compile_multimodal_workflow
from src.graph.state import GraphState, AnalysisRequest, ContentType
from src.config import config
import logging

# 配置日志
logger = logging.getLogger(__name__)


def create_analysis_request(content: str, content_type: ContentType, context: str = None) -> AnalysisRequest:
    """创建分析请求"""
    return {
        "content": content,
        "content_type": content_type,
        "context": context
    }


def run_multimodal_analysis():
    """运行多模态内容分析示例"""
    
    print("🚀 启动多模态内容分析Agent")
    print("=" * 60)
    
    # 检查配置
    config_status = config.validate_config()
    print("📋 API配置状态:")
    for api, status in config_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api.upper()}: {'已配置' if status else '未配置'}")
    
    if not any(config_status.values()):
        print("\n⚠️ 警告：所有API密钥均未配置，将无法进行实际分析")
        print("请在.env文件中配置至少一个API密钥")
        return
    
    print("\n" + "=" * 60)
    
    # 编译工作流
    logger.info("🔧 编译多模态工作流...")
    app = compile_multimodal_workflow()
    logger.info("✅ 工作流编译完成")
    
    # 准备测试数据
    logger.info("📝 准备测试数据...")
    analysis_requests = [
        create_analysis_request(
            content="https://www.python.org/about/",
            content_type=ContentType.URL,
            context="Python官网介绍页面"
        ),
        create_analysis_request(
            content="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            content_type=ContentType.CODE,
            context="Python"
        ),
        create_analysis_request(
            content="人工智能技术正在快速发展，特别是大语言模型的出现，为各行各业带来了新的机遇和挑战。",
            content_type=ContentType.TEXT,
            context="AI技术发展"
        )
    ]
    logger.info(f"✅ 准备完成，共 {len(analysis_requests)} 个分析请求")
    
    # 准备初始状态
    logger.info("⚙️ 准备初始状态...")
    initial_state: GraphState = {
        "analysis_requests": analysis_requests,
        "analysis_results": [],
        "final_summary": None,
        "consolidated_key_points": [],
        "current_step": "start",
        "messages": [],
        "metadata": {"start_time": "now", "test_mode": True}
    }
    logger.info("✅ 初始状态准备完成")
    
    try:
        # 执行工作流
        logger.info("🚀 开始执行工作流...")
        final_state = app.invoke(initial_state)
        logger.info("✅ 工作流执行完成")
        
        print("\n" + "=" * 60)
        print("🎉 分析完成！")
        
        return final_state
        
    except Exception as e:
        logger.error(f"❌ 执行失败: {str(e)}")
        print(f"\n❌ 执行失败: {str(e)}")
        print("请检查API配置和网络连接")
        return None


def run_custom_analysis(requests: list):
    """运行自定义分析"""
    
    logger.info("🔧 编译多模态工作流...")
    app = compile_multimodal_workflow()
    logger.info("✅ 工作流编译完成")
    
    logger.info("⚙️ 准备初始状态...")
    initial_state: GraphState = {
        "analysis_requests": requests,
        "analysis_results": [],
        "final_summary": None,
        "consolidated_key_points": [],
        "current_step": "start",
        "messages": [],
        "metadata": {"start_time": "now", "custom_mode": True}
    }
    logger.info("✅ 初始状态准备完成")
    
    logger.info("🚀 开始执行工作流...")
    result = app.invoke(initial_state)
    logger.info("✅ 工作流执行完成")
    
    return result


def analyze_url(url: str, context: str = None):
    """分析单个URL"""
    logger.info(f"🌐 分析URL: {url}")
    request = create_analysis_request(url, ContentType.URL, context)
    return run_custom_analysis([request])


def analyze_image(image_path: str, context: str = None):
    """分析单个图片"""
    logger.info(f"🖼️ 分析图片: {image_path}")
    request = create_analysis_request(image_path, ContentType.IMAGE, context)
    return run_custom_analysis([request])


def analyze_code(code: str, language: str = None):
    """分析单个代码块"""
    logger.info(f"💻 分析代码 (语言: {language})")
    request = create_analysis_request(code, ContentType.CODE, language)
    return run_custom_analysis([request])


def analyze_text(text: str, context: str = None):
    """分析单个文本"""
    logger.info(f"📝 分析文本: {text[:50]}...")
    request = create_analysis_request(text, ContentType.TEXT, context)
    return run_custom_analysis([request])


if __name__ == "__main__":
    run_multimodal_analysis()