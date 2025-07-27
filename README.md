# LangGraph 多模态内容分析框架

## 简介

LangGraph 多模态内容分析框架是一个基于 LangGraph 的高级内容分析工具，能够处理多种类型的内容，包括 URL、图像、代码和论坛数据。该框架利用大语言模型的强大能力，对各种内容进行深度分析和理解。

## 功能特性

- **多模态内容分析**：支持 URL、图像、代码和文本内容的分析
- **论坛数据分析**：专门针对论坛数据的分析和处理
- **数据格式适配**：提供数据适配器，支持处理用户提供的 JSON 格式数据
- **MCP工具集成**：集成Smithery MCP工具，扩展分析能力
- **模块化设计**：清晰的模块划分，便于扩展和维护
- **API 接口**：提供 RESTful API 接口，便于集成到其他系统
- **命令行工具**：提供命令行工具，便于日常使用
- **Graph日志**：完整的Graph执行过程日志，便于调试和监控

## 项目结构

```
langgraph-framework/
├── README.md                    # 项目说明文档
├── pyproject.toml              # 项目配置和依赖管理
├── uv.lock                     # 依赖锁定文件
├── .env                        # 环境变量配置文件
├── .env.example                # 环境变量配置示例文件
├── .gitignore                  # Git忽略文件
├── sample_forum_data.json      # 示例论坛数据
├── DIRECTORY_STRUCTURE.md      # 原始项目结构文档
├── DIRECTORY_STRUCTURE_OPTIMIZED.md  # 优化后项目结构文档
├── docs/                       # 文档目录
│   ├── API_DOCS.md            # API文档
│   ├── QUICK_START.md         # 快速开始指南
│   ├── FORUM_DATA_ADAPTER.md  # 论坛数据适配器使用指南
│   └── MCP_INTEGRATION.md     # MCP工具集成指南
├── examples/                  # 示例代码目录
│   ├── basic_usage.py         # 基础使用示例
│   ├── forum_analysis_demo.py # 论坛分析演示
│   ├── forum_data_adapter_example.py # 论坛数据适配器示例
│   ├── graph_logging_demo.py  # Graph日志演示
│   ├── test_custom_openai_url.py  # 自定义OpenAI URL测试
│   ├── mcp_analysis_demo.py   # MCP分析演示
│   └── sample_data/           # 示例数据目录
│       └── sample_forum_data.json
├── scripts/                   # 命令行工具脚本
│   ├── forum_analyzer.py      # 论坛分析脚本
│   ├── batch_analyzer.py      # 批量分析脚本
│   └── process_user_forum_data.py # 处理用户论坛数据脚本
├── src/                       # 源代码主目录
│   ├── __init__.py
│   ├── main.py               # 主入口文件
│   ├── config.py             # 配置管理
│   ├── analyzers/            # 分析器模块
│   │   ├── __init__.py
│   │   ├── base.py           # 基础分析器
│   │   ├── forum_analyzer.py # 论坛分析器
│   │   ├── url_analyzer.py   # URL分析器
│   │   ├── image_analyzer.py # 图像分析器
│   │   ├── code_analyzer.py  # 代码分析器
│   │   └── mcp_analyzer.py   # MCP分析器
│   ├── api/                  # API相关模块
│   │   ├── __init__.py
│   │   ├── server.py         # API服务器
│   │   └── client.py         # API客户端
│   ├── core/                 # 核心模块
│   │   ├── __init__.py
│   │   └── multimodal_agent.py # 多模态代理
│   ├── graph/                # 图相关模块
│   │   ├── __init__.py
│   │   ├── workflow.py       # 工作流定义
│   │   ├── nodes.py          # 节点定义
│   │   └── state.py          # 状态管理
│   ├── utils/                # 工具模块
│   │   ├── __init__.py
│   │   ├── helpers.py        # 辅助函数
│   │   └── forum_data_adapter.py # 论坛数据适配器
│   └── utils/                # 工具模块
└── tests/                    # 测试目录
    ├── __init__.py
    ├── test_simple.py        # 简单测试
    ├── test_api.py           # API测试
    ├── test_forum_data_adapter.py # 论坛数据适配器测试
    └── test_user_data_processing.py # 用户数据处理测试
```

