# 多模态内容分析API文档

## 基本信息

- **基础URL**: `http://localhost:5000`
- **数据格式**: JSON
- **字符编码**: UTF-8

## API端点

### 1. 首页和文档
```
GET /
```

**响应示例**:
```json
{
  "message": "多模态内容分析API",
  "version": "1.0.0",
  "endpoints": {
    "POST /analyze": "分析单个内容",
    "POST /analyze/batch": "批量分析多个内容",
    "POST /analyze/forum": "分析论坛数据",
    "GET /health": "健康检查",
    "GET /config/status": "API配置状态"
  },
  "supported_types": ["url", "image", "code", "text", "forum"]
}
```

### 2. 健康检查
```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. 配置状态检查
```
GET /config/status
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "api_status": {
      "openai": true,
      "gemini": true,
      "alibaba": false
    },
    "configured_apis": ["openai", "gemini"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 单个内容分析
```
POST /analyze
```

**请求格式**:
```json
{
  "content": "要分析的内容",
  "content_type": "url|image|code|text",
  "context": "可选的上下文信息"
}
```

**请求示例**:

#### 分析URL
```json
{
  "content": "https://www.python.org/about/",
  "content_type": "url",
  "context": "Python官网介绍页面"
}
```

#### 分析代码
```json
{
  "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "content_type": "code",
  "context": "Python"
}
```

#### 分析图片
```json
{
  "content": "https://example.com/image.jpg",
  "content_type": "image",
  "context": "产品截图"
}
```

#### 分析文本
```json
{
  "content": "人工智能技术正在快速发展，特别是大语言模型的出现...",
  "content_type": "text",
  "context": "AI技术发展"
}
```

**成功响应示例**:
```json
{
  "success": true,
  "data": {
    "input": {
      "content": "def fibonacci(n):\n    if n <= 1:\n        return n...",
      "content_type": "code",
      "context": "Python"
    },
    "analysis": {
      "summary": "这是一个递归实现的斐波那契数列函数...",
      "key_points": [
        "使用递归算法实现",
        "基本情况处理正确",
        "存在重复计算问题",
        "时间复杂度为O(2^n)",
        "建议使用动态规划优化"
      ],
      "details": [
        {
          "content_type": "code",
          "summary": "递归斐波那契函数实现",
          "key_points": ["递归实现", "性能问题", "优化建议"],
          "confidence": 0.9
        }
      ]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 5. 批量内容分析
```
POST /analyze/batch
```

**请求格式**:
```json
{
  "requests": [
    {
      "content": "内容1",
      "content_type": "url|image|code|text",
      "context": "上下文1"
    },
    {
      "content": "内容2",
      "content_type": "url|image|code|text", 
      "context": "上下文2"
    }
  ]
}
```

**请求示例**:
```json
{
  "requests": [
    {
      "content": "https://github.com/langchain-ai/langgraph",
      "content_type": "url",
      "context": "LangGraph项目页面"
    },
    {
      "content": "class MultiModalAgent:\n    def __init__(self):\n        pass",
      "content_type": "code",
      "context": "Python"
    },
    {
      "content": "LangGraph是一个用于构建多代理应用的框架",
      "content_type": "text",
      "context": "技术介绍"
    }
  ]
}
```

**成功响应示例**:
```json
{
  "success": true,
  "data": {
    "input": {
      "total_requests": 3,
      "content_types": ["url", "code", "text"]
    },
    "analysis": {
      "summary": "分析了LangGraph相关的多种内容类型，包括项目页面、代码示例和技术介绍...",
      "key_points": [
        "LangGraph是多代理框架",
        "支持复杂工作流构建",
        "代码结构简洁",
        "适用于AI应用开发"
      ],
      "individual_results": [
        {
          "request_index": 1,
          "content_type": "url",
          "summary": "LangGraph GitHub项目页面分析...",
          "key_points": ["开源项目", "活跃维护", "文档完善"],
          "confidence": 0.8
        },
        {
          "request_index": 2,
          "content_type": "code", 
          "summary": "简单的Python类定义...",
          "key_points": ["基础类结构", "待完善实现"],
          "confidence": 0.9
        },
        {
          "request_index": 3,
          "content_type": "text",
          "summary": "LangGraph技术概述...",
          "key_points": ["多代理框架", "构建工具"],
          "confidence": 0.8
        }
      ]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 6. 论坛数据分析
```
POST /analyze/forum
```

**请求格式**:
```json
{
  "forum_data": {
    "url": "论坛URL",
    "timestamp": "时间戳",
    "topicTitle": "主题标题",
    "totalPosts": 帖子总数,
    "posts": [
      {
        "postId": "帖子ID",
        "username": "用户名",
        "time": "发帖时间",
        "content": {
          "text": "帖子文本内容",
          "images": ["图片URL列表"],
          "codeBlocks": ["代码块列表"],
          "links": [
            {
              "text": "链接文本",
              "href": "链接URL"
            }
          ]
        }
      }
    ]
  }
}
```

**请求示例**:
```json
{
  "forum_data": {
    "url": "https://linux.do/t/topic/802519",
    "timestamp": "2025-07-22T14:14:27.271Z",
    "topicTitle": "大门敞开！上海 123 座地铁站实现"闸机常开门"，刷卡扫码秒通过",
    "totalPosts": 20,
    "posts": [
      {
        "postId": "post_1",
        "username": "雪梨纽西兰希思露甘奶迪",
        "time": "2 天",
        "content": {
          "text": "据"浦东发布"官方消息，为进一步提高车站闸机的客流通行能力...",
          "images": [
            "https://linux.do/uploads/default/optimized/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f_2_529x499.jpeg"
          ],
          "codeBlocks": [],
          "links": [
            {
              "text": "756×714 108 KB",
              "href": "https://linux.do/uploads/default/original/4X/2/c/0/2c09593c55f2b25dfffb3053001d84046c82d57f.jpeg"
            }
          ]
        }
      }
    ]
  }
}
```

**成功响应示例**:
```json
{
  "success": true,
  "data": {
    "input": {
      "content_type": "forum",
      "topic_title": "大门敞开！上海 123 座地铁站实现"闸机常开门"，刷卡扫码秒通过",
      "total_posts": 20
    },
    "analysis": {
      "summary": "论坛讨论了上海地铁123座车站实施"闸机常开门"模式的情况...",
      "key_points": [
        "上海地铁扩大"闸机常开门"试点范围",
        "新模式提高乘客通行效率",
        "系统具备防逃票机制",
        "用户对安全性和流程优化有讨论"
      ],
      "discussion_insights": {
        "main_topics": ["效率提升", "逃票担忧", "安全防控", "流程建议"],
        "user_sentiment": "积极讨论，关注实际效果",
        "key_participants": ["雪梨纽西兰希思露甘奶迪", "Crixs", "PHP 码农"]
      }
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "error": {
    "message": "错误描述信息",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 常见错误码

- `400 Bad Request`: 请求格式错误或缺少必需参数
- `404 Not Found`: API端点不存在
- `405 Method Not Allowed`: HTTP方法不被允许
- `500 Internal Server Error`: 服务器内部错误

## 支持的内容类型

1. **url**: 网页链接分析
   - 自动抓取网页内容
   - 提取标题和正文
   - 分析内容主题和价值

2. **image**: 图片分析
   - 支持网络图片URL
   - 支持本地图片路径
   - 识别图片内容和特征

3. **code**: 代码分析
   - 支持多种编程语言
   - 分析代码结构和功能
   - 提供优化建议

4. **text**: 文本分析
   - 提取关键信息
   - 生成摘要
   - 识别核心观点

5. **forum**: 论坛数据分析
   - 分析论坛主题和讨论内容
   - 识别关键用户和观点
   - 提取讨论要点和趋势

## 使用限制

- 批量请求最多支持10个内容
- 单个内容长度建议不超过10KB
- API调用频率建议不超过60次/分钟
- 需要配置至少一个AI服务API密钥

## Python客户端示例

```python
import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000"

def analyze_content(content, content_type, context=None):
    """分析单个内容"""
    url = f"{BASE_URL}/analyze"
    data = {
        "content": content,
        "content_type": content_type,
        "context": context
    }
    
    response = requests.post(url, json=data)
    return response.json()

def analyze_batch(requests_data):
    """批量分析内容"""
    url = f"{BASE_URL}/analyze/batch"
    data = {"requests": requests_data}
    
    response = requests.post(url, json=data)
    return response.json()

def analyze_forum(forum_data):
    """分析论坛数据"""
    url = f"{BASE_URL}/analyze/forum"
    data = {"forum_data": forum_data}
    
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 单个分析
    result = analyze_content(
        content="https://www.python.org",
        content_type="url",
        context="Python官网"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 批量分析
    batch_requests = [
        {
            "content": "def hello(): print('Hello, World!')",
            "content_type": "code",
            "context": "Python"
        },
        {
            "content": "人工智能正在改变世界",
            "content_type": "text",
            "context": "AI发展"
        }
    ]
    
    batch_result = analyze_batch(batch_requests)
    print(json.dumps(batch_result, indent=2, ensure_ascii=False))
```

## cURL示例

```bash
# 健康检查
curl -X GET http://localhost:5000/health

# 单个内容分析
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://www.python.org/about/",
    "content_type": "url",
    "context": "Python官网介绍"
  }'

# 批量分析
curl -X POST http://localhost:5000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "content": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "content_type": "code",
        "context": "Python"
      },
      {
        "content": "人工智能技术正在快速发展",
        "content_type": "text",
        "context": "AI技术"
      }
    ]
  }'

# 论坛数据分析
curl -X POST http://localhost:5000/analyze/forum \
  -H "Content-Type: application/json" \
  -d '{
    "forum_data": {
      "url": "https://linux.do/t/topic/802519",
      "timestamp": "2025-07-22T14:14:27.271Z",
      "topicTitle": "大门敞开！上海 123 座地铁站实现"闸机常开门"，刷卡扫码秒通过",
      "totalPosts": 20,
      "posts": [
        {
          "postId": "post_1",
          "username": "雪梨纽西兰希思露甘奶迪",
          "time": "2 天",
          "content": {
            "text": "据"浦东发布"官方消息，为进一步提高车站闸机的客流通行能力...",
            "images": [],
            "codeBlocks": [],
            "links": []
          }
        }
      ]
    }
  }'