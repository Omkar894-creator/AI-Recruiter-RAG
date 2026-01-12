import logging
import os
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv  # <--- ADDED THIS

# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# Import Config
from config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, LLM_MODEL

# Load Environment Variables (Critical for API Keys)
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class InterviewQuestion(BaseModel):
    question: str
    rationale: str

class MatchAnalysis(BaseModel):
    match_score: float
    candidate_name: str
    summary: str
    key_matches: List[str]
    missing_skills: List[str]
    interview_questions: List[InterviewQuestion]
    source_citations: List[str]

class SearchQueries(BaseModel):
    queries: List[str]

class RAGController:
    def __init__(self, vector_db_path: str = DB_PATH):
        print("DEBUG: Initializing RAG Controller...")
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=vector_db_path,
            embedding_function=self.embeddings
        )
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
        print(f"DEBUG: RAG Controller Ready. DB Path: {vector_db_path}")

    def _generate_search_queries(self, jd_text: str) -> List[str]:
        print("DEBUG: Generating search queries...")
        structured_llm = self.llm.with_structured_output(SearchQueries)
        prompt = ChatPromptTemplate.from_template("Extract 3 search keywords for: {jd}")
        chain = prompt | structured_llm
        result = chain.invoke({"jd": jd_text})
        print(f"DEBUG: Queries generated: {result.queries}")
        return result.queries

    def _retrieve_documents(self, queries: List[str], resume_filename: str) -> List[Document]:
        print(f"DEBUG: Retrieving documents for {resume_filename}...")
        unique_docs = {}
        clean_filename = os.path.basename(resume_filename)
        
        for query in queries:
            docs = self.vector_store.similarity_search(
                query, 
                k=4,
                filter={"source": clean_filename} 
            )
            for doc in docs:
                unique_docs[doc.page_content] = doc
        
        found_docs = list(unique_docs.values())
        print(f"DEBUG: Found {len(found_docs)} unique chunks.")
        return found_docs

    def _analyze_fit(self, jd_text: str, documents: List[Document], resume_filename: str) -> MatchAnalysis:
        print("DEBUG: Analyzing fit with LLM...")
        
        if not documents:
            print("DEBUG: No documents found! Returning empty result.")
            return MatchAnalysis(
                match_score=0, 
                candidate_name=os.path.basename(resume_filename),
                summary="No data found for this specific resume. Please check ingestion.",
                key_matches=[], missing_skills=[], interview_questions=[], source_citations=[]
            )

        context = "\n\n".join([f"Content: {d.page_content}" for d in documents])
        structured_llm = self.llm.with_structured_output(MatchAnalysis)
        
        template_string = """
        You are a strict Senior Technical Recruiter.
        
        Task: Analyze the provided 'Resume Context' against the 'JD'.
        
        1. Extract the candidate's name from the context. If not found, use the filename.
        2. Calculate a Match Score (0-100) based strictly on skills and experience.
        3. Identify Key Matches and Missing Skills.
        4. Give higher scoring weightage to candidate's experience.
        
        JD: {jd}
        
        Resume Context: {context}
        """
        
        prompt = ChatPromptTemplate.from_template(template_string)
        chain = prompt | structured_llm
        
        result = chain.invoke({"jd": jd_text, "context": context})
        print("DEBUG: Analysis complete.")
        return result

    def process_application(self, jd_text: str, resume_filename: str) -> dict:
        try:
            print("--- STARTING RAG PIPELINE ---")
            queries = self._generate_search_queries(jd_text)
            docs = self._retrieve_documents(queries, resume_filename)
            analysis = self._analyze_fit(jd_text, docs, resume_filename)
            print("--- PIPELINE FINISHED SUCCESS ---")
            return analysis.model_dump()
        except Exception as e:
            print(f"CRITICAL ERROR in answer.py: {str(e)}")
            logger.error(f"RAG Error: {e}")
            raise e