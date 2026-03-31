export interface BackendHealth {
  status: string;
}

export interface QueryResponse {
  question: string;
  sql: string;
  rows: Record<string, unknown>[];
  analysis: string;
}
