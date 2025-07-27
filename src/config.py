import os
from dotenv import load_dotenv
from typing import Optional
import openai
import google.generativeai as genai
import dashscope
import requests
import json
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# 定义常见的OpenAI API限制错误消息
OPENAI_RATE_LIMIT_ERRORS = [
    "rate_limit_exceeded",
    "insufficient_quota",
    "quota_exceeded",
    "Rate limit reached",
    "You exceeded your current quota",
    "Request rate limit exceeded"
]

class CustomOpenAIClient:
    """自定义OpenAI客户端，用于处理非标准端点"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.chat = self.ChatCompletions(self)
    
    class ChatCompletions:
        def __init__(self, client):
            self.client = client
            self.completions = self.Completions(client)
        
        class Completions:
            def __init__(self, client):
                self.client = client
            
            def create(self, model: str, messages: list, max_tokens: int = None, temperature: float = None, **kwargs):
                """创建聊天完成请求 - 智能适配不同API格式"""
                headers = {
                    'Authorization': f'Bearer {self.client.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # 检查是否是特殊的 Responses API 端点
                is_responses_api = '/v1/responses' in self.client.base_url
                
                if is_responses_api:
                    # --- 这部分逻辑保持不变，用于处理特殊的 /v1/responses API ---
                    user_input = ""
                    for message in messages:
                        if message.get('role') == 'user':
                            user_input = message.get('content', '')
                    
                    data = {
                        'model': model,
                        'input': user_input
                    }
                    
                    if temperature is not None:
                        data['temperature'] = temperature
                    
                    supported_params = ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']
                    for key, value in kwargs.items():
                        if key in supported_params and value is not None:
                            data[key] = value
                    
                    endpoint_url = self.client.base_url
                else:
                    # --- 这部分是为标准 OpenAI API 修正的逻辑 ---
                    data = {
                        'model': model,
                        'messages': messages
                    }
                    
                    if max_tokens is not None:
                        data['max_tokens'] = max_tokens
                    if temperature is not None:
                        data['temperature'] = temperature
                    
                    data.update(kwargs)
                    
                    # 修正后的URL构建逻辑
                    base_url = self.client.base_url.rstrip('/')
                    
                    if base_url.endswith('/chat/completions'):
                        # 如果base_url已经包含了完整的端点
                        endpoint_url = base_url
                    else:
                        # 否则，我们假设它是一个基础URL，需要附加标准端点
                        # 示例: "https://api.openai.com/v1" -> "https://api.openai.com/v1/chat/completions"
                        endpoint_url = f"{base_url}/chat/completions"
                
                try:
                    logger.debug(f"🔗 请求端点: {endpoint_url}")
                    # 使用 ensure_ascii=False 可以在日志中正确显示中文
                    logger.debug(f"📋 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    response = requests.post(
                        endpoint_url,
                        headers=headers,
                        json=data,
                        timeout=60 # 建议将超时时间设置得长一些
                    )
                    
                    response.raise_for_status()
                    response_data = response.json()
                    
                    return CustomResponse(response_data)
                    
                except requests.exceptions.RequestException as e:
                    error_message = f"API请求失败: {str(e)}"
                    if e.response is not None:
                        try:
                            # 尝试以JSON格式解析错误详情，并正确显示中文
                            error_details = e.response.json()
                            error_message += f"\n响应内容: {json.dumps(error_details, indent=2, ensure_ascii=False)}"
                        except json.JSONDecodeError:
                            error_message += f"\n响应内容 (非JSON): {e.response.text}"
                    raise Exception(error_message)


class CustomResponse:
    """自定义响应对象，兼容OpenAI响应格式"""
    
    def __init__(self, data: dict):
        self.choices = []
        
        # 处理Responses API格式
        if 'output' in data:
            # Responses API格式
            for output_item in data.get('output', []):
                if output_item.get('type') == 'message':
                    content_parts = output_item.get('content', [])
                    content_text = ""
                    for part in content_parts:
                        if part.get('type') == 'output_text':
                            content_text += part.get('text', '')
                    
                    choice_data = {
                        'message': {
                            'content': content_text,
                            'role': output_item.get('role', 'assistant')
                        }
                    }
                    self.choices.append(CustomChoice(choice_data))
        elif 'choices' in data:
            # 标准Chat Completions格式
            self.choices = [CustomChoice(choice) for choice in data.get('choices', [])]
        else:
            self.choices = []


class CustomChoice:
    """自定义选择对象"""
    
    def __init__(self, data: dict):
        self.message = CustomMessage(data.get('message', {}))


class CustomMessage:
    """自定义消息对象"""
    
    def __init__(self, data: dict):
        self.content = data.get('content', '')
        self.role = data.get('role', 'assistant')


class MultiKeyOpenAIClient:
    """支持多密钥自动切换的OpenAI客户端"""
    
    def __init__(self, api_keys: list, base_url: str):
        if not api_keys:
            raise ValueError("至少需要提供一个API密钥")
        
        self.api_keys = api_keys
        self.base_url = base_url.rstrip('/')
        self.current_key_index = 0
        self.chat = self.ChatCompletions(self)
    
    @property
    def current_api_key(self):
        """获取当前使用的API密钥"""
        return self.api_keys[self.current_key_index]
    
    def switch_to_next_key(self):
        """切换到下一个API密钥"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"🔄 切换到下一个API密钥，当前使用第 {self.current_key_index + 1}/{len(self.api_keys)} 个密钥")
    
    def is_rate_limit_error(self, error_message: str) -> bool:
        """检查是否为速率限制错误"""
        error_lower = error_message.lower()
        for rate_limit_error in OPENAI_RATE_LIMIT_ERRORS:
            if rate_limit_error.lower() in error_lower:
                return True
        return False
    
    class ChatCompletions:
        def __init__(self, client):
            self.client = client
            self.completions = self.Completions(client)
        
        class Completions:
            def __init__(self, client):
                self.client = client
            
            def create(self, model: str, messages: list, max_tokens: int = None, temperature: float = None, **kwargs):
                """创建聊天完成请求 - 支持多密钥自动切换"""
                # 保存原始参数，用于重试时使用
                original_params = {
                    'model': model,
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    **kwargs
                }
                
                # 尝试次数计数器
                attempt_count = 0
                max_attempts = len(self.client.api_keys)
                
                while attempt_count < max_attempts:
                    # 使用当前密钥创建客户端
                    current_client = CustomOpenAIClient(
                        api_key=self.client.current_api_key,
                        base_url=self.client.base_url
                    )
                    
                    try:
                        # 尝试执行请求
                        return current_client.chat.completions.create(**original_params)
                    except Exception as e:
                        error_message = str(e)
                        logger.warning(f"⚠️ API请求失败 (密钥 {self.client.current_key_index + 1}/{len(self.client.api_keys)}): {error_message}")
                        
                        # 检查是否为速率限制错误
                        if self.client.is_rate_limit_error(error_message):
                            # 如果是速率限制错误，切换到下一个密钥
                            self.client.switch_to_next_key()
                            attempt_count += 1
                            
                            # 如果已经尝试过所有密钥，抛出异常
                            if attempt_count >= max_attempts:
                                logger.error("❌ 所有API密钥都已达到限制")
                                raise Exception(f"所有API密钥都已达到限制: {error_message}")
                        else:
                            # 如果不是速率限制错误，直接抛出异常
                            raise e
                
                # 如果循环结束仍未成功，抛出异常
                raise Exception("API请求失败，已尝试所有密钥")


