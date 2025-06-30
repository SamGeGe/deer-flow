// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { LoadingOutlined } from "@ant-design/icons";
import { motion } from "framer-motion";
import {
  Download,
  Headphones,
  ChevronDown,
  ChevronRight,
  Lightbulb,
} from "lucide-react";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Markdown } from "~/components/deer-flow/markdown";
import { RainbowText } from "~/components/deer-flow/rainbow-text";
import { RollingText } from "~/components/deer-flow/rolling-text";
import {
  ScrollContainer,
  type ScrollContainerRef,
} from "~/components/deer-flow/scroll-container";
import { Tooltip } from "~/components/deer-flow/tooltip";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Textarea } from "~/components/ui/textarea";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "~/components/ui/collapsible";
import type { Message, Option } from "~/core/messages";
import {
  closeResearch,
  openResearch,
  useLastFeedbackMessageId,
  useLastInterruptMessage,
  useMessage,
  useMessageIds,
  useResearchMessage,
  useStore,
} from "~/core/store";
import { parseJSON } from "~/core/utils";
import { cn } from "~/lib/utils";

export function MessageListView({
  className,
  onFeedback,
  onSendMessage,
}: {
  className?: string;
  onFeedback?: (feedback: { option: Option }) => void;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
}) {
  const scrollContainerRef = useRef<ScrollContainerRef>(null);
  const messageIds = useMessageIds();
  const interruptMessage = useLastInterruptMessage();
  const waitingForFeedbackMessageId = useLastFeedbackMessageId();
  const responding = useStore((state) => state.responding);
  const noOngoingResearch = useStore(
    (state) => state.ongoingResearchId === null,
  );
  const ongoingResearchIsOpen = useStore(
    (state) => state.ongoingResearchId === state.openResearchId,
  );

  const handleToggleResearch = useCallback(() => {
    // Fix the issue where auto-scrolling to the bottom
    // occasionally fails when toggling research.
    const timer = setTimeout(() => {
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollToBottom();
      }
    }, 500);
    return () => {
      clearTimeout(timer);
    };
  }, []);

  return (
    <ScrollContainer
      className={cn("flex h-full w-full flex-col overflow-hidden", className)}
      scrollShadowColor="var(--app-background)"
      autoScrollToBottom
      ref={scrollContainerRef}
    >
      <ul className="flex flex-col">
        {messageIds.map((messageId) => (
          <MessageListItem
            key={messageId}
            messageId={messageId}
            waitForFeedback={waitingForFeedbackMessageId === messageId}
            interruptMessage={interruptMessage}
            onFeedback={onFeedback}
            onSendMessage={onSendMessage}
            onToggleResearch={handleToggleResearch}
          />
        ))}
        <div className="flex h-8 w-full shrink-0"></div>
      </ul>
      {responding && (noOngoingResearch || !ongoingResearchIsOpen) && (
        <LoadingAnimation className="ml-4" />
      )}
    </ScrollContainer>
  );
}

