# DharmaGPT - Render Deployment Guide

## Quick Start

### 1. Push to GitHub

```bash
cd /home/akshat/Placement2026/Projects/DharmaGPT
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/DharmaGPT.git
git push -u origin main
```

### 2. Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Blueprint**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create:
   - **dharmagpt-api** (Web Service)
   - **dharmagpt-frontend** (Static Site)
   - **dharmagpt-db** (PostgreSQL)

### 3. Update Environment Variables

After deployment, go to **dharmagpt-api** → **Environment** tab and update:

```bash
# Required: Update these with real values
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
```

### 4. Verify Deployment

```bash
# Check backend health
curl https://dharmagpt-api.onrender.com/api/v1/health

# Open frontend
open https://dharmagpt-frontend.onrender.com
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Render Dashboard                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │ dharmagpt-frontend│    │ dharmagpt-api    │          │
│  │ (Static Site)     │───▶│ (Web Service)    │          │
│  │                   │    │                  │          │
│  │ React + Vite      │    │ FastAPI + LangGraph│        │
│  │ Port: Auto        │    │ Port: $PORT      │          │
│  └──────────────────┘    └────────┬─────────┘          │
│                                   │                     │
│                                   ▼                     │
│                        ┌──────────────────┐            │
│                        │ dharmagpt-db     │            │
│                        │ (PostgreSQL)     │            │
│                        │ + pgvector       │            │
│                        └──────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Environment Variables

### Backend (dharmagpt-api)

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | Auto-set | From Render PostgreSQL |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | Change to your LLM provider |
| `LLM_API_KEY` | `sk-...` | Your API key |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Auto-downloads on first run |
| `LOG_LEVEL` | `info` | Set to `debug` for troubleshooting |

### Frontend (dharmagpt-frontend)

| Variable | Value | Notes |
|----------|-------|-------|
| `VITE_API_URL` | `/api` | Uses same-domain proxy |

---

## LLM Options

### Option 1: OpenAI (Recommended for Production)

```bash
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
```

### Option 2: Anthropic

```bash
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_API_KEY=sk-ant-your-key-here
LLM_MODEL=claude-3-haiku-20240307
```

### Option 3: Groq

```bash
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_your-key-here
LLM_MODEL=llama3-8b-8192
```

### Option 4: Local Ollama (Development Only)

```bash
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=
LLM_MODEL=qwen3:8b
```

---

## Troubleshooting

### Backend won't start

1. Check logs: **dharmagpt-api** → **Logs** tab
2. Common issues:
   - Missing `DATABASE_URL` → Render auto-sets this
   - Missing `LLM_API_KEY` → Add in Environment tab
   - Port issues → Render sets `$PORT` automatically

### Frontend can't connect to API

1. Check `VITE_API_URL` is set to `/api`
2. Verify backend is running: `curl https://dharmagpt-api.onrender.com/api/v1/health`
3. Check CORS: Backend allows `["*"]` by default

### Embedding model slow on first request

- First request downloads `BAAI/bge-m3` (~2.2GB)
- Subsequent requests are fast (cached)
- Consider using a smaller model for faster cold starts:
  ```bash
  EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
  ```

### Database connection errors

1. Ensure PostgreSQL is running: **dharmagpt-db** → **Info** tab
2. Check `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
3. Verify pgvector extension is enabled (auto-enabled by Render)

---

## Cost Estimate

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| dharmagpt-api | Free | $0 |
| dharmagpt-frontend | Free | $0 |
| dharmagpt-db | Free | $0 |
| **Total** | | **$0** |

> **Note:** Free tier has limitations:
> - Services spin down after 15 min of inactivity
> - 750 hours/month per service
> - 90 days of PostgreSQL data retention

---

## Production Considerations

1. **Upgrade to paid tier** for always-on services
2. **Add custom domain** for professional URL
3. **Enable auto-deploy** for CI/CD
4. **Set up monitoring** with Render's built-in metrics
5. **Configure backups** for PostgreSQL

---

## Next Steps

After deployment:

1. **Ingest real data**: Upload Gita/Ramayana PDFs via frontend
2. **Test end-to-end**: Ask questions and verify responses
3. **Monitor performance**: Check Render metrics for latency
4. **Iterate**: Adjust retrieval settings based on response quality
