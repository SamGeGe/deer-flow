// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { env } from "~/env";

export function resolveServiceURL(path: string) {
  const apiUrl = env.NEXT_PUBLIC_API_URL;

  // If an absolute API URL is provided via environment variables, use it.
  if (apiUrl) {
    let absoluteUrl = apiUrl;
    if (!absoluteUrl.endsWith("/")) {
      absoluteUrl += "/";
    }
    
    // Clean up the path - remove leading dots, slashes, and api prefixes
    let cleanPath = path;
    
    // Remove leading "./" or "/"
    cleanPath = cleanPath.replace(/^\.?\//, '');
    
    // Remove "api/" prefix if it exists (since our base URL already includes /api)
    cleanPath = cleanPath.replace(/^api\//, '');
    
    return new URL(cleanPath, absoluteUrl).toString();
  }

  // Otherwise, default to a relative path. This works when the web server
  // serves the frontend and proxies API requests from the same port.
  let cleanPath = path;
  cleanPath = cleanPath.replace(/^\.?\//, '');
  if (!cleanPath.startsWith('api/')) {
    cleanPath = `api/${cleanPath}`;
  }
  return `/${cleanPath}`;
}
