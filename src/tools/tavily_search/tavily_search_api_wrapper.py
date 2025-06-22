# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
from typing import Dict, List, Optional

import aiohttp
import requests
from langchain_community.utilities.tavily_search import TAVILY_API_URL
from langchain_community.utilities.tavily_search import (
    TavilySearchAPIWrapper as OriginalTavilySearchAPIWrapper,
)


class EnhancedTavilySearchAPIWrapper(OriginalTavilySearchAPIWrapper):
    def raw_results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        params = {
            "api_key": self.tavily_api_key.get_secret_value(),
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
        }
        response = requests.post(
            # type: ignore
            f"{TAVILY_API_URL}/search",
            json=params,
        )
        response.raise_for_status()
        return response.json()

    async def raw_results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        """Get results from the Tavily Search API asynchronously."""

        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "api_key": self.tavily_api_key.get_secret_value(),
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_domains": include_domains,
                "exclude_domains": exclude_domains,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images,
                "include_image_descriptions": include_image_descriptions,
            }
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.post(f"{TAVILY_API_URL}/search", json=params) as res:
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        raise Exception(f"Error {res.status}: {res.reason}")

        results_json_str = await fetch()
        return json.loads(results_json_str)

    def clean_results_with_images(
        self, raw_results: Dict[str, List[Dict]]
    ) -> List[Dict]:
        results = raw_results["results"]
        """Clean results from Tavily Search API."""
        clean_results = []
        max_content_length = 2000  # 限制每个结果的内容长度
        
        for result in results:
            # 截断内容以控制长度
            content = result["content"]
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            clean_result = {
                "type": "page",
                "title": result["title"],
                "url": result["url"],
                "content": content,
                "score": result["score"],
            }
            
            # 如果有原始内容，也要截断
            if raw_content := result.get("raw_content"):
                if len(raw_content) > max_content_length:
                    raw_content = raw_content[:max_content_length] + "..."
                clean_result["raw_content"] = raw_content
            clean_results.append(clean_result)
        
        # 限制图片数量以减少 token 使用
        images = raw_results.get("images", [])[:3]  # 最多返回3张图片
        for image in images:
            clean_result = {
                "type": "image",
                "image_url": image["url"],
                "image_description": image.get("description", "")[:200] + "..." if len(image.get("description", "")) > 200 else image.get("description", ""),
            }
            clean_results.append(clean_result)
        return clean_results