function MessageListItem({
  className,
  messageId,
  waitForFeedback,
  interruptMessage,
  onFeedback,
  onSendMessage,
  onToggleResearch,
}: {
  className?: string;
  messageId: string;
  waitForFeedback?: boolean;
  onFeedback?: (feedback: { option: Option }) => void;
  interruptMessage?: Message | null;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
  onToggleResearch?: () => void;
}) {
  const message = useMessage(messageId);
  const researchIds = useStore((state) => state.researchIds);
  const startOfResearch = useMemo(() => {
    return researchIds.includes(messageId);
  }, [researchIds, messageId]);
  if (message) {
    if (
      message.role === "user" ||
      message.agent === "coordinator" ||
      message.agent === "planner" ||
      message.agent === "podcast" ||
      startOfResearch
    ) {
      let content: React.ReactNode;
      if (message.agent === "planner") {
        content = (
          <div className="w-full px-4">
            <PlanCard
              message={message}
              waitForFeedback={waitForFeedback}
              interruptMessage={interruptMessage}
              onFeedback={onFeedback}
              onSendMessage={onSendMessage}
            />
          </div>
        );
      } else if (message.agent === "podcast") {
        content = (
          <div className="w-full px-4">
            <PodcastCard message={message} />
          </div>
        );
      } else if (startOfResearch) {
        content = (
          <div className="w-full px-4">
            <ResearchCard
              researchId={message.id}
              onToggleResearch={onToggleResearch}
            />
          </div>
        );
      } else {
        content = message.content ? (
          <div
            className={cn(
              "flex w-full px-4",
              message.role === "user" && "justify-end",
              className,
            )}
          >
            <MessageBubble message={message}>
              <div className="flex w-full flex-col text-wrap break-words">
                <Markdown
                  className={cn(
                    message.role === "user" &&
                      "prose-invert not-dark:text-secondary dark:text-inherit",
                  )}
                >
                  {message?.content}
                </Markdown>
              </div>
            </MessageBubble>
          </div>
        ) : null;
      }
      if (content) {
        return (
          <motion.li
            className="mt-10"
            key={messageId}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ transition: "all 0.2s ease-out" }}
            transition={{
              duration: 0.2,
              ease: "easeOut",
            }}
          >
            {content}
          </motion.li>
        );
      }
    }
    return null;
  }
}

function MessageBubble({
  className,
  message,
  children,
}: {
  className?: string;
  message: Message;
  children: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        `group flex w-fit max-w-[85%] flex-col rounded-2xl px-4 py-3 text-nowrap shadow`,
        message.role === "user" && "bg-brand rounded-ee-none",
        message.role === "assistant" && "bg-card rounded-es-none",
        className,
      )}
    >
      {children}
    </div>
  );
}

