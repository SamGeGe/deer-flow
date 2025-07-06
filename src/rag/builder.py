# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from src.config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from src.rag.ragflow import RAGFlowProvider
from src.rag.retriever import Retriever
from typing import Optional


def build_retriever() -> Optional[Retriever]:
    if SELECTED_RAG_PROVIDER == RAGProvider.RAGFLOW.value:
        return RAGFlowProvider()
    elif SELECTED_RAG_PROVIDER:
        raise ValueError(f"Unsupported RAG provider: {SELECTED_RAG_PROVIDER}")
    return None
