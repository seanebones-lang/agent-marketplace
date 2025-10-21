/**
 * TypeScript Type Definitions
 */

export interface AgentPackage {
  package_id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  engine_type: 'langgraph' | 'crewai';
  tools: string[];
  pricing: {
    per_task?: number;
    per_hour?: number;
    per_gb?: number;
    monthly?: number;
  };
  features: string[];
  performance_metrics: {
    avg_execution_time: string;
    success_rate: string;
    avg_cost?: string;
  };
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface ExecutionResult {
  package_id: string;
  status: 'success' | 'failed' | 'timeout';
  result: any;
  execution_time_ms: number;
  tokens_used: number;
  cost: number;
  error?: string;
  metadata?: Record<string, any>;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  tier?: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  services: {
    database: string;
    redis: string;
    qdrant: string;
  };
}

export interface UsageStats {
  total_executions: number;
  total_cost: number;
  total_tokens: number;
  executions_by_package: Record<string, number>;
  cost_by_package: Record<string, number>;
}

export interface Deployment {
  id: number;
  customer_id: number;
  package_id: string;
  status: 'active' | 'paused' | 'stopped';
  deployed_at: string;
  last_used_at?: string;
}

