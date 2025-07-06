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
                
                # 🚀 修复：确保响应内容是有效的JSON
                response_json = response.json()
                if response_json is None:
                    logger.error("博查API返回的JSON为None")
                    return {"error": "API返回空响应"}
                
                return response_json
                
        except httpx.HTTPError as e:
            logger.error(f"博查API请求失败: {e}")
            return {"error": f"HTTP请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"博查API响应JSON解析失败: {e}")
            return {"error": f"JSON解析失败: {str(e)}"}
        except Exception as e:
            logger.error(f"博查API请求未知错误: {e}")
            return {"error": f"未知错误: {str(e)}"}
    
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
                
                # 🚀 修复：确保响应内容是有效的JSON
                response_json = response.json()
                if response_json is None:
                    logger.error("博查API返回的JSON为None")
                    return {"error": "API返回空响应"}
                
                return response_json
                
        except httpx.HTTPError as e:
            logger.error(f"博查API异步请求失败: {e}")
            return {"error": f"HTTP请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"博查API响应JSON解析失败: {e}")
            return {"error": f"JSON解析失败: {str(e)}"}
        except Exception as e:
            logger.error(f"博查API异步请求未知错误: {e}")
            return {"error": f"未知错误: {str(e)}"}
    
    def _format_results(self, raw_response: dict) -> list:
        """将博查API响应格式化为标准格式"""
        results = []
        
        try:
            # 🚀 修复：检查raw_response是否为None或空
            if raw_response is None:
                logger.error("博查API响应为None")
                return [{"error": "API响应为空", "title": "搜索失败", "content": "API返回了空响应"}]
            
            if not raw_response:
                logger.error("博查API响应为空字典")
                return [{"error": "API响应为空字典", "title": "搜索失败", "content": "API返回了空字典"}]
            
            # 记录原始响应以便调试
            logger.info(f"博查API原始响应类型: {type(raw_response)}")
            logger.debug(f"博查API原始响应: {json.dumps(raw_response, ensure_ascii=False, indent=2)}")
            
            # 🚀 修复：检查是否是错误响应
            if "error" in raw_response:
                logger.error(f"博查API返回错误: {raw_response['error']}")
                return [{"error": raw_response["error"], "title": "搜索失败", "content": f"搜索出错: {raw_response['error']}"}]
            
            # 博查API响应结构：{ "code": 200, "data": { "webPages": {...} } }
            # 首先获取data字段
            data = raw_response.get("data", {})
            if not data:
                logger.warning(f"博查API响应中未找到data字段，完整响应: {raw_response}")
                # 检查是否有code字段表示API状态
                code = raw_response.get("code")
                if code and code != 200:
                    error_msg = raw_response.get("message", f"API返回错误码: {code}")
                    return [{"error": error_msg, "title": "搜索失败", "content": f"API错误: {error_msg}"}]
                return []
            
            # 处理网页搜索结果
            web_pages_data = data.get("webPages")
            if web_pages_data is None:
                logger.warning("webPages字段为None")
                web_pages = []
            else:
                web_pages = web_pages_data.get("value", [])
            
            logger.info(f"找到 {len(web_pages)} 个网页搜索结果")
            
            for page in web_pages:
                if page is None:
                    logger.warning("跳过None页面结果")
                    continue
                    
                result = {
                    "title": page.get("name", "") if page else "",
                    "url": page.get("url", "") if page else "",
                    "content": page.get("snippet", "") if page else "",
                    "summary": page.get("summary", "") if page else "",
                    "siteName": page.get("siteName", "") if page else "",
                    "siteIcon": page.get("siteIcon", "") if page else "",
                    "datePublished": page.get("datePublished", "") if page else ""
                }
                results.append(result)
            
            # 处理图片结果（如果包含）
            if self.include_images:
                images_data = data.get("images")
                if images_data is None:
                    logger.debug("images字段为None")
                    images = []
                else:
                    images = images_data.get("value", [])
                
                logger.info(f"找到 {len(images)} 个图片结果")
                
                for img in images[:3]:  # 限制图片数量
                    if img is None:
                        logger.warning("跳过None图片结果")
                        continue
                        
                    image_result = {
                        "title": f"图片: {img.get('name', '') if img else ''}",
                        "url": img.get("hostPageUrl", "") if img else "",
                        "content": f"图片描述: {img.get('name', '') if img else ''}",
                        "imageUrl": img.get("contentUrl", "") if img else "",
                        "width": img.get("width", "") if img else "",
                        "height": img.get("height", "") if img else ""
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
            
            logger.info(f"博查异步请求完成，响应类型: {type(raw_response)}")
            
            formatted_results = self._format_results(raw_response)
            if not formatted_results:
                logger.warning("格式化后的结果为空")
                return json.dumps([{"error": "未找到搜索结果"}], ensure_ascii=False)
            
            logger.info(f"博查异步搜索成功，返回 {len(formatted_results)} 个结果")
            return json.dumps(formatted_results, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"博查异步搜索执行失败: {e}")
            return json.dumps([{"error": f"搜索失败: {str(e)}"}], ensure_ascii=False) 