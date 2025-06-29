import { parse } from "best-effort-json-parser";

export function parseJSON<T>(json: string | null | undefined, fallback: T): T {
  if (!json || typeof json !== 'string') {
    return fallback;
  }

  try {
    // 改进的清理逻辑，更好地处理markdown代码块
    let cleaned = json.trim();
    
    // 处理markdown代码块包装
    if (cleaned.startsWith('```')) {
      // 提取代码块内容 - 使用修复后的正则表达式
      const codeBlockMatch = cleaned.match(/^```(?:js|json|ts|plaintext)?\n([\s\S]*?)\n```$/);
      if (codeBlockMatch && codeBlockMatch[1] !== undefined) {
        cleaned = codeBlockMatch[1].trim();
      } else {
        // 备用方案：简单字符串替换
        if (cleaned.startsWith('```json\n') && cleaned.endsWith('\n```')) {
          cleaned = cleaned.replace('```json\n', '').replace('\n```', '');
        } else {
          // 如果不是完整的代码块，尝试移除开头和结尾的```
          cleaned = cleaned.replace(/^```(?:js|json|ts|plaintext)?\s*\n?/, '');
          cleaned = cleaned.replace(/\n?```$/, '');
        }
      }
    }
    
    // 移除其他常见包装
    cleaned = cleaned.replace(/\(\)$/, '');
    
    if (!cleaned) {
      return fallback;
    }

    // 1. 首先尝试标准JSON解析
    try {
      const rawResult = JSON.parse(cleaned) as any;
      
      // 2. 应用数据适配层 - 将后台格式转换为前端期望格式
      const adaptedResult = adaptBackendDataToFrontend(rawResult);
      
      return adaptedResult as T;
    } catch (standardError) {
      // 2. 如果标准解析失败，尝试修复常见的JSON问题
      const repaired = repairCommonJSONIssues(cleaned);
      if (repaired !== cleaned) {
        try {
          const rawResult = JSON.parse(repaired) as any;
          const adaptedResult = adaptBackendDataToFrontend(rawResult);
          return adaptedResult as T;
        } catch (repairedError) {
          // 继续尝试best-effort parser
        }
      }

      // 3. 使用best-effort parser作为最后手段
      const originalWarn = console.warn;
      try {
        console.warn = (...args: any[]) => {
          const message = args.join(' ');
          if (!message.includes('parsed json with extra tokens')) {
            originalWarn.apply(console, args);
          }
        };

        const rawResult = parse(cleaned) as any;
        console.warn = originalWarn;
        
        // 验证结果是否有用
        if (rawResult && typeof rawResult === 'object') {
          const adaptedResult = adaptBackendDataToFrontend(rawResult);
          return adaptedResult as T;
        }
        
        return fallback;
      } catch (bestEffortError: any) {
        console.warn = originalWarn;
        // 只在开发环境显示详细错误
        if (process.env.NODE_ENV === 'development') {
          console.debug('JSON解析失败，使用备用值:', {
            error: bestEffortError.message,
            fallback: typeof fallback
          });
        }
        return fallback;
      }
    }
  } catch (error) {
    // 静默处理，避免控制台噪音
    return fallback;
  }
}

/**
 * 数据适配层：将后台JSON格式转换为前端期望格式
 */
function adaptBackendDataToFrontend(rawData: any): any {
  if (!rawData || typeof rawData !== 'object') {
    return rawData;
  }

  // 如果是规划员数据，进行格式适配
  if (rawData.locale || rawData.has_enough_context !== undefined || 
      (rawData.steps && Array.isArray(rawData.steps))) {
    
    // 适配规划员数据格式
    const adapted: any = {
      title: rawData.title || "研究计划",
      thought: rawData.thought || "",
      steps: rawData.steps ? rawData.steps.map((step: any, index: number) => ({
        title: step.title || step.description || `步骤 ${index + 1}`,
        description: step.description || step.title || "研究任务"
      })) : []
    };

    // 保留原始数据作为备用（动态属性）
    if (rawData.locale) adapted._locale = rawData.locale;
    if (rawData.has_enough_context !== undefined) adapted._hasEnoughContext = rawData.has_enough_context;
    if (rawData.step_type) adapted._stepType = rawData.step_type;

    return adapted;
  }

  // 对于其他数据，直接返回
  return rawData;
}

// 修复常见的JSON问题
function repairCommonJSONIssues(json: string): string {
  let repaired = json;

  try {
    // 修复尾随逗号
    repaired = repaired.replace(/,(\s*[}\]])/g, '$1');
    
    // 修复缺少引号的键名
    repaired = repaired.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:/g, '$1"$2":');
    
    // 修复单引号
    repaired = repaired.replace(/'/g, '"');
    
    // 修复不完整的字符串（在流式传输中常见）
    if (repaired.includes('"') && !repaired.endsWith('"') && !repaired.endsWith('"}') && !repaired.endsWith('"]')) {
      // 检查是否是不完整的字符串值
      const lastQuoteIndex = repaired.lastIndexOf('"');
      if (lastQuoteIndex > 0 && repaired.charAt(lastQuoteIndex - 1) === ':') {
        // 这可能是一个不完整的字符串值，暂时不修复
        return json; // 返回原始值，等待更多数据
      }
    }
    
    return repaired;
  } catch (error) {
    return json; // 如果修复过程出错，返回原始值
  }
}

// 新增：专门用于流式JSON解析的函数
export function parseStreamingJSON<T>(
  json: string | null | undefined, 
  fallback: T,
  options: {
    isStreaming?: boolean;
    allowPartial?: boolean;
  } = {}
): { result: T; isPartial: boolean } {
  if (!json || typeof json !== 'string') {
    return { result: fallback, isPartial: false };
  }

  const { isStreaming = false, allowPartial = true } = options;

  // 如果正在流式传输且允许部分解析
  if (isStreaming && allowPartial) {
    // 尝试提取部分有效的JSON
    const partialResult = extractPartialJSON(json, fallback);
    if (partialResult.success) {
      return { result: partialResult.data, isPartial: true };
    }
  }

  // 否则使用标准解析
  const result = parseJSON(json, fallback);
  return { result, isPartial: false };
}

// 提取部分JSON数据
function extractPartialJSON<T>(json: string, fallback: T): { success: boolean; data: T } {
  try {
    const cleaned = json.trim();
    
    // 尝试找到完整的对象或数组
    let braceCount = 0;
    let bracketCount = 0;
    let inString = false;
    let escaped = false;
    let lastCompleteIndex = -1;

    for (let i = 0; i < cleaned.length; i++) {
      const char = cleaned[i];
      
      if (escaped) {
        escaped = false;
        continue;
      }
      
      if (char === '\\') {
        escaped = true;
        continue;
      }
      
      if (char === '"') {
        inString = !inString;
        continue;
      }
      
      if (!inString) {
        if (char === '{') braceCount++;
        else if (char === '}') braceCount--;
        else if (char === '[') bracketCount++;
        else if (char === ']') bracketCount--;
        
        // 如果找到了完整的对象或数组
        if (braceCount === 0 && bracketCount === 0 && (char === '}' || char === ']')) {
          lastCompleteIndex = i;
        }
      }
    }

    // 如果找到了完整的部分，尝试解析它
    if (lastCompleteIndex > 0) {
      const partialJSON = cleaned.substring(0, lastCompleteIndex + 1);
      try {
        const parsed = JSON.parse(partialJSON) as T;
        return { success: true, data: parsed };
      } catch (error) {
        // 部分解析失败，继续尝试其他方法
      }
    }

    return { success: false, data: fallback };
  } catch (error) {
    return { success: false, data: fallback };
  }
}
