# SHL Assessment Recommendation System

Intelligent recommendation system for SHL assessments using **Hybrid Search + LLM Reranking**.

## Features

- **Groq LLM** (llama-3.1-8b-instant) for intelligent reranking
- **Pydantic** structured output for reliable parsing
- **Hybrid Search**: BM25 keyword + TF-IDF semantic
- **Sentence Transformers** embeddings (384-dim)
- **Smart Balancing**: Distributes test types (K/P/C/B)
- **FastAPI** backend with auto-documentation
- **Modern Web UI** with dark theme

## Quick Start

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd sih
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 4. Run API
python -m uvicorn api.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# 5. Open Frontend
open frontend/index.html
```

## API Usage

**POST /recommend**
```json
{
  "query": "Python developer with communication skills",
  "top_k": 10
}
```

**Response**
```json
{
  "query": "...",
  "recommendations": [
    {
      "assessment_name": "Python (New)",
      "assessment_url": "https://...",
      "test_type": "K",
      "score": 0.89
    }
  ]
}
```

## Project Structure

```
├── api/              # FastAPI backend
├── frontend/         # Web interface
├── data/             # Assessments & embeddings
├── config.py         # Configuration
├── scraper.py        # Data collection
├── embeddings.py     # Sentence transformers
├── retriever.py      # Hybrid search
├── llm_service.py    # Groq LLM (Pydantic)
├── evaluator.py      # Mean Recall@10
└── predictions.csv   # Test set predictions
```

## Tech Stack

- **LLM**: Groq (ChatGroq from langchain-groq)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Search**: BM25 + TF-IDF
- **API**: FastAPI + Pydantic
- **Frontend**: Vanilla JS/CSS

## Evaluation

**Metric**: Mean Recall@10  
**Dataset**: 101 assessments, 54 training queries  
**Predictions**: 90 rows (9 test queries × 10 recommendations)

```bash
# Run evaluation
python evaluator.py

# Generate predictions
python generate_predictions.py
```

## Deployment

**API (Render):**
```
Build: pip install -r requirements.txt
Start: uvicorn api.main:app --host 0.0.0.0 --port $PORT
Env: GROQ_API_KEY=your_key
```

**Frontend (Netlify):**
- Drag & drop `frontend/` folder
- Update `API_BASE_URL` in `frontend/app.js`

## Assignment Requirements

✅ **Data**: 101 SHL assessments scraped  
✅ **Retrieval**: Hybrid BM25 + semantic search  
✅ **LLM**: Groq for query understanding & reranking  
✅ **API**: FastAPI with /health and /recommend  
✅ **Frontend**: Web interface included  
✅ **Evaluation**: Mean Recall@10 implemented  
✅ **Predictions**: predictions.csv generated  
✅ **Documentation**: APPROACH.md (2-page technical doc)

## Author

SHL AI Internship Assignment - GenAI Recommendation System

## License

Educational project for SHL assessment
