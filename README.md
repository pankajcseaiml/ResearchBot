# KIT’s College of Engineering (Autonomous), Kolhapur
### Department of Computer Science & Engineering
**Course Name:** Generative and Agentic AI Lab  
**Course Code:** UAMPC0731  
**Internal PoE A.Y. 2026-2027**  
**CO: 3 | BL: 5 | Conduction Date: Oct 2026**  
**Assignment No. 10:** Medical Healthcare & Research Analyst Agents — GenAI & ML DevOps Lab — Containerization  
*(Medical Healthcare for Even roll numbers | Research Analyst Agents for Odd roll numbers)*

---

# ResearchBot — Multi-Agent Research Analyst 🔬

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io)
[![Agno Framework](https://img.shields.io/badge/Agno-TeamMode.coordinate-orange.svg)](https://agno.com)
[![Groq API](https://img.shields.io/badge/Groq-LLaMA--3.3--70B-purple.svg)](https://console.groq.com)
[![Docker](https://img.shields.io/badge/Docker-Multi--Container-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Cloud--Native-326CE5.svg)](https://kubernetes.io/)
[![Helm](https://img.shields.io/badge/Helm-v3-0F1689.svg)](https://helm.sh/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)](https://pytest.org)

**ResearchBot** is a production-ready, multi-agent research guidance and analysis assistant designed for undergraduate **GenAI & ML DevOps coursework**. It coordinates a three-agent team using the **Agno framework** (`TeamMode.coordinate`), **FastAPI**, and the **Groq API** (running fast open-weight models such as LLaMA 3.3 70B), accompanied by both a clean **single-page HTML/CSS/JS frontend** and a modern **Streamlit web interface**.

The system accepts a research inquiry, classifies and scopes the question, retrieves grounded evidence strictly from a curated local research corpus, cross-examines all findings, and synthesizes an 8-section structured Markdown report with source citations and a mandatory educational disclaimer.

---

## 🏛️ Multi-Agent Architecture

ResearchBot coordinates exactly **three collaborating agents** via Agno's `Team` framework in sequential coordinate mode (`TeamMode.coordinate`):

```
+-----------------------------------------------------------------+
|                       User Research Query                       |
+--------------------------------+--------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------+
|                       Agno Research Team                        |
|                     (TeamMode.coordinate)                       |
|                                                                 |
|  1. Research Query Analyzer                                     |
|     - Classifies research domain (AI, ML, Cloud, Security, etc.)|
|     - Extracts objectives, core issues, and constraints         |
|     - Formulates targeted retrieval keywords                    |
|                                                                 |
|                                v                                |
|  2. Research & Analysis Agent                                   |
|     - Invokes `search_research_library` tool                    |
|     - Grounded in curated local research corpus                 |
|     - Extracts empirical findings, trade-offs, and benchmarks   |
|     - Attributes citations to document IDs (e.g., sample-rag-001)|
|                                                                 |
|                                v                                |
|  3. Research Answer Reviewer                                    |
|     - Cross-examines all claims against retrieved evidence      |
|     - Strips unsupported / hallucinated assertions              |
|     - Formats final 8-section verified Markdown report          |
|     - Enforces educational disclaimer                           |
+--------------------------------+--------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------+
|                     Final Reviewed Answer                       |
|  1. Research Classification       5. Analysis & Interpretation  |
|  2. Executive Summary             6. Limitations & Gaps         |
|  3. Research Findings             7. Conclusion                 |
|  4. Evidence & Source Analysis    8. Consulted Sources          |
|  + Mandatory Educational Disclaimer                             |
+-----------------------------------------------------------------+
```

### Member Agents
1. **Research Query Analyzer**: Breaks down user inquiries into distinct domains (e.g., AI/ML, Cloud Computing, Cybersecurity, MLOps, Data Privacy) and frames precise research objectives.
2. **Research & Analysis Agent**: Calls the `search_research_library` tool to investigate sample materials and technical benchmarks to ground findings.
3. **Research Answer Reviewer**: Audits claims against available evidence, eliminates speculative assertions, ensures prudent phrasing, and formats verified guidance.

---

## 📁 Project Structure

```
ResearchBot/
├── .env.example              # Template for environment configuration
├── .gitignore                # Git exclusions (prevents committing secrets)
├── .dockerignore             # Docker build context exclusions
├── requirements.txt          # Python project dependencies
├── README.md                 # Project documentation and student guide
├── Dockerfile                # Optimized, non-root, slim container definition
├── docker-compose.yml        # Local multi-container orchestration (FastAPI + Streamlit)
├── compose.yaml              # Docker Compose v2 specification alias
├── streamlit_app.py          # Option A: Streamlit Web UI interface
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD: Automated Pytest, Docker Build, & K8s/Helm lint
├── k8s/                      # Cloud-Native Kubernetes Manifests
│   ├── configmap.yaml        # Application runtime settings
│   ├── secret.yaml           # API key secret template
│   ├── deployment.yaml       # Rolling update, probes, security context, limits
│   ├── service.yaml          # ClusterIP service definition
│   ├── ingress.yaml          # NGINX Ingress controller routing
│   ├── hpa.yaml              # HorizontalPodAutoscaler (CPU & Memory metrics)
│   └── kustomization.yaml    # Declarative Kustomize resource bundle
├── helm/
│   └── researchbot/          # Production Helm Chart
│       ├── Chart.yaml        # Chart metadata
│       ├── values.yaml       # Configurable deployment values
│       └── templates/        # Manifest templates (_helpers, deployment, service, etc.)
├── app/
│   ├── __init__.py
│   ├── config.py             # Environment variable loading & secret sanitization
│   ├── main.py               # FastAPI application (GET /, POST /ask, GET /health)
│   ├── schemas.py            # Pydantic models for request & response validation
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_team.py  # Agno Team definition and multi-agent coordination
│   │   └── tools.py          # Curated research library search tool
│   ├── data/
│   │   ├── __init__.py
│   │   └── sample_documents.py # Grounding documents (RAG, MLOps, Security, Cloud)
│   └── static/
│       ├── index.html        # Clean single-page user interface
│       ├── style.css         # Modern design system & responsive styling
│       └── app.js            # Frontend client logic & progress animation
└── tests/
    ├── __init__.py
    ├── test_health.py        # Tests for /health and / endpoints
    ├── test_validation.py    # Tests for input validation and error handling
    └── test_agents.py        # Tests for Agno agents, Team, and search tool
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, 3.13, or 3.14
- **Groq API Key**: A free key from [Groq Console](https://console.groq.com/keys)
- **Docker & Docker Compose**: For container execution
- **Kubectl & Minikube/Kind**: For cloud-native deployment

### 2. Setup Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# macOS / Linux
cp .env.example .env

# Windows PowerShell
copy .env.example .env
```

Open `.env` and configure your settings:
```ini
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
HOST=127.0.0.1
PORT=8000
REQUEST_TIMEOUT=60
MAX_QUESTION_LENGTH=5000
MAX_RESEARCH_RESULTS=5
```

---

## 💻 Running the Application

### Option A: Streamlit Frontend (Recommended UI)
Run the clean, white-themed Streamlit web interface:
```bash
streamlit run streamlit_app.py
```
Open your browser at **[http://localhost:8501](http://localhost:8501)**.

### Option B: FastAPI Backend & API Endpoints
Run the FastAPI application:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Web UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive API Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:
```bash
pytest -v
```

All **21 automated tests** run offline without incurring Groq API charges and verify:
- Health endpoint status, secret redaction, and agent registration
- Input validation (empty questions, whitespace-only, exceeding max character length)
- Graceful HTTP 503 error handling when `GROQ_API_KEY` is not configured
- Agno Team creation, member roles, and tool attachments
- Library search accuracy, multi-field scoring, and source tracking

---

## 🐳 Containerization & DevOps Implementation

As part of the **GenAI & ML DevOps Lab Assignment**, this project implements all four core competencies:

### 1. Containerization (`Dockerfile` & `.dockerignore`)
- **Base image:** Minimal `python:3.11-slim` footprint
- **Security:** Runs as non-root user `appuser` (UID 1001)
- **Layer caching:** Requirements installed before copying application source code
- **Built-in Health Check:** Automated Docker `HEALTHCHECK` probing `http://localhost:8000/health`
- **Build & Run:**
  ```bash
  docker build -t researchbot:latest .
  docker run -d -p 8000:8000 --env-file .env --name researchbot-container researchbot:latest
  ```

### 2. Local Multi-Container Orchestration (`docker-compose.yml`)
Spawns an isolated multi-service stack containing:
- **`researchbot-api`**: FastAPI multi-agent backend on port 8000 with volume mounts and resource reservations
- **`researchbot-ui`**: Streamlit frontend on port 8501, dynamically connected to the backend via an isolated bridge network
```bash
# Start both services
docker compose up -d --build

# View container logs
docker compose logs -f

# Check health and status
docker compose ps

# Teardown stack
docker compose down
```

### 3. Cloud-Native Deployment (`k8s/` & `helm/`)
#### A. Kubernetes Manifests (`k8s/`)
Deploy using Kustomize:
```bash
# Apply all manifests declaratively
kubectl apply -k k8s/

# Or apply individual manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

#### B. Helm Chart Deployment (`helm/researchbot/`)
Deploy using the production Helm chart:
```bash
# Lint the chart
helm lint helm/researchbot

# Install or upgrade release
helm upgrade --install researchbot helm/researchbot/ \
  --set secret.groqApiKey="gsk_your_actual_key"

# Verify status
kubectl get pods,svc,hpa,ingress -l app.kubernetes.io/name=researchbot
```

### 4. CI/CD Pipeline (`.github/workflows/ci.yml`)
The GitHub Actions workflow triggers automatically on push and pull requests to `main` / `master` and executes:
1. **Automated Testing**: Sets up Python 3.11 and executes the 21-test Pytest suite.
2. **Container Build Validation**: Builds the Docker image with Docker Buildx.
3. **K8s & Helm Validation**: Verifies Kustomize compilation and lints the Helm chart.

---

## 🔌 API Endpoints Specification

### 1. `GET /`
Serves the responsive single-page web application.

### 2. `GET /health`
Returns system health, active model, and agent registration status without leaking secrets:
```json
{
  "status": "healthy",
  "app_name": "ResearchBot — Multi-Agent Research & Analysis Assistant",
  "groq_configured": true,
  "model": "llama-3.3-70b-versatile",
  "agents": [
    "Research Query Analyzer",
    "Research & Analysis Agent",
    "Research Answer Reviewer"
  ],
  "research_library_available": true
}
```

### 3. `POST /ask`
Submits a query to the multi-agent team.

**Request Body:**
```json
{
  "question": "What are the latency, factual accuracy, and hallucination trade-offs in Retrieval-Augmented Generation (RAG) systems?"
}
```

**Response Body:**
```json
{
  "status": "success",
  "question": "What are the latency, factual accuracy, and hallucination trade-offs in Retrieval-Augmented Generation (RAG) systems?",
  "answer": "## 1. Research Classification\n- **Primary Domain:** Artificial Intelligence / Retrieval-Augmented Generation\n...",
  "sources": [
    "sample-rag-001 — Retrieval-Augmented Generation Overview: Architectures, Benefits, and Latency Trade-offs"
  ],
  "disclaimer": "Disclaimer: ResearchBot is an educational research and analysis assistant designed for learning and demonstration..."
}
```

---

## ⚖️ Educational Disclaimer

> **Disclaimer:** ResearchBot is an educational research and analysis assistant designed for learning and demonstration. Its output may contain mistakes, incomplete information, or outdated findings. Results are limited by the sources available to the system and do not replace independent verification, professional judgment, or consultation with qualified experts where appropriate.
