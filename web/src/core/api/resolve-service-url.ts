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
  let baseUrl: string;

  // Priority 1: Use the explicit environment variable.
  if (process.env.NEXT_PUBLIC_API_URL) {
    baseUrl = process.env.NEXT_PUBLIC_API_URL;
    
    // 如果是相对路径（如 "/api"）
    if (baseUrl.startsWith('/')) {
      // 在浏览器环境中，构造完整URL
      if (typeof window !== 'undefined') {
      const protocol = window.location.protocol;
      const hostname = window.location.hostname;
      const port = window.location.port;
      baseUrl = `${protocol}//${hostname}${port ? ':' + port : ''}${baseUrl}`;
      } else {
        // 在服务器端且是相对路径时，抛出可预期的错误
        // 这允许上级代码优雅地处理这种情况
        throw new Error(`Cannot resolve relative API URL "${baseUrl}" in server-side context. This is expected in Docker environments.`);
      }
    }
  }
  // Priority 2: Fallback for browser environment during local development.
  else if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    // Assume backend runs on port 9001 for local dev if not specified.
    baseUrl = `${protocol}//${hostname}:9001`;
  }
  // Priority 3: Fallback for server-side environment during local development.
  else {
    baseUrl = 'http://localhost:9001';
  }

  // Clean up the base URL
  const sanitizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  // 判断 baseUrl 是否已以 /api 结尾
  const baseEndsWithApi = sanitizedBase.endsWith('/api');

  // 处理 cleanPath
  let cleanPath = path;
  cleanPath = cleanPath.replace(/^\./, '');
  cleanPath = cleanPath.replace(/^\//, '');
  cleanPath = cleanPath.replace(/^api\//, '');
  
  // 只在 baseUrl 没有 /api 时加 /api/ 前缀
  if (!baseEndsWithApi) {
    cleanPath = '/api/' + cleanPath;
  } else {
    cleanPath = '/' + cleanPath;
  }

  return new URL(sanitizedBase + cleanPath);
}
