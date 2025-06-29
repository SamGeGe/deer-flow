#!/usr/bin/env python3
"""
专门测试QwQ模型在高推理模式下的输出字段
"""
import sys
import os
sys.path.append('src')

from src.llms.llm import get_llm_with_reasoning_effort
from src.config.agents import AGENT_LLM_MAP
from langchain_core.messages import HumanMessage, SystemMessage

def test_qwq_high_reasoning():
    print("=== 测试QwQ高推理模式输出 ===")
    
    # 测试消息
    test_messages = [
        SystemMessage(content="你是一个有用的助手。"),
        HumanMessage(content="请简单回答：1+1等于多少？")
    ]
    
    print("\n测试高推理模式（reporter）:")
    try:
        llm_high = get_llm_with_reasoning_effort(AGENT_LLM_MAP["reporter"], "high")
        response_high = llm_high.invoke(test_messages)
        
        print(f"响应类型: {type(response_high)}")
        print(f"content字段: '{response_high.content}'")
        print(f"content长度: {len(response_high.content) if response_high.content else 0}")
        
        # 检查additional_kwargs中是否有推理内容
        if hasattr(response_high, 'additional_kwargs'):
            print(f"additional_kwargs keys: {list(response_high.additional_kwargs.keys())}")
            for key, value in response_high.additional_kwargs.items():
                if key != 'refusal' and value:
                    print(f"  {key}: '{value[:100]}...' (长度: {len(str(value))})")
        
        # 检查是否有reasoning_content
        if hasattr(response_high, 'additional_kwargs') and 'reasoning_content' in response_high.additional_kwargs:
            reasoning = response_high.additional_kwargs['reasoning_content']
            print(f"reasoning_content: '{reasoning[:100]}...' (长度: {len(reasoning)})")
        
    except Exception as e:
        print(f"高推理模式错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qwq_high_reasoning() 