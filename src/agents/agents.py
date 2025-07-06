# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.config.agents import AGENT_LLM_MAP


# Create agents using configured LLM types
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str, reasoning_effort: str = "low"):
    """Factory function to create agents with consistent configuration."""
    
    # Get LLM with reasoning effort control
    llm = get_llm_with_reasoning_effort(AGENT_LLM_MAP[agent_type], reasoning_effort)
    
    # Create custom prompt function that adds /no_think when needed
    def custom_prompt(state):
        messages = apply_prompt_template(prompt_template, state)
        # Add /no_think for low reasoning effort
        if reasoning_effort == "low":
            messages = add_no_think_if_needed(messages, llm, reasoning_effort)
        return messages
    
    return create_react_agent(
        name=agent_name,
        model=llm,
        tools=tools,
        prompt=custom_prompt,
    )
