import pandas as pd
from retriever import LightweightRetriever
from llm_service import LLMService
import config

def generate_predictions():
    print("=" * 60)
    print("Generating Test Set Predictions")
    print("=" * 60)

    print("\nInitializing retriever...")
    retriever = LightweightRetriever()
    retriever.load_and_fit()

    print("Initializing LLM service...")
    llm_service = LLMService()

    print("\nLoading test data...")
    test_df = pd.read_excel(config.TRAIN_DATA_FILE, sheet_name='Test-Set')
    test_queries = test_df['Query'].tolist()

    print(f"Found {len(test_queries)} test queries")

    predictions = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Processing query...")
        print(f"Query: {query[:100]}...")

        candidates = retriever.hybrid_search(query, top_k=30)

        if llm_service:
            reranked = llm_service.rerank_assessments(query, candidates, top_k=10)
        else:
            reranked = candidates[:10]

        for assessment in reranked:
            predictions.append({
                'Query': query,
                'Assessment_url': assessment['url']
            })

        print(f"  Generated {len(reranked)} recommendations")

    predictions_df = pd.DataFrame(predictions)

    output_file = 'predictions.csv'
    predictions_df.to_csv(output_file, index=False)

    print("\n" + "=" * 60)
    print(f"Predictions saved to {output_file}")
    print(f"Total rows: {len(predictions_df)}")
    print("=" * 60)

    print("\nSample predictions:")
    print(predictions_df.head(15))

if __name__ == "__main__":
    generate_predictions()
