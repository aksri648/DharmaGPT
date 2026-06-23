interface SettingsViewProps {
  llmApiKey: string
  setLlmApiKey: (v: string) => void
  llmBaseUrl: string
  setLlmBaseUrl: (v: string) => void
}

export default function SettingsView({ llmApiKey, setLlmApiKey, llmBaseUrl, setLlmBaseUrl }: SettingsViewProps) {
  return (
    <div className="settings-view">
      <h2>Settings</h2>
      <p className="settings-desc">Configure your LLM connection. Values are stored in your browser's localStorage.</p>

      <div className="settings-form">
        <div className="settings-field">
          <label htmlFor="baseUrl">LLM Base URL</label>
          <input
            id="baseUrl"
            type="text"
            value={llmBaseUrl}
            onChange={(e) => setLlmBaseUrl(e.target.value)}
            placeholder="http://localhost:11434/v1"
          />
          <span className="settings-hint">Ollama endpoint or OpenAI-compatible API base</span>
        </div>

        <div className="settings-field">
          <label htmlFor="apiKey">LLM API Key</label>
          <input
            id="apiKey"
            type="password"
            value={llmApiKey}
            onChange={(e) => setLlmApiKey(e.target.value)}
            placeholder="ollama or your API key"
          />
          <span className="settings-hint">Stored locally — never sent to any server other than your LLM endpoint</span>
        </div>

        <div className="settings-note">
          <strong>Note:</strong> These settings override the server-side defaults from <code>.env</code>.
          The values are sent as HTTP headers on each request so the server can use them.
        </div>
      </div>
    </div>
  )
}
