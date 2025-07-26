# 论坛数据适配器使用指南

## 概述

论坛数据适配器 (`ForumDataAdapter`) 是一个用于处理用户提供的JSON格式论坛数据的工具，它可以将用户数据转换为项目内部使用的 `ForumData` 格式，以便进行后续的分析和处理。

## 功能特性

1. **数据格式转换**：将用户提供的JSON格式转换为项目内部的 `ForumData` 格式
2. **数据验证**：验证用户提供的数据格式是否正确
3. **文件操作**：支持从JSON文件加载数据和将数据保存到JSON文件
4. **便捷函数**：提供简单的函数接口供快速使用

## 数据格式说明

### 用户提供的JSON格式

```json
{
  "url": "https://example.com/forum/topic",
  "timestamp": "2025-07-22T14:14:27.271Z",
  "topicTitle": "论坛主题",
  "replyInfo": "",
  "totalPosts": 20,
  "posts": [
    {
      "postId": "post_1",
      "username": "用户名",
      "time": "2 天",
      "content": {
        "text": "帖子内容",
        "images": ["https://example.com/image.jpg"],
        "codeBlocks": [],
        "links": [
          {
            "text": "链接文本",
            "href": "https://example.com"
          }
        ]
      }
    }
  ]
}
```

### 项目内部ForumData格式

```python
class ForumData(TypedDict):
    """论坛数据结构"""
    url: str
    timestamp: str
    topic_title: str  # 注意字段名差异
    total_posts: int  # 注意字段名差异
    posts: List[Dict[str, Any]]
```

## 使用方法

### 1. 基本数据转换

```python
from src.utils.forum_data_adapter import ForumDataAdapter

# 用户数据
user_data = {
    "url": "https://example.com/forum/topic",
    "timestamp": "2025-07-22T14:14:27.271Z",
    "topicTitle": "论坛主题",
    "totalPosts": 20,
    "posts": [...]
}

# 转换数据
forum_data = ForumDataAdapter.convert_user_data_to_forum_data(user_data)
```

### 2. 数据验证

```python
# 验证用户数据格式
is_valid = ForumDataAdapter.validate_user_data(user_data)
if is_valid:
    print("数据格式正确")
else:
    print("数据格式不正确")
```

### 3. 文件操作

```python
# 从JSON文件加载数据
forum_data = ForumDataAdapter.load_from_json_file("forum_data.json")

# 保存数据到JSON文件
ForumDataAdapter.save_forum_data_to_json(forum_data, "converted_data.json")
```

### 4. 便捷函数

```python
from src.utils.forum_data_adapter import (
    convert_user_forum_data,
    load_forum_data_from_json
)

# 使用便捷函数
forum_data = convert_user_forum_data(user_data)
forum_data = load_forum_data_from_json("forum_data.json")
```

## 运行示例

项目提供了完整的示例程序来演示适配器的使用：

```bash
# 运行完整演示
python examples/forum_data_adapter_example.py

# 处理指定的JSON文件
python examples/forum_data_adapter_example.py path/to/your/forum_data.json
```

## 运行测试

可以运行测试来验证适配器的功能：

```bash
python -m tests.test_forum_data_adapter
```

## 集成到项目中

适配器可以轻松集成到项目的分析流程中：

```python
from src.utils.forum_data_adapter import load_forum_data_from_json
from src.analyzers.forum_analyzer import ForumAnalyzer

# 加载并转换数据
forum_data = load_forum_data_from_json("forum_data.json")

# 使用论坛分析器分析数据
analyzer = ForumAnalyzer()
analysis_result = analyzer.analyze_forum(forum_data)
```

## 注意事项

1. 确保用户提供的JSON数据包含所有必需字段
2. 适配器会自动处理字段名的转换（如 `topicTitle` → `topic_title`）
3. 适配器不会修改原始数据结构，而是创建新的转换后的数据
4. 在处理大文件时，注意内存使用情况