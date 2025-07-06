# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import logging
import os
from typing import Annotated, List, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessageChunk, ToolMessage, BaseMessage
from langgraph.types import Command

from src.config.report_style import ReportStyle
from src.config.tools import SELECTED_RAG_PROVIDER
from src.graph.builder import build_graph_with_memory
from src.podcast.graph.builder import build_graph as build_podcast_graph
from src.ppt.graph.builder import build_graph as build_ppt_graph
from src.prose.graph.builder import build_graph as build_prose_graph
from src.prompt_enhancer.graph.builder import build_graph as build_prompt_enhancer_graph
from src.rag.builder import build_retriever
from src.rag.retriever import Resource
from src.server.chat_request import (
    ChatRequest,
    EnhancePromptRequest,
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    TTSRequest,
)
from src.server.mcp_request import MCPServerMetadataRequest, MCPServerMetadataResponse
from src.server.mcp_utils import load_mcp_tools
from src.server.rag_request import (
    RAGConfigResponse,
    RAGResourceRequest,
    RAGResourcesResponse,
)
from src.server.config_request import ConfigResponse
from src.llms.llm import get_configured_llm_models
from src.tools import VolcengineTTS

logger = logging.getLogger(__name__)

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"

app = FastAPI(
    title="DeerFlow API",
    description="API for Deer",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Serve static files from the "outputs" directory
if not os.path.exists("outputs"):
    os.makedirs("outputs")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

graph = build_graph_with_memory()


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())
    return StreamingResponse(
        _astream_workflow_generator(
            request.model_dump()["messages"],
            thread_id,
            request.resources,
            request.max_plan_iterations,
            request.max_step_num,
            request.max_search_results,
            request.auto_accepted_plan,
            request.interrupt_feedback,
            request.mcp_settings,
            request.enable_background_investigation,
            request.report_style,
            request.enable_deep_thinking,
        ),
        media_type="text/event-stream",
    )


