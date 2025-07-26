#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛分析脚本 - 命令行工具
"""

import sys
import os
import json
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.analyzers.forum_analyzer import ForumAnalyzer
from src.graph.state import ContentType


def load_forum_data(file_path: str) -> dict:
    """加载论坛数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_analysis_result(result: dict, output_path: str):
    """保存分析结果"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='论坛内容分析工具')
    parser.add_argument('input_file', help='输入的论坛数据JSON文件')
    parser.add_argument('-o', '--output', help='输出分析结果的JSON文件')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    try:
        # 加载论坛数据
        print(f"📂 加载论坛数据: {args.input_file}")
        forum_data = load_forum_data(args.input_file)
        print(f"✅ 数据加载成功: {forum_data.get('topicTitle', '')}")
        
        # 创建分析器并执行分析
        print("🔍 开始分析...")
        analyzer = ForumAnalyzer()
        result = analyzer.analyze_forum(forum_data)
        
        if result and result.get("confidence", 0) > 0.5:
            print("✅ 分析完成!")
            
            # 显示基本信息
            print(f"置信度: {result['confidence']:.2f}")
            print(f"摘要: {result['summary'][:100]}...")
            
            if args.verbose:
                print("\n🔑 关键要点:")
                for i, point in enumerate(result["key_points"][:10], 1):
                    print(f"  {i}. {point}")
                
                metadata = result.get("metadata", {})
                if metadata:
                    print(f"\n📊 统计信息:")
                    print(f"  - 总帖子数: {metadata.get('total_posts', 0)}")
                    print(f"  - 参与用户: {metadata.get('users_count', 0)}人")
                    print(f"  - 外部链接: {metadata.get('links_count', 0)}个")
                    print(f"  - 图片内容: {metadata.get('images_count', 0)}张")
            
            # 保存结果
            if args.output:
                save_analysis_result(result, args.output)
                print(f"💾 结果已保存到: {args.output}")
            else:
                # 如果没有指定输出文件，显示简要结果
                print(f"\n📋 分析结果:")
                print(f"  - 主题: {result.get('original_content', '')}")
                print(f"  - 关键点数: {len(result.get('key_points', []))}")
                print(f"  - 媒体请求数: {len(result.get('media_requests', []))}")
                
        else:
            print(f"❌ 分析失败: {result.get('analysis', '未知错误')}")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"❌ 文件未找到: {args.input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()