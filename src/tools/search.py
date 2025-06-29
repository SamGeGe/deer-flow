# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Optional

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper
from langchain_core.tools import BaseTool

from src.config import SearchEngine, SELECTED_SEARCH_ENGINE
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)

from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)

# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(BraveSearch)
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)


class FallbackSearchTool(BaseTool):
    """搜索工具，支持从 Tavily 回退到 DuckDuckGo"""
    
    name: str = "web_search"
    description: str = "搜索网络信息"
    max_search_results: int = 5  # 添加字段定义
    tavily_tool: Optional[BaseTool] = None
    duckduckgo_tool: Optional[BaseTool] = None
    
    def __init__(self, max_search_results: int, **kwargs):
        super().__init__(**kwargs)
        self.max_search_results = max_search_results
        self.tavily_tool = None
        self.duckduckgo_tool = LoggedDuckDuckGoSearch(
            name="web_search_fallback",
            num_results=max_search_results,
        )
        
        # 尝试初始化 Tavily 工具
        try:
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if tavily_api_key and tavily_api_key.strip():
                self.tavily_tool = LoggedTavilySearch(
                    name="web_search_primary",
                    max_results=max_search_results,
                    include_raw_content=False,  # 禁用原始内容以减少 token 使用
                    include_images=True,
                    include_image_descriptions=True,
                )
                logger.info("Tavily 搜索工具初始化成功，将作为主要搜索引擎")
            else:
                logger.info("未找到 TAVILY_API_KEY，将使用 DuckDuckGo 作为搜索引擎")
        except Exception as e:
            logger.warning(f"Tavily 搜索工具初始化失败: {e}，将使用 DuckDuckGo 作为回退")
    
    def _run(self, query: str) -> str:
        """执行搜索，优先使用 Tavily，失败时回退到 DuckDuckGo"""
        
        # 首先尝试使用 Tavily
        if self.tavily_tool:
            try:
                logger.info(f"尝试使用 Tavily 搜索: {query}")
                result = self.tavily_tool._run(query)
                logger.info("Tavily 搜索成功")
                return result
            except Exception as e:
                logger.warning(f"Tavily 搜索失败: {e}，回退到 DuckDuckGo")
        
        # 回退到 DuckDuckGo
        try:
            logger.info(f"使用 DuckDuckGo 搜索: {query}")
            result = self.duckduckgo_tool._run(query)
            logger.info("DuckDuckGo 搜索成功")
            return result
        except Exception as e:
            logger.error(f"DuckDuckGo 搜索也失败了: {e}")
            return json.dumps([{"error": "所有搜索引擎都不可用", "details": str(e)}])
    
    async def _arun(self, query: str) -> str:
        """异步执行搜索"""
        return self._run(query)


# Get the selected search tool
def get_web_search_tool(max_search_results: int):
    # 如果配置为使用回退机制或者是 Tavily，则使用回退工具
    if SELECTED_SEARCH_ENGINE in [SearchEngine.TAVILY.value, "fallback", "auto"]:
        return FallbackSearchTool(max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(
            name="web_search",
            num_results=max_search_results,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=ArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    else:
        # 默认使用回退机制
        logger.info(f"未识别的搜索引擎 {SELECTED_SEARCH_ENGINE}，使用回退机制")
        return FallbackSearchTool(max_search_results)
