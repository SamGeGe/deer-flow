// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Bird, Microscope, Podcast, Usb, User } from "lucide-react";

import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid";

import { SectionHeader } from "../components/section-header";

const features = [
  {
    Icon: Microscope,
    name: "更深、更广的探索",
    description:
      "使用高级工具解锁更深刻的见解。我们强大的搜索+爬虫和 Python 工具可收集全面的数据，提供深入的报告以增强您的研究。",
    href: "https://github.com/bytedance/deer-flow/blob/main/src/tools",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-3",
  },
  {
    Icon: User,
    name: "人机协同（Human-in-the-loop）",
    description:
      "通过简单的自然语言，优化您的研究计划或调整重点领域。",
    href: "https://github.com/bytedance/deer-flow/blob/main/src/graph/nodes.py",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-3 lg:row-end-4",
  },
  {
    Icon: Bird,
    name: "语言技术栈",
    description: "使用 LangChain 和 LangGraph 框架充满信心地构建。",
    href: "https://www.langchain.com/",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2",
  },
  {
    Icon: Usb,
    name: "MCP 集成",
    description: "通过无缝的 MCP 集成，增强您的研究工作流程并扩展您的工具包。",
    href: "https://github.com/bytedance/deer-flow/blob/main/src/graph/nodes.py",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3",
  },
  {
    Icon: Podcast,
    name: "播客生成",
    description: "从报告中即时生成播客。非常适合在移动中学习或轻松分享研究结果。",
    href: "https://github.com/bytedance/deer-flow/blob/main/src/podcast",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-3 lg:row-end-4",
  },
];

export function CoreFeatureSection() {
  return (
    <section className="relative flex w-full flex-col content-around items-center justify-center">
      <SectionHeader
        anchor="core-features"
        title="核心功能"
        description="了解 DeerFlow 高效的原因。"
      />
      <BentoGrid className="w-3/4 lg:grid-cols-2 lg:grid-rows-3">
        {features.map((feature) => (
          <BentoCard key={feature.name} {...feature} />
        ))}
      </BentoGrid>
    </section>
  );
}
