import { useState, useRef } from "react"
import { uploadPdfApi } from "../api"
import type { IngestResponse } from "../types"

interface UploadViewProps {
  llmApiKey: string
  llmBaseUrl: string
}

export default function UploadView({ llmApiKey, llmBaseUrl }: UploadViewProps) {
  const [file, setFile] = useState<File | null>(null)
  const [source, setSource] = useState("gita")
  const [speaker, setSpeaker] = useState("")
  const [themes, setThemes] = useState("")
  const [emotions, setEmotions] = useState("")
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<IngestResponse | null>(null)
  const [error, setError] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError("")
    setResult(null)
    try {
      const res = await uploadPdfApi(file, source, speaker, themes, emotions, llmApiKey, llmBaseUrl)
      setResult(res)
    } catch (err: any) {
      setError(err.message || "Upload failed")
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && f.type === "application/pdf") setFile(f)
  }

  return (
    <div className="upload-view">
      <h2>Upload Scripture PDF</h2>
      <p className="upload-desc">Index a Bhagavad Gita or Ramayana PDF into the vector store.</p>

      <div className="upload-form">
        <div
          className={`drop-zone ${dragOver ? "drag-over" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          {file ? (
            <p className="file-name">{file.name} ({(file.size / 1024).toFixed(0)} KB)</p>
          ) : (
            <p>Drag & drop a PDF here, or click to browse</p>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            hidden
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>

        <div className="upload-field">
          <label>Source</label>
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="gita">Bhagavad Gita</option>
            <option value="ramayana">Ramayana</option>
          </select>
        </div>

        <div className="upload-field">
          <label>Speaker (optional)</label>
          <input value={speaker} onChange={(e) => setSpeaker(e.target.value)} placeholder="e.g. Krishna" />
        </div>

        <div className="upload-field">
          <label>Themes (comma-separated)</label>
          <input value={themes} onChange={(e) => setThemes(e.target.value)} placeholder="duty, courage, detachment" />
        </div>

        <div className="upload-field">
          <label>Emotions (comma-separated)</label>
          <input value={emotions} onChange={(e) => setEmotions(e.target.value)} placeholder="fear, anxiety" />
        </div>

        <button className="upload-btn" onClick={handleSubmit} disabled={loading || !file}>
          {loading ? "Indexing..." : "Index PDF"}
        </button>

        {error && <div className="upload-error">{error}</div>}

        {result && (
          <div className="upload-success">
            <p>✅ Indexed successfully</p>
            <p>{result.pages_loaded} pages → {result.chunks_indexed} chunks</p>
            <p>Collection: {result.collection}</p>
          </div>
        )}
      </div>
    </div>
  )
}
