export interface QueryAnalysis {
  emotion: string
  theme: string
  category: string
  sub_emotions: string[]
  confidence: number
}

export interface RetrievedVerse {
  text: string
  translation: string
  chapter: number
  verse: number
  speaker: string | null
  score: number
  themes: string[]
  source: string
}

export interface RetrievedStory {
  title: string
  summary: string
  teaching: string
  score: number
  themes: string[]
  source: string
}

export interface Citation {
  source: string
  chapter: number | null
  verse: number | null
  text: string
  valid: boolean
}

export interface ChatResponse {
  response: string
  query_analysis: QueryAnalysis | null
  verses_used: RetrievedVerse[]
  stories_used: RetrievedStory[]
  citations: Citation[]
  validation_status: string | null
}

export interface IngestResponse {
  status: string
  pages_loaded: number
  chunks_indexed: number
  source: string
  collection: string
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  verses?: RetrievedVerse[]
  stories?: RetrievedStory[]
  citations?: Citation[]
}

export type Tab = "chat" | "upload" | "settings"
