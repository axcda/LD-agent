from src.core.multimodal_agent import (
    run_multimodal_analysis,
    analyze_url,
    analyze_image,
    analyze_code,
    analyze_text,
    create_analysis_request
)
from src.graph.state import ContentType
from src.config import config


def demo_basic_workflow():
    """演示基本工作流"""
    print("🎯 运行基本多模态分析演示")
    return run_multimodal_analysis()


def demo_url_analysis():
    """演示URL分析"""
    print("🔗 URL分析示例")
    url = "https://github.com/langchain-ai/langgraph"
    result = analyze_url(url, "LangGraph项目页面")
    return result


def demo_code_analysis():
    """演示代码分析"""
    print("💻 代码分析示例")
    code = """
class MultiModalAgent:
    def __init__(self, config):
        self.config = config
        self.analyzers = {
            'url': URLAnalyzer(),
            'image': ImageAnalyzer(), 
            'code': CodeAnalyzer()
        }
    
    def analyze(self, content, content_type):
        analyzer = self.analyzers.get(content_type)
        return analyzer.analyze(content)
    """
    result = analyze_code(code, "Python")
    return result


def demo_text_analysis():
    """演示文本分析"""
    print("📝 文本分析示例")
    text = """
    LangGraph是一个用于构建多代理和多步应用的框架，基于LangChain构建。
    它提供了状态图的概念，允许开发者定义复杂的工作流程，包括循环、条件分支等。
    主要特点包括：状态持久化、错误恢复、人工干预、流式处理等。
    """
    result = analyze_text(text, "LangGraph技术介绍")
    return result


def interactive_mode():
    """交互式模式"""
    print("🎮 进入交互式分析模式")
    print("支持的内容类型: url, image, code, text")
    print("输入 'quit' 退出")
    
    while True:
        try:
            content_type = input("\n请选择内容类型 (url/image/code/text): ").strip().lower()
            
            if content_type == 'quit':
                break
                
            if content_type not in ['url', 'image', 'code', 'text']:
                print("❌ 无效的内容类型")
                continue
            
            content = input("请输入要分析的内容: ").strip()
            if not content:
                print("❌ 内容不能为空")
                continue
            
            context = input("请输入上下文信息 (可选): ").strip() or None
            
            # 执行分析
            print(f"\n🔍 正在分析 {content_type} 内容...")
            
            if content_type == 'url':
                result = analyze_url(content, context)
            elif content_type == 'image':
                result = analyze_image(content, context)
            elif content_type == 'code':
                language = input("请输入编程语言 (可选): ").strip() or None
                result = analyze_code(content, language)
            else:  # text
                result = analyze_text(content, context)
            
            if result:
                print("✅ 分析完成")
            else:
                print("❌ 分析失败")
                
        except KeyboardInterrupt:
            print("\n👋 退出交互模式")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def main():
    """主函数"""
    print("🤖 多模态内容分析Agent")
    print("=" * 50)
    
    # 检查配置
    config_status = config.validate_config()
    configured_apis = [api for api, status in config_status.items() if status]
    
    if not configured_apis:
        print("⚠️ 未检测到任何API配置")
        print("请在.env文件中配置API密钥:")
        print("- OPENAI_API_KEY")
        print("- GOOGLE_API_KEY") 
        print("- ALIBABA_API_KEY")
        return
    
    print(f"✅ 已配置API: {', '.join(configured_apis)}")
    
    while True:
        print("\n📋 选择运行模式:")
        print("1. 基本演示 (多种内容类型)")
        print("2. URL分析演示")
        print("3. 代码分析演示")
        print("4. 文本分析演示")
        print("5. 交互式模式")
        print("0. 退出")
        
        try:
            choice = input("\n请选择 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再见!")
                break
            elif choice == '1':
                demo_basic_workflow()
            elif choice == '2':
                demo_url_analysis()
            elif choice == '3':
                demo_code_analysis()
            elif choice == '4':
                demo_text_analysis()
            elif choice == '5':
                interactive_mode()
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    main()
