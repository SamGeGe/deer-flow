# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import Annotated

from langchain_core.tools import tool
from .decorators import log_io

from src.crawler import Crawler

logger = logging.getLogger(__name__)


@tool
@log_io
def crawl_tool(
    url: Annotated[str, "The url to crawl."],
) -> str:
    """Use this to crawl a url and get a readable content in markdown format."""
    try:
        crawler = Crawler()
        article = crawler.crawl(url)
        if article and hasattr(article, 'to_markdown'):
            content = article.to_markdown()
            if content:
                return f"URL: {url}\n\nContent:\n{content[:2000]}"
            else:
                return f"URL: {url}\n\nContent: [Empty content extracted]"
        else:
            return f"URL: {url}\n\nContent: [Failed to extract article content]"
    except IndexError as e:
        error_msg = f"Failed to crawl {url}. IndexError: {str(e)} - This may be due to malformed HTML or parsing issues."
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Failed to crawl {url}. Error: {str(e)}"
        logger.error(error_msg)
        return error_msg
