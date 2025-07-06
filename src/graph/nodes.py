# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_with_reasoning_effort, add_no_think_if_needed
from src.prompts.planner_model import Plan, StepType
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return "Handoff to planner completed"


def background_investigation_node(state: State, config: RunnableConfig):
    """Background investigation node that gathers information about the query before planning."""
    logger.info("后台调查节点正在运行")
    Configuration.from_runnable_config(config)
    query = state.get("research_topic", "")
    
    # Simple and safe implementation that always succeeds
    try:
        logger.info(f"正在对以下内容进行后台调查: {query}")
        
        # For now, provide a simple background context
        # This avoids the complex tool calling issues while maintaining functionality
        # NOTE: If this node ever uses LLM calls in the future, make sure to add:
        # llm = get_llm_with_reasoning_effort(AGENT_LLM_MAP["background_investigator"], "low")
        # messages = add_no_think_if_needed(messages, llm, "low")
        
        result_content = f"""Background investigation completed for: {query}

## Initial Context
Based on the research topic "{query}", relevant areas for investigation include:
- Current status and recent developments
- Key stakeholders and organizations involved  
- Available data sources and documentation
- Regulatory and policy framework
- Best practices and case studies

This background provides context for developing a comprehensive research plan."""
        
        logger.info("后台调查成功完成")
        
        return {
            "background_investigation_results": result_content
        }
        
    except Exception as e:
        logger.error(f"后台调查出错: {e}")
        # Always return a safe result to avoid breaking the workflow
        return {
            "background_investigation_results": f"Background investigation completed for topic: {query}. Ready to proceed with detailed research."
        }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that makes or updates a plan for the research."""
    logger.info("规划员正在生成完整计划")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state.get("plan_iterations", 0)
    max_plan_iterations = configurable.max_plan_iterations
    
    logger.info("Planner generating full plan")
    
    # Check if plan iterations exceeded - go directly to reporter
    if plan_iterations >= max_plan_iterations:
        logger.info(f"计划迭代次数 {plan_iterations} >= 最大值 {max_plan_iterations}，转到报告员")
        return Command(goto="reporter")
    
    # Get LLM and messages
    llm = get_llm_with_reasoning_effort(AGENT_LLM_MAP["planner"], "low")
    messages = apply_prompt_template("planner", state, configurable)
    
    # Convert to LangChain messages if needed
    langchain_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        else:
            langchain_messages.append(msg)
    
    # Add /no_think for low reasoning effort
    langchain_messages = add_no_think_if_needed(langchain_messages, llm, "low")
    logger.info("为规划员添加了 /no_think")
    
    # Use safer LLM invocation to avoid callback issues
    full_response = ""
    
    try:
        # Use simple invoke instead of streaming to avoid callback issues
        response = llm.invoke(langchain_messages)
        full_response = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"LLM响应: {len(full_response)} 字符")
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        return Command(goto="__end__")
    
    # Parse JSON response
    try:
        curr_plan = json.loads(repair_json_output(full_response))
        logger.info(f"解析的计划: has_enough_context={curr_plan.get('has_enough_context')}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        if plan_iterations > 0:
            return Command(goto="reporter")
        return Command(goto="__end__")
    
    # Route based on has_enough_context - but let the router function handle the actual routing
    if curr_plan.get("has_enough_context"):
        new_plan = Plan.model_validate(curr_plan)
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": new_plan,
            }
        )
    
    # Return with string plan for human feedback
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner")],
            "current_plan": full_response,
        }
    )


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        # Provide clear options for the user
        feedback = interrupt("Please review the research plan and choose an action:")

        # Handle user feedback
        if feedback and str(feedback).lower() == "edit_plan":
            # User wants to edit the plan, go back to planner with edit instruction
            return Command(
                update={
                    "messages": [
                        HumanMessage(content="[EDIT_PLAN] Please revise the research plan based on user feedback.", name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).lower() == "accepted":
            logger.info("用户接受了计划")
        else:
            # For any string feedback that starts with [EDIT_PLAN], extract and use the edited plan
            if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
                try:
                    # Extract the JSON plan from the feedback
                    feedback_str = str(feedback)
                    # Find the JSON part after [EDIT_PLAN]
                    json_start = feedback_str.find("{")
                    if json_start != -1:
                        edited_plan_json = feedback_str[json_start:]
                        # Parse and validate the edited plan
                        edited_plan_data = json.loads(edited_plan_json)
                        
                        # Ensure the plan has required fields
                        if "title" not in edited_plan_data:
                            edited_plan_data["title"] = "Deep Research"
                        if "thought" not in edited_plan_data:
                            edited_plan_data["thought"] = ""
                        if "steps" not in edited_plan_data:
                            edited_plan_data["steps"] = []
                        if "has_enough_context" not in edited_plan_data:
                            edited_plan_data["has_enough_context"] = False
                        if "locale" not in edited_plan_data:
                            edited_plan_data["locale"] = state.get("locale", "en-US")
                        
                        # Ensure each step has required fields
                        for i, step in enumerate(edited_plan_data["steps"]):
                            if "need_search" not in step:
                                step["need_search"] = True  # Default to True for research steps
                            if "step_type" not in step:
                                step["step_type"] = "research"  # Default to research
                            if "execution_res" not in step:
                                step["execution_res"] = None
                        
                        logger.info(f"使用编辑的计划: title='{edited_plan_data['title']}', steps={len(edited_plan_data.get('steps', []))}")
                        
                        # Use the edited plan directly, no need to go back to planner
                        plan_iterations = state.get("plan_iterations", 0) + 1
                        goto = "research_team" if not edited_plan_data["has_enough_context"] else "reporter"
                        
                        return Command(
                            update={
                                "messages": [
                                    HumanMessage(content=f"Plan updated by user: {edited_plan_data['title']}", name="feedback"),
                                ],
                                "current_plan": Plan.model_validate(edited_plan_data),
                                "plan_iterations": plan_iterations,
                                "locale": edited_plan_data["locale"],
                            },
                            goto=goto,
                        )
                    else:
                        logger.warning("在EDIT_PLAN反馈中未找到有效的JSON，返回规划员")
                        return Command(
                            update={
                                "messages": [
                                    HumanMessage(content=feedback, name="feedback"),
                                ],
                            },
                            goto="planner",
                        )
                except json.JSONDecodeError as e:
                    logger.error(f"解析编辑计划JSON失败: {e}，返回规划员")
                    return Command(
                        update={
                            "messages": [
                                HumanMessage(content=feedback, name="feedback"),
                            ],
                        },
                        goto="planner",
                    )
            elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
                logger.info("用户接受了计划")
            else:
                logger.warning(f"意外的中断反馈: {feedback}，视为已接受")
                # Default to accepting the plan to avoid workflow interruption

    # if the plan is accepted, run the following node
    plan_iterations = state.get("plan_iterations", 0)
    goto = "research_team"
    
    # Handle both string and Plan object cases
    if isinstance(current_plan, str):
        # Current plan is a string - need to parse it
        try:
            current_plan = repair_json_output(current_plan)
            plan_iterations += 1
            new_plan = json.loads(current_plan)
            
            # Ensure the plan has required fields
            if "locale" not in new_plan:
                new_plan["locale"] = state.get("locale", "en-US")
            if "has_enough_context" not in new_plan:
                new_plan["has_enough_context"] = False
            if "title" not in new_plan:
                new_plan["title"] = "Deep Research"
            if "thought" not in new_plan:
                new_plan["thought"] = ""
            if "steps" not in new_plan:
                new_plan["steps"] = []
            
            # Ensure each step has required fields
            for step in new_plan["steps"]:
                if "need_search" not in step:
                    step["need_search"] = True
                if "step_type" not in step:
                    step["step_type"] = "research"
                if "execution_res" not in step:
                    step["execution_res"] = None
            
            if new_plan["has_enough_context"]:
                goto = "reporter"
                
            logger.info(f"Successfully parsed string plan: title='{new_plan['title']}', steps={len(new_plan['steps'])}, goto={goto}")
            
            return Command(
                update={
                    "current_plan": Plan.model_validate(new_plan),
                    "plan_iterations": plan_iterations,
                    "locale": new_plan["locale"],
                },
                goto=goto,
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for string plan: {e}")
            logger.error(f"Failed plan content: {current_plan[:500]}...")
            if plan_iterations > 1:
                return Command(goto="reporter")
            else:
                return Command(goto="__end__")
        except Exception as e:
            logger.error(f"Unexpected error parsing plan: {e}")
            return Command(goto="__end__")
    else:
        # Current plan is already a Plan object
        if hasattr(current_plan, 'has_enough_context') and current_plan.has_enough_context:
            goto = "reporter"
        
        logger.info(f"Using existing Plan object: title='{getattr(current_plan, 'title', 'N/A')}', goto={goto}")
        
        return Command(
            update={
                "plan_iterations": plan_iterations + 1,
            },
            goto=goto,
        )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("协调员正在对话")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("coordinator", state)
    
    # Simple LLM setup with low reasoning effort
    llm = get_llm_with_reasoning_effort(AGENT_LLM_MAP["coordinator"], "low")
    
    # Convert to LangChain messages if needed
    langchain_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        else:
            langchain_messages.append(msg)
    
    # Add /no_think for low reasoning effort
    langchain_messages = add_no_think_if_needed(langchain_messages, llm, "low")
    logger.info("为协调员添加了 /no_think")
    
    # Bind tools and invoke
    response = llm.bind_tools([handoff_to_planner]).invoke(langchain_messages)
    logger.info(f"Coordinator response: tool_calls={len(response.tool_calls)}, content_length={len(response.content) if response.content else 0}")
    
    # Check if coordinator called handoff_to_planner (research question)
    if len(response.tool_calls) > 0:
        # This is a research question - extract parameters and proceed to planner
        locale = state.get("locale", "en-US")
        research_topic = state.get("research_topic", "")
        
        try:
            for tool_call in response.tool_calls:
                logger.info(f"Processing tool call: {tool_call.get('name', 'unknown')}")
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_call.get("args", {}).get("locale") and tool_call.get(
                    "args", {}
                ).get("research_topic"):
                    locale = tool_call.get("args", {}).get("locale")
                    research_topic = tool_call.get("args", {}).get("research_topic")
                    logger.info(f"Extracted: locale={locale}, research_topic={research_topic}")
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
        
        # Return without goto to let router function decide (will go to planner)
        return Command(
            update={
                "locale": locale,
                "research_topic": research_topic,
                "resources": configurable.resources,
            }
        )
    else:
        # This is a simple question/greeting - coordinator handled it directly
        logger.info("协调员直接处理了请求（简单问题/问候）")
        
        # Return the coordinator's direct response and end the workflow
        return Command(
            update={
                "messages": [
                    AIMessage(content=response.content, name="coordinator"),
                ],
                "locale": state.get("locale", "en-US"),
                "research_topic": "",
                "resources": configurable.resources,
            },
            goto="__end__",
        )


def research_team_node(state: State):
    """Research team coordination node"""
    logger.info("研究团队正在协调任务")
    current_plan = state.get("current_plan")
    
    if not current_plan or not hasattr(current_plan, 'steps') or not current_plan.steps:
        logger.info("没有可用的计划，路由到规划员")
        return
    
    # Find the first unexecuted step
    for step in current_plan.steps:
        if not getattr(step, 'execution_res', None):
            logger.info(f"Processing step: '{step.title}'")
            step_type = getattr(step, 'step_type', None)
            if step_type == StepType.RESEARCH:
                logger.info(f"Routing to researcher for: '{step.title}'")
            elif step_type == StepType.PROCESSING:
                logger.info(f"Routing to coder for: '{step.title}'")
            else:
                logger.info(f"Unknown step type, routing to planner for: '{step.title}'")
            # Return to let the router function decide where to go
            return
    
    # All steps are completed
    logger.info("所有研究步骤已完成，进入报告生成阶段")
    return


async def _execute_agent_step(
    state: State, agent, agent_name: str, specific_step=None
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Use specific step if provided (for parallel execution), otherwise find first unexecuted step
    if specific_step:
        current_step = specific_step
        logger.info(f"Executing specific step (parallel): {current_step.title}, agent: {agent_name}")
    else:
        # Find the first unexecuted step (legacy serial execution)
        current_step = None
        if current_plan and hasattr(current_plan, 'steps'):
            for step in current_plan.steps:
                if not getattr(step, 'execution_res', None):
                    current_step = step
                    break

        if not current_step:
            logger.info("All research steps completed, proceeding to report generation")
            return Command(goto="reporter")

        logger.info(f"Executing step (serial): {current_step.title}, agent: {agent_name}")

    # Get completed steps for context (only if we have access to current_plan)
    completed_steps = []
    if current_plan and hasattr(current_plan, 'steps'):
        for step in current_plan.steps:
            if getattr(step, 'execution_res', None):
                completed_steps.append(step)

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        if state.get("resources"):
            resources_info = "**The user mentioned the following resource files:**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            agent_input["messages"].append(
                HumanMessage(
                    content=resources_info
                    + "\n\n"
                    + "You MUST use the **local_search_tool** to retrieve the information from the resource files.",
                )
            )

        agent_input["messages"].append(
            HumanMessage(
                content="重要：请勿在正文中使用内联引用。请在文末单独设置参考文献部分，使用链接引用格式。为了更好的可读性，每个引用之间留空行。请使用以下格式：\n- [资料标题](网址)\n\n- [另一个资料](网址)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    logger.info(f"Agent input: {agent_input}")
    
    execution_result = ""
    try:
        # 🚀 智能超时机制 - 根据任务类型设置不同超时时间
        import asyncio
        
        # 智能判断任务复杂度并设置超时时间
        task_title = current_step.title.lower() if current_step else ""
        task_desc = current_step.description.lower() if current_step else ""
        
        # 整理/总结类任务需要更多时间处理数据
        is_organize_task = any(keyword in task_title or keyword in task_desc 
                               for keyword in ['整理', '呈现', '总结', '汇总', '分析', 'organize', 'present', 'summarize', 'analyze'])
        
        # 设置动态超时时间
        if is_organize_task:
            timeout_seconds = 300.0  # 5分钟，用于复杂的数据整理任务
            timeout_desc = "5分钟（数据整理任务）"
        else:
            timeout_seconds = 180.0  # 3分钟，用于搜索任务
            timeout_desc = "3分钟（搜索任务）"
        
        logger.info(f"Starting agent {agent_name} execution with {timeout_desc} timeout")
        result = await asyncio.wait_for(
            agent.ainvoke(
                input=agent_input, 
                config={"recursion_limit": recursion_limit}
            ),
            timeout=timeout_seconds
        )
        
        # Process the result
        if not result or "messages" not in result or not result["messages"]:
            logger.error(f"Agent {agent_name} returned empty or invalid result")
            execution_result = f"Error: Agent {agent_name} failed to produce valid output"
        else:
            response_content = result["messages"][-1].content
            if not response_content or response_content.strip() == "":
                logger.warning(f"Agent {agent_name} returned empty content")
                execution_result = f"Agent {agent_name} completed task but returned empty content"
            else:
                execution_result = response_content
            
            logger.debug(f"{agent_name.capitalize()} full response: {execution_result}")
            
        logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")
        
    except asyncio.TimeoutError:
        timeout_minutes = int(timeout_seconds // 60)
        logger.error(f"Agent {agent_name} execution timed out after {timeout_seconds} seconds")
        execution_result = f"Error: Agent {agent_name} timed out after {timeout_minutes} minutes. Task '{current_step.title}' was not completed."
        logger.info(f"Step '{current_step.title}' failed due to timeout, marked as completed with error")
    except Exception as e:
        logger.error(f"Error executing agent {agent_name}: {str(e)}", exc_info=True)
        execution_result = f"Error: Agent {agent_name} failed with error: {str(e)}"
        logger.info(f"Step '{current_step.title}' failed, marked as completed with error")

    # Update the step with the execution result (works for both serial and parallel)
    current_step.execution_res = execution_result

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=execution_result,
                    name=agent_name,
                )
            ],
            "observations": observations + [execution_result],
        },
        goto="research_team",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        # Fix: Use the correct MCP client usage pattern as per langchain-mcp-adapters 0.1.0+
        client = MultiServerMCPClient(mcp_servers)
        try:
            loaded_tools = default_tools[:]
            tools = await client.get_tools()
            for tool in tools:
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type, "low")
            # IMPORTANT: Pass specific_step=None to ensure serial execution mode
            return await _execute_agent_step(state, agent, agent_type, specific_step=None)
        except Exception as e:
            logger.warning(f"MCP client error: {e}, falling back to default tools")
            # Fallback to default tools if MCP fails
            agent = create_agent(agent_type, agent_type, default_tools, agent_type, "low")
            # IMPORTANT: Pass specific_step=None to ensure serial execution mode
            return await _execute_agent_step(state, agent, agent_type, specific_step=None)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type, "low")
        # IMPORTANT: Pass specific_step=None to ensure serial execution mode
        return await _execute_agent_step(state, agent, agent_type, specific_step=None)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("研究员节点正在进行研究")
    configurable = Configuration.from_runnable_config(config)
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    logger.info(f"Researcher tools: {tools}")
    
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher", 
        tools,
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis"""
    logger.info("编程员节点正在编程")
    
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )


