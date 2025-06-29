# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.prompts.planner_model import StepType

logger = logging.getLogger(__name__)

from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    reporter_node,
    research_team_node,
    researcher_node,
    coder_node,
    human_feedback_node,
    background_investigation_node,
)


def continue_to_running_research_team(state: State):
    """Router function for research team coordination"""
    try:
        current_plan = state.get("current_plan")
        if not current_plan or not hasattr(current_plan, 'steps') or not current_plan.steps:
            logger.info("🔄 Router: No plan available, going to planner")
            return "planner"
        
        # Find the first unexecuted step and route based on step_type
        for step in current_plan.steps:
            if not getattr(step, 'execution_res', None):
                step_type = getattr(step, 'step_type', None)
                step_title = getattr(step, 'title', '').lower()
                step_description = getattr(step, 'description', '').lower()
                
                # 🚀 智能路由策略：优先使用researcher处理大多数任务
                
                # 总结类任务 → researcher
                summary_keywords = ['总结', '汇总', '综合', '概述', '整理', '呈现', 'summary', 'summarize', 'present', 'conclude']
                is_summary_task = any(keyword in step_title or keyword in step_description for keyword in summary_keywords)
                
                # 简单数学计算任务 → researcher (LLM直接计算)
                simple_math_keywords = ['计算', '比例', '倍数', '百分比', '对比', '相比', 'calculate', 'ratio', 'compare', 'percentage']
                is_simple_math = any(keyword in step_title or keyword in step_description for keyword in simple_math_keywords)
                
                # 复杂编程任务 → coder (需要实际代码执行)
                complex_coding_keywords = ['算法', '编程', '文件', '图表', '绘图', '数据分析', '统计', 'algorithm', 'programming', 'file', 'chart', 'plot', 'data analysis', 'statistics']
                is_complex_coding = any(keyword in step_title or keyword in step_description for keyword in complex_coding_keywords)
                
                if is_summary_task:
                    logger.info(f"🔄 Router: Summary task detected, going to researcher for: '{step.title}'")
                    return "researcher"
                elif is_simple_math and not is_complex_coding:
                    logger.info(f"🔄 Router: Simple math task detected, going to researcher for: '{step.title}'")
                    return "researcher"
                elif step_type == StepType.RESEARCH:
                    logger.info(f"🔄 Router: Research task, going to researcher")
                    return "researcher"
                elif step_type == StepType.PROCESSING and is_complex_coding:
                    logger.info(f"🔄 Router: Complex coding task, going to coder")
                    return "coder"
                elif step_type == StepType.PROCESSING:
                    # 默认处理任务也先尝试researcher（LLM直接处理）
                    logger.info(f"🔄 Router: Processing task, trying researcher first for: '{step.title}'")
                    return "researcher"
                else:
                    # Default to researcher
                    logger.info(f"🔄 Router: Unknown step type, defaulting to researcher")
                    return "researcher"
        
        # All steps are executed, go to reporter
        logger.info("🔄 Router: All tasks completed, going to reporter")
        return "reporter"
        
    except Exception as e:
        logger.error(f"Router error: {e}")
        return "reporter"


def continue_from_coordinator(state: State):
    """Router function for coordinator node"""
    try:
        # Check if coordinator handled the request directly (simple greeting/question)
        research_topic = state.get("research_topic", "")
        
        # If research_topic is empty, it means coordinator handled it directly
        if not research_topic or research_topic.strip() == "":
            # Coordinator handled directly, end the workflow
            return "__end__"
        
        # This is a research question, proceed with research workflow
        enable_background_investigation = state.get("enable_background_investigation", False)
        if enable_background_investigation:
            return "background_investigator"
        return "planner"
    except Exception as e:
        logger.error(f"Router error in coordinator: {e}")
        return "__end__"


def continue_from_planner(state: State):
    """Router function for planner node"""
    try:
        current_plan = state.get("current_plan")
        logger.info(f"ROUTER DEBUG: current_plan type={type(current_plan)}, value={str(current_plan)[:100]}...")
        
        if isinstance(current_plan, str):
            # If current_plan is a string, we need human feedback
            logger.info("ROUTER: Going to human_feedback (string plan)")
            return "human_feedback"
        elif hasattr(current_plan, 'has_enough_context') and current_plan.has_enough_context:
            # If we have enough context, go directly to reporter
            logger.info("ROUTER: Going to reporter (enough context)")
            return "reporter"
        else:
            # Otherwise, need human feedback
            logger.info(f"ROUTER: Going to human_feedback (not enough context, has_enough_context={getattr(current_plan, 'has_enough_context', 'N/A')})")
            return "human_feedback"
    except Exception as e:
        logger.error(f"Router error in planner: {e}")
        return "human_feedback"


def continue_from_human_feedback(state: State):
    """Router function for human_feedback node"""
    try:
        current_plan = state.get("current_plan")
        if hasattr(current_plan, 'has_enough_context') and current_plan.has_enough_context:
            return "reporter"
        return "research_team"
    except Exception as e:
        logger.error(f"Router error in human_feedback: {e}")
        return "research_team"


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("background_investigator", background_investigation_node)
    builder.add_node("planner", planner_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("research_team", research_team_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)
    builder.add_node("human_feedback", human_feedback_node)
    
    # Add conditional edges for proper routing
    builder.add_conditional_edges(
        "coordinator",
        continue_from_coordinator,
        ["background_investigator", "planner", "__end__"],
    )
    builder.add_edge("background_investigator", "planner")
    builder.add_conditional_edges(
        "planner",
        continue_from_planner,
        ["human_feedback", "reporter"],
    )
    builder.add_conditional_edges(
        "human_feedback",
        continue_from_human_feedback,
        ["research_team", "reporter"],
    )
    builder.add_conditional_edges(
        "research_team",
        continue_to_running_research_team,
        ["planner", "researcher", "coder", "reporter"],
    )
    builder.add_edge("researcher", "research_team")
    builder.add_edge("coder", "research_team")
    builder.add_edge("reporter", END)
    return builder


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    try:
        # use persistent memory to save conversation history
        # TODO: be compatible with SQLite / PostgreSQL
        memory = MemorySaver()

        # build state graph
        builder = _build_base_graph()
        return builder.compile(checkpointer=memory)
    except Exception as e:
        logger.warning(f"Failed to build graph with memory: {e}, falling back to no-memory version")
        try:
            # 降级到无内存版本
            builder = _build_base_graph()
            return builder.compile()
        except Exception as fallback_error:
            logger.error(f"Failed to build graph even without memory: {fallback_error}")
            # 返回最基本的图
            basic_builder = StateGraph(State)
            basic_builder.add_node("coordinator", coordinator_node)
            basic_builder.add_node("reporter", reporter_node)
            basic_builder.add_edge(START, "coordinator")
            basic_builder.add_edge("coordinator", "reporter")
            basic_builder.add_edge("reporter", END)
            return basic_builder.compile()


def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph()
    return builder.compile()


graph = build_graph()
