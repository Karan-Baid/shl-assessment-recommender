import os
from typing import List, Dict, Optional
import config
import json
from pydantic import BaseModel, Field

class QueryIntent(BaseModel):
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills mentioned in query")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills or behavioral traits")
    role: str = Field(default="", description="Job role or title")
    test_types_needed: List[str] = Field(default_factory=lambda: ['K', 'P'], description="Test types needed: K, P, C, B")

class LLMService:

    def __init__(self):
        self.provider = None
        self.model = None

        if self._init_groq():
            print(f"✓ Initialized Groq LLM: {config.GROQ_MODEL}")
            return

        if self._init_gemini():
            print(f"✓ Initialized Gemini LLM: {config.GEMINI_MODEL}")
            return

        print("WARNING: No LLM configured. Reranking will use fallback logic.")

    def _init_groq(self) -> bool:
        try:
            from langchain_groq import ChatGroq

            api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
            if not api_key:
                return False

            self.model = ChatGroq(
                api_key=api_key,
                model=config.GROQ_MODEL,
                temperature=config.LLM_TEMPERATURE
            )
            self.structured_model = self.model.with_structured_output(QueryIntent)
            self.provider = "groq"
            return True

        except Exception as e:
            print(f"Could not initialize Groq: {e}")
            return False

    def _init_gemini(self) -> bool:
        try:
            import google.generativeai as genai

            api_key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return False

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            self.provider = "gemini"
            return True

        except Exception as e:
            print(f"Could not initialize Gemini: {e}")
            return False

    def _call_llm(self, prompt: str) -> Optional[str]:
        if not self.model:
            return None

        try:
            if self.provider == "groq":
                response = self.model.invoke(prompt)
                return response.content

            elif self.provider == "gemini":
                response = self.model.generate_content(
                    prompt,
                    generation_config={'temperature': config.LLM_TEMPERATURE}
                )
                return response.text

        except Exception as e:
            print(f"LLM call failed ({self.provider}): {e}")
            return None

    def extract_query_intent(self, query: str) -> Dict:
        if not self.model:
            return {'technical_skills': [], 'soft_skills': [], 'role': '', 'test_types_needed': ['K', 'P']}

        if self.provider == "groq" and hasattr(self, 'structured_model'):
            prompt = f"""Analyze this job query and extract key information:

Query: {query}

Extract:
1. Technical skills mentioned (e.g., Java, Python, SQL)
2. Soft skills/behavioral traits (e.g., collaboration, leadership)
3. Job role/title
4. Whether cognitive/personality/behavioral tests are needed

Test types:
- K (Knowledge & Skills) for technical skills
- P (Personality & Behavior) for soft skills, personality traits
- C (Cognitive) for reasoning, problem-solving
- B (Behavioral) for behavioral assessments
"""

            try:
                result = self.structured_model.invoke(prompt)
                return result.model_dump()
            except Exception as e:
                print(f"Structured extraction failed: {e}")
                return {'technical_skills': [], 'soft_skills': [], 'role': '', 'test_types_needed': ['K', 'P']}

        return {'technical_skills': [], 'soft_skills': [], 'role': '', 'test_types_needed': ['K', 'P']}

    def rerank_assessments(
        self,
        query: str,
        assessments: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        if not self.model or not assessments:
            return self._balance_test_types(assessments, ['K', 'P'], top_k)

        intent = self.extract_query_intent(query)
        needed_types = intent.get('test_types_needed', ['K', 'P'])

        return self._balance_test_types(assessments, needed_types, top_k)

    def _balance_test_types(
        self,
        assessments: List[Dict],
        needed_types: List[str],
        top_k: int
    ) -> List[Dict]:
        if not needed_types:
            return assessments[:top_k]

        slots_per_type = top_k // len(needed_types)
        balanced = []
        type_counts = {t: 0 for t in needed_types}

        for asmt in assessments:
            test_type = asmt.get('test_type', 'K')
            if test_type in needed_types and type_counts[test_type] < slots_per_type:
                balanced.append(asmt)
                type_counts[test_type] += 1
                if len(balanced) >= top_k:
                    break

        for asmt in assessments:
            if asmt not in balanced and len(balanced) < top_k:
                balanced.append(asmt)

        return balanced[:top_k]

def main():
    print("=" * 60)
    print("LLM Service Test")
    print("=" * 60)

    service = LLMService()

    test_query = "I am hiring for Java developers who can also collaborate effectively with my business teams"

    print(f"\nTest Query: {test_query}")
    print("-" * 60)

    if service.model:
        intent = service.extract_query_intent(test_query)
        print("\nExtracted Intent:")
        print(json.dumps(intent, indent=2))
    else:
        print("\nNo LLM configured - skipping intent extraction test")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
