# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.prompts.template import get_prompt_template
from src.prose.graph.state import ProseState

logger = logging.getLogger(__name__)


def prose_shorter_node(state: ProseState):
    logger.info("Generating prose shorter content...")
    
    # 🔧 修复：使用低推理模式并添加 /no_think
    model = get_llm_with_reasoning_effort(AGENT_LLM_MAP["prose_writer"], "low")
    
    messages = [
        SystemMessage(content=get_prompt_template("prose/prose_shorter")),
        HumanMessage(content=f"The existing text is: {state['content']}"),
    ]
    
    # 添加 /no_think 后缀
    messages = add_no_think_if_needed(messages, model, "low")
    logger.info("为prose_shorter_node添加了 /no_think")
    
    prose_content = model.invoke(messages)
    logger.info(f"prose_content: {prose_content}")
    return {"output": prose_content.content}
