import json#h
import pandas as pd
from typing import List, Dict, Tuple
from retriever import LightweightRetriever
from llm_service import LLMService
import config

class Evaluator:

    def __init__(self, retriever, llm_service=None):
        self.retriever = retriever
        self.llm_service = llm_service

    def calculate_recall_at_k(
        self,
        predicted: List[str],
        relevant: List[str],
        k: int = 10
    ) -> float:
        predicted_k = predicted[:k]
        relevant_found = len(set(predicted_k) & set(relevant))
        total_relevant = len(relevant)

        return relevant_found / total_relevant if total_relevant > 0 else 0.0

    def evaluate_on_dataset(self, queries_with_labels: Dict[str, List[str]], k: int = 10) -> Dict:
        recall_scores = []
        results_per_query = []

        print(f"Evaluating on {len(queries_with_labels)} queries...")
        print("=" * 60)

        for i, (query, relevant_urls) in enumerate(queries_with_labels.items(), 1):

            candidates = self.retriever.hybrid_search(query, top_k=30)

            if self.llm_service:
                reranked = self.llm_service.rerank_assessments(query, candidates, top_k=k)
            else:
                reranked = candidates[:k]

            predicted_urls = [a['url'] for a in reranked]

            recall = self.calculate_recall_at_k(predicted_urls, relevant_urls, k=k)
            recall_scores.append(recall)

            results_per_query.append({
                'query': query,
                'recall_at_k': recall,
                'relevant_count': len(relevant_urls),
                'predicted_urls': predicted_urls,
                'relevant_urls': relevant_urls
            })

            print(f"\nQuery {i}: {query[:80]}...")
            print(f"  Recall@{k}: {recall:.4f}")
            print(f"  Relevant assessments: {len(relevant_urls)}")
            print(f"  Found in top-{k}: {int(recall * len(relevant_urls))}")

        mean_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0

        print("\n" + "=" * 60)
        print(f"Mean Recall@{k}: {mean_recall:.4f}")
        print("=" * 60)

        return {
            'mean_recall_at_k': mean_recall,
            'k': k,
            'num_queries': len(queries_with_labels),
            'per_query_results': results_per_query
        }

    def load_training_data(self) -> Dict[str, List[str]]:
        df = pd.read_excel(config.TRAIN_DATA_FILE, sheet_name='Train-Set')

        queries_labels = df.groupby('Query')['Assessment_url'].apply(list).to_dict()
        return queries_labels

def main():
    print("=" * 60)
    print("Assessment Recommendation System - Evaluation")
    print("=" * 60)

    print("\nInitializing retriever...")
    retriever = LightweightRetriever()
    retriever.load_and_fit()

    print("Initializing LLM service...")
    llm_service = LLMService()

    evaluator = Evaluator(retriever, llm_service)

    print("\nLoading training data...")
    queries_labels = evaluator.load_training_data()
    print(f"Loaded {len(queries_labels)} labeled queries")

    print("\n" + "=" * 60)
    print("Running Evaluation...")
    print("=" * 60)

    results = evaluator.evaluate_on_dataset(queries_labels, k=10)

    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to evaluation_results.json")
    print(f"\nFinal Mean Recall@10: {results['mean_recall_at_k']:.4f}")

if __name__ == "__main__":
    main()
