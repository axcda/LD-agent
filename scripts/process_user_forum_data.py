#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理用户论坛数据脚本
提供命令行接口来处理用户提供的JSON格式论坛数据
"""

import sys
import os
import json
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.forum_data_adapter import (
    ForumDataAdapter,
    convert_user_forum_data,
    load_forum_data_from_json
)
from src.analyzers.forum_analyzer import ForumAnalyzer


def process_forum_data(input_file: str, output_file: str = None, analyze: bool = False):
    """
    处理论坛数据
    
    Args:
        input_file: 输入JSON文件路径
        output_file: 输出JSON文件路径（可选）
        analyze: 是否进行分析
    """
    print(f"📂 处理文件: {input_file}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误: 文件不存在: {input_file}")
        return False
    
    try:
        # 加载并转换数据
        print("🔄 加载并转换数据...")
        forum_data = load_forum_data_from_json(input_file)
        print("✅ 数据加载和转换成功")
        print(f"   主题: {forum_data['topic_title']}")
        print(f"   帖子数: {forum_data['total_posts']}")
        
        # 保存转换后的数据
        if output_file:
            print(f"💾 保存转换后的数据到: {output_file}")
            ForumDataAdapter.save_forum_data_to_json(forum_data, output_file)
            print("✅ 数据保存成功")
        
        # 分析数据
        if analyze:
            print("🔍 分析论坛数据...")
            analyzer = ForumAnalyzer()
            analysis_result = analyzer.analyze_forum(forum_data)
            
            if analysis_result.get('confidence', 0) > 0.5:
                print("✅ 论坛分析完成")
                print(f"   置信度: {analysis_result['confidence']}")
                print(f"   摘要: {analysis_result.get('summary', '')[:100]}...")
                
                # 保存分析结果
                analysis_output = output_file.replace('.json', '_analysis.json') if output_file else 'forum_analysis_result.json'
                print(f"💾 保存分析结果到: {analysis_output}")
                
                # 创建分析结果的简化版本用于保存
                simplified_result = {
                    "topic": forum_data['topic_title'],
                    "total_posts": forum_data['total_posts'],
                    "analysis": {
                        "summary": analysis_result.get('summary', ''),
                        "key_points": analysis_result.get('key_points', []),
                        "confidence": analysis_result.get('confidence', 0)
                    }
                }
                
                with open(analysis_output, 'w', encoding='utf-8') as f:
                    json.dump(simplified_result, f, ensure_ascii=False, indent=2)
                print("✅ 分析结果保存成功")
            else:
                print("❌ 论坛分析失败")
                print(f"   错误信息: {analysis_result.get('analysis', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="处理用户提供的JSON格式论坛数据")
    parser.add_argument("input_file", help="输入JSON文件路径")
    parser.add_argument("-o", "--output", help="输出JSON文件路径")
    parser.add_argument("-a", "--analyze", action="store_true", help="是否进行论坛分析")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    print("🚀 论坛数据处理工具")
    print("=" * 50)
    
    if args.verbose:
        print(f"输入文件: {args.input_file}")
        print(f"输出文件: {args.output}")
        print(f"执行分析: {args.analyze}")
    
    success = process_forum_data(args.input_file, args.output, args.analyze)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 处理完成")
        sys.exit(0)
    else:
        print("❌ 处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()