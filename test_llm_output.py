#!/usr/bin/env python3
"""
测试LLM在不同模式下的输出字段
"""
import sys
import os
sys.path.append('src')

from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.config.agents import AGENT_LLM_MAP
from langchain_core.messages import HumanMessage, SystemMessage

def test_llm_output():
    print("=== 测试LLM输出字段 ===")
    
    # 测试消息
    test_messages = [
        SystemMessage(content="你是一个有用的助手。"),
        HumanMessage(content="请简单回答：1+1等于多少？")
    ]
    
    print("\n1. 测试高推理模式（reporter）:")
    try:
        llm_high = get_llm_with_reasoning_effort(AGENT_LLM_MAP["reporter"], "high")
        response_high = llm_high.invoke(test_messages)
        print(f"响应类型: {type(response_high)}")
        print(f"响应属性: {dir(response_high)}")
        if hasattr(response_high, 'content'):
            print(f"content字段: '{response_high.content}'")
        if hasattr(response_high, 'additional_kwargs'):
            print(f"additional_kwargs: {response_high.additional_kwargs}")
        if hasattr(response_high, 'response_metadata'):
            print(f"response_metadata: {response_high.response_metadata}")
    except Exception as e:
        print(f"高推理模式错误: {e}")
    
    print("\n2. 测试低推理模式（coordinator）with /no_think:")
    try:
        llm_low = get_llm_with_reasoning_effort(AGENT_LLM_MAP["coordinator"], "low")
        # 添加/no_think
        messages_with_nothink = add_no_think_if_needed(test_messages, llm_low, "low")
        print(f"添加/no_think后的消息: {[msg.content for msg in messages_with_nothink]}")
        
        response_low = llm_low.invoke(messages_with_nothink)
        print(f"响应类型: {type(response_low)}")
        print(f"响应属性: {dir(response_low)}")
        if hasattr(response_low, 'content'):
            print(f"content字段: '{response_low.content}'")
        if hasattr(response_low, 'additional_kwargs'):
            print(f"additional_kwargs: {response_low.additional_kwargs}")
        if hasattr(response_low, 'response_metadata'):
            print(f"response_metadata: {response_low.response_metadata}")
    except Exception as e:
        print(f"低推理模式错误: {e}")
    
    print("\n3. 测试流式输出:")
    try:
        llm_stream = get_llm_with_reasoning_effort(AGENT_LLM_MAP["coordinator"], "low")
        messages_stream = add_no_think_if_needed(test_messages, llm_stream, "low")
        
        print("流式响应chunks:")
        for i, chunk in enumerate(llm_stream.stream(messages_stream)):
            print(f"Chunk {i}: 类型={type(chunk)}, 属性={dir(chunk)}")
            if hasattr(chunk, 'content'):
                print(f"  content: '{chunk.content}'")
            if hasattr(chunk, 'additional_kwargs'):
                print(f"  additional_kwargs: {chunk.additional_kwargs}")
            if hasattr(chunk, 'response_metadata'):
                print(f"  response_metadata: {chunk.response_metadata}")
            if i >= 5:  # 只看前几个chunk
                print("  ...")
                break
    except Exception as e:
        print(f"流式输出错误: {e}")

if __name__ == "__main__":
    test_llm_output() 