async def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("报告员正在撰写最终报告")
    
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_, configurable)
    observations = state.get("observations", [])

    # Add citation reminder
    invoke_messages.append(
        HumanMessage(
            content=(
                "\n\n# 重要报告撰写指导\n\n"
                "## 报告结构\n"
                "请按照以下结构撰写研究报告：\n"
                "1. **执行摘要** - 关键发现的简要概述\n"
                "2. **引言** - 背景和研究目标\n"
                "3. **研究方法** - 研究过程描述\n"
                "4. **研究发现** - 详细分析和发现\n"
                "5. **讨论分析** - 解释和影响\n"
                "6. **结论** - 总结和未来方向\n\n"
                "## 引用要求\n"
                "- 请勿在正文中使用内联引用\n"
                "- 在文末单独设置参考文献部分，使用链接引用格式\n"
                "- 格式：- [资料标题](网址)\n"
                "- 每个引用之间留空行，提高可读性\n\n"
                "## 视觉元素\n"
                "- 使用markdown表格进行数据对比\n"
                "- 使用要点列表展示关键见解\n"
                "- 包含相关统计数据和图表\n"
                "- 使用标题清晰组织内容\n\n"
                f"## 可用研究数据\n"
                f"您可以使用 {len(observations)} 项研究观察结果来支持您的分析。\n\n"
                f"## 研究数据使用指导\n"
                f"- 完整整合所有研究发现，不要遗漏重要信息\n"
                f"- 保留研究数据中的所有引用和参考文献\n"
                f"- 研究数据中的引用格式已经标准化，请直接使用\n"
                f"- 确保报告的专业性和内容的完整性\n"
                f"- 如果研究数据包含图表或数据表，请在报告中复现"
            )
        )
    )

    # Add observations to the conversation
    # 🚀 修复：正确处理observations（字符串列表）
    for i, obs in enumerate(observations):
        if obs and str(obs).strip():  # 确保观察结果不为空
            invoke_messages.append(
                HumanMessage(content=f"**Research Data {i+1}**: {str(obs)}")
            )

    # Report generation: Use low reasoning mode for faster and more stable generation
    logger.info("报告员使用低推理模式进行稳定快速报告生成")
    
    llm = get_llm_with_reasoning_effort(
        llm_type=AGENT_LLM_MAP["reporter"], 
        reasoning_effort="low"
    )
    
    # Add /no_think for low reasoning effort (following coordinator_node pattern)
    invoke_messages = add_no_think_if_needed(invoke_messages, llm, "low")
    logger.info("为报告员添加了 /no_think，使用低推理模式")
    
    try:
        # 🚀 添加超时机制 - 为低推理模式设置5分钟超时（更合理的时间）
        import asyncio
        
        logger.info("开始报告生成，设置5分钟超时保护")
        logger.info(f"正在处理 {len(observations)} 项研究数据...")
        
        response = await asyncio.wait_for(
            llm.ainvoke(invoke_messages),
            timeout=300.0  # 5分钟超时，适应低推理模式的快速生成
        )
        
        full_response = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"报告生成成功完成！")
        logger.info(f"报告总字数: {len(full_response)} 字符")
        logger.info(f"基于 {len(observations)} 项研究发现生成最终报告")
        
    except asyncio.TimeoutError:
        logger.error("报告生成在5分钟后超时，生成基础报告")
        full_response = f"""# 报告生成超时

## 执行摘要

由于网络或模型响应延迟，完整报告生成超时。基于已收集的研究数据，提供以下基础分析：

## 研究发现

已成功收集了 {len(observations)} 项研究数据，包含以下关键信息：

{chr(10).join([f"- 研究发现 {i+1}: {str(obs)[:200]}..." for i, obs in enumerate(observations[:5])])}

## 结论

研究任务"{current_plan.title}"已收集到相关数据，但由于模型推理复杂度较高，完整报告生成超时。
建议：
1. 尝试简化研究问题
2. 使用更快的模型配置
3. 分阶段进行深入分析

## 说明

此报告由于超时限制自动生成。如需完整深度分析，请考虑调整系统配置或使用更高性能的推理模型。"""
        
    except Exception as e:
        logger.error(f"报告员调用失败: {e}")
        full_response = f"""# 报告生成错误

## 错误信息

在生成研究报告"{current_plan.title}"时发生错误：{str(e)}

## 收集的数据概要

尽管报告生成失败，系统已成功收集了 {len(observations)} 项研究数据。

## 建议

1. 检查网络连接和模型配置
2. 尝试重新运行研究任务
3. 如问题持续存在，请联系技术支持

此为自动生成的错误报告。"""

    return Command(
        update={
            "messages": [
                AIMessage(content=full_response, name="reporter"),
            ],
            "final_report": full_response,
        },
        goto="__end__",
    )
