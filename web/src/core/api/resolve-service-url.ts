// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Resolves the service URL by intelligently determining the base API URL.
 *
 * The resolution logic is as follows, in order of priority:
 * 1. `process.env.NEXT_PUBLIC_API_URL`: This environment variable is the most reliable
 *    method and should be set explicitly for production, Docker, and local development environments.
 * 2. Browser context (`typeof window !== 'undefined'`): If the environment variable is not set,
 *    and the code is running in a browser, it constructs the URL based on the current window's
 *    protocol and hostname, defaulting to port 9001 for the backend (typical for local development).
 * 3. Server-side context: If not in a browser (e.g., during SSR) and the environment variable
 *    is missing, it defaults to `http://localhost:9001`. This is a fallback for local development
 *    and will likely fail in a containerized environment if the variable isn't set.
 *
 * @param path The API path to resolve (e.g., '/api/chat').
 * @returns A URL object pointing to the resolved service endpoint.
 */
export function resolveServiceURL(path: string): URL {
  // 优先使用环境变量
  if (process.env.NEXT_PUBLIC_API_URL) {
    let baseUrl = process.env.NEXT_PUBLIC_API_URL;
    if (baseUrl.endsWith('/')) baseUrl = baseUrl.slice(0, -1);
    // 统一处理 path，确保只有一个 /api 前缀
    let cleanPath = path.replace(/^\/*/, '');
    if (!cleanPath.startsWith('api/')) {
      cleanPath = 'api/' + cleanPath;
    }
    return new URL(`${baseUrl}/${cleanPath}`);
  }
  // 没有环境变量，直接用相对路径，交给前端代理
  let cleanPath = path.replace(/^\/*/, '');
  if (!cleanPath.startsWith('api/')) {
    cleanPath = 'api/' + cleanPath;
  }
  return new URL(`/${cleanPath}`, window.location.origin);
}

