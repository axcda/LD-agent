from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes import input_node, analysis_node, summary_node, output_node


def create_multimodal_workflow() -> StateGraph:
    """创建多模态内容分析工作流"""
    
    # 创建状态图
    workflow = StateGraph(GraphState)
    
    # 添加节点
    workflow.add_node("input", input_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("output", output_node)
    
    # 设置入口点
    workflow.set_entry_point("input")
    
    # 添加边（定义节点之间的连接）
    workflow.add_edge("input", "analysis")
    workflow.add_edge("analysis", "summary")
    workflow.add_edge("summary", "output")
    workflow.add_edge("output", END)
    
    return workflow


def compile_multimodal_workflow() -> callable:
    """编译多模态分析工作流以便执行"""
    workflow = create_multimodal_workflow()
    return workflow.compile()


# 保持向后兼容
def create_workflow() -> StateGraph:
    """保持向后兼容的工作流创建函数"""
    return create_multimodal_workflow()


def compile_workflow() -> callable:
    """保持向后兼容的工作流编译函数"""
    return compile_multimodal_workflow()