# AI Contract Risk Analyzer — Enterprise SaaS

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C.svg?style=flat)](https://www.langchain.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4.svg?style=flat&logo=google)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6600.svg?style=flat)](https://www.trychroma.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

An enterprise-grade, portfolio-ready full-stack AI SaaS application that ingests legal contracts (PDF or DOCX) and automatically analyzes them using Large Language Models (Google Gemini 1.5 Flash), LangChain, and Retrieval-Augmented Generation (RAG) with ChromaDB.

---

## 🌟 Key Features

- **Upload & Text Extraction**: Accepts PDF and DOCX documents with page number and section metadata tracking using PyMuPDF and `python-docx`.
- **RAG Vector Database Pipeline**: Chunks documents recursively (`RecursiveCharacterTextSplitter`), generates semantic embeddings (`text-embedding-004`), and indexes them in ChromaDB.
- **12-Clause Risk Detection**: Evaluates 12 critical commercial clause categories:
  - Termination Clause
  - Confidentiality
  - Auto Renewal
  - Payment Terms
  - Unlimited Liability
  - Indemnification
  - Non-Compete
  - Intellectual Property
  - Force Majeure
  - Governing Law
  - Dispute Resolution
  - Jurisdiction
- **Structured Risk Scoring & Summaries**: Computes numeric contract risk score (0–100), overall risk severity (Low / Medium / High), executive summaries, missing clauses, and mitigation recommendations.
- **Interactive Contract RAG Chatbot**: Scoped document Q&A with exact source paragraph citations, confidence scores, and page references.
- **Executive PDF Report Export**: Compiles professional downloadable PDF risk assessment reports with ReportLab.
- **JWT Authentication & RBAC**: Secure user registration, password hashing (PBKDF2/SHA-256), bearer tokens, and admin capabilities.
- **Analytics & Admin Dashboard**: Real-time risk distribution metrics, clause frequencies, system storage tracking, and audit logs.
- **Modern React 18 UI**: Glassmorphism design system built with React 18, TypeScript, Vite, Tailwind CSS, and Lucide Icons.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────────────────────────────────────┐
                                  │                React 18 + TypeScript Frontend             │
                                  │   (Vite + Tailwind CSS + Lucide Icons + Framer Motion) │
                                  └─────────────────────────────┬────────────────────────────┘
                                                                │ REST / JSON (Axios)
                                  ┌─────────────────────────────▼────────────────────────────┐
                                  │                   FastAPI Backend API                    │
                                  │  - Auth (JWT / bcrypt)                                   │
                                  │  - Contract Upload & Text Extraction                     │
                                  │  - RAG Engine (LangChain + Gemini + ChromaDB)            │
                                  │  - Risk Analysis Engine (12 Clause Types)                │
                                  │  - Q&A Chatbot with Source Citations                     │
                                  │  - PDF Report Generator                                  │
                                  │  - Analytics & Admin Endpoints                           │
                                  └───┬──────────────────────────┬───────────────────────────┘
                                      │                          │
                      ┌───────────────▼──────────────┐  ┌────────▼────────────────┐
                      │    Database (SQLAlchemy)     │  │  ChromaDB Vector Store │
                      │  Users, Contracts, Analysis, │  │  Semantic Embeddings   │
                      │  Audit Logs, Chat History    │  │  & Text Chunks         │
                      └──────────────────────────────┘  └────────────────────────┘
```

---

## 📁 Repository Structure

```
ai-contract-risk-analyzer/
├── backend/
│   ├── api/
│   │   ├── routes/          # Auth, Upload, Analyze, Contracts, Chat, Analytics, Admin
│   │   └── dependencies.py  # JWT validation, DB sessions, current_user
│   ├── database/            # SQLAlchemy engine, session maker, ORM models
│   ├── services/            # Auth, Document Extraction, Analysis, PDF Report, Analytics
│   ├── rag/                 # Chunker, Embeddings, Vector Store, LangChain RAG pipeline
│   ├── models/              # Request & Response Pydantic schemas
│   ├── utils/               # Security, Logging, Exceptions, Text Extractor
│   ├── config.py            # Application settings (pydantic-settings)
│   └── main.py              # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Sidebar, RiskBadge, LoadingSkeleton
│   │   ├── context/         # AuthContext, ThemeContext
│   │   ├── pages/           # Landing, Login, Register, Dashboard, Upload, Detail, Chat, Analytics, Admin
│   │   ├── services/        # Axios API client
│   │   └── types/           # TypeScript interface definitions
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Google Gemini API Key (get free at [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Backend Setup

```bash
# Navigate to project root
cd ai-contract-risk-analyzer

# Create virtual environment
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Set your Gemini API Key in .env:
# GOOGLE_API_KEY=your_actual_api_key_here

# Run backend FastAPI server
uvicorn backend.main:app --reload --port 8000
```
Backend API interactive Swagger docs available at: `http://localhost:8000/docs`

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🐳 Docker Deployment

To launch the full-stack system in Docker:

```bash
# From project root
docker-compose -f docker/docker-compose.yml up --build
```
Access Frontend at `http://localhost:5173` and Backend API at `http://localhost:8000`.

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Authenticate & get JWT bearer token |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `POST` | `/api/v1/upload` | Upload & index PDF/DOCX contract |
| `POST` | `/api/v1/analyze` | Execute 12-clause risk analysis |
| `GET` | `/api/v1/contracts` | List user's contracts |
| `DELETE` | `/api/v1/contracts/{id}` | Delete contract from DB & vector store |
| `GET` | `/api/v1/contracts/{id}/report` | Download executive PDF report |
| `POST` | `/api/v1/chat` | RAG Q&A with source paragraph citations |
| `GET` | `/api/v1/analytics` | Dashboard metrics & risk breakdown |
| `GET` | `/api/v1/admin/stats` | System health & audit logs |
| `GET` | `/health` | Health check endpoint |

---

## 📄 License
MIT License. Built for portfolio & demonstration purposes.
