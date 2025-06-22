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
    return new URL(path, absoluteUrl).toString();
  }

  // Otherwise, default to a relative path. This works when the web server
  // serves the frontend and proxies API requests from the same port.
  const relativePath = `/api/${path.startsWith('/') ? path.substring(1) : path}`;
  return relativePath;
}