class Config:
    """配置管理类"""
    
    def __init__(self):
        # 读取单个API密钥（向后兼容）
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            
        # 读取多个API密钥
        openai_api_keys_str = os.getenv("OPENAI_API_KEYS")
        if openai_api_keys_str:
            # 分割并清理密钥
            self.openai_api_keys = [key.strip() for key in openai_api_keys_str.split(",") if key.strip()]
        else:
            # 如果没有配置多个密钥，但配置了单个密钥，则使用单个密钥
            self.openai_api_keys = [self.openai_api_key] if self.openai_api_key else []
            
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        
        self.alibaba_api_key = os.getenv("ALIBABA_API_KEY")
        if self.alibaba_api_key:
            dashscope.api_key = self.alibaba_api_key
        
        self.max_tokens = int(os.getenv("MAX_TOKENS", 32768))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
        
        # Smithery MCP配置
        self.smithery_mcp_key = os.getenv("SMITHEREY_MCP_KEY")
        self.smithery_mcp_profile = os.getenv("SMITHEREY_MCP_PROFILE")
        
        # Tavily配置
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def get_openai_client(self):
        """获取OpenAI客户端"""
        # 检查是否配置了API密钥
        if not self.openai_api_keys:
            raise ValueError("OpenAI API密钥未配置")
        
        base_url = self.openai_base_url.rstrip('/')
        # 如果配置了多个API密钥，返回多密钥客户端
        if len(self.openai_api_keys) > 1:
            return MultiKeyOpenAIClient(api_keys=self.openai_api_keys, base_url=base_url)
        else:
            # 如果只有一个API密钥，返回原来的客户端（保持向后兼容）
            return CustomOpenAIClient(api_key=self.openai_api_keys[0], base_url=base_url)
    
    def get_gemini_model(self, model_name: str = "gemini-2.5-flash"):
        """获取Gemini模型"""
        if not self.google_api_key:
            raise ValueError("Google API密钥未配置")
        return genai.GenerativeModel(model_name)
    
    def get_smithery_mcp_config(self):
        """获取Smithery MCP配置"""
        if not self.smithery_mcp_key or not self.smithery_mcp_profile:
            return None
        
        return {
            "key": self.smithery_mcp_key,
            "profile": self.smithery_mcp_profile
        }
    
    def validate_config(self) -> dict:
        """验证配置"""
        status = {
            "openai": bool(self.openai_api_keys),
            "gemini": bool(self.google_api_key),
            "alibaba": bool(self.alibaba_api_key),
            "smithery_mcp": bool(self.smithery_mcp_key and self.smithery_mcp_profile)
        }
        return status


# 全局配置实例
config = Config()