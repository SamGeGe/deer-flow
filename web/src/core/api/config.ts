import { type DeerFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __deerflowConfig: DeerFlowConfig;
  }
}

export async function loadConfig() {
  const res = await fetch(resolveServiceURL("./api/config"));
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
    // If config is not loaded or incomplete, load it asynchronously
    loadConfig().then(config => {
      window.__deerflowConfig = config;
    }).catch(error => {
      console.warn('Failed to load config:', error);
      // Set default config on error
      window.__deerflowConfig = {
        rag: { provider: null },
        models: { basic: [], reasoning: [] }
      };
    });
    
    // Return default config while loading
    return {
      rag: { provider: null },
      models: { basic: [], reasoning: [] }
    };
  }
  
  return window.__deerflowConfig;
}
