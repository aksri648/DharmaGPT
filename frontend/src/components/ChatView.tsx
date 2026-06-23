import { useState, useRef, useEffect } from "react"
import type { Message } from "../types"
import { chatApi } from "../api"

interface ChatViewProps {
  messages: Message[]
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
  threadId: string
  llmApiKey: string
  llmBaseUrl: string
  onClearChat: () => void
}

const MAX_INPUT_LENGTH = 2000

export default function ChatView({ messages, setMessages, threadId, llmApiKey, llmBaseUrl, onClearChat }: ChatViewProps) {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput("")

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const data = await chatApi(text, threadId, llmApiKey, llmBaseUrl)
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        verses: data.verses_used,
        stories: data.stories_used,
        citations: data.citations,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `**Error**: ${err.message || "Something went wrong"}`,
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <h2>How can I help you today?</h2>
            <p>Share what's on your mind — I'll respond with wisdom from the Bhagavad Gita and Ramayana.</p>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <div className="message-avatar">{m.role === "user" ? "🧘" : "🕉️"}</div>
            <div className="message-bubble">
              <div className="message-content">{m.content}</div>
              {m.citations && m.citations.length > 0 && (
                <div className="message-citations">
                  {m.citations.map((c, i) => (
                    <span key={i} className={`citation-badge ${c.valid ? "valid" : "invalid"}`}>
                      {c.source} {c.chapter}.{c.verse} {c.valid ? "✅" : "⚠️"}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🕉️</div>
            <div className="message-bubble loading">
              <span className="dot-pulse" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-bar">
        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Ask for guidance..."
          rows={1}
          maxLength={MAX_INPUT_LENGTH}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <div className="chat-input-actions">
          {messages.length > 0 && (
            <button className="chat-clear-btn" onClick={onClearChat} disabled={loading}>
              Clear
            </button>
          )}
          <button className="chat-send-btn" onClick={send} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
