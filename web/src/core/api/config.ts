import { type DeerFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __deerflowConfig: DeerFlowConfig;
  }
}

export async function loadConfig() {
  const res = await fetch(resolveServiceURL("config").toString());
  const config = await res.json();
  return config;
}

// Flag to prevent multiple simultaneous config loads
let isLoadingConfig = false;

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
      }).catch(error => {
        console.warn('Failed to load config:', error);
        // Set default config on error
        window.__deerflowConfig = {
          rag: { provider: null },
          models: { basic: [], reasoning: [] }
        };
        isLoadingConfig = false;
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
