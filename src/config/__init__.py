# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from .tools import SELECTED_SEARCH_ENGINE, SearchEngine
from .questions import BUILT_IN_QUESTIONS, BUILT_IN_QUESTIONS_ZH_CN
from .loader import load_yaml_config

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Team configuration
TEAM_MEMBER_CONFIGRATIONS = {
    "researcher": {
        "name": "researcher",
        "desc": (
            "负责搜索和收集相关信息，理解用户需求并进行研究分析"
        ),
        "desc_for_llm": (
            "使用搜索引擎和网络爬虫从互联网收集信息。"
            "输出总结发现的Markdown报告。研究员不能进行数学计算或编程。"
        ),
        "is_optional": False,
    },
    "coder": {
        "name": "coder",
        "desc": (
            "负责代码实现、调试和优化，处理技术编程任务"
        ),
        "desc_for_llm": (
            "执行Python或Bash命令，进行数学计算，并输出Markdown报告。"
            "必须用于所有数学计算。"
        ),
        "is_optional": True,
    },
}

TEAM_MEMBERS = list(TEAM_MEMBER_CONFIGRATIONS.keys())

__all__ = [
    # Other configurations
    "TEAM_MEMBERS",
    "TEAM_MEMBER_CONFIGRATIONS",
    "SELECTED_SEARCH_ENGINE",
    "SearchEngine",
    "BUILT_IN_QUESTIONS",
    "BUILT_IN_QUESTIONS_ZH_CN",
]
