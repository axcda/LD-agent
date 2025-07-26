from typing import Dict, Any, List
from src.graph.state import GraphState, AnalysisRequest, AnalysisResult, ContentType
from src.analyzers import URLAnalyzer, ImageAnalyzer, CodeAnalyzer, ForumAnalyzer
from src.config import config
import logging

# 配置日志
logger = logging.getLogger(__name__)


def input_node(state: GraphState) -> Dict[str, Any]:
    """输入节点：处理分析请求"""
    logger.info("=== 📥 输入节点：处理分析请求 ===")
    
    analysis_requests = state.get("analysis_requests", [])
    
    if not analysis_requests:
        logger.warning("⚠️ 未提供分析请求")
        return {
            "current_step": "input_error",
            "messages": state.get("messages", []) + ["未提供分析请求"],
        }
    
    logger.info(f"📥 收到 {len(analysis_requests)} 个分析请求")
    for i, req in enumerate(analysis_requests):
        logger.info(f"  {i+1}. 类型: {req['content_type'].value}, 内容: {req['content'][:50]}...")
    
    logger.info("✅ 输入节点处理完成")
    return {
        "current_step": "input_processed",
        "messages": state.get("messages", []) + [f"已接收 {len(analysis_requests)} 个分析请求"],
        "metadata": {**state.get("metadata", {}), "input_processed": True}
    }


def analysis_node(state: GraphState) -> Dict[str, Any]:
    """分析节点：执行多模态内容分析"""
    logger.info("\n=== 🔍 分析节点：执行内容分析 ===")
    
    analysis_requests = state.get("analysis_requests", [])
    analysis_results = []
    
    # 检查是否有论坛数据需要处理
    forum_data = state.get("forum_data")
    if forum_data:
        logger.info("🔍 检测到论坛数据，使用论坛分析器")
        forum_analyzer = ForumAnalyzer()
        forum_result = forum_analyzer.analyze_forum(forum_data)
        analysis_results.append(forum_result)
        
        # 如果有媒体内容需要进一步分析
        media_requests = forum_result.get("media_requests", [])
        if media_requests:
            logger.info(f"📎 发现 {len(media_requests)} 个媒体内容需要分析")
            # 将媒体请求添加到分析队列
            analysis_requests.extend(media_requests)
    
    # 初始化分析器
    url_analyzer = URLAnalyzer()
    image_analyzer = ImageAnalyzer()
    code_analyzer = CodeAnalyzer()
    
    for i, request in enumerate(analysis_requests):
        logger.info(f"\n🔍 分析第 {i+1} 个内容 ({request['content_type'].value})")
        
        try:
            if request['content_type'] == ContentType.URL:
                logger.info("🌐 使用URL分析器")
                result = url_analyzer.analyze_url(request['content'])
            elif request['content_type'] == ContentType.IMAGE:
                logger.info("🖼️ 使用图像分析器")
                result = image_analyzer.analyze_image(request['content'])
            elif request['content_type'] == ContentType.CODE:
                # 从context中获取编程语言信息
                language = request.get('context', 'Unknown')
                logger.info(f"💻 使用代码分析器 (语言: {language})")
                result = code_analyzer.analyze_code(request['content'], language)
            else:
                # 文本内容使用基础分析器
                logger.info("📝 使用文本分析器")
                analyzer = URLAnalyzer()  # 复用URL分析器的文本分析能力
                prompt = f"请分析以下文本内容：\n{request['content']}\n\n请提供总结和关键点。"
                analysis = analyzer.analyze_with_openai(prompt)
                
                result = {
                    "content_type": ContentType.TEXT,
                    "original_content": request['content'][:100] + "...",
                    "analysis": analysis,
                    "summary": analysis[:200] + "...",
                    "key_points": analyzer._extract_key_points(analysis),
                    "confidence": 0.8
                }
            
            analysis_results.append(result)
            logger.info(f"✅ 分析完成，置信度: {result['confidence']}")
            
        except Exception as e:
            logger.error(f"❌ 分析失败: {str(e)}")
            error_result = {
                "content_type": request['content_type'],
                "original_content": request['content'][:100],
                "analysis": f"分析失败: {str(e)}",
                "summary": "分析过程中出现错误",
                "key_points": [],
                "confidence": 0.0
            }
            analysis_results.append(error_result)
    
    logger.info(f"\n📊 完成 {len(analysis_results)} 个内容的分析")
    logger.info("✅ 分析节点处理完成")
    
    return {
        "current_step": "analysis_completed",
        "messages": state.get("messages", []) + [f"完成 {len(analysis_results)} 个内容的分析"],
        "analysis_results": analysis_results,
        "metadata": {**state.get("metadata", {}), "analysis_completed": True}
    }


