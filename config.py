import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

DATA_DIR = "data"
CATALOG_FILE = os.path.join(DATA_DIR, "assessments_catalog.json")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.npy")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
TRAIN_DATA_FILE = "Gen_AI Dataset.xlsx"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

TOP_K_RETRIEVAL = 30
TOP_K_FINAL = 10
BM25_WEIGHT = 0.4
SEMANTIC_WEIGHT = 0.6

SHL_CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
MIN_ASSESSMENTS = 377
SCRAPE_DELAY = 1

GROQ_MODEL = "llama-3.1-8b-instant"
GEMINI_MODEL = "gemini-1.5-flash"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048

TEST_TYPES = {
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'B': 'Behavioral',
    'C': 'Cognitive'
}
#hi
