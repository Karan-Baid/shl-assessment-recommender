import json
import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import config#hi

class LightweightRetriever:

    def __init__(self):
        self.assessments = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.tfidf_matrix = None
        self.bm25 = None
        self.tokenized_corpus = []

    def load_and_fit(self, assessments_file: str = None):

        if assessments_file is None:
            assessments_file = config.CATALOG_FILE.replace('.json', '_processed.json')

        with open(assessments_file, 'r', encoding='utf-8') as f:
            self.assessments = json.load(f)

        print(f"Loaded {len(self.assessments)} assessments")

        print("Fitting TF-IDF vectorizer...")
        search_texts = [a['search_text'] for a in self.assessments]
        self.tfidf_matrix = self.vectorizer.fit_transform(search_texts)

        print("Initializing BM25 index...")
        self.tokenized_corpus = [
            assessment['search_text'].lower().split()
            for assessment in self.assessments
        ]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        print("Retriever initialized successfully")

    def semantic_search(self, query: str, top_k: int = 30) -> List[Tuple[int, float]]:
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(int(idx), float(similarities[idx])) for idx in top_indices]

    def keyword_search(self, query: str, top_k: int = 30) -> List[Tuple[int, float]]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices]

    def hybrid_search(
        self,
        query: str,
        top_k: int = 30,
        bm25_weight: float = None,
        semantic_weight: float = None
    ) -> List[Dict]:
        if bm25_weight is None:
            bm25_weight = config.BM25_WEIGHT
        if semantic_weight is None:
            semantic_weight = config.SEMANTIC_WEIGHT

        semantic_results = self.semantic_search(query, top_k=top_k * 2)
        keyword_results = self.keyword_search(query, top_k=top_k * 2)

        combined_scores = {}

        for idx, score in semantic_results:
            combined_scores[idx] = semantic_weight * score

        keyword_scores = [score for _, score in keyword_results]
        max_keyword_score = max(keyword_scores) if keyword_scores and max(keyword_scores) > 0 else 1.0

        for idx, score in keyword_results:
            normalized_score = score / max_keyword_score
            if idx in combined_scores:
                combined_scores[idx] += bm25_weight * normalized_score
            else:
                combined_scores[idx] = bm25_weight * normalized_score

        sorted_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in sorted_indices:
            assessment = self.assessments[idx].copy()
            assessment['retrieval_score'] = float(score)
            results.append(assessment)

        return results

    def get_assessment_by_url(self, url: str) -> Dict:
        for assessment in self.assessments:
            if assessment['url'] == url:
                return assessment
        return None

def main():
    print("=" * 60)
    print("Lightweight Retriever Test")
    print("=" * 60)

    retriever = LightweightRetriever()
    retriever.load_and_fit()

    test_queries = [
        "Java developer with collaboration skills",
        "Python SQL analyst",
        "Sales professional",
    ]

    for query in test_queries:
        print(f"\n\nQuery: '{query}'")
        print("-" * 60)

        results = retriever.hybrid_search(query, top_k=5)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['name']}")
            print(f"   Score: {result['retrieval_score']:.4f}")
            print(f"   Type: {result['test_type']}")
            print(f"   URL: {result['url'][:80]}...")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
