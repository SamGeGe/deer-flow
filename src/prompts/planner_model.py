# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"


class Step(BaseModel):
    need_search: bool = Field(..., description="必须为每个步骤明确设置")
    title: str
    description: str = Field(..., description="准确指定要收集的数据")
    step_type: StepType = Field(..., description="指示步骤的性质")
    execution_res: Optional[str] = Field(
        default=None, description="步骤执行结果"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="例如 'en-US' 或 'zh-CN'，基于用户的语言"
    )
    has_enough_context: bool
    thought: str
    title: str
    steps: List[Step] = Field(
        default_factory=list,
        description="获取更多上下文的研究和处理步骤",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        }
                    ],
                }
            ]
        }
