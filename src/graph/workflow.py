from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes import input_node, analysis_node, summary_node, output_node
import logging

# 配置日志
import os
# 从环境变量获取日志级别，默认为INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


def create_multimodal_workflow() -> StateGraph:
    """创建多模态内容分析工作流"""
    logger.info("🔧 开始创建工作流...")
    logger.debug("🔧 创建状态图对象...")
    
    # 创建状态图
    workflow = StateGraph(GraphState)
    logger.info("📊 状态图创建完成")
    logger.debug(f"📊 状态图类型: {type(workflow)}")
    
    # 添加节点
    logger.info("➕ 正在添加节点...")
    logger.debug("➕ 添加输入节点...")
    workflow.add_node("input", input_node)
    logger.debug("➕ 添加分析节点...")
    workflow.add_node("analysis", analysis_node)
    logger.debug("➕ 添加总结节点...")
    workflow.add_node("summary", summary_node)
    logger.debug("➕ 添加输出节点...")
    workflow.add_node("output", output_node)
    logger.info("✅ 节点添加完成: input, analysis, summary, output")
    
    # 设置入口点
    logger.info("📍 设置入口点为 'input'")
    logger.debug("📍 调用set_entry_point方法...")
    workflow.set_entry_point("input")
    logger.debug("📍 入口点设置完成")
    
    # 添加边（定义节点之间的连接）
    logger.info("🔗 正在连接节点...")
    logger.debug("🔗 连接 input -> analysis...")
    workflow.add_edge("input", "analysis")
    logger.debug("🔗 连接 analysis -> summary...")
    workflow.add_edge("analysis", "summary")
    logger.debug("🔗 连接 summary -> output...")
    workflow.add_edge("summary", "output")
    logger.debug("🔗 连接 output -> END...")
    workflow.add_edge("output", END)
    logger.info("✅ 节点连接完成")
    
    logger.info("✅ 工作流创建完成")
    logger.debug(f"✅ 返回工作流对象: {type(workflow)}")
    return workflow


def compile_multimodal_workflow() -> callable:
    """编译多模态分析工作流以便执行"""
    logger.info("🔨 正在编译工作流...")
    workflow = create_multimodal_workflow()
    compiled_workflow = workflow.compile()
    logger.info("✅ 工作流编译完成")
    return compiled_workflow


# 保持向后兼容
def create_workflow() -> StateGraph:
    """保持向后兼容的工作流创建函数"""
    logger.info("🔄 使用向后兼容的工作流创建函数")
    return create_multimodal_workflow()


def compile_workflow() -> callable:
    """保持向后兼容的工作流编译函数"""
    logger.info("🔄 使用向后兼容的工作流编译函数")
    return compile_multimodal_workflow()