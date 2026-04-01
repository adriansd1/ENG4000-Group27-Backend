import type { BackendHealth, KnowledgeBaseUploadResponse, QueryResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;

    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string" && payload.detail.trim()) {
        detail = payload.detail;
      }
    } catch {
      // Keep default HTTP detail when the response body is not JSON.
    }

    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export async function fetchBackendHealth() {
  return request<BackendHealth>("/health", { method: "GET" });
}

export async function queryEnergyExpert(question: string) {
  return request<QueryResponse>("/api/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export async function uploadKnowledgeBaseDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return request<KnowledgeBaseUploadResponse>("/api/kb/upload", {
    method: "POST",
    body: formData,
  });
}
