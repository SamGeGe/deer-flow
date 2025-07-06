import { type DeerFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __deerflowConfig: DeerFlowConfig;
  }
}

// Flag to prevent multiple simultaneous config loads
let isLoadingConfig = false;
let retryCount = 0;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1秒

async function checkServerHealth(): Promise<boolean> {
  try {
    const response = await fetch(resolveServiceURL("health").toString(), {
      method: "GET",
      timeout: 5000,
    } as any);
    return response.ok;
  } catch {
    return false;
  }
}

export async function loadConfig() {
  // 首先检查服务器健康状态
  const isHealthy = await checkServerHealth();
  if (!isHealthy) {
    console.warn('后端服务器连接失败，使用默认配置');
    throw new Error('Backend server is not available');
  }

  const res = await fetch(resolveServiceURL("config").toString());
  const config = await res.json();
  return config;
}

export function getConfig(): DeerFlowConfig {
  if (typeof window === "undefined") {
    // Server-side: return default config to avoid errors
    return {
      rag: { provider: null },
      models: { basic: [], reasoning: [] }
    };
  }
  
  // Client-side: try to get config from window, if not available, load it
  if (typeof window.__deerflowConfig === "undefined" || !window.__deerflowConfig.models) {
    // Only load config if not already loading
    if (!isLoadingConfig) {
      isLoadingConfig = true;
      loadConfig().then(config => {
        window.__deerflowConfig = config;
        isLoadingConfig = false;
        retryCount = 0; // 重置重试计数
      }).catch(error => {
        console.warn('Failed to load config:', error);
        
        // 实现重试机制
        if (retryCount < MAX_RETRIES) {
          retryCount++;
          console.info(`重试加载配置 (${retryCount}/${MAX_RETRIES})...`);
          setTimeout(() => {
            isLoadingConfig = false;
            // 递归重试
            getConfig();
          }, RETRY_DELAY * retryCount);
        } else {
          // 达到最大重试次数，设置默认配置
          console.error('配置加载失败，使用默认配置');
          window.__deerflowConfig = {
            rag: { provider: null },
            models: { basic: [], reasoning: [] }
          };
          isLoadingConfig = false;
          retryCount = 0;
        }
      });
    }
    
    // Return default config while loading
    return {
      rag: { provider: null },
      models: { basic: [], reasoning: [] }
    };
  }
  
  return window.__deerflowConfig;
}
