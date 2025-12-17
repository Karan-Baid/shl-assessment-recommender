import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.models import RecommendationRequest, RecommendationResponse
from retriever import LightweightRetriever
from llm_service import LLMService

app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="Intelligent recommendation system for SHL assessments using Hybrid Search + LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = None
llm_service = None

@app.on_event("startup")
async def startup_event():
    global retriever, llm_service

    print("Initializing Assessment Recommendation System...")

    retriever = LightweightRetriever()
    retriever.load_and_fit()

    llm_service = LLMService()

    print("\nSystem initialized successfully!")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Assessment Recommendation API is running",
        "llm_active": llm_service.provider is not None,
        "assessments_loaded": len(retriever.assessments)
    }

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_assessments(request: RecommendationRequest):
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        retrieved = retriever.search(request.query, top_k=30)
        
        if not retrieved:
            return RecommendationResponse(
                query=request.query,
                recommendations=[],
                total_results=0
            )
        
        if llm_service.provider:
            final = llm_service.rerank_assessments(
                query=request.query,
                assessments=retrieved,
                top_k=request.top_k
            )
        else:
            final = retrieved[:request.top_k]
        
        recommendations = []
        for asmt in final:
            recommendations.append({
                "assessment_name": asmt['name'],
                "assessment_url": asmt['url'],
                "test_type": asmt.get('test_type', 'K'),
                "score": asmt.get('score', 0.0)
            })
        
        return RecommendationResponse(
            query=request.query,
            recommendations=recommendations,
            total_results=len(recommendations)
        )
    
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
async def root():
    return {
        "name": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