function ResearchCard({
  className,
  researchId,
  onToggleResearch,
}: {
  className?: string;
  researchId: string;
  onToggleResearch?: () => void;
}) {
  const reportId = useStore((state) => state.researchReportIds.get(researchId));
  const hasReport = reportId !== undefined;
  const reportGenerating = useStore(
    (state) => hasReport && state.messages.get(reportId)!.isStreaming,
  );
  const openResearchId = useStore((state) => state.openResearchId);
  const state = useMemo(() => {
    if (hasReport) {
      return reportGenerating ? "正在生成报告..." : "报告已生成";
    }
          return "研究中...";
  }, [hasReport, reportGenerating]);
  const msg = useResearchMessage(researchId);
  const title = useMemo(() => {
    if (msg && msg.content) {
      // 改进：支持流式传输期间的部分JSON解析
      try {
        const result = parseJSON(msg.content, { title: "" });
        return result.title || "深度研究";
      } catch (error) {
        console.debug('Failed to parse research title:', error);
        return "深度研究";
      }
    }
    return "深度研究";
  }, [msg?.content]); // 移除对 isStreaming 的依赖，实时解析
  const handleOpen = useCallback(() => {
    if (openResearchId === researchId) {
      closeResearch();
    } else {
      openResearch(researchId);
    }
    onToggleResearch?.();
  }, [openResearchId, researchId, onToggleResearch]);
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle>
                      <RainbowText animated={state !== "报告已生成"}>
            {title}
          </RainbowText>
        </CardTitle>
      </CardHeader>
      <CardFooter>
        <div className="flex w-full">
          <RollingText className="text-muted-foreground flex-grow text-sm">
            {state}
          </RollingText>
          <Button
            variant={!openResearchId ? "default" : "outline"}
            onClick={handleOpen}
          >
            {researchId !== openResearchId ? "打开" : "关闭"}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

function ThoughtBlock({
  className,
  content,
  isStreaming,
  hasMainContent,
}: {
  className?: string;
  content: string;
  isStreaming?: boolean;
  hasMainContent?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(true);

  const [hasAutoCollapsed, setHasAutoCollapsed] = useState(false);

  React.useEffect(() => {
    if (hasMainContent && !hasAutoCollapsed) {
      setIsOpen(false);
      setHasAutoCollapsed(true);
    }
  }, [hasMainContent, hasAutoCollapsed]);

  if (!content || content.trim() === "") {
    return null;
  }
  return (
    <div className={cn("mb-6 w-full", className)}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            className={cn(
              "h-auto w-full justify-start rounded-xl border px-6 py-4 text-left transition-all duration-200",
              "hover:bg-accent hover:text-accent-foreground",
              isStreaming
                ? "border-primary/20 bg-primary/5 shadow-sm"
                : "border-border bg-card",
            )}
          >
            <div className="flex w-full items-center gap-3">
              <Lightbulb
                size={18}
                className={cn(
                  "shrink-0 transition-colors duration-200",
                  isStreaming ? "text-primary" : "text-muted-foreground",
                )}
              />
              <span
                className={cn(
                  "leading-none font-semibold transition-colors duration-200",
                  isStreaming ? "text-primary" : "text-foreground",
                )}
              >
                深度思考
              </span>
              {isStreaming && <LoadingAnimation className="ml-2 scale-75" />}
              <div className="flex-grow" />
              {isOpen ? (
                <ChevronDown
                  size={16}
                  className="text-muted-foreground transition-transform duration-200"
                />
              ) : (
                <ChevronRight
                  size={16}
                  className="text-muted-foreground transition-transform duration-200"
                />
              )}
            </div>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:slide-up-2 data-[state=open]:slide-down-2 mt-3">
          <Card
            className={cn(
              "transition-all duration-200",
              isStreaming ? "border-primary/20 bg-primary/5" : "border-border",
            )}
          >
            <CardContent>
              <div className="flex h-40 w-full overflow-y-auto">
                <ScrollContainer
                  className={cn(
                    "flex h-full w-full flex-col overflow-hidden",
                    className,
                  )}
                  scrollShadow={false}
                  autoScrollToBottom
                >
                  <Markdown
                    className={cn(
                      "prose dark:prose-invert max-w-none transition-colors duration-200",
                      isStreaming ? "prose-primary" : "opacity-80",
                    )}
                    animated={isStreaming}
                  >
                    {content}
                  </Markdown>
                </ScrollContainer>
              </div>
            </CardContent>
          </Card>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

const GREETINGS = ["启动深度研究并生成报告"];
function PlanCard({
  className,
  message,
  interruptMessage,
  onFeedback,
  waitForFeedback,
  onSendMessage,
}: {
  className?: string;
  message: Message;
  interruptMessage?: Message | null;
  onFeedback?: (feedback: { option: Option }) => void;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
  waitForFeedback?: boolean;
}) {
  const plan = useMemo<{
    title?: string;
    thought?: string;
    steps?: { title?: string; description?: string }[];
  }>(() => {
    // 改进：实时解析JSON，不等待流式传输完成
    if (!message.content) {
      return {};
    }
    
    try {
      // 使用改进的JSON解析器
      const result = parseJSON(message.content, {});
      
      // 添加详细的调试信息
      if (message.agent === 'planner' || message.agent === 'coordinator') {
        const typedResult = result as any; // 临时类型断言用于调试
        console.debug('计划解析详情:', {
          agent: message.agent,
          messageId: message.id,
          isStreaming: message.isStreaming,
          contentLength: message.content?.length || 0,
          contentPreview: message.content?.substring(0, 200) + '...',
          parsedKeys: result ? Object.keys(result) : [],
          hasTitle: !!typedResult?.title,
          hasThought: !!typedResult?.thought,
          hasSteps: !!typedResult?.steps,
          stepsCount: Array.isArray(typedResult?.steps) ? typedResult.steps.length : 0,
          result
        });
        
        // 验证解析结果的质量
        if (result && typeof result === 'object') {
          if (!typedResult.title && !typedResult.thought && !typedResult.steps) {
            console.warn('解析结果为空对象，可能存在JSON格式问题:', {
              agent: message.agent,
              rawContent: message.content
            });
          }
        }
      }
      
      return result;
    } catch (error) {
      console.error('计划解析失败:', {
        agent: message.agent,
        messageId: message.id,
        error,
        contentLength: message.content?.length || 0,
        contentSample: message.content?.substring(0, 300) + '...'
      });
      return {};
    }
  }, [message.content, message.agent, message.id]); // 添加messageId依赖

  // 编辑状态管理
  const [isEditing, setIsEditing] = useState(false);
  const [editedPlan, setEditedPlan] = useState(plan);

  // 当原始计划更新时，同步编辑状态
  useEffect(() => {
    if (!isEditing) {
      setEditedPlan(plan);
    }
  }, [plan, isEditing]);

  // 编辑步骤函数
  const updateStep = useCallback((stepIndex: number, field: 'title' | 'description', value: string) => {
    setEditedPlan(prev => ({
      ...prev,
      steps: prev.steps?.map((step, i) => 
        i === stepIndex ? { ...step, [field]: value } : step
      ) || []
    }));
  }, []);

  // 更新标题和思考
  const updatePlanField = useCallback((field: 'title' | 'thought', value: string) => {
    setEditedPlan(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // 保存编辑
  const handleSaveEdit = useCallback(() => {
    if (onSendMessage) {
      // 将编辑后的计划发送给后端
      const editedPlanJson = JSON.stringify(editedPlan);
      onSendMessage(
        `Plan updated: ${editedPlanJson}`,
        {
          interruptFeedback: `[EDIT_PLAN] ${editedPlanJson}`,
        },
      );
    }
    setIsEditing(false);
  }, [editedPlan, onSendMessage]);

  // 取消编辑
  const handleCancelEdit = useCallback(() => {
    setEditedPlan(plan);
    setIsEditing(false);
  }, [plan]);

  const reasoningContent = message.reasoningContent;
  const hasMainContent = Boolean(
    message.content && message.content.trim() !== "",
  );

  // 判断是否正在思考：有推理内容但还没有主要内容
  const isThinking = Boolean(reasoningContent && !hasMainContent);

  // 改进：即使在流式传输期间也显示已解析的计划内容
  const shouldShowPlan = hasMainContent && (plan.title || plan.thought || plan.steps);
  
  const handleAccept = useCallback(async () => {
    if (onSendMessage) {
      onSendMessage(
        `${GREETINGS[Math.floor(Math.random() * GREETINGS.length)]}`,
        {
          interruptFeedback: "accepted",
        },
      );
    }
  }, [onSendMessage]);
  
  return (
    <div className={cn("w-full", className)}>
      {reasoningContent && (
        <ThoughtBlock
          content={reasoningContent}
          isStreaming={isThinking}
          hasMainContent={hasMainContent}
        />
      )}
      {shouldShowPlan && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <Card className="w-full">
            <CardHeader>
              <CardTitle>
                {isEditing ? (
                  <Input
                    value={editedPlan.title || ""}
                    onChange={(e) => updatePlanField('title', e.target.value)}
                    placeholder="研究计划标题"
                    className="text-xl font-bold"
                  />
                ) : (
                  <Markdown animated={message.isStreaming}>
                    {`### ${
                      plan.title && plan.title.trim() !== ""
                        ? plan.title
                        : "深度研究"
                    }`}
                  </Markdown>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {(plan.thought || isEditing) && (
                <div className="mb-4">
                  {isEditing ? (
                    <Textarea
                      value={editedPlan.thought || ""}
                      onChange={(e) => updatePlanField('thought', e.target.value)}
                      placeholder="研究思路和背景..."
                      className="min-h-20"
                    />
                  ) : (
                    <Markdown className="opacity-80" animated={message.isStreaming}>
                      {plan.thought}
                    </Markdown>
                  )}
                </div>
              )}
              {((plan.steps && plan.steps.length > 0) || isEditing) && (
                <div className="my-2">
                  <h4 className="text-sm font-medium text-muted-foreground mb-3">研究步骤</h4>
                  <ul className="flex list-decimal flex-col gap-4 border-l-[2px] pl-8">
                    {isEditing ? (
                      editedPlan.steps?.map((step, i) => (
                        <li key={`edit-step-${i}`} className="space-y-2">
                          <Input
                            value={step.title || ""}
                            onChange={(e) => updateStep(i, 'title', e.target.value)}
                            placeholder={`步骤 ${i + 1} 标题`}
                            className="font-medium"
                          />
                          <Textarea
                            value={step.description || ""}
                            onChange={(e) => updateStep(i, 'description', e.target.value)}
                            placeholder={`步骤 ${i + 1} 详细描述`}
                            className="text-sm min-h-16"
                          />
                        </li>
                      ))
                    ) : (
                      plan.steps?.map((step, i) => (
                        <li key={`step-${i}`}>
                          <h3 className="mb text-lg font-medium">
                            <Markdown animated={message.isStreaming}>
                              {step.title}
                            </Markdown>
                          </h3>
                          <div className="text-muted-foreground text-sm">
                            <Markdown animated={message.isStreaming}>
                              {step.description}
                            </Markdown>
                          </div>
                        </li>
                      ))
                    )}
                  </ul>
                </div>
              )}
            </CardContent>
            <CardFooter className="flex justify-end">
              {!message.isStreaming && (
                <motion.div
                  className="flex gap-2"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                >
                  {isEditing ? (
                    // 编辑模式按钮
                    <>
                      <Button
                        variant="outline"
                        onClick={handleCancelEdit}
                      >
                        取消
                      </Button>
                      <Button
                        variant="default"
                        onClick={handleSaveEdit}
                      >
                        保存计划
                      </Button>
                    </>
                  ) : (
                    // 非编辑模式按钮
                    interruptMessage?.options?.length ? (
                      interruptMessage.options.map((option) => (
                        <Button
                          key={option.value}
                          variant={
                            option.value === "accepted" ? "default" : "outline"
                          }
                          disabled={!waitForFeedback}
                          onClick={() => {
                            if (option.value === "accepted") {
                              void handleAccept();
                            } else if (option.value === "edit_plan") {
                              // 进入编辑模式
                              setIsEditing(true);
                            } else {
                              onFeedback?.({
                                option,
                              });
                            }
                          }}
                        >
                          {option.text}
                        </Button>
                      ))
                    ) : (
                      // 默认按钮（如果没有interrupt选项）
                      <>
                        <Button
                          variant="outline"
                          onClick={() => setIsEditing(true)}
                        >
                          编辑计划
                        </Button>
                        <Button
                          variant="default"
                          onClick={handleAccept}
                        >
                          开始研究
                        </Button>
                      </>
                    )
                  )}
                </motion.div>
              )}
            </CardFooter>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

function PodcastCard({
  className,
  message,
}: {
  className?: string;
  message: Message;
}) {
  const data = useMemo(() => {
    return JSON.parse(message.content ?? "");
  }, [message.content]);
  const title = useMemo<string | undefined>(() => data?.title, [data]);
  const audioUrl = useMemo<string | undefined>(() => data?.audioUrl, [data]);
  const isGenerating = useMemo(() => {
    return message.isStreaming;
  }, [message.isStreaming]);
  const hasError = useMemo(() => {
    return data?.error !== undefined;
  }, [data]);
  const [isPlaying, setIsPlaying] = useState(false);
  return (
    <Card className={cn("w-[508px]", className)}>
      <CardHeader>
        <div className="text-muted-foreground flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            {isGenerating ? <LoadingOutlined /> : <Headphones size={16} />}
            {!hasError ? (
              <RainbowText animated={isGenerating}>
                {isGenerating
                  ? "正在生成播客..."
                  : isPlaying
                  ? "正在播放播客..."
                  : "播客"}
              </RainbowText>
                          ) : (
                <div className="text-red-500">
                  生成播客时出错，请重试。
                </div>
              )}
          </div>
          {!hasError && !isGenerating && (
            <div className="flex">
              <Tooltip title="下载播客">
                <Button variant="ghost" size="icon" asChild>
                  <a
                    href={audioUrl}
                    download={`${(title ?? "podcast").replaceAll(" ", "-")}.mp3`}
                  >
                    <Download size={16} />
                  </a>
                </Button>
              </Tooltip>
            </div>
          )}
        </div>
        <CardTitle>
          <div className="text-lg font-medium">
            <RainbowText animated={isGenerating}>{title}</RainbowText>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {audioUrl ? (
          <audio
            className="w-full"
            src={audioUrl}
            controls
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
        ) : (
          <div className="w-full"></div>
        )}
      </CardContent>
    </Card>
  );
}
