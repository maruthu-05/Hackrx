# Google Gemini API Setup Guide

## Getting Your Gemini API Key

### Step 1: Go to Google AI Studio
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account

### Step 2: Create API Key
1. Click on "Get API key" in the left sidebar
2. Click "Create API key"
3. Select "Create API key in new project" (or choose existing project)
4. Copy your API key

### Step 3: Configure Your Application
1. Open the `.env` file in your project
2. Replace the placeholder with your actual API key:
```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

## Why Gemini?

✅ **Cost Effective**: Much cheaper than OpenAI GPT-4  
✅ **High Performance**: Excellent quality responses  
✅ **Fast**: Quick response times  
✅ **Large Context**: Can handle long documents  
✅ **Free Tier**: Generous free usage limits  

## Gemini Models Available

- **gemini-1.5-flash**: Fast, efficient (recommended for this project)
- **gemini-1.5-pro**: More capable, slower
- **gemini-1.0-pro**: Older version, still good

## Rate Limits

**Free Tier**:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per minute

**Paid Tier**:
- Much higher limits
- Pay per token usage

## Testing Your Setup

After setting up your API key, test it:

```bash
python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('✅ Gemini API key configured successfully!')"
```

## Troubleshooting

**Error: "API key not valid"**
- Double-check your API key in the .env file
- Make sure there are no extra spaces
- Verify the key is active in Google AI Studio

**Error: "Quota exceeded"**
- You've hit the free tier limits
- Wait for the quota to reset or upgrade to paid tier

**Error: "Model not found"**
- Check if you're using a valid model name
- Try 'gemini-1.5-flash' or 'gemini-1.5-pro'