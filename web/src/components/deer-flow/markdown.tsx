// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Check, Copy } from "lucide-react";
import { useMemo, useState } from "react";
import ReactMarkdown, {
  type Options as ReactMarkdownOptions,
} from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

import { Button } from "~/components/ui/button";
import { rehypeSplitWordsIntoSpans } from "~/core/rehype";
import { autoFixMarkdown } from "~/core/utils/markdown";
import { cn } from "~/lib/utils";

import Image from "./image";
import { Tooltip } from "./tooltip";
import { Link } from "./link";
import { resolveServiceURL } from "~/core/api";

export function Markdown({
  className,
  children,
  style,
  enableCopy,
  animated = false,
  checkLinkCredibility = false,
  ...props
}: ReactMarkdownOptions & {
  className?: string;
  enableCopy?: boolean;
  style?: React.CSSProperties;
  animated?: boolean;
  checkLinkCredibility?: boolean;
}) {
  // 自动分段长文本
  function autoParagraph(text: string) {
    // 每隔120字符加一个换行，避免一大坨文字
    return text.replace(/(.{120})/g, "$1\n");
  }

  const components: ReactMarkdownOptions["components"] = useMemo(() => {
    return {
      a: ({ href, children }) => (
        <span className="reference-link">
          <Link href={href} checkLinkCredibility={checkLinkCredibility}>
            {children}
          </Link>
        </span>
      ),
      code: ({ className, children, ...props }) => {
        // 针对 LaTeX 公式块
        if (className?.includes("language-math")) {
          return <div className="latex-block">{children}</div>;
        }
        // 普通代码块
        return <code className={cn(className, "code-block")} {...props}>{children}</code>;
      },
      blockquote: ({ children }) => (
        <blockquote className="reference-list">{children}</blockquote>
      ),
      p: ({ children }) => {
        // 对长文本自动分段
        if (typeof children === "string") {
          return <p>{autoParagraph(children)}</p>;
        }
        return <p>{children}</p>;
      },
      ul: ({ children }) => <ul className="reference-list">{children}</ul>,
      ol: ({ children }) => <ol className="reference-list">{children}</ol>,
    };
  }, [checkLinkCredibility]);

  const rehypePlugins = useMemo(() => {
    if (animated) {
      return [rehypeKatex, rehypeSplitWordsIntoSpans];
    }
    return [rehypeKatex];
  }, [animated]);
  return (
    <div className={cn(className, "prose dark:prose-invert")} style={style}>
      <style>{`
        .latex-block {
          background: #f8f8ff;
          border-left: 4px solid #b3b3ff;
          padding: 8px 16px;
          margin: 12px 0;
          font-size: 1.1em;
          text-align: center;
          overflow-x: auto;
        }
        .reference-list {
          color: #666;
          font-size: 0.95em;
          margin-left: 1em;
          border-left: 2px solid #eee;
          padding-left: 1em;
        }
        .reference-link {
          color: #1a0dab;
          word-break: break-all;
        }
        .code-block {
          background: #f5f5f5;
          color: #c7254e;
          border-radius: 4px;
          padding: 2px 6px;
        }
      `}</style>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={rehypePlugins}
        components={components}
        {...props}
      >
        {autoFixMarkdown(
          dropMarkdownQuote(processKatexInMarkdown(children ?? "")) ?? "",
        )}
      </ReactMarkdown>
      {enableCopy && typeof children === "string" && (
        <div className="flex">
          <CopyButton content={children} />
        </div>
      )}
    </div>
  );
}

function CopyButton({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <Tooltip title="Copy">
      <Button
        variant="outline"
        size="sm"
        className="rounded-full"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(content);
            setCopied(true);
            setTimeout(() => {
              setCopied(false);
            }, 1000);
          } catch (error) {
            console.error(error);
          }
        }}
      >
        {copied ? (
          <Check className="h-4 w-4" />
        ) : (
          <Copy className="h-4 w-4" />
        )}{" "}
      </Button>
    </Tooltip>
  );
}

function processKatexInMarkdown(markdown?: string | null) {
  if (!markdown) return markdown;

  const markdownWithKatexSyntax = markdown
    .replace(/\\\\\[/g, "$$$$") // Replace '\\[' with '$$'
    .replace(/\\\\\]/g, "$$$$") // Replace '\\]' with '$$'
    .replace(/\\\\\(/g, "$$$$") // Replace '\\(' with '$$'
    .replace(/\\\\\)/g, "$$$$") // Replace '\\)' with '$$'
    .replace(/\\\[/g, "$$$$") // Replace '\[' with '$$'
    .replace(/\\\]/g, "$$$$") // Replace '\]' with '$$'
    .replace(/\\\(/g, "$$$$") // Replace '\(' with '$$'
    .replace(/\\\)/g, "$$$$"); // Replace '\)' with '$$';
  return markdownWithKatexSyntax;
}

function dropMarkdownQuote(markdown?: string | null) {
  if (!markdown) return markdown;
  return markdown
    .replace(/^```markdown\n/gm, "")
    .replace(/^```text\n/gm, "")
    .replace(/^```\n/gm, "")
    .replace(/\n```$/gm, "");
}
