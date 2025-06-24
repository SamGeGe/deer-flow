// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { GithubFilled } from "@ant-design/icons";
import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { AuroraText } from "~/components/magicui/aurora-text";
import { FlickeringGrid } from "~/components/magicui/flickering-grid";
import { ShineBorder } from "~/components/magicui/shine-border";
import { Button } from "~/components/ui/button";
import { env } from "~/env";
import { LogoIcon } from "~/components/deer-flow/logo";

export function Jumbotron() {
  return (
    <section className="flex h-[95vh] w-full flex-col items-center justify-center pb-15 px-4">
      <FlickeringGrid
        id="deer-hero-bg"
        className={`absolute inset-0 z-0 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]`}
        squareSize={4}
        gridGap={4}
        color="#60A5FA"
        maxOpacity={0.133}
        flickerChance={0.1}
      />
      <div className="relative z-10 flex flex-col items-center justify-center gap-8 md:gap-12">
        <ShineBorder
          className="relative flex h-20 w-20 items-center justify-center rounded-full border-2 bg-white/5 md:h-32 md:w-32"
          color="#60A5FA"
        >
          <LogoIcon className="h-16 w-16 md:h-28 md:w-28" />
        </ShineBorder>
        <h1 className="text-center text-3xl font-bold md:text-6xl">
          <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
            深度研究{" "}
          </span>
          <AuroraText>触手可及</AuroraText>
        </h1>
        <p className="max-w-4xl px-4 text-center text-base opacity-85 md:text-2xl">
          遇见 DeerFlow，你的个人深度研究助理。借助搜索引擎、网页爬虫、Python
          和 MCP 服务等强大工具，它能即时提供深刻见解、生成综合报告，甚至制作引人入胜的播客。
        </p>
        <div className="flex w-full max-w-md gap-6 px-4">
          <Button 
            className="flex w-full text-base md:text-lg md:w-auto md:px-8" 
            size="lg" 
            asChild
          >
            <Link
              target={
                env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY ? "_blank" : undefined
              }
              href={
                env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY
                  ? "https://github.com/bytedance/deer-flow"
                  : "/chat"
              }
            >
              开始使用 <ChevronRight />
            </Link>
          </Button>
        </div>
      </div>
      <div className="absolute bottom-4 md:bottom-8 flex text-xs opacity-50 px-4 text-center">
        <p>* DEER 是"深度探索与高效研究"的缩写。</p>
      </div>
    </section>
  );
}
