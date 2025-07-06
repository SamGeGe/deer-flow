# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import List, Optional, Type
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from src.config.tools import SELECTED_RAG_PROVIDER
from src.rag import Document, Retriever, Resource, build_retriever

logger = logging.getLogger(__name__)


class SearchInput(BaseModel):
    keywords: str = Field(description="搜索关键词")


class RetrieverTool(BaseTool):
    name: str = "local_search_tool"
    description: str = (
        "Useful for retrieving information from the file with `rag://` uri prefix, it should be higher priority than the web search or writing code. Input should be a search keywords."
    )
    args_schema: Type[BaseModel] = SearchInput

    retriever: Retriever = Field(default_factory=Retriever)
    resources: list[Resource] = Field(default_factory=list)

    def _run(
        self,
        keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> list[Document]:
        logger.info(
            f"Retriever tool query: {keywords}", extra={"resources": self.resources}
        )
        documents = self.retriever.query_relevant_documents(keywords, self.resources)
        if not documents:
            return "No results found from the local knowledge base."
        return [doc.to_dict() for doc in documents]

    async def _arun(
        self,
        keywords: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> list[Document]:
        # Safer async implementation to avoid callback errors
        try:
            logger.info(
                f"Async retriever tool query: {keywords}", extra={"resources": self.resources}
            )
            documents = self.retriever.query_relevant_documents(keywords, self.resources)
            if not documents:
                return "No results found from the local knowledge base."
            return [doc.to_dict() for doc in documents]
        except Exception as e:
            logger.error(f"Async retriever error: {e}")
            return "Error occurred while searching local knowledge base."


def get_retriever_tool(resources: List[Resource]) -> Optional[RetrieverTool]:
    if not resources:
        return None
    logger.info(f"create retriever tool: {SELECTED_RAG_PROVIDER}")
    retriever = build_retriever()

    if not retriever:
        return None
    return RetrieverTool(retriever=retriever, resources=resources)
