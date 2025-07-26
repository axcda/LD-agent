import os
from dotenv import load_dotenv
from typing import Optional
import openai
import google.generativeai as genai
import dashscope

load_dotenv()


class Config:
    """配置管理类"""
    
    def __init__(self):
        # OpenAI配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            
        # OpenAI基础URL配置
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # Google Gemini配置
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        
        # 阿里百炼配置
        self.alibaba_api_key = os.getenv("ALIBABA_API_KEY")
        if self.alibaba_api_key:
            dashscope.api_key = self.alibaba_api_key
        
        # 通用配置
        self.max_tokens = int(os.getenv("MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
    
    def get_openai_client(self):
        """获取OpenAI客户端"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API密钥未配置")
        return openai.OpenAI(api_key=self.openai_api_key, base_url=self.openai_base_url)
    
    def get_gemini_model(self, model_name: str = "gemini-1.5-flash"):
        """获取Gemini模型"""
        if not self.google_api_key:
            raise ValueError("Google API密钥未配置")
        return genai.GenerativeModel(model_name)
    
    def validate_config(self) -> dict:
        """验证配置"""
        status = {
            "openai": bool(self.openai_api_key),
            "gemini": bool(self.google_api_key), 
            "alibaba": bool(self.alibaba_api_key)
        }
        return status


# 全局配置实例
config = Config()