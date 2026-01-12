# 🤖 AI Recruiter Co-Pilot (RAG-Based Candidate Screening)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-REST%20API-green)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-Chroma-red)

**An intelligent, RAG-powered recruitment assistant that automates resume screening, detects skill gaps, and generates technical interview questions based on Job Descriptions (JDs).**

---

## 🚀 Overview

The **AI Recruiter Co-Pilot** is a full-stack Retrieval-Augmented Generation (RAG) application designed to simulate a Senior Technical Recruiter. unlike basic keyword matchers, this system "reasons" about a candidate's profile.

It performs a **semantic gap analysis** to identify:
1.  **True Matches:** (e.g., "Malware Detection" project matches "Cybersecurity" requirement).
2.  **Critical Gaps:** (e.g., "Azure" experience does NOT satisfy an "AWS" requirement).
3.  **Seniority Mismatches:** (e.g., Penalizes a Fresher applying for a Senior role).

---

## ⚡ Key Features

* **📄 Smart Ingestion Pipeline:** * Converts PDF Resumes into semantic chunks.
    * Uses **LLM-based Semantic Chunking** to preserve context (headers, projects, dates).
* **🧠 Advanced RAG Logic:**
    * **Strict Filtering:** Automatically penalizes candidates who lack required years of experience.
    * **Hallucination Checks:** Ensures cited skills actually exist in the resume context.
* **🎯 Interactive UI:**
    * Modern, Glassmorphism-based dashboard.
    * Real-time "Upload & Ingest" functionality.
* **📊 Structured Analysis:**
    * Returns a **Match Score (0-100%)**.
    * Highlights **✅ Key Matches** vs **⚠️ Critical Gaps**.
    * Generates **3-5 Tailored Interview Questions**.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Flask (Python) | REST API architecture serving JSON responses. |
| **Orchestration** | LangChain | Manages the RAG pipeline, prompts, and retrieval. |
| **LLM** | GPT-4o-mini | Used for reasoning, extraction, and structured JSON output. |
| **Embeddings** | text-embedding-3-large | High-dimensional vector embeddings for accurate retrieval. |
| **Vector DB** | ChromaDB | Local vector store for persisting resume chunks. |
| **Frontend** | HTML5 / CSS3 / JS | Responsive, modern UI with Fetch API integration. |

---

## 📂 Project Structure

```bash
Pro_RAG/
│
├── app.py                # Flask Server (API Routes)
├── answer.py             # RAG Controller (The "Brain")
├── ingestion.py          # PDF Loader & Semantic Chunker
├── config.py             # Central Configuration (Paths, Models)
│
├── chroma_db/            # Vector Database (Auto-generated)
├── resumes/              # Raw PDF Storage
│
├── static/
│   ├── css/style.css     # Modern styling (Glassmorphism)
│   └── js/script.js      # Frontend Logic (API calls)
│
└── templates/
    └── index.html        # Main Dashboard UI
