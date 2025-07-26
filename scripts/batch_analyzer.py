#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量内容分析脚本
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.multimodal_agent import run_custom_analysis, create_analysis_request
from src.graph.state import ContentType


def load_batch_requests(file_path: str) -> List[Dict[str, Any]]:
    """从JSON文件加载批量分析请求"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('requests', data) if isinstance(data, dict) else data


def save_batch_result(result: Dict[str, Any], output_path: str):
    """保存批量分析结果"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def create_sample_requests():
    """创建示例分析请求"""
    return [
        {
            "content": "https://www.python.org/about/",
            "content_type": "url",
            "context": "Python官网介绍页面"
        },
        {
            "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "content_type": "code",
            "context": "Python"
        },
        {
            "content": "人工智能技术正在快速发展，特别是大语言模型的出现，为各行各业带来了新的机遇和挑战。",
            "content_type": "text",
            "context": "AI技术发展"
        }
    ]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量内容分析工具')
    parser.add_argument('input_file', nargs='?', help='输入的分析请求JSON文件（可选）')
    parser.add_argument('-o', '--output', help='输出分析结果的JSON文件')
    parser.add_argument('--sample', action='store_true', help='使用示例数据进行演示')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 确定分析请求来源
    if args.sample:
        requests_data = create_sample_requests()
        print("🎯 使用示例数据进行演示")
    elif args.input_file:
        try:
            requests_data = load_batch_requests(args.input_file)
            print(f"📂 从文件加载请求: {args.input_file}")
        except Exception as e:
            print(f"❌ 加载请求文件失败: {str(e)}")
            sys.exit(1)
    else:
        print("❌ 请指定输入文件或使用 --sample 参数")
        parser.print_help()
        sys.exit(1)
    
    if not isinstance(requests_data, list):
        print("❌ 请求数据格式错误：应为列表格式")
        sys.exit(1)
    
    print(f"✅ 准备分析 {len(requests_data)} 个内容")
    
    # 转换为分析请求对象
    analysis_requests = []
    for i, req_data in enumerate(requests_data):
        try:
            content = req_data["content"]
            content_type_str = req_data["content_type"]
            context = req_data.get("context")
            
            # 转换内容类型
            type_mapping = {
                "url": ContentType.URL,
                "image": ContentType.IMAGE, 
                "code": ContentType.CODE,
                "text": ContentType.TEXT
            }
            
            if content_type_str.lower() not in type_mapping:
                print(f"❌ 请求{i+1}: 不支持的内容类型 {content_type_str}")
                continue
                
            content_type = type_mapping[content_type_str.lower()]
            analysis_requests.append(create_analysis_request(content, content_type, context))
            
        except KeyError as e:
            print(f"❌ 请求{i+1}缺少必需字段: {str(e)}")
        except Exception as e:
            print(f"❌ 请求{i+1}处理错误: {str(e)}")
    
    if not analysis_requests:
        print("❌ 没有有效的分析请求")
        sys.exit(1)
    
    print(f"✅ 成功创建 {len(analysis_requests)} 个分析请求")
    
    # 执行批量分析
    print("\n🔍 开始批量分析...")
    try:
        result = run_custom_analysis(analysis_requests)
        
        if result:
            print("✅ 批量分析完成!")
            
            # 显示统计信息
            analysis_results = result.get("analysis_results", [])
            successful_count = sum(1 for r in analysis_results if r.get("confidence", 0) > 0.5)
            
            print(f"\n📊 分析统计:")
            print(f"  - 总请求数: {len(analysis_requests)}")
            print(f"  - 成功分析: {successful_count}")
            print(f"  - 失败分析: {len(analysis_requests) - successful_count}")
            
            # 显示详细结果
            if args.verbose and analysis_results:
                print(f"\n📋 详细结果:")
                for i, analysis_result in enumerate(analysis_results[:5], 1):
                    print(f"  {i}. 类型: {analysis_result['content_type'].value}")
                    print(f"     置信度: {analysis_result['confidence']:.2f}")
                    print(f"     摘要: {analysis_result['summary'][:100]}...")
                    print()
            
            # 保存结果
            if args.output:
                save_batch_result(result, args.output)
                print(f"💾 结果已保存到: {args.output}")
            else:
                # 显示简要总结
                final_summary = result.get("final_summary", "无可用总结")
                key_points = result.get("consolidated_key_points", [])
                
                print(f"\n🎯 综合总结:")
                print(final_summary[:200] + "..." if len(final_summary) > 200 else final_summary)
                
                if key_points:
                    print(f"\n🔑 关键要点:")
                    for i, point in enumerate(key_points[:5], 1):
                        print(f"  {i}. {point}")
                        
        else:
            print("❌ 批量分析执行失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 批量分析过程中出现错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()