async def _astream_workflow_generator(
    messages: List[dict],
    thread_id: str,
    resources: List[Resource],
    max_plan_iterations: int,
    max_step_num: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation: bool,
    report_style: ReportStyle,
    enable_deep_thinking: bool,
):
    input_ = {
        "messages": messages,
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": auto_accepted_plan,
        "enable_background_investigation": enable_background_investigation,
        "research_topic": messages[-1]["content"] if messages else "",
    }
    if not auto_accepted_plan and interrupt_feedback:
        resume_msg = f"[{interrupt_feedback}]"
        # add the last message to the resume message
        if messages:
            resume_msg += f" {messages[-1]['content']}"
        input_ = Command(resume=resume_msg)
    async for agent, _, event_data in graph.astream(
        input_,
        config={
            "thread_id": thread_id,
            "resources": resources,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "max_search_results": max_search_results,
            "mcp_settings": mcp_settings,
            "report_style": report_style.value,
            "enable_deep_thinking": enable_deep_thinking,
        },
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        try:
            # 新增：根据 agent 推送 progress/activity
            agent_name = None
            try:
                if isinstance(agent, (list, tuple)) and len(agent) > 0:
                    agent_name = str(agent[0]).split(":")[0]
                elif agent:
                    agent_name = str(agent).split(":")[0]
            except (IndexError, AttributeError):
                agent_name = None
                
            if agent_name:
                progress_map = {
                    "coordinator": "正在分析你的问题...",
                    "background_investigator": "正在调用搜索引擎获取资料...",
                    "planner": "正在生成研究计划...",
                    "research_team": "研究团队正在协作...",
                    "researcher": "正在查找和整理资料...",
                    "coder": "正在分析和生成代码...",
                    "reporter": "正在撰写最终报告...",
                    "human_feedback": "等待用户反馈...",
                }
                if agent_name in progress_map and progress_map[agent_name]:
                    yield _make_event(
                        "activity",
                        {"activity": progress_map[agent_name]},
                    )
            if isinstance(event_data, dict):
                if "__interrupt__" in event_data:
                    yield _make_event(
                        "interrupt",
                        {
                            "thread_id": thread_id,
                            "id": event_data["__interrupt__"][0].ns[0],
                            "role": "assistant",
                            "content": event_data["__interrupt__"][0].value,
                            "finish_reason": "interrupt",
                            "options": [
                                {"text": "编辑计划", "value": "edit_plan"},
                                {"text": "开始研究", "value": "accepted"},
                            ],
                        },
                    )
                continue
            message_chunk, message_metadata = cast(
                tuple[BaseMessage, dict[str, any]], event_data
            )
            event_stream_message: dict[str, any] = {
                "thread_id": thread_id,
                "agent": agent_name or "unknown",
                "id": message_chunk.id,
                "role": "assistant",
                "content": message_chunk.content,
            }
            if message_chunk.additional_kwargs.get("reasoning_content"):
                event_stream_message["reasoning_content"] = message_chunk.additional_kwargs[
                    "reasoning_content"
                ]
            if message_chunk.response_metadata.get("finish_reason"):
                event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                    "finish_reason"
                )
            if isinstance(message_chunk, ToolMessage):
                # Tool Message - Return the result of the tool call
                event_stream_message["tool_call_id"] = message_chunk.tool_call_id
                yield _make_event("tool_call_result", event_stream_message)
            elif isinstance(message_chunk, AIMessageChunk):
                # AI Message - Raw message tokens
                if message_chunk.tool_calls:
                    # AI Message - Tool Call
                    event_stream_message["tool_calls"] = message_chunk.tool_calls
                    event_stream_message["tool_call_chunks"] = (
                        message_chunk.tool_call_chunks
                    )
                    yield _make_event("tool_calls", event_stream_message)
                elif message_chunk.tool_call_chunks:
                    # AI Message - Tool Call Chunks
                    event_stream_message["tool_call_chunks"] = (
                        message_chunk.tool_call_chunks
                    )
                    yield _make_event("tool_call_chunks", event_stream_message)
                else:
                    # AI Message - Raw message tokens
                    yield _make_event("message_chunk", event_stream_message)
        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            # 发送错误事件但不中断流
            yield _make_event("error", {
                "detail": f"Stream error: {str(e)[:100]}...",
                "agent": agent_name or "unknown"
            })
            # 继续处理下一个事件，而不是中断整个流


