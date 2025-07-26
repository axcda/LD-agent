#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛分析演示
"""

import sys
import os
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.analyzers.forum_analyzer import ForumAnalyzer
from src.graph.state import ContentType


def load_sample_forum_data():
    """加载示例论坛数据"""
    sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'sample_forum_data.json')
    with open(sample_data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def demo_forum_analysis():
    """演示论坛分析"""
    print("📊 论坛分析演示")
    print("=" * 50)
    
    # 加载示例数据
    try:
        forum_data = load_sample_forum_data()
        print(f"✅ 成功加载论坛数据: {forum_data.get('topicTitle', '')}")
    except Exception as e:
        print(f"❌ 加载论坛数据失败: {str(e)}")
        return
    
    # 创建论坛分析器
    analyzer = ForumAnalyzer()
    
    # 执行分析
    print("\n🔍 开始分析论坛内容...")
    result = analyzer.analyze_forum(forum_data)
    
    # 显示结果
    if result and result.get("confidence", 0) > 0.5:
        print("\n✅ 分析成功完成!")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"摘要: {result['summary'][:200]}...")
        
        if result.get("key_points"):
            print("\n🔑 关键要点:")
            for i, point in enumerate(result["key_points"][:5], 1):
                print(f"  {i}. {point}")
        
        # 显示元数据
        metadata = result.get("metadata", {})
        if metadata:
            print(f"\n📊 分析统计:")
            print(f"  - 总帖子数: {metadata.get('total_posts', 0)}")
            print(f"  - 参与用户: {metadata.get('users_count', 0)}人")
            print(f"  - 外部链接: {metadata.get('links_count', 0)}个")
            print(f"  - 图片内容: {metadata.get('images_count', 0)}张")
            
        # 显示媒体分析请求
        media_requests = result.get("media_requests", [])
        if media_requests:
            print(f"\n📎 媒体内容分析请求: {len(media_requests)}个")
            for i, req in enumerate(media_requests[:3], 1):
                print(f"  {i}. {req['content_type'].value}: {req['content'][:50]}...")
                
    else:
        print(f"\n❌ 分析失败: {result.get('analysis', '未知错误')}")


def main():
    """主函数"""
    print("🤖 多模态内容分析 - 论坛分析演示")
    print("=" * 50)
    
    demo_forum_analysis()
    
    print("\n" + "=" * 50)
    print("✅ 演示运行完成")


if __name__ == "__main__":
    main()