# DharmaGPT - Azure Deployment Guide

## Overview

This guide covers deploying DharmaGPT on Azure using Docker containers.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Container Instance              │
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │    frontend       │    │    backend        │          │
│  │  (nginx:80)       │───▶│  (uvicorn:8000)   │          │
│  │                   │    │                  │          │
│  │  React + Vite     │    │ FastAPI + LangGraph│        │
│  └──────────────────┘    └────────┬─────────┘          │
│                                   │                     │
│                                   ▼                     │
│                        ┌──────────────────┐            │
│                        │    db            │            │
│                        │  (PostgreSQL)    │            │
│                        │  + pgvector      │            │
│                        └──────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Azure CLI installed
- Docker installed
- Azure Container Registry (ACR) created

## Step 1: Create Azure Resources

### Option A: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name dharmagpt-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group dharmagpt-rg \
  --name dharmagptacr \
  --sku Basic

# Enable admin user for ACR
az acr update -n dharmagptacr --admin-enabled true
```

### Option B: Using Azure Portal

1. Create a Resource Group
2. Create an Azure Container Registry (Basic tier is fine)
3. Enable admin user

## Step 2: Build and Push Images

```bash
# Set variables
ACR_NAME=dharmagptacr
RESOURCE_GROUP=dharmagpt-rg

# Login to ACR
az acr login --name $ACR_NAME

# Build backend image
docker build -t $ACR_NAME.azurecr.io/dharmagpt-api:latest -f Dockerfile.backend .

# Build frontend image
docker build -t $ACR_NAME.azurecr.io/dharmagpt-frontend:latest -f Dockerfile.frontend .

# Push images
docker push $ACR_NAME.azurecr.io/dharmagpt-api:latest
docker push $ACR_NAME.azurecr.io/dharmagpt-frontend:latest
```

## Step 3: Deploy to Azure Container Instances

### Option A: Using Azure CLI

```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv)

# Create container group with all 3 containers
az container create \
  --resource-group $RESOURCE_GROUP \
  --name dharmagpt \
  --image $ACR_NAME.azurecr.io/dharmagpt-api:latest \
  --registry-login-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_NAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label dharmagpt \
  --ports 80 8000 5432 \
  --ip-address Public \
  --environment-variables \
    DATABASE_URL="postgresql://postgres:postgres@localhost:5432/dharmagpt" \
    LLM_BASE_URL="https://api.openai.com/v1" \
    LLM_API_KEY="sk-your-key" \
    LLM_MODEL="gpt-4o-mini" \
    EMBEDDING_MODEL="text-embedding-3-small" \
  --cpu 2 \
  --memory 4
```

### Option B: Using docker-compose.yml

```bash
# Set environment variables
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your-secure-password
export POSTGRES_DB=dharmagpt
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_API_KEY=sk-your-key
export LLM_MODEL=gpt-4o-mini

# Deploy
docker-compose up -d
```

## Step 4: Deploy to Azure App Service (Production)

For production, use Azure App Service with containers:

```bash
# Create App Service Plan
az appservice plan create \
  --name dharmagpt-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create Web App for Backend
az webapp create \
  --name dharmagpt-api \
  --resource-group $RESOURCE_GROUP \
  --plan dharmagpt-plan \
  --deployment-container-image-name $ACR_NAME.azurecr.io/dharmagpt-api:latest

# Create Web App for Frontend
az webapp create \
  --name dharmagpt-frontend \
  --resource-group $RESOURCE_GROUP \
  --plan dharmagpt-plan \
  --deployment-container-image-name $ACR_NAME.azurecr.io/dharmagpt-frontend:latest

# Configure App Settings for Backend
az webapp config appsettings set \
  --name dharmagpt-api \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DATABASE_URL="postgresql://user:password@your-neon-host/dharmagpt?sslmode=require" \
    LLM_BASE_URL="https://api.openai.com/v1" \
    LLM_API_KEY="sk-your-key" \
    LLM_MODEL="gpt-4o-mini"
```

## Step 5: Configure Neon DB

Since you're using Neon DB:

1. Go to [Neon Console](https://console.neon.tech)
2. Create a new project
3. Copy the connection string
4. Enable pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. Update `DATABASE_URL` in Azure App Service settings

## Step 6: Verify Deployment

```bash
# Check backend health
curl https://dharmagpt-api.azurewebsites.net/api/v1/health

# Open frontend
open https://dharmagpt-frontend.azurewebsites.net
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `LLM_BASE_URL` | LLM API endpoint | `https://api.openai.com/v1` |
| `LLM_API_KEY` | LLM API key | `sk-...` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `LOG_LEVEL` | Logging level | `info` |

## Cost Estimate

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Azure Container Registry | Basic | ~$5 |
| Azure App Service | B1 | ~$55 |
| Neon DB | Free | $0 |
| **Total** | | **~$60/month** |

## Troubleshooting

### Container won't start

1. Check container logs:
   ```bash
   az container logs --resource-group $RESOURCE_GROUP --name dharmagpt
   ```

2. Common issues:
   - Missing environment variables
   - Database connection failed
   - Port conflicts

### OOM errors

If you see out-of-memory errors:
- Upgrade to a larger App Service plan (B2 or higher)
- Use a smaller embedding model
- Optimize dependencies

### Database connection issues

1. Ensure Neon DB is running
2. Check firewall rules (Neon allows all IPs by default)
3. Verify connection string format
