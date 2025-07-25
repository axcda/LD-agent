# 多模态内容分析API - 快速开始

## 🚀 启动API服务器

```bash
# 启动服务器
uv run python api_server.py

# 服务器将在 http://localhost:8888 启动
```

## 📝 JSON接口使用

### 单个内容分析

```bash
curl -X POST http://localhost:8888/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "content_type": "code",
    "context": "Python"
  }'
```

### 批量分析

```bash
curl -X POST http://localhost:8888/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "content": "https://www.python.org",
        "content_type": "url",
        "context": "Python官网"
      },
      {
        "content": "人工智能正在改变世界",
        "content_type": "text",
        "context": "AI发展"
      }
    ]
  }'
```

## 🐍 Python客户端

```python
from api_client_demo import MultiModalAnalysisClient

client = MultiModalAnalysisClient()

# 分析代码
result = client.analyze_code(
    "def hello(): print('Hello!')", 
    "Python"
)

# 分析文本  
result = client.analyze_text(
    "这是一段测试文本",
    "测试用例"
)

# 分析URL
result = client.analyze_url(
    "https://www.example.com",
    "示例网站"
)

print(result)
```

## 📊 响应格式

```json
{
  "success": true,
  "data": {
    "input": {
      "content": "输入内容摘要...",
      "content_type": "code",
      "context": "Python"
    },
    "analysis": {
      "summary": "分析总结...",
      "key_points": [
        "关键点1",
        "关键点2"
      ],
      "details": [
        {
          "content_type": "code",
          "summary": "详细分析...",
          "confidence": 0.9
        }
      ]
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## 🛠️ 支持的内容类型

- `url`: 网页链接分析
- `image`: 图片内容分析  
- `code`: 代码块分析
- `text`: 文本总结分析

## ⚙️ 配置

在 `.env` 文件中配置API密钥：

```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key  
ALIBABA_API_KEY=your_alibaba_key
```

## 📖 完整文档

详细的API文档请参考 `API_DOCS.md`