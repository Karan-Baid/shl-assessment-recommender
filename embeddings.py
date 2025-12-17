import json
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import config
from data_processor import load_catalog, process_catalog, get_search_texts

class EmbeddingGenerator:

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = config.EMBEDDING_MODEL

        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.assessments = None

    def generate_embeddings(self, texts: list) -> np.ndarray:
        print(f"Generating embeddings for {len(texts)} texts...")

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )

        print(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings

    def process_and_embed_catalog(self):

        raw_catalog = load_catalog()
        self.assessments = process_catalog(raw_catalog)

        search_texts = get_search_texts(self.assessments)

        self.embeddings = self.generate_embeddings(search_texts)

        return self.embeddings, self.assessments

    def save_embeddings(self, filename: str = None):
        if filename is None:
            filename = config.EMBEDDINGS_FILE

        if self.embeddings is None:
            raise ValueError("No embeddings to save. Generate them first.")

        np.save(filename, self.embeddings)
        print(f"Saved embeddings to {filename}")

    def load_embeddings(self, filename: str = None):
        if filename is None:
            filename = config.EMBEDDINGS_FILE

        self.embeddings = np.load(filename)
        print(f"Loaded embeddings from {filename} with shape: {self.embeddings.shape}")
        return self.embeddings

    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode([query], convert_to_numpy=True)[0]

def main():
    print("=" * 60)
    print("Embedding Generation")
    print("=" * 60)

    generator = EmbeddingGenerator()

    embeddings, assessments = generator.process_and_embed_catalog()

    generator.save_embeddings()

    processed_file = config.CATALOG_FILE.replace('.json', '_processed.json')
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    print(f"Saved processed assessments to {processed_file}")

    print("\n" + "=" * 60)
    print("Embedding generation complete!")
    print(f"  Total assessments: {len(assessments)}")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    print("=" * 60)

if __name__ == "__main__":
    main()
