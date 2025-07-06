# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
import uuid

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.prompts.template import get_prompt_template

from .state import PPTState

logger = logging.getLogger(__name__)


def ppt_composer_node(state: PPTState):
    logger.info("Generating ppt content...")
    
    # 🔧 修复：使用低推理模式并添加 /no_think
    model = get_llm_with_reasoning_effort(AGENT_LLM_MAP["ppt_composer"], "low")
    
    messages = [
        SystemMessage(content=get_prompt_template("ppt/ppt_composer")),
        HumanMessage(content=state["input"]),
    ]
    
    # 添加 /no_think 后缀
    messages = add_no_think_if_needed(messages, model, "low")
    logger.info("为ppt_composer_node添加了 /no_think")
    
    ppt_content = model.invoke(messages)
    logger.info(f"ppt_content: {ppt_content}")
    # save the ppt content in a temp file
    temp_ppt_file_path = os.path.join(os.getcwd(), f"ppt_content_{uuid.uuid4()}.md")
    with open(temp_ppt_file_path, "w") as f:
        f.write(ppt_content.content)
    return {"ppt_content": ppt_content, "ppt_file_path": temp_ppt_file_path}
