import logging
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader

from config import DB_PATH, COLLECTION_NAME, RESUME_DIR, EMBEDDING_MODEL, LLM_MODEL

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chunk(BaseModel):
    headline: str = Field(description="Heading for this section")
    summary: str = Field(description="Summary of this chunk")
    original_text: str = Field(description="Exact resume text")

class Chunks(BaseModel):
    chunks: List[Chunk]

class IngestionPipeline:
    def __init__(self):
        self.source_path = RESUME_DIR
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
    def load_single_document(self, file_path: Path) -> List[Document]:
        """Loads a single PDF file."""
        try:
            clean_filename = file_path.name
            loader = PyPDFLoader(str(file_path))
            pages = loader.load()
            full_text = "\n\n".join([p.page_content for p in pages])
            
            if full_text.strip():
                return [Document(
                    page_content=full_text,
                    metadata={"source": clean_filename}
                )]
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
        return []

    def semantic_chunking(self, documents):
        if not documents: return []
        
        llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
        structured_llm = llm.with_structured_output(Chunks)
        
        final_docs = []
        for doc in documents:
            prompt = f"Split this resume into sections. Source: {doc.metadata['source']}\n\nText: {doc.page_content}"
            try:
                result = structured_llm.invoke(prompt)
                for chunk in result.chunks:
                    final_docs.append(Document(
                        page_content=f"{chunk.headline}\n{chunk.original_text}",
                        metadata=doc.metadata
                    ))
            except Exception as e:
                logger.error(f"Chunking error: {e}")
                # Fallback: keep original doc if LLM fails
                final_docs.append(doc)
                
        return final_docs

    def ingest_new_file(self, file_path: Path):
        """
        Public method to ingest a single uploaded file.
        Removes old versions of the file first to prevent duplicates.
        """
        logger.info(f"Processing new upload: {file_path.name}")
        
        # 1. Connect to DB
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=DB_PATH,
            embedding_function=self.embeddings
        )

        # 2. Clear existing chunks for this specific file (Prevent Duplicates)
        # ChromaDB allows filtering by metadata for deletion
        try:
            # We fetch IDs first (safe pattern) or just delete by metadata
            # Note: Chroma's delete with where clause is the standard way
            vector_store._collection.delete(where={"source": file_path.name})
            logger.info(f"Cleared old version of {file_path.name}")
        except Exception as e:
            logger.warning(f"Could not clear old data (might be new file): {e}")

        # 3. Process & Ingest
        raw_docs = self.load_single_document(file_path)
        chunks = self.semantic_chunking(raw_docs)
        
        if chunks:
            vector_store.add_documents(chunks)
            logger.info(f"Successfully ingested {len(chunks)} chunks for {file_path.name}")
            return True
        return False

    def run(self, reset_db=True):
        """Batch ingestion for initialization."""
        if reset_db and os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        
        # Load all
        documents = []
        pdf_files = list(self.source_path.rglob("*.pdf"))
        for p in pdf_files:
            documents.extend(self.load_single_document(p))
            
        chunks = self.semantic_chunking(documents)
        
        Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=DB_PATH,
            collection_name=COLLECTION_NAME
        )
        logger.info(f"Batch ingestion complete. {len(chunks)} chunks stored.")

if __name__ == "__main__":
    IngestionPipeline().run()