from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendRequest(BaseModel):
    query: str = Field(..., description="Job description or natural language query")
    top_k: Optional[int] = Field(10, description="Number of recommendations to return")

class Assessment(BaseModel):
    assessment_name: str = Field(..., description="Name of the assessment")
    assessment_url: str = Field(..., description="URL to the assessment")
    test_type: Optional[str] = Field(None, description="Type of test (K/P/B/C)")
    score: Optional[float] = Field(None, description="Relevance score")

class RecommendResponse(BaseModel):
    query: str = Field(..., description="Original query")
    recommendations: List[Assessment] = Field(..., description="List of recommended assessments")
    total_results: int = Field(..., description="Total number of recommendations")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
