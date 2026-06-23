import type { ChatResponse, IngestResponse } from "./types"

const API_BASE = import.meta.env.VITE_API_URL || ""

export async function chatApi(
  message: string,
  threadId: string,
  llmApiKey?: string,
  llmBaseUrl?: string,
): Promise<ChatResponse> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (llmApiKey) headers["X-LLM-Api-Key"] = llmApiKey
  if (llmBaseUrl) headers["X-LLM-Base-Url"] = llmBaseUrl

  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message, thread_id: threadId }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function uploadPdfApi(
  file: File,
  source: string,
  speaker: string,
  themes: string,
  emotions: string,
  llmApiKey?: string,
  llmBaseUrl?: string,
): Promise<IngestResponse> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("source", source)
  if (speaker.trim()) formData.append("speaker", speaker.trim())
  formData.append("themes", themes)
  formData.append("emotions", emotions)

  const headers: Record<string, string> = {}
  if (llmApiKey) headers["X-LLM-Api-Key"] = llmApiKey
  if (llmBaseUrl) headers["X-LLM-Base-Url"] = llmBaseUrl

  const res = await fetch(`${API_BASE}/api/v1/ingest/pdf`, {
    method: "POST",
    headers,
    body: formData,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}
