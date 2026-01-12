import os
from pathlib import Path

# Common Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "chroma_db")  # Use an absolute path for reliability
COLLECTION_NAME = "resume_store"
RESUME_DIR = BASE_DIR /"resumes"

os.makedirs(RESUME_DIR, exist_ok=True)

# Models (Must match in both scripts)
EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o-mini"