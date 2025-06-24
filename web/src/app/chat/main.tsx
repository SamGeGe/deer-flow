// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useMemo } from "react";

import { useStore } from "~/core/store";
import { cn } from "~/lib/utils";

import { MessagesBlock } from "./components/messages-block";
import { ResearchBlock } from "./components/research-block";

export default function Main() {
  const openResearchId = useStore((state) => state.openResearchId);
  const doubleColumnMode = useMemo(
    () => openResearchId !== null,
    [openResearchId],
  );
  return (
    <div
      className={cn(
        "flex h-full w-full justify-center-safe px-2 md:px-4 pt-12 pb-4",
        doubleColumnMode && "gap-2 md:gap-8",
      )}
    >
      <MessagesBlock
        className={cn(
          "shrink-0 transition-all duration-300 ease-out",
          !doubleColumnMode &&
            `w-full max-w-[768px] md:w-[768px] md:translate-x-[min(max(calc((100vw-538px)*0.75),575px)/2,960px/2)]`,
          doubleColumnMode && `w-full md:w-[538px]`,
        )}
      />
      <ResearchBlock
        className={cn(
          "transition-all duration-300 ease-out",
          "hidden md:block",
          "w-[min(max(calc((100vw-538px)*0.75),575px),960px)] pb-4",
          !doubleColumnMode && "scale-0",
          doubleColumnMode && "",
        )}
        researchId={openResearchId}
      />
      {doubleColumnMode && (
        <div className="fixed inset-0 z-50 bg-background md:hidden">
          <div className="flex h-full flex-col">
            <div className="flex h-12 items-center justify-between px-4 border-b">
              <h2 className="font-semibold">研究报告</h2>
                             <button
                 onClick={() => useStore.getState().closeResearch()}
                 className="text-muted-foreground hover:text-foreground"
               >
                 关闭
               </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ResearchBlock
                className="h-full w-full px-4 pb-4"
                researchId={openResearchId}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
