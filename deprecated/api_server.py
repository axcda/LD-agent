from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, List
import traceback
import json
from datetime import datetime

from multimodal_agent import run_custom_analysis, create_analysis_request
from graph.state import ContentType
from config import config


app = Flask(__name__)
CORS(app)  # 允许跨域请求


def create_error_response(message: str, status_code: int = 400) -> tuple:
    """创建错误响应"""
    return jsonify({
        "success": False,
        "error": {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }), status_code


def create_success_response(data: Any) -> Dict[str, Any]:
    """创建成功响应"""
    return jsonify({
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })


def validate_content_type(content_type: str) -> ContentType:
    """验证并转换内容类型"""
    type_mapping = {
        "url": ContentType.URL,
        "image": ContentType.IMAGE, 
        "code": ContentType.CODE,
        "text": ContentType.TEXT
    }
    
    if content_type.lower() not in type_mapping:
        raise ValueError(f"不支持的内容类型: {content_type}")
    
    return type_mapping[content_type.lower()]


@app.route("/", methods=["GET"])
def home():
    """API首页"""
    return jsonify({
        "message": "多模态内容分析API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "分析单个内容",
            "POST /analyze/batch": "批量分析多个内容",
            "GET /health": "健康检查",
            "GET /config/status": "API配置状态"
        },
        "supported_types": ["url", "image", "code", "text"]
    })


@app.route("/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/config/status", methods=["GET"])
def config_status():
    """获取API配置状态"""
    try:
        status = config.validate_config()
        return create_success_response({
            "api_status": status,
            "configured_apis": [api for api, configured in status.items() if configured]
        })
    except Exception as e:
        return create_error_response(f"配置检查失败: {str(e)}", 500)


@app.route("/analyze", methods=["POST"])
def analyze_single():
    """
    分析单个内容
    
    JSON格式:
    {
        "content": "要分析的内容",
        "content_type": "url|image|code|text",
        "context": "可选的上下文信息"
    }
    """
    try:
        # 解析JSON数据
        if not request.is_json:
            return create_error_response("请求必须是JSON格式")
        
        data = request.get_json()
        
        # 验证必需字段
        if "content" not in data:
            return create_error_response("缺少必需字段: content")
        
        if "content_type" not in data:
            return create_error_response("缺少必需字段: content_type")
        
        content = data["content"]
        content_type_str = data["content_type"]
        context = data.get("context")
        
        # 验证内容不为空
        if not content or not content.strip():
            return create_error_response("content字段不能为空")
        
        # 验证内容类型
        try:
            content_type = validate_content_type(content_type_str)
        except ValueError as e:
            return create_error_response(str(e))
        
        # 创建分析请求
        analysis_request = create_analysis_request(content, content_type, context)
        
        # 执行分析
        result = run_custom_analysis([analysis_request])
        
        if not result:
            return create_error_response("分析执行失败", 500)
        
        # 格式化响应数据
        response_data = {
            "input": {
                "content": content[:100] + "..." if len(content) > 100 else content,
                "content_type": content_type_str,
                "context": context
            },
            "analysis": {
                "summary": result.get("final_summary"),
                "key_points": result.get("consolidated_key_points", []),
                "details": []
            }
        }
        
        # 添加详细分析结果
        analysis_results = result.get("analysis_results", [])
        for analysis_result in analysis_results:
            response_data["analysis"]["details"].append({
                "content_type": analysis_result["content_type"].value,
                "summary": analysis_result["summary"],
                "key_points": analysis_result["key_points"],
                "confidence": analysis_result["confidence"]
            })
        
        return create_success_response(response_data)
        
    except Exception as e:
        return create_error_response(f"服务器内部错误: {str(e)}", 500)


@app.route("/analyze/batch", methods=["POST"])
def analyze_batch():
    """
    批量分析多个内容
    
    JSON格式:
    {
        "requests": [
            {
                "content": "内容1",
                "content_type": "url",
                "context": "上下文1"
            },
            {
                "content": "内容2", 
                "content_type": "code",
                "context": "Python"
            }
        ]
    }
    """
    try:
        # 解析JSON数据
        if not request.is_json:
            return create_error_response("请求必须是JSON格式")
        
        data = request.get_json()
        
        # 验证必需字段
        if "requests" not in data:
            return create_error_response("缺少必需字段: requests")
        
        requests_data = data["requests"]
        
        if not isinstance(requests_data, list):
            return create_error_response("requests字段必须是数组")
        
        if len(requests_data) == 0:
            return create_error_response("requests数组不能为空")
        
        if len(requests_data) > 10:  # 限制批量请求数量
            return create_error_response("批量请求数量不能超过10个")
        
        # 验证和创建分析请求
        analysis_requests = []
        
        for i, req_data in enumerate(requests_data):
            if "content" not in req_data or "content_type" not in req_data:
                return create_error_response(f"请求{i+1}缺少必需字段")
            
            content = req_data["content"]
            content_type_str = req_data["content_type"]
            context = req_data.get("context")
            
            if not content or not content.strip():
                return create_error_response(f"请求{i+1}的content字段不能为空")
            
            try:
                content_type = validate_content_type(content_type_str)
            except ValueError as e:
                return create_error_response(f"请求{i+1}: {str(e)}")
            
            analysis_requests.append(create_analysis_request(content, content_type, context))
        
        # 执行批量分析
        result = run_custom_analysis(analysis_requests)
        
        if not result:
            return create_error_response("批量分析执行失败", 500)
        
        # 格式化响应数据
        response_data = {
            "input": {
                "total_requests": len(requests_data),
                "content_types": list(set(req["content_type"] for req in requests_data))
            },
            "analysis": {
                "summary": result.get("final_summary"),
                "key_points": result.get("consolidated_key_points", []),
                "individual_results": []
            }
        }
        
        # 添加每个请求的详细结果
        analysis_results = result.get("analysis_results", [])
        for i, analysis_result in enumerate(analysis_results):
            response_data["analysis"]["individual_results"].append({
                "request_index": i + 1,
                "content_type": analysis_result["content_type"].value,
                "summary": analysis_result["summary"],
                "key_points": analysis_result["key_points"],
                "confidence": analysis_result["confidence"]
            })
        
        return create_success_response(response_data)
        
    except Exception as e:
        return create_error_response(f"服务器内部错误: {str(e)}", 500)


@app.errorhandler(404)
def not_found(error):
    return create_error_response("API端点不存在", 404)


@app.errorhandler(405)
def method_not_allowed(error):
    return create_error_response("HTTP方法不被允许", 405)


@app.errorhandler(500)
def internal_error(error):
    return create_error_response("服务器内部错误", 500)


if __name__ == "__main__":
    print("🚀 启动多模态内容分析API服务器")
    print("=" * 50)
    
    # 检查配置
    try:
        status = config.validate_config()
        configured_apis = [api for api, configured in status.items() if configured]
        
        if not configured_apis:
            print("⚠️ 警告：未检测到任何API配置")
            print("请在.env文件中配置API密钥")
        else:
            print(f"✅ 已配置API: {', '.join(configured_apis)}")
        
        print("\n📋 API端点:")
        print("  GET  /                - API首页和文档")
        print("  GET  /health          - 健康检查")
        print("  GET  /config/status   - 配置状态")
        print("  POST /analyze         - 单个内容分析") 
        print("  POST /analyze/batch   - 批量内容分析")
        
        print(f"\n🌐 服务器将在 http://localhost:9980 启动")
        print("=" * 50)
        
        app.run(host="0.0.0.0", port=9980, debug=False)
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("请检查配置和依赖")