# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Dict, Union
import os

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from typing import get_args

from src.config import load_yaml_config
from src.config.agents import LLMType

# Cache for LLM instances
_llm_cache: dict[LLMType, ChatOpenAI] = {}


def _get_config_file_path() -> str:
    """Get the path to the configuration file."""
    return str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())


def _get_llm_type_config_keys() -> dict[str, str]:
    """Get mapping of LLM types to their configuration keys."""
    return {
        "reasoning": "REASONING_MODEL",
        "basic": "BASIC_MODEL",
        "vision": "VISION_MODEL",
    }


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}__{KEY}
    e.g., BASIC_MODEL__api_key, BASIC_MODEL__base_url
    """
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
    return conf


def _create_llm_use_conf(
    llm_type: LLMType, conf: Dict[str, Any]
) -> Union[ChatOpenAI, ChatDeepSeek]:
    """Create LLM instance using configuration."""
    llm_type_config_keys = _get_llm_type_config_keys()
    config_key = llm_type_config_keys.get(llm_type)

    if not config_key:
        raise ValueError(f"Unknown LLM type: {llm_type}")

    llm_conf = conf.get(config_key, {})
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM configuration for {llm_type}: {llm_conf}")

    # Get configuration from environment variables
    env_conf = _get_env_llm_conf(llm_type)

    # Merge configurations, with environment variables taking precedence
    merged_conf = {**llm_conf, **env_conf}

    if not merged_conf:
        raise ValueError(f"No configuration found for LLM type: {llm_type}")

    if llm_type == "reasoning":
        merged_conf["api_base"] = merged_conf.pop("base_url", None)
    else:
        # For ChatOpenAI with OpenRouter, map configuration keys to expected parameter names
        if "api_key" in merged_conf:
            merged_conf["openai_api_key"] = merged_conf.pop("api_key")
        if "base_url" in merged_conf:
            # For OpenRouter, use openai_api_base (preferred) or base_url
            merged_conf["openai_api_base"] = merged_conf.pop("base_url")

    # Debug: Print the configuration being passed to ChatOpenAI
    print(f"Creating LLM of type {llm_type} with config: {merged_conf}")

    return (
        ChatOpenAI(**merged_conf)
        if llm_type != "reasoning"
        else ChatDeepSeek(**merged_conf)
    )


def get_llm_by_type(
    llm_type: LLMType,
) -> ChatOpenAI:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    conf = load_yaml_config(_get_config_file_path())
    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm


def get_llm_with_reasoning_effort(
    llm_type: LLMType = "basic", 
    reasoning_effort: str = None
) -> Union[ChatOpenAI, ChatDeepSeek]:
    """
    Get LLM instance with specific reasoning effort configuration.
    
    Args:
        llm_type: Type of LLM to use
        reasoning_effort: Control reasoning effort - "low", "medium", "high", or None
                         - None/low: Fast mode (no deep thinking)
                         - high: Deep thinking mode
    
    Returns:
        LLM instance configured with appropriate reasoning effort
    """
    base_llm = get_llm_by_type(llm_type)
    
    # If it's a ChatDeepSeek instance and we want to control reasoning
    if isinstance(base_llm, ChatDeepSeek) and reasoning_effort:
        # Create a new instance with reasoning_effort parameter
        conf = load_yaml_config(_get_config_file_path())
        llm_type_config_keys = _get_llm_type_config_keys()
        config_key = llm_type_config_keys.get(llm_type)
        
        if config_key:
            llm_conf = conf.get(config_key, {})
            env_conf = _get_env_llm_conf(llm_type)
            merged_conf = {**llm_conf, **env_conf}
            
            # Add reasoning_effort parameter
            merged_conf["reasoning_effort"] = reasoning_effort
            
            if llm_type == "reasoning":
                merged_conf["api_base"] = merged_conf.pop("base_url", None)
            
            return ChatDeepSeek(**merged_conf)
    
    # For ChatOpenAI instances (including QwQ models), we'll handle /no_think at the message level
    # Store the reasoning effort preference on the LLM instance for later use
    if hasattr(base_llm, '_reasoning_effort') or reasoning_effort:
        base_llm._reasoning_effort = reasoning_effort
    
    return base_llm


def add_no_think_if_needed(messages: list, llm, reasoning_effort: str = None) -> list:
    """
    Add /no_think directive to messages when low reasoning effort is requested.
    
    根据QwQ官方文档，no_think控制存在稳定性问题，因此我们需要在每个用户消息中
    都添加/no_think来确保一致的行为。
    
    Args:
        messages: List of messages to send to the LLM
        llm: The LLM instance
        reasoning_effort: The reasoning effort level
    
    Returns:
        Modified messages list with /no_think added if appropriate
    """
    # Get reasoning effort from parameter or LLM instance
    effort = reasoning_effort or getattr(llm, '_reasoning_effort', None)
    
    # Add /no_think for any model when using low reasoning effort
    if effort == "low":
        modified_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                # Handle dict-style messages
                if msg.get("role") == "user" and msg.get("content"):
                    content = msg["content"]
                    # 强制添加/no_think，即使已经存在（确保稳定性）
                    if not content.strip().endswith("/no_think"):
                        content = content.rstrip() + " /no_think"
                    modified_messages.append({**msg, "content": content})
                else:
                    modified_messages.append(msg)
            else:
                # Handle LangChain message objects
                from langchain_core.messages import HumanMessage
                if isinstance(msg, HumanMessage):
                    content = msg.content
                    # 强制添加/no_think，即使已经存在（确保稳定性）
                    if not content.strip().endswith("/no_think"):
                        content = content.rstrip() + " /no_think"
                    modified_messages.append(HumanMessage(content=content))
                else:
                    modified_messages.append(msg)
        return modified_messages
    
    return messages


def get_configured_llm_models() -> dict[str, list[str]]:
    """
    Get all configured LLM models grouped by type.

    Returns:
        Dictionary mapping LLM type to list of configured model names.
    """
    try:
        conf = load_yaml_config(_get_config_file_path())
        llm_type_config_keys = _get_llm_type_config_keys()

        configured_models: dict[str, list[str]] = {}

        for llm_type in get_args(LLMType):
            # Get configuration from YAML file
            config_key = llm_type_config_keys.get(llm_type, "")
            yaml_conf = conf.get(config_key, {}) if config_key else {}

            # Get configuration from environment variables
            env_conf = _get_env_llm_conf(llm_type)

            # Merge configurations, with environment variables taking precedence
            merged_conf = {**yaml_conf, **env_conf}

            # Check if model is configured
            model_name = merged_conf.get("model")
            if model_name:
                configured_models.setdefault(llm_type, []).append(model_name)

        return configured_models

    except Exception as e:
        # Log error and return empty dict to avoid breaking the application
        print(f"Warning: Failed to load LLM configuration: {e}")
        return {}


# In the future, we will use reasoning_llm and vl_llm for different purposes
# reasoning_llm = get_llm_by_type("reasoning")
# vl_llm = get_llm_by_type("vision")
