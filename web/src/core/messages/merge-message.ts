// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import type {
  ChatEvent,
  InterruptEvent,
  MessageChunkEvent,
  ToolCallChunksEvent,
  ToolCallResultEvent,
  ToolCallsEvent,
} from "../api";
import { deepClone } from "../utils/deep-clone";

import type { Message } from "./types";

export function mergeMessage(message: Message, event: ChatEvent) {
  try {
    if (event.type === "message_chunk") {
      mergeTextMessage(message, event);
    } else if (event.type === "tool_calls" || event.type === "tool_call_chunks") {
      mergeToolCallMessage(message, event);
    } else if (event.type === "tool_call_result") {
      mergeToolCallResultMessage(message, event);
    } else if (event.type === "interrupt") {
      mergeInterruptMessage(message, event);
    }
    
    // 处理完成状态
    if (event.data.finish_reason) {
      message.finishReason = event.data.finish_reason;
      message.isStreaming = false;
      
      // 调试信息：流式传输完成
      if (process.env.NODE_ENV === 'development') {
        console.debug('消息流式传输完成:', {
          messageId: message.id,
          agent: message.agent,
          contentLength: message.content?.length || 0,
          hasReasoningContent: !!message.reasoningContent,
          finishReason: message.finishReason
        });
      }
      
      if (message.toolCalls) {
        message.toolCalls.forEach((toolCall) => {
          if (toolCall.argsChunks?.length) {
            try {
              toolCall.args = JSON.parse(toolCall.argsChunks.join(""));
              delete toolCall.argsChunks;
            } catch (error) {
              console.warn('工具调用参数JSON解析失败:', {
                toolCallId: toolCall.id,
                argsChunks: toolCall.argsChunks,
                error
              });
              // 保留原始chunks，不删除
            }
          }
        });
      }
    }
    
    return deepClone(message);
  } catch (error) {
    console.error('消息合并错误:', {
      messageId: message.id,
      eventType: event.type,
      error
    });
    
    // 返回原消息，避免完全失败
    return message;
  }
}

function mergeTextMessage(message: Message, event: MessageChunkEvent) {
  try {
    // 处理主要内容
    if (event.data.content) {
      const newContent = String(event.data.content); // 确保是字符串
      message.content = (message.content || "") + newContent;
      message.contentChunks = message.contentChunks || [];
      message.contentChunks.push(newContent);
    }
    
    // 处理推理内容
    if (event.data.reasoning_content) {
      const newReasoningContent = String(event.data.reasoning_content);
      message.reasoningContent = (message.reasoningContent || "") + newReasoningContent;
      message.reasoningContentChunks = message.reasoningContentChunks || [];
      message.reasoningContentChunks.push(newReasoningContent);
    }
    
    // 调试信息：内容更新
    if (process.env.NODE_ENV === 'development' && (event.data.content || event.data.reasoning_content)) {
      console.debug('文本消息合并:', {
        messageId: message.id,
        agent: message.agent,
        newContentLength: event.data.content?.length || 0,
        totalContentLength: message.content?.length || 0,
        newReasoningLength: event.data.reasoning_content?.length || 0,
        totalReasoningLength: message.reasoningContent?.length || 0
      });
    }
  } catch (error) {
    console.error('文本消息合并错误:', {
      messageId: message.id,
      error,
      eventData: event.data
    });
  }
}

function mergeToolCallMessage(
  message: Message,
  event: ToolCallsEvent | ToolCallChunksEvent,
) {
  try {
    if (event.type === "tool_calls" && event.data.tool_calls[0]?.name) {
      message.toolCalls = event.data.tool_calls.map((raw) => ({
        id: raw.id,
        name: raw.name,
        args: raw.args,
        result: undefined,
      }));
    }

    message.toolCalls ??= [];
    for (const chunk of event.data.tool_call_chunks) {
      if (chunk.id) {
        const toolCall = message.toolCalls.find(
          (toolCall) => toolCall.id === chunk.id,
        );
        if (toolCall) {
          toolCall.argsChunks = [chunk.args];
        }
      } else {
        const streamingToolCall = message.toolCalls.find(
          (toolCall) => toolCall.argsChunks?.length,
        );
        if (streamingToolCall) {
          streamingToolCall.argsChunks!.push(chunk.args);
        }
      }
    }
    
    // 调试信息：工具调用更新
    if (process.env.NODE_ENV === 'development') {
      console.debug('工具调用消息合并:', {
        messageId: message.id,
        toolCallsCount: message.toolCalls?.length || 0,
        chunksCount: event.data.tool_call_chunks?.length || 0
      });
    }
  } catch (error) {
    console.error('工具调用消息合并错误:', {
      messageId: message.id,
      error,
      eventData: event.data
    });
  }
}

function mergeToolCallResultMessage(
  message: Message,
  event: ToolCallResultEvent,
) {
  try {
    const toolCall = message.toolCalls?.find(
      (toolCall) => toolCall.id === event.data.tool_call_id,
    );
    if (toolCall) {
      toolCall.result = event.data.content;
      
      // 调试信息：工具调用结果
      if (process.env.NODE_ENV === 'development') {
        console.debug('工具调用结果合并:', {
          messageId: message.id,
          toolCallId: toolCall.id,
          resultLength: event.data.content?.length || 0
        });
      }
    }
  } catch (error) {
    console.error('工具调用结果合并错误:', {
      messageId: message.id,
      toolCallId: event.data.tool_call_id,
      error
    });
  }
}

function mergeInterruptMessage(message: Message, event: InterruptEvent) {
  try {
    message.isStreaming = false;
    message.options = event.data.options;
    
    // 调试信息：中断消息
    if (process.env.NODE_ENV === 'development') {
      console.debug('中断消息合并:', {
        messageId: message.id,
        optionsCount: event.data.options?.length || 0
      });
    }
  } catch (error) {
    console.error('中断消息合并错误:', {
      messageId: message.id,
      error
    });
  }
}
