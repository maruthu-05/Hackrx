# Deployment Guide

## Quick Deployment Options

### 1. Railway (Recommended - Easy & Fast)

1. **Create account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy**: Railway auto-detects Python and deploys
4. **Environment Variables**: Add `OPENAI_API_KEY` in Railway dashboard
5. **Custom Domain**: Get HTTPS URL automatically

**Railway Deploy Button**:
```
https://railway.app/new/template?template=https://github.com/your-repo
```

### 2. Render

1. **Create account**: Go to [render.com](https://render.com)
2. **New Web Service**: Connect your GitHub repo
3. **Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. **Environment Variables**: Add `OPENAI_API_KEY`
5. **Deploy**: Automatic HTTPS

### 3. Heroku

```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

### 4. Vercel (Serverless)

```bash
# Install Vercel CLI
npm i -g vercel
vercel --prod
```

## Environment Variables Required

```env
GEMINI_API_KEY=your-gemini-api-key-here
PORT=8000
```

## Pre-Deployment Checklist

✅ **API Structure**
- [x] POST endpoint: `/hackrx/run`
- [x] Bearer token authentication
- [x] JSON request/response format
- [x] HTTPS ready

✅ **Performance**
- [x] Response time < 30 seconds
- [x] Error handling
- [x] Timeout protection
- [x] Memory optimization

✅ **Security**
- [x] API key validation
- [x] Input sanitization
- [x] CORS configuration
- [x] HTTPS enforcement

## Testing Your Deployed API

Replace `YOUR_DEPLOYED_URL` with your actual URL:

```bash
curl -X POST "YOUR_DEPLOYED_URL/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer 9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## Submission Format

When submitting to the platform:

**Webhook URL**: `https://your-domain.com/hackrx/run`
**Description**: `FastAPI + GPT-4 + FAISS + Sentence Transformers`

## Troubleshooting

**Issue**: Timeout errors
**Solution**: Optimize embedding model or use caching

**Issue**: Memory errors
**Solution**: Use smaller embedding models or increase server memory

**Issue**: SSL certificate errors
**Solution**: Ensure HTTPS is properly configured on your hosting platform