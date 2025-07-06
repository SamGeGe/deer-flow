# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.prompts.template import get_prompt_template

from ..types import Script
from .state import PodcastState

logger = logging.getLogger(__name__)


def script_writer_node(state: PodcastState):
    logger.info("Generating script for podcast...")
    
    # 🔧 修复：使用低推理模式并添加 /no_think
    model = get_llm_with_reasoning_effort(AGENT_LLM_MAP["podcast_script_writer"], "low")
    
    messages = [
        SystemMessage(content=get_prompt_template("podcast/podcast_script_writer")),
        HumanMessage(content=state["input"]),
    ]
    
    # 添加 /no_think 后缀
    messages = add_no_think_if_needed(messages, model, "low")
    logger.info("为script_writer_node添加了 /no_think")
    
    script = model.with_structured_output(Script, method="json_mode").invoke(messages)
    print(script)
    return {"script": script, "audio_chunks": []}
