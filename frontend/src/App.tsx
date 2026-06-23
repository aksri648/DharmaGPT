import { useState, useEffect } from "react"
import type { Tab, Message } from "./types"
import Sidebar from "./components/Sidebar"
import ChatView from "./components/ChatView"
import UploadView from "./components/UploadView"
import SettingsView from "./components/SettingsView"
import "./App.css"

const LS_API_KEY = "dharmagpt_llm_api_key"
const LS_BASE_URL = "dharmagpt_llm_base_url"

function getThreadId(): string {
  const existing = sessionStorage.getItem("dharmagpt_thread_id")
  if (existing) return existing
  const id = crypto.randomUUID()
  sessionStorage.setItem("dharmagpt_thread_id", id)
  return id
}

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("chat")
  const [messages, setMessages] = useState<Message[]>([])
  const [threadId] = useState(() => getThreadId())
  const [llmApiKey, setLlmApiKey] = useState(() => localStorage.getItem(LS_API_KEY) || "")
  const [llmBaseUrl, setLlmBaseUrl] = useState(() => localStorage.getItem(LS_BASE_URL) || "")

  useEffect(() => {
    localStorage.setItem(LS_API_KEY, llmApiKey)
  }, [llmApiKey])

  useEffect(() => {
    localStorage.setItem(LS_BASE_URL, llmBaseUrl)
  }, [llmBaseUrl])

  const clearChat = () => {
    setMessages([])
    const newId = crypto.randomUUID()
    sessionStorage.setItem("dharmagpt_thread_id", newId)
    window.location.reload()
  }

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="main-content">
        {activeTab === "chat" && (
          <ChatView
            messages={messages}
            setMessages={setMessages}
            threadId={threadId}
            llmApiKey={llmApiKey}
            llmBaseUrl={llmBaseUrl}
            onClearChat={clearChat}
          />
        )}
        {activeTab === "upload" && (
          <UploadView llmApiKey={llmApiKey} llmBaseUrl={llmBaseUrl} />
        )}
        {activeTab === "settings" && (
          <SettingsView
            llmApiKey={llmApiKey}
            setLlmApiKey={setLlmApiKey}
            llmBaseUrl={llmBaseUrl}
            setLlmBaseUrl={setLlmBaseUrl}
          />
        )}
      </main>
    </div>
  )
}

export default App
