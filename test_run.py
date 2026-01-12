import os
import json
import logging
from ingestion import IngestionPipeline
from answer import RAGController
from config import DB_PATH, COLLECTION_NAME, RESUME_DIR

# Configure logging to see what's happening under the hood
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("TestRunner")

# ==========================================
# 1. The Sample Job Description (Designed to test Gaps & Matches)
# ==========================================
SAMPLE_JD = """
JOB TITLE: Junior Data Scientist / Analyst

ABOUT THE ROLE:
We are looking for a data professional to join our FinTech security team. 
You will be responsible for building dashboards and detecting anomalies in financial transactions.

REQUIREMENTS:
1.  **Core Tech:** Strong proficiency in Python and SQL is a must.
2.  **Visualization:** Experience with Power BI or Tableau to visualize loan/financial data.
3.  **Domain Knowledge:** Experience with Malware Detection, Fraud Analysis, or Security Systems is highly preferred.
4.  **Cloud Skills:** Must have experience with AWS (Amazon Web Services).
5.  **Experience:** Minimum 2 years of full-time industry experience required.

NICE TO HAVE:
- Experience with "YOLO" algorithms or Computer Vision.
- Knowledge of Snowflake.
"""

def run_test():
    print("\n" + "="*50)
    print("🚀 STARTING END-TO-END RAG TEST")
    print("="*50 + "\n")

    # ---------------------------------------------------------
    # STEP 1: INGESTION (Simulating the 'Upload' phase)
    # ---------------------------------------------------------
    print("📂 PHASE 1: Running Ingestion Pipeline...")
    
    # Initialize the pipeline pointing to your 'data' folder
    ingestor = IngestionPipeline(
        source_dir=RESUME_DIR,
        db_path=DB_PATH,
        collection_name=COLLECTION_NAME
    )
    
    # Run ingestion (using reset_db=True to ensure a clean test)
    ingestor.run(reset_db=True)
    print("✅ Ingestion Complete. Resume vectors stored in ChromaDB.")

    # ---------------------------------------------------------
    # STEP 2: RAG ANALYSIS (Simulating the 'Recruiter' phase)
    # ---------------------------------------------------------
    print("\n🧠 PHASE 2: Running RAG Logic...")
    
    # Initialize the RAG Controller
    rag = RAGController(vector_db_path=DB_PATH)
    
    # Run the analysis
    # Note: resume_id is used for filtering. If your ingestor saves metadata 
    # as 'Mohit_Resume.pdf', pass that filename.
    result = rag.process_application(
        jd_text=SAMPLE_JD
    )

    # ---------------------------------------------------------
    # STEP 3: DISPLAY RESULTS
    # ---------------------------------------------------------
    print("\n📊 PHASE 3: ANALYSIS RESULTS")
    print("="*50)
    
    # Pretty print the JSON output
    print(json.dumps(result, indent=2))
    
    # Specific Checks to verify "Intelligence"
    print("\n" + "="*50)
    print("🕵️  AUTO-VERIFICATION CHECKS")
    print("="*50)
    
    score = result.get("match_score", 0)
    missing = result.get("missing_critical_skills", [])
    strengths = result.get("key_strengths", [])
    
    # Check 1: Did it find the Malware Project? (Match)
    has_malware = any(x in str(strengths).upper() for x in ["MALWARE", "YOLO"])
    print(f"[*] Detection of 'Malware/YOLO' Skill: {'✅ PASS' if has_malware else '❌ FAIL'}")

    # Check 2: Did it catch the AWS Gap? (Resume has Azure, JD wants AWS)
    has_aws_gap = any("AWS" in m.upper() for m in missing) # Handles "AWS (Amazon...)"
    print(f"[*] Detection of 'AWS' Gap:             {'✅ PASS' if has_aws_gap else '❌ FAIL'}")

    # Check 3: Did it catch the Experience Gap? (Resume is Intern, JD wants 2 Years)
    has_exp_gap = score < 100 and any("experience" in m.lower() for m in missing)
    print(f"[*] Detection of 'Experience' Gap:      {'✅ PASS' if has_exp_gap else '⚠️  WARNING (Score too high?)'}")

if __name__ == "__main__":
    run_test()