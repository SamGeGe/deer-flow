// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import "~/styles/globals.css";

import { type Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";

import { ThemeProviderWrapper } from "~/components/deer-flow/theme-provider-wrapper";
import { loadConfig } from "~/core/api/config";
import { env } from "~/env";

import { Toaster } from "../components/deer-flow/toaster";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "🦌 DeerFlow",
  description:
    "Deep Exploration and Efficient Research, an AI tool that combines language models with specialized tools for research tasks.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  // In Docker environment, skip server-side config loading to avoid connection issues
  // Config will be loaded on the client side instead
  let conf = {};
  
  // 检测是否在Docker环境中：如果API_URL是相对路径，则很可能在Docker中
  const isDockerEnv = process.env.NEXT_PUBLIC_API_URL?.startsWith('/') || process.env.NODE_ENV === 'production';
  
  // Only load config on server-side in development mode and non-Docker environment
  if (process.env.NODE_ENV === 'development' && !isDockerEnv) {
    try {
      conf = await loadConfig();
    } catch (error) {
      console.warn('Failed to load config on server-side:', error);
      conf = {};
    }
  }
  
  return (
    <html lang="en" className={`${geist.variable}`} suppressHydrationWarning>
      <head>
        <script>{`window.__deerflowConfig = ${JSON.stringify(conf)}`}</script>
        {/* Define isSpace function globally to fix markdown-it issues with Next.js + Turbopack
          https://github.com/markdown-it/markdown-it/issues/1082#issuecomment-2749656365 */}
        <Script id="markdown-it-fix" strategy="beforeInteractive">
          {`
            if (typeof window !== 'undefined' && typeof window.isSpace === 'undefined') {
              window.isSpace = function(code) {
                return code === 0x20 || code === 0x09 || code === 0x0A || code === 0x0B || code === 0x0C || code === 0x0D;
              };
            }
          `}
        </Script>
      </head>
      <body className="bg-app">
        <ThemeProviderWrapper>{children}</ThemeProviderWrapper>
        <Toaster />
        {
          // NO USER BEHAVIOR TRACKING OR PRIVATE DATA COLLECTION BY DEFAULT
          //
          // When `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` is `true`, the script will be injected
          // into the page only when `AMPLITUDE_API_KEY` is provided in `.env`
        }
        {env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && env.AMPLITUDE_API_KEY && (
          <>
            <Script src="https://cdn.amplitude.com/script/d2197dd1df3f2959f26295bb0e7e849f.js"></Script>
            <Script id="amplitude-init" strategy="lazyOnload">
              {`window.amplitude.init('${env.AMPLITUDE_API_KEY}', {"fetchRemoteConfig":true,"autocapture":true});`}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
