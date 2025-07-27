import subprocess
import json
import logging
from typing import Optional, Dict, Any
from ..config import config

logger = logging.getLogger(__name__)

class MCPToolError(Exception):
    """MCP工具相关异常"""
    pass

class SmitheryMCPClient:
    """Smithery MCP客户端"""
    
    def __init__(self):
        self.config = config.get_smithery_mcp_config()
        if not self.config:
            raise MCPToolError("Smithery MCP配置未找到，请检查环境变量配置")
    
    def run_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行Smithery MCP工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            # 构建命令
            cmd = [
                "npx", "-y", "@smithery/cli@latest", "run", tool_name,
                "--key", self.config["key"],
                "--profile", self.config["profile"]
            ]
            
            # 添加参数
            for key, value in arguments.items():
                cmd.extend([f"--{key}", str(value)])
            
            logger.debug(f"执行MCP工具命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                raise MCPToolError(f"工具执行失败: {result.stderr}")
            
            # 解析输出
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout}
                
        except subprocess.TimeoutExpired:
            raise MCPToolError("工具执行超时")
        except Exception as e:
            raise MCPToolError(f"工具执行异常: {str(e)}")

# 全局MCP工具实例
smithery_client: Optional[SmitheryMCPClient] = None

def get_smithery_client() -> SmitheryMCPClient:
    """
    获取Smithery MCP客户端实例
    
    Returns:
        SmitheryMCPClient实例
    """
    global smithery_client
    if smithery_client is None:
        try:
            smithery_client = SmitheryMCPClient()
        except MCPToolError as e:
            logger.warning(f"无法初始化Smithery MCP客户端: {e}")
            smithery_client = None
    return smithery_client

def run_smithery_tool(tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    运行Smithery工具
    
    Args:
        tool_name: 工具名称
        arguments: 工具参数
        
    Returns:
        工具执行结果，如果客户端未初始化则返回None
    """
    client = get_smithery_client()
    if client is None:
        return None
    
    try:
        return client.run_tool(tool_name, arguments)
    except MCPToolError as e:
        logger.error(f"运行Smithery工具失败: {e}")
        return None