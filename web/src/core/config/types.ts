export interface ModelConfig {
  basic: string[];
  reasoning: string[];
}

export interface RagConfig {
  provider: string | null;
}

export interface DeerFlowConfig {
  rag: RagConfig;
  models: ModelConfig;
}
