"""Curated sample research documents for demonstration, retrieval, and testing.

Each document is clearly marked as an educational demonstration document.
The corpus covers AI/ML, RAG & LLMs, Cloud/Software Engineering, Cybersecurity,
Research Methodology, and Sustainability/Business Innovation.
"""

from typing import Any, Dict, List

SAMPLE_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "id": "sample-rag-001",
        "title": "Retrieval-Augmented Generation Overview: Architectures, Benefits, and Latency Trade-offs",
        "category": "Retrieval-Augmented Generation and Large Language Models",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-rag-001)",
        "keywords": ["rag", "retrieval-augmented generation", "vector database", "dense retrieval", "embeddings", "hallucination", "latency"],
        "content": (
            "Retrieval-Augmented Generation (RAG) is an architectural framework that enhances Large Language Model (LLM) "
            "responses by retrieving authoritative factual evidence from external knowledge stores before generating text. "
            "In modern RAG architectures, documents are segmented into semantic chunks, converted into dense vector embeddings, "
            "and indexed within specialized vector databases such as Qdrant, Milvus, or FAISS. When a user issues a prompt, "
            "the system performs similarity search using distance metrics (e.g., cosine similarity) to extract top-k context passages.\n\n"
            "The primary benefit of RAG is a demonstrable reduction in factual hallucinations: empirical evaluations in enterprise Q&A "
            "benchmarks indicate an average 42% decrease in fabricated citations and unsupported statements compared to parametric-only models. "
            "Furthermore, RAG systems eliminate the need for frequent, computationally prohibitive fine-tuning by allowing real-time "
            "updates to the knowledge corpus.\n\n"
            "However, RAG introduces tangible system trade-offs. The retrieval step and subsequent context stuffing increase end-to-end "
            "inference latency by 120ms to 250ms per request. Furthermore, retrieval degradation occurs when queries are lexically ambiguous, "
            "or when vector embeddings fail to capture subtle domain distinctions. Hybrid retrieval—combining dense vector search with "
            "traditional BM25 sparse keyword ranking—has emerged as the leading mitigation to boost retrieval recall across complex queries."
        ),
    },
    {
        "id": "sample-rag-002",
        "title": "Mitigating Chunk Boundary Fragmentation and Re-Ranking in Advanced RAG Pipelines",
        "category": "Retrieval-Augmented Generation and Large Language Models",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-rag-002)",
        "keywords": ["chunking", "re-ranking", "rag", "cross-encoder", "semantic drift", "context window"],
        "content": (
            "Naïve chunking strategies in RAG—such as fixed character length splitting—frequently cause semantic fragmentation, "
            "where critical contextual clauses are split across boundary lines. Advanced RAG pipelines address this by implementing "
            "hierarchical chunking (parent-child documents) and semantic chunking based on embedding distance shifts between sentences.\n\n"
            "Integrating a secondary Cross-Encoder re-ranker (e.g., Cohere Rerank or BGE-Reranker) significantly improves precision-at-k. "
            "While bi-encoder embeddings permit rapid approximate nearest neighbor search over millions of vectors, cross-encoders compute "
            "direct token-level cross-attention between question and passage, boosting Top-3 precision from 68% to 84% in multi-hop reasoning tasks.\n\n"
            "The trade-off lies in compute overhead: cross-encoder scoring adds 40ms to 90ms of compute per re-ranking candidate batch. "
            "System designers must strike a balance between candidate pool size (typically 20-50 retrieved candidates) and final re-ranked passages (3-5 items)."
        ),
    },
    {
        "id": "sample-llm-001",
        "title": "Large Language Models: Foundational Architectures, Alignment, and Prompt Optimization",
        "category": "Artificial Intelligence and Machine Learning",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-llm-001)",
        "keywords": ["llm", "transformer", "attention mechanism", "alignment", "rlhf", "prompt engineering", "few-shot"],
        "content": (
            "Large Language Models based on the decoder-only Transformer architecture (such as the LLaMA and GPT model families) "
            "utilize self-attention mechanisms to model complex linguistic dependencies across extensive context windows. "
            "Training typically proceeds in two core phases: self-supervised pre-training on trillions of tokens to learn world knowledge, "
            "followed by post-training alignment through Reinforcement Learning from Human Feedback (RLHF) or Direct Preference Optimization (DPO).\n\n"
            "Alignment guides models toward helpful, harmless, and honest behavior. While RLHF prevents obvious safety violations, "
            "it can induce 'sycophancy'—where the model falsely agrees with user misconceptions—and 'mode collapse' on creative tasks. "
            "Prompt engineering techniques such as Chain-of-Thought (CoT) and structured few-shot examples measurably improve reasoning "
            "benchmarks by decomposing complex multi-step deductions into verifiable intermediate stages."
        ),
    },
    {
        "id": "sample-ai-001",
        "title": "Explainable Artificial Intelligence: Interpretability, Bias Audits, and Model Transparency",
        "category": "Artificial Intelligence and Machine Learning",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-ai-001)",
        "keywords": ["xai", "explainable ai", "shap", "lime", "bias", "fairness", "model interpretability"],
        "content": (
            "Explainable Artificial Intelligence (XAI) focuses on creating methods that enable human engineers and domain experts "
            "to understand, trust, and audit machine learning predictions. Post-hoc interpretability frameworks like SHAP (SHapley Additive exPlanations) "
            "and LIME (Local Interpretable Model-agnostic Explanations) approximate feature contributions for individual decisions.\n\n"
            "In high-stakes domains including healthcare diagnostics, criminal justice, and loan origination, explainability is a legal "
            "and ethical necessity. Algorithmic bias audits demonstrate that unconstrained models often perpetuate historical demographic "
            "disparities present in training datasets. Limitations of current XAI tools include computational complexity on large feature spaces "
            "and susceptibility to adversarial manipulation, where explanation weights are perturbed without altering the underlying prediction."
        ),
    },
    {
        "id": "sample-mlops-001",
        "title": "Machine Learning Operations (MLOps): Continuous Delivery and Concept Drift Detection in Production",
        "category": "Data Analysis and Research Methodology",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-mlops-001)",
        "keywords": ["mlops", "data drift", "concept drift", "feature store", "model monitoring", "ci/cd", "continuous training"],
        "content": (
            "Machine Learning Operations (MLOps) establishes disciplined engineering practices for operationalizing machine learning models. "
            "Unlike traditional software deployment, ML systems degrade silently due to data drift (statistical distribution changes in input features) "
            "and concept drift (shifts in the statistical relationship between features and target labels).\n\n"
            "Robust MLOps pipelines employ statistical tests—such as the Kolmogorov-Smirnov test and Population Stability Index (PSI)—to monitor "
            "incoming production data streams in real time. Continuous training (CT) loops automatically trigger model retraining and validation "
            "upon drift detection. Centralized feature stores guarantee feature consistency between training time and real-time inference, "
            "mitigating train-serve skew which accounts for over 30% of production ML outages."
        ),
    },
    {
        "id": "sample-se-001",
        "title": "Microservices vs. Serverless Architectures: Resilience, Cold Starts, and Operational Costs",
        "category": "Software Engineering and Cloud Computing",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-se-001)",
        "keywords": ["microservices", "serverless", "cloud computing", "cold start", "resilience", "kubernetes", "faas"],
        "content": (
            "The choice between containerized microservices (typically managed on Kubernetes) and serverless function-as-a-service (FaaS) "
            "involves critical trade-offs between architectural control, resource utilization, and operational overhead.\n\n"
            "Serverless platforms provide automatic scaling from zero to thousands of concurrent instances with zero idle server cost, "
            "making them ideal for spiky, event-driven workloads. However, serverless applications suffer from cold starts (latency spikes "
            "of 200ms to 3s when spinning up new runtime containers) and strict execution time limits (typically 15 minutes).\n\n"
            "Conversely, containerized microservices deployed across Kubernetes clusters offer deterministic sub-millisecond network latency, "
            "custom hardware accelerators (GPUs), and complex stateful orchestration. Their primary drawbacks are significant base infrastructure "
            "costs and the substantial operational complexity of managing ingress controllers, service meshes, and cluster upgrades."
        ),
    },
    {
        "id": "sample-cloud-001",
        "title": "Cloud-Native DevOps: CI/CD Pipelines, Infrastructure as Code, and Container Security",
        "category": "Software Engineering and Cloud Computing",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-cloud-001)",
        "keywords": ["devops", "ci/cd", "infrastructure as code", "terraform", "docker", "container security", "helm"],
        "content": (
            "Cloud-native DevOps integrates automated software delivery pipelines with declarative Infrastructure as Code (IaC) "
            "using tools such as Terraform and Kubernetes manifests. Immutable infrastructure patterns dictate that production containers "
            "and virtual machines are never modified in place; updates require building and deploying fresh container images.\n\n"
            "Container security in modern CI/CD incorporates static application security testing (SAST), software bill of materials (SBOM) "
            "generation, and container image vulnerability scanning with tools like Trivy. Implementing non-root user execution, read-only "
            "root filesystems, and strict Linux capability dropping drastically restricts the blast radius of container escape exploits."
        ),
    },
    {
        "id": "sample-sec-001",
        "title": "Zero Trust Cybersecurity Architectures: Identity-Driven Defense and Micro-Segmentation",
        "category": "Cybersecurity and Privacy",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-sec-001)",
        "keywords": ["zero trust", "cybersecurity", "micro-segmentation", "least privilege", "identity verification", "mfa"],
        "content": (
            "The Zero Trust cybersecurity paradigm operates under the core principle of 'never trust, always verify'. Traditional "
            "perimeter-based defenses (castle-and-moat models) assume that internal network traffic is inherently benign. Zero Trust "
            "replaces this assumption with continuous mutual TLS authentication, context-aware access policies, and strict least-privilege permissions.\n\n"
            "Key pillars of Zero Trust include network micro-segmentation, software-defined perimeters (SDP), and multi-factor authentication (MFA). "
            "By segmenting workloads down to individual service boundaries, lateral movement by malicious adversaries is constrained during a breach. "
            "Organizational challenges in adopting Zero Trust include legacy system incompatibility and the overhead of maintaining granular access control policies."
        ),
    },
    {
        "id": "sample-priv-001",
        "title": "Privacy-Preserving Machine Learning: Differential Privacy and Federated Learning",
        "category": "Cybersecurity and Privacy",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-priv-001)",
        "keywords": ["privacy", "differential privacy", "federated learning", "data protection", "gdpr", "cryptography"],
        "content": (
            "Privacy-Preserving Machine Learning (PPML) reconciles data-driven model utility with personal privacy guarantees under regulations "
            "such as GDPR and HIPAA. Federated Learning allows decentralized edge clients to collaboratively train a shared global model without "
            "transmitting raw private datasets to a central server; only gradient updates are exchanged.\n\n"
            "However, raw gradients remain vulnerable to model inversion and membership inference attacks. Differential Privacy (DP) solves this "
            "by injecting calibrated mathematical noise (e.g., Gaussian or Laplacian mechanisms) into the gradient aggregation step, providing "
            "a formal mathematical privacy budget (epsilon, delta). The central research challenge is the privacy-utility trade-off: higher privacy "
            "budgets protect individual participant identities but can introduce accuracy degradation of 3% to 8% on complex classification tasks."
        ),
    },
    {
        "id": "sample-data-001",
        "title": "Empirical Research Methodologies in Computer Science: Statistical Rigor and Reproducibility",
        "category": "Data Analysis and Research Methodology",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-data-001)",
        "keywords": ["research methodology", "statistical rigor", "reproducibility", "hypothesis testing", "p-value", "benchmarking"],
        "content": (
            "Rigorous empirical research in computer science demands strict experimental design, statistical significance testing, "
            "and reproducibility standards. Common methodological pitfalls include p-hacking, selective reporting of benchmark results, "
            "and failure to account for hardware variance or non-deterministic floating-point operations in deep learning runs.\n\n"
            "Best practices advocate pre-registering research hypotheses, reporting confidence intervals alongside effect sizes (Cohen's d), "
            "and conducting non-parametric tests (such as the Wilcoxon signed-rank test) when normality assumptions are violated. "
            "Replication packages featuring containerized runtime environments, deterministic random seeds, and open datasets are "
            "increasingly mandated by leading peer-reviewed venues to combat the ongoing reproducibility crisis."
        ),
    },
    {
        "id": "sample-sust-001",
        "title": "Sustainable Computing: Energy Efficiency, Carbon-Aware Scheduling, and Hardware Lifecycles",
        "category": "Sustainability, Technology, and Business Innovation",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-sust-001)",
        "keywords": ["sustainability", "green computing", "carbon-aware scheduling", "energy efficiency", "data center", "emissions"],
        "content": (
            "The exponential expansion of generative AI models and hyper-scale data centers has elevated sustainable computing into "
            "a critical engineering discipline. Data center energy consumption currently accounts for approximately 1.5% to 2% of global electricity use, "
            "with cooling and compute representing the major power sinks.\n\n"
            "Carbon-aware workload schedulers optimize computational jobs by dynamically shifting non-urgent batch processing (such as model retraining) "
            "to geographical regions or time windows when local renewable energy generation (wind and solar) is at peak capacity. At the software level, "
            "model quantization (FP16 to INT8 or INT4) and sparse attention mechanisms reduce inference energy consumption by up to 60% without "
            "significant loss of predictive fidelity."
        ),
    },
    {
        "id": "sample-biz-001",
        "title": "Technology Innovation and Digital Transformation: Business Agility, ROI, and Risk Management",
        "category": "Sustainability, Technology, and Business Innovation",
        "source": "ResearchBot Curated Educational Corpus — Demonstration Library (sample-biz-001)",
        "keywords": ["business innovation", "digital transformation", "roi", "risk management", "agility", "enterprise tech"],
        "content": (
            "Enterprise digital transformation requires aligning modern technological adoption (such as cloud migration, automation, and AI) "
            "with measurable business outcomes and rigorous risk governance frameworks. Organizations that pursue technology adoption in isolation "
            "frequently encounter organizational friction, technical debt accumulation, and negative Return on Investment (ROI).\n\n"
            "Successful transformation methodologies emphasize cross-functional product teams, continuous feedback loops, and incremental value "
            "delivery over massive multi-year waterfall deployments. Robust technology risk management incorporates supply chain dependencies, "
            "compliance audits, and business continuity planning to ensure operational resilience in volatile digital markets."
        ),
    },
]


def get_sample_documents() -> List[Dict[str, Any]]:
    """Return the complete list of curated sample research documents."""
    return list(SAMPLE_DOCUMENTS)
