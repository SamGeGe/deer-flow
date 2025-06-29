# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from src.rag.retriever import Resource
from src.config.report_style import ReportStyle


class ContentItem(BaseModel):
    type: str = Field(..., description="内容类型（文本、图片等）")
    text: Optional[str] = Field(None, description="如果类型是'text'则为文本内容")
    image_url: Optional[str] = Field(
        None, description="如果类型是'image'则为图片URL"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="消息发送者的角色（用户或助手）"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="消息的内容，可以是字符串或内容项列表",
    )


class ChatRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = Field(
        [], description="用户与助手之间的消息历史"
    )
    resources: Optional[List[Resource]] = Field(
        [], description="用于研究的资源"
    )
    debug: Optional[bool] = Field(False, description="是否启用调试日志")
    thread_id: Optional[str] = Field(
        "__default__", description="特定的对话标识符"
    )
    max_plan_iterations: Optional[int] = Field(
        1, description="计划迭代的最大次数"
    )
    max_step_num: Optional[int] = Field(
        3, description="计划中的最大步骤数"
    )
    max_search_results: Optional[int] = Field(
        3, description="搜索结果的最大数量"
    )
    auto_accepted_plan: Optional[bool] = Field(
        False, description="是否自动接受计划"
    )
    interrupt_feedback: Optional[str] = Field(
        None, description="用户对计划的中断反馈"
    )
    mcp_settings: Optional[dict] = Field(
        None, description="聊天请求的MCP设置"
    )
    enable_background_investigation: Optional[bool] = Field(
        True, description="是否在计划之前进行背景调查"
    )
    report_style: Optional[ReportStyle] = Field(
        ReportStyle.ACADEMIC, description="报告的风格"
    )
    enable_deep_thinking: Optional[bool] = Field(
        False, description="是否启用深度思考"
    )


class TTSRequest(BaseModel):
    text: str = Field(..., description="要转换为语音的文本")
    voice_type: Optional[str] = Field(
        "BV700_V2_streaming", description="使用的语音类型"
    )
    encoding: Optional[str] = Field("mp3", description="音频编码格式")
    speed_ratio: Optional[float] = Field(1.0, description="语音速度比例")
    volume_ratio: Optional[float] = Field(1.0, description="语音音量比例")
    pitch_ratio: Optional[float] = Field(1.0, description="语音音调比例")
    text_type: Optional[str] = Field("plain", description="文本类型（plain或ssml）")
    with_frontend: Optional[int] = Field(
        1, description="是否使用前端处理"
    )
    frontend_type: Optional[str] = Field("unitTson", description="前端类型")


class GeneratePodcastRequest(BaseModel):
    content: str = Field(..., description="播客的内容")


class GeneratePPTRequest(BaseModel):
    content: str = Field(..., description="PPT的内容")


class GenerateProseRequest(BaseModel):
    prompt: str = Field(..., description="散文的内容")
    option: str = Field(..., description="散文写作的选项")
    command: Optional[str] = Field(
        "", description="散文写作的用户自定义命令"
    )


class EnhancePromptRequest(BaseModel):
    prompt: str = Field(..., description="要增强的原始提示")
    context: Optional[str] = Field(
        "", description="关于预期用途的附加上下文"
    )
    report_style: Optional[str] = Field(
        "academic", description="报告的风格"
    )
