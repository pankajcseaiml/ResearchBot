"""Streamlit Web Interface for ResearchBot — Multi-Agent Research Assistant.

Designed for Generative and Agentic AI Lab (A.Y. 2026-2027)
Department of Computer Science & Engineering, KIT's College of Engineering (Autonomous), Kolhapur.
"""

import os
import time
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="ResearchBot — Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Custom Styling (Clean Modern Minimalist Theme)
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .badge-course {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background: #e0f2fe;
        color: #0369a1;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .agent-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 0.9rem;
        margin-bottom: 0.6rem;
    }
    .agent-title {
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .agent-desc {
        font-size: 0.85rem;
        color: #64748b;
    }
    .disclaimer-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 0.85rem 1rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        color: #92400e;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    '<span class="badge-course">KIT College of Engineering • CSE Dept • Generative & Agentic AI Lab (UAMPC0731)</span>',
    unsafe_allow_html=True,
)
st.markdown('<div class="main-title">🔬 ResearchBot — Multi-Agent Research Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Assignment No. 10 — Research Analyst Agents | Coordinated Multi-Agent Architecture powered by FastAPI, Agno Framework, and Groq</div>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    
    # Check backend health
    backend_healthy = False
    system_info = {}
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if resp.status_code == 200:
            system_info = resp.json()
            backend_healthy = True
            st.success("● FastAPI Backend Online")
        else:
            st.warning("Backend returned non-200 status")
    except Exception:
        st.error(f"● Backend Unreachable ({BACKEND_URL})")

    st.markdown("---")
    st.subheader("🏛️ Multi-Agent Architecture")
    st.caption("Sequential coordination via Agno `TeamMode.coordinate`")

    st.markdown(
        """
        <div class="agent-box">
            <div class="agent-title">1. Query Analyzer</div>
            <div class="agent-desc">Decomposes inquiries, classifies research domains, and extracts material keywords.</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">2. Research Agent</div>
            <div class="agent-desc">Invokes <code>search_research_library</code> on curated corpus, extracting grounded evidence.</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">3. Answer Reviewer</div>
            <div class="agent-desc">Audits claims against evidence, strips unsupported assertions, and formats the 8-section report.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("💡 Sample Inquiries")
    sample_queries = [
        "What are the latency, factual accuracy, and hallucination trade-offs in Retrieval-Augmented Generation (RAG)?",
        "Explain Zero Trust architecture principles, continuous verification, and micro-segmentation benchmarks.",
        "How do concept drift and data drift monitoring operate in production MLOps pipelines?",
        "Compare differential privacy mechanisms and federated learning trade-offs for sensitive data.",
    ]

    selected_sample = st.selectbox(
        "Choose a sample question to populate:",
        ["-- Select a sample --"] + sample_queries,
    )

# Main Application Form
default_text = selected_sample if selected_sample != "-- Select a sample --" else ""

with st.form("research_form", clear_on_submit=False):
    st.subheader("Enter Research Investigation Query")
    user_query = st.text_area(
        label="Research Question",
        value=default_text,
        placeholder="e.g. What are the key advantages and architectural trade-offs of Retrieval-Augmented Generation?",
        height=120,
        help="Enter a research inquiry. The multi-agent team will classify, retrieve local grounded evidence, audit citations, and deliver a structured report.",
    )
    submitted = st.form_submit_button("🚀 Submit to Multi-Agent Team", use_container_width=True)

if submitted:
    if not user_query.strip():
        st.warning("Please enter a research question before submitting.")
    else:
        st.info("Initiating 3-agent coordination pipeline...")

        # Progress simulation and step tracker
        progress_bar = st.progress(15)
        status_text = st.empty()

        status_text.text("Step 1/3: Research Query Analyzer is classifying domain and extracting objectives...")
        time.sleep(0.4)
        progress_bar.progress(40)

        status_text.text("Step 2/3: Research & Analysis Agent is querying the local curated research library...")
        time.sleep(0.4)
        progress_bar.progress(70)

        status_text.text("Step 3/3: Research Answer Reviewer is verifying claims against retrieved evidence...")

        # Send request to FastAPI backend
        start_time = time.time()
        try:
            resp = requests.post(
                f"{BACKEND_URL}/ask",
                json={"question": user_query.strip()},
                timeout=90,
            )
            elapsed = round(time.time() - start_time, 2)
            progress_bar.progress(100)
            status_text.empty()

            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ Research completed successfully in {elapsed}s")

                # Display Results
                tab1, tab2, tab3 = st.tabs(["📄 Structured Research Report", "📚 Consulted Sources", "ℹ️ Raw Response"])

                with tab1:
                    st.markdown(data.get("answer", "No answer generated."))

                with tab2:
                    sources = data.get("sources", [])
                    if sources:
                        st.subheader("Consulted Local Library Evidence")
                        for s in sources:
                            st.markdown(f"- **{s}**")
                    else:
                        st.write("No matching documents from the local library were cited.")

                with tab3:
                    st.json(data)

                # Mandatory Disclaimer
                disclaimer = data.get(
                    "disclaimer",
                    "Disclaimer: ResearchBot provides educational and informational guidance only."
                )
                st.markdown(
                    f'<div class="disclaimer-box">⚠️ <strong>Notice:</strong> {disclaimer}</div>',
                    unsafe_allow_html=True,
                )

            elif resp.status_code == 503:
                data = resp.json()
                st.error(f"⚠️ Service Unavailable: {data.get('message', 'Groq API Key not configured')}")
                st.info("Tip: Ensure `GROQ_API_KEY` is set in your `.env` file or container environment.")
            else:
                data = resp.json() if resp.headers.get("content-type") == "application/json" else {"message": resp.text}
                st.error(f"Error {resp.status_code}: {data.get('message', 'An error occurred during research.')}")

        except requests.exceptions.ConnectionError:
            progress_bar.progress(100)
            status_text.empty()
            st.error(
                f"Could not connect to FastAPI backend at `{BACKEND_URL}`. "
                "Please ensure the backend is running (`uvicorn app.main:app` or `docker-compose up`)."
            )
        except requests.exceptions.Timeout:
            progress_bar.progress(100)
            status_text.empty()
            st.error("Request timed out. The multi-agent workflow took longer than the configured timeout.")
        except Exception as ex:
            progress_bar.progress(100)
            status_text.empty()
            st.error(f"An unexpected error occurred: {str(ex)}")

# Footer
st.markdown("---")
st.caption(
    "KIT’s College of Engineering (Autonomous), Kolhapur | "
    "Course: Generative and Agentic AI Lab (UAMPC0731) | Internal PoE A.Y. 2026-2027"
)
