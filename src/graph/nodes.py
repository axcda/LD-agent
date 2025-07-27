from typing import Dict, Any, List
from src.graph.state import GraphState, AnalysisRequest, AnalysisResult, ContentType
from src.analyzers import URLAnalyzer, ImageAnalyzer, CodeAnalyzer, ForumAnalyzer, MCPAnalyzer, TavilyAnalyzer
from src.config import config
import logging
import os

# 配置日志
# 从环境变量获取日志级别，默认为INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


def input_node(state: GraphState) -> Dict[str, Any]:
    """输入节点：处理分析请求"""
    logger.info("=== 📥 输入节点：处理分析请求 ===")
    logger.debug(f"📥 输入状态: {state}")
    
    analysis_requests = state.get("analysis_requests", [])
    logger.debug(f"📋 分析请求数量: {len(analysis_requests)}")
    
    if not analysis_requests:
        logger.warning("⚠️ 未提供分析请求")
        logger.debug("↩️ 返回错误状态")
        return {
            "current_step": "input_error",
            "messages": state.get("messages", []) + ["未提供分析请求"],
        }
    
    logger.info(f"📥 收到 {len(analysis_requests)} 个分析请求")
    for i, req in enumerate(analysis_requests):
        logger.info(f"  {i+1}. 类型: {req['content_type'].value}, 内容: {req['content'][:50]}...")
        logger.debug(f"     详细内容: {req}")
    
    logger.info("✅ 输入节点处理完成")
    logger.debug("↩️ 返回处理结果")
    return {
        "current_step": "input_processed",
        "messages": state.get("messages", []) + [f"已接收 {len(analysis_requests)} 个分析请求"],
        "metadata": {**state.get("metadata", {}), "input_processed": True}
    }