## 安装和配置

### 环境要求

- Python 3.8+
- uv (用于依赖管理)

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd langgraph-framework

# 安装依赖
uv sync
```

### 配置环境变量

复制 `.env.example` 文件为 `.env` 并配置相应的 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API 密钥
```

#### OpenAI API配置

在 `.env` 文件中配置您的 OpenAI API 密钥：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

##### 多密钥配置（推荐）

为了防止单个API密钥达到使用限制，您可以配置多个API密钥，系统会在遇到限制时自动切换：

```env
OPENAI_API_KEYS=your_openai_api_key_1,your_openai_api_key_2,your_openai_api_key_3
```

系统会按顺序使用这些密钥，并在遇到API限制时自动切换到下一个密钥。

#### 自定义OpenAI基础URL（可选）

如果您需要使用自定义的OpenAI API端点（例如代理服务器），可以配置 `OPENAI_BASE_URL`：

```env
OPENAI_BASE_URL=https://api.openai.com/v1/responses
```

默认情况下，使用标准的OpenAI API端点 `https://api.openai.com/v1`。

## 使用方法

### 命令行工具

#### 基本使用

```bash
# 运行基础使用示例
uv run python examples/basic_usage.py

# 运行论坛分析演示
uv run python examples/forum_analysis_demo.py

# 运行Graph日志演示
uv run python examples/graph_logging_demo.py

# 测试自定义OpenAI URL配置
uv run python examples/test_custom_openai_url.py

#### MCP工具使用

```bash
# 运行MCP分析演示
uv run python examples/mcp_analysis_demo.py
```
```

#### 论坛数据处理

```bash
# 处理用户提供的JSON格式论坛数据
uv run python scripts/process_user_forum_data.py input.json -o output.json --analyze

# 运行论坛数据适配器示例
uv run python examples/forum_data_adapter_example.py
```

#### 批量分析

```bash
# 批量分析
uv run python scripts/batch_analyzer.py --sample --verbose
```

### API 服务

```bash
# 启动API服务器
uv run python src/api/server.py
```

### Graph日志

框架现在包含了完整的Graph执行过程日志，可以帮助您更好地理解工作流的执行过程：

1. **工作流创建日志**：在 `src/graph/workflow.py` 中添加了工作流创建和编译的日志
2. **节点执行日志**：在 `src/graph/nodes.py` 中为每个节点添加了详细的执行日志
3. **Agent执行日志**：在 `src/core/multimodal_agent.py` 中添加了Agent执行过程的日志
4. **API调用日志**：在 `src/api/server.py` 中添加了API请求处理的日志

通过这些日志，您可以清楚地看到：
- Graph工作流的创建和编译过程
- 每个节点的执行情况
- 分析请求的处理流程
- API请求的处理过程

### 论坛数据适配器

项目提供了一个论坛数据适配器，可以处理用户提供的 JSON 格式数据，并将其转换为项目内部使用的格式。详细使用方法请参考 [FORUM_DATA_ADAPTER.md](docs/FORUM_DATA_ADAPTER.md)。

## 测试

```bash
# 运行所有测试
uv run python -m tests.test_simple
uv run python -m tests.test_api
uv run python -m tests.test_forum_data_adapter
uv run python -m tests.test_user_data_processing
```

## 文档

- [快速开始指南](docs/QUICK_START.md)
- [API 文档](docs/API_DOCS.md)
- [论坛数据适配器使用指南](docs/FORUM_DATA_ADAPTER.md)
- [MCP工具集成指南](docs/MCP_INTEGRATION.md)
- [优化后的项目结构](DIRECTORY_STRUCTURE_OPTIMIZED.md)

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

[MIT License](LICENSE)