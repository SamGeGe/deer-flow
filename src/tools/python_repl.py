# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import re
from typing import Annotated
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from .decorators import log_io

# Initialize REPL and logger
repl = PythonREPL()
logger = logging.getLogger(__name__)


def preprocess_python_code(code: str) -> str:
    """
    预处理Python代码以修复常见语法问题，特别是f-string中的中文格式错误
    
    Args:
        code: 原始Python代码字符串
        
    Returns:
        修复了常见问题的预处理Python代码
    """
    if not code or not isinstance(code, str):
        return code
    
    logger.debug(f"预处理前的代码: {code}")
    
    # 🚀 核心修复：处理f-string中各种中文语法错误
    
    # 方法1：修复变量名后面直接跟空格和中文的情况（最常见的错误）
    # 错误：{variable_name 中文} 
    # 正确：{variable_name} 中文
    def fix_variable_space_chinese(match):
        var_name = match.group(1)          # 变量名
        space_and_chinese = match.group(2) # 空格+中文文本
        return f"{{{var_name}}}{space_and_chinese}"
    
    # 匹配 {variable_name 中文} 模式 - 这是最常见的错误
    pattern1 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)(\s+[\u4e00-\u9fff][^}]*)\}'
    code = re.sub(pattern1, fix_variable_space_chinese, code)
        
    # 方法2：修复格式说明符后面跟空格和中文的情况  
    # 错误：{variable:.4f 倍}
    # 正确：{variable:.4f} 倍
    def fix_format_space_chinese(match):
        var_and_format = match.group(1)    # 变量名:格式说明符
        space_and_chinese = match.group(2) # 空格+中文文本
        return f"{{{var_and_format}}}{space_and_chinese}"
    
    # 匹配 {variable:format 中文} 模式
    pattern2 = r'\{([a-zA-Z_][a-zA-Z0-9_]*:[^}\s]+)(\s+[\u4e00-\u9fff][^}]*)\}'
    code = re.sub(pattern2, fix_format_space_chinese, code)
    
    # 方法3：修复格式说明符直接紧贴中文的情况
    # 错误：{variable:.4f倍}  
    # 正确：{variable:.4f} 倍
    def fix_format_direct_chinese(match):
        var_name = match.group(1)       # 变量名
        format_spec = match.group(2)    # 格式说明符
        chinese_text = match.group(3)   # 中文文本
        return f"{{{var_name}:{format_spec}}} {chinese_text}"
    
    # 匹配 {variable:format中文} 模式
    pattern3 = r'\{([a-zA-Z_][a-zA-Z0-9_]*):([^}\u4e00-\u9fff]+)([\u4e00-\u9fff][^}]*)\}'
    code = re.sub(pattern3, fix_format_direct_chinese, code)
    
    # 方法4：修复变量名直接紧贴中文的情况
    # 错误：{variable中文}
    # 正确：{variable} 中文  
    def fix_variable_direct_chinese(match):
        var_name = match.group(1)       # 变量名
        chinese_text = match.group(2)   # 中文文本
        return f"{{{var_name}}} {chinese_text}"
    
    # 匹配 {variable中文} 模式
    pattern4 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)([\u4e00-\u9fff][^}]*)\}'
    code = re.sub(pattern4, fix_variable_direct_chinese, code)
    
    # 方法5：通用的缺少闭合花括号修复
    # 处理任何f-string中缺少}的情况
    def fix_missing_closing_brace_general(match):
        prefix = match.group(1)  # f" 部分
        content = match.group(2) # 内容部分
        suffix = match.group(3)  # " 部分
        
        # 计算缺少的闭合花括号数量
        open_count = content.count('{')
        close_count = content.count('}')
        missing_braces = max(0, open_count - close_count)
        
        if missing_braces > 0:
            # 在引号前添加缺失的闭合花括号
            return f'{prefix}{content}{"}" * missing_braces}{suffix}'
        return match.group(0)
    
    # 匹配f-string并修复缺少的闭合花括号
    pattern5 = r'(f["\'])([^"\']*\{[^"\']*?)(["\'])'
    code = re.sub(pattern5, fix_missing_closing_brace_general, code)
    
    logger.debug(f"预处理后的代码: {code}")
    
    return code


@tool
@log_io
def python_repl_tool(code: Annotated[str, "Python code to execute"]) -> str:
    """
    Execute Python code in REPL.
    
    Args:
        code: The Python code to execute
        
    Returns:
        The output of the code execution or error message
    """
    logger.info("Executing Python code")
    
    try:
        # Preprocess the code to fix common syntax issues
        processed_code = preprocess_python_code(code)
        
        # Execute the code
        result = repl.run(processed_code)
        
        logger.info("Code execution successful")
        return f"Successfully executed:\n```python\n{processed_code}\n```\n{result}"

    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Error executing code:\n```python\n{processed_code if 'processed_code' in locals() else code}\n```\nError: {str(e)}"
