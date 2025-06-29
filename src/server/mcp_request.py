# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MCPServerMetadataRequest(BaseModel):
    """MCP服务器元数据的请求模型。"""

    transport: str = Field(
        ..., description="MCP服务器连接的类型（stdio或sse）"
    )
    command: Optional[str] = Field(
        None, description="要执行的命令（用于stdio类型）"
    )
    args: Optional[List[str]] = Field(
        None, description="命令参数（用于stdio类型）"
    )
    url: Optional[str] = Field(
        None, description="SSE服务器的URL（用于sse类型）"
    )
    env: Optional[Dict[str, str]] = Field(None, description="环境变量")
    timeout_seconds: Optional[int] = Field(
        None, description="操作的可选自定义超时时间（秒）"
    )


class MCPServerMetadataResponse(BaseModel):
    """MCP服务器元数据的响应模型。"""

    transport: str = Field(
        ..., description="MCP服务器连接的类型（stdio或sse）"
    )
    command: Optional[str] = Field(
        None, description="要执行的命令（用于stdio类型）"
    )
    args: Optional[List[str]] = Field(
        None, description="命令参数（用于stdio类型）"
    )
    url: Optional[str] = Field(
        None, description="SSE服务器的URL（用于sse类型）"
    )
    env: Optional[Dict[str, str]] = Field(None, description="环境变量")
    tools: List = Field(
        default_factory=list, description="来自MCP服务器的可用工具"
    )
