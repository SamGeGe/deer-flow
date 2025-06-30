# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Optional

import httpx
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class BochaSearchTool(BaseTool):
    """博查AI搜索工具，支持Web搜索和AI搜索"""
    
    name: str = "bocha_search"
    description: str = "使用博查AI搜索引擎搜索网络信息，获得高质量的搜索结果"
    
    api_key: str = Field(default_factory=lambda: os.getenv("BOCHA_API_KEY", ""))
    max_results: int = Field(default=5)
    include_images: bool = Field(default=True)
    include_summary: bool = Field(default=True)
    search_type: str = Field(default="web-search")  # "web-search" 或 "ai-search"
    base_url: str = Field(default="https://api.bochaai.com/v1")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            raise ValueError("BOCHA_API_KEY environment variable is required")
    
    def _make_request(self, query: str) -> dict:
        """发送HTTP请求到博查API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "query": query,
            "summary": self.include_summary,
            "freshness": "noLimit",
            "count": self.max_results
        }
        
        url = f"{self.base_url}/{self.search_type}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"博查API请求失败: {e}")
            raise e
    
    async def _make_request_async(self, query: str) -> dict:
        """异步发送HTTP请求到博查API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "query": query,
            "summary": self.include_summary,
            "freshness": "noLimit",
            "count": self.max_results
        }
        
        url = f"{self.base_url}/{self.search_type}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"博查API异步请求失败: {e}")
            raise e
    
    def _format_results(self, raw_response: dict) -> list:
        """将博查API响应格式化为标准格式"""
        results = []
        
        try:
            # 博查API响应结构：{ "code": 200, "data": { "webPages": {...} } }
            # 首先获取data字段
            data = raw_response.get("data", {})
            if not data:
                logger.warning("博查API响应中未找到data字段")
                return []
            
            # 处理网页搜索结果
            web_pages = data.get("webPages", {}).get("value", [])
            
            for page in web_pages:
                result = {
                    "title": page.get("name", ""),
                    "url": page.get("url", ""),
                    "content": page.get("snippet", ""),
                    "summary": page.get("summary", ""),
                    "siteName": page.get("siteName", ""),
                    "siteIcon": page.get("siteIcon", ""),
                    "datePublished": page.get("datePublished", "")
                }
                results.append(result)
            
            # 处理图片结果（如果包含）
            if self.include_images:
                images = data.get("images", {}).get("value", [])
                for img in images[:3]:  # 限制图片数量
                    image_result = {
                        "title": f"图片: {img.get('name', '')}",
                        "url": img.get("hostPageUrl", ""),
                        "content": f"图片描述: {img.get('name', '')}",
                        "imageUrl": img.get("contentUrl", ""),
                        "width": img.get("width", ""),
                        "height": img.get("height", "")
                    }
                    results.append(image_result)
            
            logger.info(f"博查搜索成功，返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"博查搜索结果格式化失败: {e}")
            return []
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行搜索"""
        try:
            logger.info(f"使用博查搜索: {query}")
            raw_response = self._make_request(query)
            
            formatted_results = self._format_results(raw_response)
            if not formatted_results:
                return json.dumps([{"error": "未找到搜索结果"}], ensure_ascii=False)
            
            return json.dumps(formatted_results, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"博查搜索执行失败: {e}")
            return json.dumps([{"error": f"搜索失败: {str(e)}"}], ensure_ascii=False)
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """异步执行搜索"""
        try:
            logger.info(f"使用博查异步搜索: {query}")
            raw_response = await self._make_request_async(query)
            
            formatted_results = self._format_results(raw_response)
            if not formatted_results:
                return json.dumps([{"error": "未找到搜索结果"}], ensure_ascii=False)
            
            return json.dumps(formatted_results, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"博查异步搜索执行失败: {e}")
            return json.dumps([{"error": f"搜索失败: {str(e)}"}], ensure_ascii=False) 