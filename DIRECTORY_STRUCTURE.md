langgraph-framework/
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── uv.lock
│
├── src/                           # 主要源代码
│   ├── __init__.py
│   ├── config.py                  # 配置管理
│   ├── main.py                    # 主程序入口
│   │
│   ├── core/                      # 核心功能
│   │   ├── __init__.py
│   │   ├── multimodal_agent.py    # 主要的多模态代理
│   │   └── types.py               # 通用类型定义
│   │
│   ├── analyzers/                 # 内容分析器模块
│   │   ├── __init__.py
│   │   ├── base.py                # 基础分析器
│   │   ├── url_analyzer.py        # URL分析器
│   │   ├── image_analyzer.py      # 图片分析器  
│   │   ├── code_analyzer.py       # 代码分析器
│   │   └── forum_analyzer.py      # 论坛分析器
│   │
│   ├── graph/                     # LangGraph相关
│   │   ├── __init__.py
│   │   ├── state.py               # 状态定义
│   │   ├── nodes.py               # 节点实现
│   │   └── workflow.py            # 工作流定义
│   │
│   ├── api/                       # API相关
│   │   ├── __init__.py
│   │   ├── server.py              # Flask API服务器
│   │   └── client.py              # API客户端
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── preprocessing.py       # 数据预处理
│       └── validation.py          # 数据验证
│
├── scripts/                       # 脚本和工具
│   ├── forum_analyzer.py          # 论坛分析脚本
│   └── batch_analyzer.py          # 批量分析脚本
│
├── tests/                         # 测试代码
│   ├── __init__.py
│   ├── test_api.py                # API测试
│   ├── test_analyzers.py          # 分析器测试
│   └── test_graph.py              # 图工作流测试
│
├── examples/                      # 示例和演示
│   ├── basic_usage.py             # 基础使用示例
│   ├── forum_analysis_demo.py     # 论坛分析演示
│   └── sample_data/               # 示例数据
│       └── sample_forum_data.json
│
└── docs/                          # 文档
    ├── API_DOCS.md
    ├── QUICK_START.md
    └── architecture.md