def _make_event(event_type: str, data: dict[str, any]):
    try:
        if data.get("content") == "":
            data.pop("content")
        # 确保数据可以被JSON序列化
        json_data = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event_type}\ndata: {json_data}\n\n"
    except Exception as e:
        logger.error(f"Error serializing event data: {e}")
        # 返回一个安全的错误事件
        safe_data = {
            "error": "Event serialization failed",
            "event_type": event_type,
            "detail": str(e)[:100]
        }
        return f"event: error\ndata: {json.dumps(safe_data, ensure_ascii=False)}\n\n"


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    app_id = os.getenv("VOLCENGINE_TTS_APPID", "")
    if not app_id:
        raise HTTPException(status_code=400, detail="VOLCENGINE_TTS_APPID is not set")
    access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")
    if not access_token:
        raise HTTPException(
            status_code=400, detail="VOLCENGINE_TTS_ACCESS_TOKEN is not set"
        )

    try:
        cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")
        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_V2_streaming")

        tts_client = VolcengineTTS(
            appid=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type,
        )
        # Call the TTS API
        result = tts_client.text_to_speech(
            text=request.text[:1024],
            encoding=request.encoding,
            speed_ratio=request.speed_ratio,
            volume_ratio=request.volume_ratio,
            pitch_ratio=request.pitch_ratio,
            text_type=request.text_type,
            with_frontend=request.with_frontend,
            frontend_type=request.frontend_type,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=str(result["error"]))

        # Decode the base64 audio data
        audio_data = base64.b64decode(result["audio_data"])

        # Return the audio file
        return Response(
            content=audio_data,
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=tts_output.{request.encoding}"
                )
            },
        )

    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_podcast_graph()
        final_state = workflow.invoke({"input": report_content})
        audio_bytes = final_state["output"]
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_ppt_graph()
        final_state = workflow.invoke({"input": report_content})
        generated_file_path = final_state["generated_file_path"]
        with open(generated_file_path, "rb") as f:
            ppt_bytes = f.read()
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")
        logger.info(f"Generating prose for prompt: {sanitized_prompt}")
        workflow = build_prose_graph()
        events = workflow.astream(
            {
                "content": request.prompt,
                "option": request.option,
                "command": request.command,
            },
            stream_mode="messages",
            subgraphs=True,
        )
        return StreamingResponse(
            (f"data: {event[0].content}\n\n" async for _, event in events),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.post("/api/prompt/enhance")
async def enhance_prompt(request: EnhancePromptRequest):
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")
        logger.info(f"Enhancing prompt: {sanitized_prompt}")

        # Convert string report_style to ReportStyle enum
        report_style = None
        if request.report_style:
            try:
                # Handle both uppercase and lowercase input
                style_mapping = {
                    "ACADEMIC": ReportStyle.ACADEMIC,
                    "POPULAR_SCIENCE": ReportStyle.POPULAR_SCIENCE,
                    "NEWS": ReportStyle.NEWS,
                    "SOCIAL_MEDIA": ReportStyle.SOCIAL_MEDIA,
                    "academic": ReportStyle.ACADEMIC,
                    "popular_science": ReportStyle.POPULAR_SCIENCE,
                    "news": ReportStyle.NEWS,
                    "social_media": ReportStyle.SOCIAL_MEDIA,
                }
                report_style = style_mapping.get(
                    request.report_style, ReportStyle.ACADEMIC
                )
            except BaseException:
                # If invalid style, default to ACADEMIC
                report_style = ReportStyle.ACADEMIC
        else:
            report_style = ReportStyle.ACADEMIC

        workflow = build_prompt_enhancer_graph()
        final_state = workflow.invoke(
            {
                "prompt": request.prompt,
                "context": request.context,
                "report_style": report_style,
            }
        )
        return {"result": final_state["output"]}
    except Exception as e:
        logger.exception(f"Error occurred during prompt enhancement: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint

        # Use custom timeout from request if provided
        if request.timeout_seconds is not None:
            timeout = request.timeout_seconds

        # Load tools from the MCP server using the utility function
        tools = await load_mcp_tools(
            server_type=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            timeout_seconds=timeout,
        )

        # Create the response with tools
        response = MCPServerMetadataResponse(
            transport=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            tools=tools,
        )

        return response
    except Exception as e:
        logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@app.get("/api/rag/config", response_model=RAGConfigResponse)
async def rag_config():
    """Get the config of the RAG."""
    return RAGConfigResponse(provider=SELECTED_RAG_PROVIDER)


@app.get("/api/rag/resources", response_model=RAGResourcesResponse)
async def rag_resources(request: Annotated[RAGResourceRequest, Query()]):
    """Get the resources of the RAG."""
    retriever = build_retriever()
    if retriever:
        return RAGResourcesResponse(resources=retriever.list_resources(request.query))
    return RAGResourcesResponse(resources=[])


@app.get("/api/config", response_model=ConfigResponse)
async def config():
    """Get the config of the server."""
    configured_models = get_configured_llm_models()
    
    # Ensure all expected model types are present, even if empty
    models = {
        "basic": configured_models.get("basic", []),
        "reasoning": configured_models.get("reasoning", []),
    }
    
    return ConfigResponse(
        rag=RAGConfigResponse(provider=SELECTED_RAG_PROVIDER),
        models=models,
    )