def analysis_node(state: GraphState) -> Dict[str, Any]:
    """分析节点：执行多模态内容分析"""
    logger.info("\n=== 🔍 分析节点：执行内容分析 ===")
    logger.debug(f"🔍 分析节点接收状态: {state}")
    
    analysis_requests = state.get("analysis_requests", [])
    analysis_results = []
    logger.debug(f"📋 初始分析请求数量: {len(analysis_requests)}")
    
    # 检查是否有论坛数据需要处理
    forum_data = state.get("forum_data")
    logger.debug(f"📂 论坛数据存在: {bool(forum_data)}")
    if forum_data:
        logger.info("🔍 检测到论坛数据，使用论坛分析器")
        logger.debug(f"📂 论坛数据详情: {forum_data}")
        forum_analyzer = ForumAnalyzer()
        logger.debug("🔧 创建论坛分析器实例")
        forum_result = forum_analyzer.analyze_forum(forum_data)
        logger.debug(f"📊 论坛分析结果: {forum_result}")
        analysis_results.append(forum_result)
        
        # 如果有媒体内容需要进一步分析
        media_requests = forum_result.get("media_requests", [])
        logger.debug(f"📎 媒体请求数量: {len(media_requests)}")
        if media_requests:
            logger.info(f"📎 发现 {len(media_requests)} 个媒体内容需要分析")
            # 将媒体请求添加到分析队列
            analysis_requests.extend(media_requests)
            logger.debug(f"📋 更新后分析请求数量: {len(analysis_requests)}")
        
        # 添加链接分析结果到分析结果中
        link_analyses = forum_result.get("link_analyses", [])
        logger.debug(f"🔗 链接分析数量: {len(link_analyses)}")
        if link_analyses:
            logger.info(f"🔗 发现 {len(link_analyses)} 个链接分析结果")
            for link_analysis in link_analyses:
                analysis_results.append(link_analysis["analysis"])
    
    # 初始化分析器
    logger.debug("🔧 初始化分析器...")
    url_analyzer = URLAnalyzer()
    image_analyzer = ImageAnalyzer()
    code_analyzer = CodeAnalyzer()
    mcp_analyzer = MCPAnalyzer()
    tavily_analyzer = TavilyAnalyzer()
    logger.debug("✅ 分析器初始化完成")
    
    for i, request in enumerate(analysis_requests):
        logger.info(f"\n🔍 分析第 {i+1} 个内容 ({request['content_type'].value})")
        logger.debug(f"📝 分析请求详情: {request}")
        
        try:
            # 首先尝试使用MCP分析器
            logger.info("🔧 尝试使用MCP分析器")
            mcp_result = mcp_analyzer.analyze_content(request['content'], request['content_type'])
            
            if mcp_result and mcp_result.get('analysis') != "MCP分析失败: None":
                logger.info("✅ MCP分析器成功返回结果")
                result = {
                    "content_type": request['content_type'],
                    "original_content": request['content'][:100] + "...",
                    "analysis": mcp_result.get('analysis', '无分析结果'),
                    "summary": mcp_result.get('analysis', '无分析结果')[:200] + "...",
                    "key_points": mcp_result.get('key_points', []),
                    "confidence": 0.9,  # MCP分析器置信度更高
                    "metadata": {**mcp_result.get('metadata', {}), "analyzer": "mcp"}
                }
                logger.debug(f"🔧 MCP分析结果: {result}")
            else:
                logger.info("🔧 MCP分析器不可用，检查是否为搜索请求")
                # 检查是否是搜索请求
                if request['content_type'] == ContentType.TEXT and request['content'].startswith("search:"):
                    logger.info("🔍 检测到搜索请求，使用Tavily分析器")
                    query = request['content'][7:].strip()  # 移除"search:"前缀
                    logger.debug(f"🔍 搜索查询: {query}")
                    
                    # 执行Tavily搜索
                    tavily_result = tavily_analyzer.search(query)
                    logger.debug(f"🔍 Tavily搜索结果: {tavily_result}")
                    
                    if tavily_result["success"]:
                        # 格式化搜索结果
                        search_content = f"搜索查询: {query}\n\n"
                        if tavily_result.get("answer"):
                            search_content += f"答案: {tavily_result['answer']}\n\n"
                        
                        search_content += "搜索结果:\n"
                        for i, result in enumerate(tavily_result["results"], 1):
                            search_content += f"{i}. {result['title']}\n"
                            search_content += f"   URL: {result['url']}\n"
                            search_content += f"   内容: {result['content'][:200]}...\n\n"
                        
                        result = {
                            "content_type": ContentType.TEXT,
                            "original_content": request['content'],
                            "analysis": search_content,
                            "summary": f"搜索查询 '{query}' 的结果摘要",
                            "key_points": [f"搜索结果 {i}: {r['title']}" for i, r in enumerate(tavily_result["results"], 1)],
                            "confidence": 0.85,
                            "metadata": {"analyzer": "tavily", "query": query}
                        }
                    else:
                        # 搜索失败，使用基础文本分析
                        logger.warning(f"❌ Tavily搜索失败: {tavily_result.get('error', '未知错误')}")
                        logger.info("📝 使用文本分析器作为备选方案")
                        analyzer = URLAnalyzer()  # 复用URL分析器的文本分析能力
                        prompt = f"请分析以下文本内容：\n{request['content']}\n\n请提供总结和关键点。"
                        logger.debug(f"📝 发送分析请求到OpenAI...")
                        analysis = analyzer.analyze_with_openai(prompt)
                        logger.debug(f"📝 文本分析结果: {analysis}")
                        
                        result = {
                            "content_type": ContentType.TEXT,
                            "original_content": request['content'][:100] + "...",
                            "analysis": analysis,
                            "summary": analysis[:200] + "...",
                            "key_points": analyzer.extractKeyPoints(analysis),
                            "confidence": 0.7,
                            "metadata": {"analyzer": "fallback"}
                        }
                else:
                    logger.info("🔧 使用传统分析器")
                if request['content_type'] == ContentType.URL:
                    logger.info("🌐 使用URL分析器")
                    logger.debug(f"🔗 分析URL: {request['content']}")
                    result = url_analyzer.analyze_url(request['content'])
                    logger.debug(f"🌐 URL分析结果: {result}")
                elif request['content_type'] == ContentType.IMAGE:
                    logger.info("🖼️ 使用图像分析器")
                    logger.debug(f"🖼️ 分析图像: {request['content']}")
                    result = image_analyzer.analyze_image(request['content'])
                    logger.debug(f"🖼️ 图像分析结果: {result}")
                elif request['content_type'] == ContentType.CODE:
                    # 从context中获取编程语言信息
                    language = request.get('context', 'Unknown')
                    logger.info(f"💻 使用代码分析器 (语言: {language})")
                    logger.debug(f"💻 分析代码: {request['content']}")
                    result = code_analyzer.analyze_code(request['content'], language)
                    logger.debug(f"💻 代码分析结果: {result}")
                else:
                    # 文本内容使用基础分析器
                    logger.info("📝 使用文本分析器")
                    logger.debug(f"📝 分析文本: {request['content']}")
                    analyzer = URLAnalyzer()  # 复用URL分析器的文本分析能力
                    prompt = f"请分析以下文本内容：\n{request['content']}\n\n请提供总结和关键点。"
                    logger.debug(f"📝 发送分析请求到OpenAI...")
                    analysis = analyzer.analyze_with_openai(prompt)
                    logger.debug(f"📝 文本分析结果: {analysis}")
                    
                    result = {
                        "content_type": ContentType.TEXT,
                        "original_content": request['content'][:100] + "...",
                        "analysis": analysis,
                        "summary": analysis[:200] + "...",
                        "key_points": analyzer.extractKeyPoints(analysis),
                        "confidence": 0.8
                    }
            
            analysis_results.append(result)
            logger.info(f"✅ 分析完成，置信度: {result['confidence']}")
            logger.debug(f"📊 当前分析结果数量: {len(analysis_results)}")
            
        except Exception as e:
            logger.error(f"❌ 分析失败: {str(e)}")
            logger.debug(f"❌ 错误详情: {e}", exc_info=True)
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
    logger.debug(f"↩️ 返回分析结果: {analysis_results}")
    
    return {
        "current_step": "analysis_completed",
        "messages": state.get("messages", []) + [f"完成 {len(analysis_results)} 个内容的分析"],
        "analysis_results": analysis_results,
        "metadata": {**state.get("metadata", {}), "analysis_completed": True}
    }


