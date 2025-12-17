import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.models import RecommendRequest, RecommendResponse, Assessment, HealthResponse
from retriever import LightweightRetriever
from llm_service import LLMService
import config

app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="Intelligent assessment recommendation system using hybrid search and LLM reranking",
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

    print("System initialized successfully!")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Assessment Recommendation API is running"
    )

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_assessments(request: RecommendRequest):
    try:
        if not retriever:
            raise HTTPException(status_code=500, detail="Retriever not initialized")

        top_k = min(request.top_k or 10, 10)

        candidates = retriever.hybrid_search(
            query=request.query,
            top_k=config.TOP_K_RETRIEVAL
        )

        if llm_service:
            reranked = llm_service.rerank_assessments(
                query=request.query,
                assessments=candidates,
                top_k=top_k
            )
        else:
            reranked = candidates[:top_k]

        recommendations = []
        for asmt in reranked:
            recommendations.append(Assessment(
                assessment_name=asmt['name'],
                assessment_url=asmt['url'],
                test_type=asmt.get('test_type'),
                score=asmt.get('retrieval_score', 0.0)
            ))

        return RecommendResponse(
            query=request.query,
            recommendations=recommendations,
            total_results=len(recommendations)
        )

    except Exception as e:
        print(f"Error in recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
