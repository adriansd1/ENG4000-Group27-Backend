export interface BackendHealth {
  status: string;
}

export interface QueryResponse {
  question: string;
  sql: string;
  rows: Record<string, unknown>[];
  analysis: string;
}

export interface KnowledgeBaseIngestResult {
  status: string;
  files?: number;
  chunks?: number;
  message?: string;
  seconds_elapsed?: number;
}

export interface KnowledgeBaseUploadResponse {
  status: string;
  filename: string;
  path: string;
  ingest: KnowledgeBaseIngestResult;
}