def summary_node(state: GraphState) -> Dict[str, Any]:
    """总结节点：生成综合总结和归纳"""
    logger.info("\n=== 📋 总结节点：生成综合总结 ===")
    logger.debug(f"📋 总结节点接收状态: {state}")
    
    analysis_results = state.get("analysis_results", [])
    logger.debug(f"📊 分析结果数量: {len(analysis_results)}")
    
    if not analysis_results:
        logger.warning("⚠️ 没有分析结果可以总结")
        logger.debug("↩️ 返回空总结")
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
    
    logger.debug("🔍 开始收集分析结果...")
    for result in analysis_results:
        logger.debug(f"  🔍 处理结果: {result}")
        if result['confidence'] > 0.5:  # 只包含置信度较高的结果
            all_summaries.append(result['summary'])
            
            # 对于图像分析结果，过滤掉无价值的关键点
            if result['content_type'] == ContentType.IMAGE:
                filtered_key_points = []
                for point in result['key_points']:
                    # 过滤掉无价值的关键词
                    if not any(keyword in point.lower() for keyword in [
                        "资源类型", "二进制数据", "乱码", "无标题", "无附加说明",
                        "上下文", "可信度", "价值评估", "图片下载", "无法分析"
                    ]):
                        filtered_key_points.append(point)
                all_key_points.extend(filtered_key_points)
            else:
                all_key_points.extend(result['key_points'])
                
            content_types.append(result['content_type'].value)
            logger.debug(f"    ✅ 添加高置信度结果")
        else:
            logger.debug(f"    ❌ 跳过低置信度结果 (置信度: {result['confidence']})")
    
    logger.info(f"📈 收集到 {len(all_summaries)} 个高置信度摘要和 {len(all_key_points)} 个关键点")
    logger.debug(f"📋 摘要内容: {all_summaries}")
    logger.debug(f"🔑 关键点: {all_key_points}")
    logger.debug(f"🏷️ 内容类型: {content_types}")
    
    # 生成综合总结
    combined_content = "\n".join([f"- {summary}" for summary in all_summaries])
    logger.debug(f"📝 组合内容长度: {len(combined_content)}")
    
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
    logger.debug("🤖 准备生成综合总结...")
    
    try:
        # 使用OpenAI生成最终总结
        logger.info("🤖 使用OpenAI生成综合总结")
        logger.debug("🔧 创建URL分析器实例...")
        analyzer = URLAnalyzer()  # 复用分析器
        logger.debug("📤 发送请求到OpenAI...")
        final_summary = analyzer.analyzeWithOpenai(prompt)
        logger.debug(f"📥 OpenAI响应: {final_summary[:100]}...")
        
        if "失败" in final_summary:
            logger.info("🔄 OpenAI失败，尝试使用Gemini")
            logger.debug("📤 发送请求到Gemini...")
            final_summary = analyzer.analyzeWithGemini(prompt)
            logger.debug(f"📥 Gemini响应: {final_summary[:100]}...")
        
        # 精选关键点（去重并限制数量）
        unique_key_points = []
        seen_points = set()
        logger.debug("📋 开始精选关键点...")
        
        for point in all_key_points:
            cleaned_point = point.strip().lower()
            # 检查是否已经存在相似的关键点
            is_duplicate = False
            for seen_point in seen_points:
                # 如果两个关键点的相似度很高，则认为是重复的
                if len(cleaned_point) > 10 and len(seen_point) > 10:
                    # 对于较长的关键点，使用更宽松的去重策略
                    if cleaned_point in seen_point or seen_point in cleaned_point:
                        is_duplicate = True
                        break
                else:
                    # 对于较短的关键点，使用严格的去重策略
                    if cleaned_point == seen_point:
                        is_duplicate = True
                        break
            
            if not is_duplicate and len(unique_key_points) < 10:  # 增加关键点数量限制
                unique_key_points.append(point.strip())
                seen_points.add(cleaned_point)
                logger.debug(f"  ✅ 添加关键点: {point.strip()}")
            else:
                logger.debug(f"  ❌ 跳过关键点: {point.strip()}")
        
        logger.info(f"📋 生成综合总结，包含 {len(unique_key_points)} 个关键点")
        logger.info("✅ 总结节点处理完成")
        logger.debug(f"↩️ 返回总结结果")
        
        return {
            "current_step": "summary_completed",
            "messages": state.get("messages", []) + ["生成综合总结完成"],
            "final_summary": final_summary,
            "consolidated_key_points": unique_key_points,
            "metadata": {**state.get("metadata", {}), "summary_completed": True}
        }
        
    except Exception as e:
        logger.error(f"❌ 总结生成失败: {str(e)}")
        logger.debug(f"❌ 错误详情: {e}", exc_info=True)
        
        # 降级处理：手动组合总结
        fallback_summary = f"分析了 {len(analysis_results)} 个内容，包括 {', '.join(set(content_types))}。"
        if all_summaries:
            fallback_summary += " 主要内容：" + " ".join(all_summaries[:3])
        
        logger.info("🔧 使用备用方式生成总结")
        logger.debug(f"↩️ 返回备用总结结果")
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
    logger.debug(f"📤 输出节点接收状态: {state}")
    
    final_summary = state.get("final_summary", "无可用总结")
    consolidated_key_points = state.get("consolidated_key_points", [])
    analysis_results = state.get("analysis_results", [])
    
    logger.debug(f"📝 最终总结: {final_summary[:100]}...")
    logger.debug(f"🔑 关键点数量: {len(consolidated_key_points)}")
    logger.debug(f"📊 分析结果数量: {len(analysis_results)}")
    
    # 生成最终报告
    logger.debug("📄 开始生成报告...")
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
    logger.debug("📝 添加关键要点...")
    
    for i, point in enumerate(consolidated_key_points, 1):
        report_lines.append(f"  {i}. {point}")
        logger.debug(f"  {i}. {point}")
    
    if analysis_results:
        logger.debug("📋 添加分析详情...")
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
    logger.debug("↩️ 返回输出结果")
    
    return {
        "current_step": "output_generated",
        "messages": state.get("messages", []) + ["生成最终报告完成"],
        "final_report": final_report,
        "metadata": {**state.get("metadata", {}), "output_generated": True}
    }