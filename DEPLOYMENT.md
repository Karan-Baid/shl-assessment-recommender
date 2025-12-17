# Single URL Deployment - Complete Web App

## ✅ Updated: Frontend + Backend = ONE URL!

The app now serves everything from a single URL.

---

## Deploy to Render (5 minutes)

### Step 1: Go to Render
https://render.com (sign up with GitHub)

### Step 2: Create Web Service
- Click "New +" → "Web Service"
- Connect: `Karan-Baid/shl-assessment-recommender`
- Name: `shl-assessment-app`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variable
- Key: `GROQ_API_KEY`
- Value: `your_groq_api_key_here` (from .env file)

### Step 4: Deploy!
Click "Create Web Service"

---

## You'll Get ONE URL:

```
https://shl-assessment-app.onrender.com
```

This URL will show:
- ✅ Frontend (web interface) at `/`
- ✅ API docs at `/docs`
- ✅ Health check at `/health`
- ✅ Recommendations at `/recommend`

**Submit THIS ONE URL in your SHL form!**

---

## Alternative: Deploy to Railway

```bash
# Install Railway
curl -fsSL https://railway.app/install.sh | sh

# Login and deploy
railway login
railway init
railway up

# Add API key
railway variables set GROQ_API_KEY=your_groq_api_key_here
```

Railway automatically gives you one URL for everything!

---

## What Changed?

**Before**: 
- Frontend: localhost or Netlify
- API: localhost or Render  
- 2 separate URLs ❌

**Now**:
- Everything served from FastAPI
- ONE URL for complete app ✅

---

## Test Locally

```bash
cd /home/karan/projects/sih
source venv/bin/activate
python -m uvicorn api.main:app --reload

# Open browser:
# http://localhost:8000 → Full web app!
```

---

## For Submission:

**After deploying to Render, submit:**
- Web App URL: `https://shl-assessment-app.onrender.com`
- GitHub URL: `https://github.com/Karan-Baid/shl-assessment-recommender`
- 2-Page Doc: Upload `APPROACH.md`
- Predictions: Upload `predictions.csv`

**That's it!** ✅