def summary_node(state: GraphState) -> Dict[str, Any]:
    """总结节点：生成综合总结和归纳"""
    logger.info("\n=== 📋 总结节点：生成综合总结 ===")
    
    analysis_results = state.get("analysis_results", [])
    
    if not analysis_results:
        logger.warning("⚠️ 没有分析结果可以总结")
        return {
            "current_step": "summary_error",
            "messages": state.get("messages", []) + ["没有分析结果可以总结"],
            "final_summary": "无可用内容进行总结",
            "consolidated_key_points": []
        }
    
    # 收集所有分析结果
    all_summaries = []
    all_key_points = []
    content_types = []
    
    for result in analysis_results:
        if result['confidence'] > 0.5:  # 只包含置信度较高的结果
            all_summaries.append(result['summary'])
            all_key_points.extend(result['key_points'])
            content_types.append(result['content_type'].value)
    
    logger.info(f"📈 收集到 {len(all_summaries)} 个高置信度摘要和 {len(all_key_points)} 个关键点")
    
    # 生成综合总结
    combined_content = "\n".join([f"- {summary}" for summary in all_summaries])
    
    prompt = f"""
    请基于以下分析结果生成一个综合总结：

    内容类型: {', '.join(set(content_types))}
    分析内容:
    {combined_content}

    关键点:
    {chr(10).join([f"- {point}" for point in all_key_points[:10]])}

    请提供：
    1. 整体主题和核心观点
    2. 主要发现和洞察
    3. 实用性和价值评估
    4. 综合建议
    
    请用简洁明了的语言总结，突出最重要的信息。
    """
    
    try:
        # 使用OpenAI生成最终总结
        logger.info("🤖 使用OpenAI生成综合总结")
        analyzer = URLAnalyzer()  # 复用分析器
        final_summary = analyzer.analyze_with_openai(prompt)
        
        if "失败" in final_summary:
            logger.info("🔄 OpenAI失败，尝试使用Gemini")
            final_summary = analyzer.analyze_with_gemini(prompt)
        
        # 精选关键点（去重并限制数量）
        unique_key_points = []
        seen_points = set()
        
        for point in all_key_points:
            cleaned_point = point.strip().lower()
            if cleaned_point not in seen_points and len(unique_key_points) < 8:
                unique_key_points.append(point.strip())
                seen_points.add(cleaned_point)
        
        logger.info(f"📋 生成综合总结，包含 {len(unique_key_points)} 个关键点")
        logger.info("✅ 总结节点处理完成")
        
        return {
            "current_step": "summary_completed",
            "messages": state.get("messages", []) + ["生成综合总结完成"],
            "final_summary": final_summary,
            "consolidated_key_points": unique_key_points,
            "metadata": {**state.get("metadata", {}), "summary_completed": True}
        }
        
    except Exception as e:
        logger.error(f"❌ 总结生成失败: {str(e)}")
        
        # 降级处理：手动组合总结
        fallback_summary = f"分析了 {len(analysis_results)} 个内容，包括 {', '.join(set(content_types))}。"
        if all_summaries:
            fallback_summary += " 主要内容：" + " ".join(all_summaries[:3])
        
        logger.info("🔧 使用备用方式生成总结")
        return {
            "current_step": "summary_fallback",
            "messages": state.get("messages", []) + ["使用备用方式生成总结"],
            "final_summary": fallback_summary,
            "consolidated_key_points": all_key_points[:5],
            "metadata": {**state.get("metadata", {}), "summary_fallback": True}
        }


def output_node(state: GraphState) -> Dict[str, Any]:
    """输出节点：格式化并展示最终结果"""
    logger.info("\n=== 📤 输出节点：生成最终报告 ===")
    
    final_summary = state.get("final_summary", "无可用总结")
    consolidated_key_points = state.get("consolidated_key_points", [])
    analysis_results = state.get("analysis_results", [])
    
    # 生成最终报告
    report_lines = [
        "=" * 60,
        "📊 多模态内容分析报告",
        "=" * 60,
        "",
        "🎯 综合总结:",
        final_summary,
        "",
        "🔑 关键要点:",
    ]
    
    for i, point in enumerate(consolidated_key_points, 1):
        report_lines.append(f"  {i}. {point}")
    
    if analysis_results:
        report_lines.extend([
            "",
            "📋 分析详情:",
            f"  - 总计分析: {len(analysis_results)} 个内容",
            f"  - 成功分析: {sum(1 for r in analysis_results if r['confidence'] > 0.5)} 个",
            f"  - 内容类型: {', '.join(set(r['content_type'].value for r in analysis_results))}",
        ])
    
    report_lines.extend([
        "",
        "=" * 60,
        "✅ 分析完成"
    ])
    
    final_report = "\n".join(report_lines)
    logger.info(final_report)
    logger.info("✅ 输出节点处理完成")
    
    return {
        "current_step": "output_generated",
        "messages": state.get("messages", []) + ["生成最终报告完成"],
        "final_report": final_report,
        "metadata": {**state.get("metadata", {}), "output_generated": True}
    }