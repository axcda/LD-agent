# Agents 设计文档

## 概述

LangGraph 多模态内容分析框架采用基于 LangGraph 的 Agent 架构，通过状态图（StateGraph）管理复杂的工作流程。系统中的 Agents 负责协调不同类型内容的分析任务，包括 URL、图像、代码、文本和论坛数据。

## 核心 Agents

### MultimodalAgent

`MultimodalAgent` 是系统的核心代理，负责协调整个多模态内容分析流程。

**主要功能：**
- 接收和处理多种类型的内容分析请求
- 编排基于 LangGraph 的工作流
- 管理分析任务的执行顺序和状态
- 整合各个分析器的结果生成综合报告

**关键方法：**
- `run_multimodal_analysis()`: 运行多模态内容分析示例
- `run_custom_analysis(requests)`: 运行自定义分析
- `analyze_url(url, context)`: 分析单个 URL
- `analyze_image(image_path, context)`: 分析单个图片
- `analyze_code(code, language)`: 分析单个代码块
- `analyze_text(text, context)`: 分析单个文本

**文件位置：** `src/core/multimodal_agent.py`

## 工作流系统

系统采用 LangGraph 的状态图（StateGraph）来定义和管理工作流。工作流包含四个核心节点：

### 1. 输入节点 (input_node)
**功能：** 处理分析请求，验证输入数据的有效性
**文件：** `src/graph/nodes.py`

### 2. 分析节点 (analysis_node)
**功能：** 执行多模态内容分析，调用相应的分析器处理不同类型的内容
**文件：** `src/graph/nodes.py`

### 3. 总结节点 (summary_node)
**功能：** 生成综合总结和归纳，整合所有分析结果
**文件：** `src/graph/nodes.py`

### 4. 输出节点 (output_node)
**功能：** 格式化并展示最终结果，生成分析报告
**文件：** `src/graph/nodes.py`

**工作流文件：** `src/graph/workflow.py`

## 分析器 (Analyzers)

系统包含多种专用分析器，每种分析器负责处理特定类型的内容：

### ContentAnalyzer (基类)
所有分析器的基类，提供通用的 AI 分析功能。
**文件：** `src/analyzers/base.py`

### URLAnalyzer
负责分析网页内容，提取关键信息和要点。
**文件：** `src/analyzers/url_analyzer.py`

### ImageAnalyzer
负责分析图像内容，提取图像中的信息。
**文件：** `src/analyzers/image_analyzer.py`

### CodeAnalyzer
负责分析代码内容，提供代码理解和分析。
**文件：** `src/analyzers/code_analyzer.py`

### ForumAnalyzer
专门用于分析论坛数据，处理帖子、用户和讨论内容。
**文件：** `src/analyzers/forum_analyzer.py`

## 状态管理

系统使用 `GraphState` 来管理整个工作流的状态，确保各节点间的数据传递和状态一致性。

**状态结构：**
- `analysis_requests`: 分析请求列表
- `analysis_results`: 分析结果列表
- `final_summary`: 最终总结
- `consolidated_key_points`: 整合的关键点
- `current_step`: 当前步骤
- `messages`: 消息列表
- `metadata`: 元数据

**文件：** `src/graph/state.py`

## 配置管理

系统通过 `Config` 类管理各种 API 密钥和配置参数，支持多密钥自动切换功能。

**支持的配置：**
- OpenAI API 密钥（支持多个）
- Google API 密钥
- 阿里百炼 API 密钥
- 自定义 OpenAI 基础 URL

**文件：** `src/config.py`

## 使用方法

### 基本使用
```python
from src.core.multimodal_agent import run_multimodal_analysis

# 运行多模态分析示例
result = run_multimodal_analysis()
```

### 自定义分析
```python
from src.core.multimodal_agent import analyze_url, analyze_code

# 分析 URL
url_result = analyze_url("https://example.com", "示例网站")

# 分析代码
code_result = analyze_code("print('Hello, World!')", "Python")
```

### 交互式模式
```python
from src.main import interactive_mode

# 启动交互式分析模式
interactive_mode()
```

## 扩展性

系统设计具有良好的扩展性，可以通过以下方式添加新的分析功能：

1. 创建新的分析器类，继承自 `ContentAnalyzer`
2. 在工作流中添加新的处理节点（如需要）
3. 更新状态管理以支持新的数据类型
4. 在主入口添加新的调用接口

这种模块化设计使得系统可以轻松支持新的内容类型和分析需求。