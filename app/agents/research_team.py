"""Multi-Agent Research Team orchestration for ResearchBot.

Implements the three-agent architecture using Agno's Team framework and TeamMode.coordinate:
1. Research Query Analyzer: Classifies domain, objectives, and retrieval keywords.
2. Research & Analysis Agent: Searches local library, evaluates evidence, and extracts citations.
3. Research Answer Reviewer: Verifies claims, removes unsupported conclusions, and structures the final report.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from agno.agent import Agent
from agno.models.groq import Groq
from agno.team import Team, TeamMode

from app.agents.tools import search_documents, search_research_library
from app.config import (
    AGENT_NAMES,
    EDUCATIONAL_DISCLAIMER,
    get_settings,
)


class ResearchBotException(Exception):
    """Base exception for ResearchBot operations."""
    pass


class ConfigurationError(ResearchBotException):
    """Raised when required configuration or API credentials are missing."""
    pass


class UpstreamServiceError(ResearchBotException):
    """Raised when upstream Groq API encounters an error."""
    pass


class ResearchTimeoutError(ResearchBotException):
    """Raised when research execution exceeds configured timeout."""
    pass


def _check_agent_content_for_error(content: str) -> None:
    """Validate that an agent's output is not an upstream API error JSON."""
    if not content or not isinstance(content, str):
        return
    trimmed = content.strip()
    if trimmed.startswith('{"error"') or ('"error":' in trimmed and ('"message":' in trimmed or '"code":' in trimmed)):
        try:
            data = json.loads(trimmed)
            if isinstance(data, dict) and "error" in data:
                err = data["error"]
                msg = err.get("message", "Upstream model error.") if isinstance(err, dict) else str(err)
                code = err.get("code") if isinstance(err, dict) else None
                if code == "model_not_found" or "does not exist" in msg.lower():
                    raise UpstreamServiceError(
                        f"Configured model unavailable on Groq: {msg}. Please check GROQ_MODEL in your .env file."
                    )
                elif "tokens" in str(code) or "rate_limit" in str(code) or "limit" in msg.lower():
                    raise UpstreamServiceError(f"Groq API rate or token limit: {msg}")
                raise UpstreamServiceError(f"Groq upstream error: {msg}")
        except json.JSONDecodeError:
            pass


def get_agent_names() -> List[str]:
    """Return the exact registered agent names."""
    return list(AGENT_NAMES)


def get_groq_model(model_name: Optional[str] = None, api_key: Optional[str] = None) -> Groq:
    """Instantiate the Groq model provider using active settings.

    Args:
        model_name: Optional model override.
        api_key: Optional API key override.
    """
    settings = get_settings()
    configured_model = model_name or settings.GROQ_MODEL
    key = api_key if api_key is not None else settings.GROQ_API_KEY
    return Groq(
        id=configured_model,
        api_key=key,
        timeout=settings.REQUEST_TIMEOUT,
        max_tokens=550,
    )


def create_research_agents(model: Optional[Any] = None) -> Tuple[Agent, Agent, Agent]:
    """Create and configure the three collaborating research agents.

    1. Research Query Analyzer
    2. Research & Analysis Agent (with search_research_library tool)
    3. Research Answer Reviewer
    """
    query_analyzer = Agent(
        name="Research Query Analyzer",
        role="Classifies research domain, extracts core objectives, and formulates targeted search terms.",
        model=model,
        instructions=[
            "Classify the research question into an appropriate domain (e.g. AI, Machine Learning, "
            "Data Science, Software Engineering, Cybersecurity, Business, Science, Technology, or General Research).",
            "Extract the user's primary objective, explicit context, and constraints.",
            "Decompose complex questions into targeted sub-questions.",
            "Generate specific keywords and domain terminology for document retrieval.",
            "Do not assume facts that the user has not supplied.",
            "Return a structured analysis plan for the Research & Analysis Agent.",
        ],
    )

    research_agent = Agent(
        name="Research & Analysis Agent",
        role="Searches the curated research library and compiles evidence-based findings.",
        tools=[search_research_library],
        model=model,
        instructions=[
            "Invoke the `search_research_library` tool to locate relevant local research documents.",
            "Retrieve and analyze passages strictly from the curated local research library.",
            "Extract important findings, definitions, statistics, benchmarks, and architectural trade-offs.",
            "Distinguish facts supported by documents from interpretations and open questions.",
            "Identify conflicting findings or limitations in the available evidence.",
            "Explicitly attribute findings to document identifiers (e.g., sample-rag-001).",
            "Never invent sources or claim to have accessed the live internet.",
            "Provide the Research Answer Reviewer with organized evidence, findings, and citations.",
        ],
    )

    answer_reviewer = Agent(
        name="Research Answer Reviewer",
        role="Verifies findings against retrieved evidence and synthesizes the final structured Markdown report.",
        model=model,
        instructions=[
            "Cross-check all factual claims against the retrieved research library documents.",
            "Verify that cited sources directly support the statements attributed to them.",
            "Remove unsupported claims or explicitly label them as unverified.",
            "Identify limitations, information gaps, and context missing from the local library.",
            "Structure the final response using clear Markdown with the 8 standard sections: "
            "1. Research Classification, 2. Executive Summary, 3. Research Findings, "
            "4. Evidence and Source Analysis, 5. Analysis and Interpretation, "
            "6. Limitations and Information Gaps, 7. Conclusion, 8. Sources Consulted.",
            "Ensure the educational disclaimer is preserved.",
            "Do not fabricate citations to make an answer appear more comprehensive.",
        ],
    )

    return query_analyzer, research_agent, answer_reviewer


def create_research_team(model: Optional[Any] = None) -> Team:
    """Create an Agno Team coordinating the three research agents with TeamMode.coordinate.

    Args:
        model: Optional model instance. If omitted and Groq is configured, instantiates Groq.
    """
    settings = get_settings()
    active_model = model
    if active_model is None and settings.is_groq_configured:
        active_model = get_groq_model()

    analyzer, researcher, reviewer = create_research_agents(model=active_model)

    team = Team(
        name="Agno Research Team",
        members=[analyzer, researcher, reviewer],
        mode=TeamMode.coordinate,
        model=active_model,
        description="Coordinated multi-agent team conducting source-grounded research.",
        instructions=[
            "Coordinate research sequentially across the three registered members:",
            "1. Delegate query classification and planning to Research Query Analyzer.",
            "2. Delegate document retrieval and evidence extraction to Research & Analysis Agent.",
            "3. Delegate verification, source checking, and report synthesis to Research Answer Reviewer.",
            "Synthesize the final answer strictly grounded in evidence from the local research library.",
        ],
    )
    return team


def _format_markdown_report(
    question: str,
    domain: str,
    executive_summary: str,
    findings: str,
    evidence_analysis: str,
    interpretation: str,
    limitations: str,
    conclusion: str,
    sources: List[Dict[str, Any]],
) -> str:
    """Assemble the structured 8-section Markdown research report."""
    sources_section = ""
    if sources:
        sources_lines = [
            f"- **[{s.get('id', 'Unknown')}]** {s.get('title', 'Untitled')} — *{s.get('category', 'General')}*\n  Source: {s.get('source', 'Local Library')}"
            for s in sources
        ]
        sources_section = "\n".join(sources_lines)
    else:
        sources_section = "No direct matching sources were located in the local curated research library for this query."

    report = (
        f"## 1. Research Classification\n"
        f"- **Primary Domain:** {domain}\n"
        f"- **Central Question:** {question}\n\n"
        f"## 2. Executive Summary\n"
        f"{executive_summary}\n\n"
        f"## 3. Research Findings\n"
        f"{findings}\n\n"
        f"## 4. Evidence and Source Analysis\n"
        f"{evidence_analysis}\n\n"
        f"## 5. Analysis and Interpretation\n"
        f"{interpretation}\n\n"
        f"## 6. Limitations and Information Gaps\n"
        f"{limitations}\n\n"
        f"## 7. Conclusion\n"
        f"{conclusion}\n\n"
        f"## 8. Sources Consulted\n"
        f"{sources_section}\n\n"
        f"---\n"
        f"*{EDUCATIONAL_DISCLAIMER}*"
    )
    return report


async def run_research_workflow(
    question: str,
    team: Optional[Team] = None,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute the multi-agent coordinate research workflow.

    Coordinates Analyzer -> Researcher -> Reviewer to produce a structured,
    source-grounded research report.

    Args:
        question: User research question.
        team: Optional pre-configured Agno Team instance.
        timeout: Execution timeout in seconds.

    Returns:
        Dictionary with 'question', 'answer', 'sources', and 'disclaimer'.
    """
    settings = get_settings()
    req_timeout = timeout or settings.REQUEST_TIMEOUT

    # Ensure Groq credentials exist unless a pre-configured team with mock model is supplied
    if team is None and not settings.is_groq_configured:
        raise ConfigurationError(
            "Groq API key is not configured. Please set GROQ_API_KEY in your .env file."
        )

    active_team = team or create_research_team()
    analyzer, researcher, reviewer = active_team.members

    try:
        # Wrap execution in timeout
        return await asyncio.wait_for(
            _execute_coordinated_steps(question, active_team, analyzer, researcher, reviewer),
            timeout=float(req_timeout),
        )
    except asyncio.TimeoutError:
        raise ResearchTimeoutError(
            f"Research workflow timed out after {req_timeout} seconds."
        )
    except ConfigurationError:
        raise
    except Exception as e:
        # Check for upstream connection/API errors without leaking keys
        err_msg = str(e).lower()
        if "api_key" in err_msg or "unauthorized" in err_msg or "authentication" in err_msg:
            raise ConfigurationError("Upstream authentication failed. Please verify your GROQ_API_KEY.")
        if "rate_limit" in err_msg or "429" in err_msg:
            raise UpstreamServiceError("Groq API rate limit exceeded. Please retry after a brief pause.")
        if "connection" in err_msg or "timeout" in err_msg or "503" in err_msg or "502" in err_msg:
            raise UpstreamServiceError("Upstream Groq API connection issue. Please verify network access.")
        raise UpstreamServiceError(f"Research workflow encountered an error: {str(e)}")


async def _execute_coordinated_steps(
    question: str,
    team: Team,
    analyzer: Agent,
    researcher: Agent,
    reviewer: Agent,
) -> Dict[str, Any]:
    """Coordinate the sequential Analyzer -> Researcher -> Reviewer execution."""
    # Step 1: Research Query Analyzer
    analyzer_prompt = (
        f"Analyze the following research question:\n"
        f"'{question}'\n\n"
        f"Provide:\n"
        f"1. Research Domain\n"
        f"2. Core Objective\n"
        f"3. Key Sub-Questions\n"
        f"4. Recommended Retrieval Keywords"
    )
    
    analyzer_output = analyzer.run(analyzer_prompt)
    analysis_text = analyzer_output.content if hasattr(analyzer_output, "content") else str(analyzer_output)
    _check_agent_content_for_error(analysis_text)

    # Step 2: Research & Analysis Agent
    # Deterministic document retrieval via local research library
    retrieved_docs = search_documents(query=question, limit=get_settings().MAX_RESEARCH_RESULTS)

    docs_summary = ""
    sources_list: List[str] = []
    if retrieved_docs:
        docs_parts = []
        for d in retrieved_docs:
            source_entry = f"{d['id']} — {d['title']}"
            sources_list.append(source_entry)
            docs_parts.append(
                f"Document ID: {d['id']}\n"
                f"Title: {d['title']}\n"
                f"Category: {d['category']}\n"
                f"Excerpt: {d['relevant_excerpt']}\n"
                f"Source: {d['source']}\n"
            )
        docs_summary = "\n---\n".join(docs_parts)
    else:
        docs_summary = "No documents in the local curated library matched the query."

    researcher_prompt = (
        f"Original User Question: {question}\n\n"
        f"Query Analysis:\n{analysis_text}\n\n"
        f"Retrieved Library Evidence:\n{docs_summary}\n\n"
        f"Extract key findings, supported facts, numerical observations, opposing considerations, "
        f"and cite document IDs (e.g. sample-rag-001) for each claim. Never claim internet search. Keep it concise."
    )
    researcher_output = researcher.run(researcher_prompt)
    findings_text = researcher_output.content if hasattr(researcher_output, "content") else str(researcher_output)
    _check_agent_content_for_error(findings_text)

    # Step 3: Research Answer Reviewer
    sources_summary = "\n".join([f"- {s}" for s in sources_list]) if sources_list else "No direct matches."
    reviewer_prompt = (
        f"You are the Research Answer Reviewer.\n"
        f"Question: {question}\n\n"
        f"Consulted Library Sources:\n{sources_summary}\n\n"
        f"Researcher Findings:\n{findings_text}\n\n"
        f"Verify that all claims are backed by the retrieved evidence. Remove or label unverified claims.\n"
        f"Produce the final structured research report with these exact section headings:\n"
        f"## 1. Research Classification\n"
        f"## 2. Executive Summary\n"
        f"## 3. Research Findings\n"
        f"## 4. Evidence and Source Analysis\n"
        f"## 5. Analysis and Interpretation\n"
        f"## 6. Limitations and Information Gaps\n"
        f"## 7. Conclusion\n"
        f"## 8. Sources Consulted\n\n"
        f"List the actual consulted sources under Sources Consulted.\n"
        f"Include the educational disclaimer at the end."
    )
    reviewer_output = reviewer.run(reviewer_prompt)
    final_report = reviewer_output.content if hasattr(reviewer_output, "content") else str(reviewer_output)
    _check_agent_content_for_error(final_report)

    # Ensure educational disclaimer is present in the final report
    if EDUCATIONAL_DISCLAIMER not in final_report:
        final_report = f"{final_report}\n\n---\n*{EDUCATIONAL_DISCLAIMER}*"

    return {
        "question": question,
        "answer": final_report,
        "sources": sources_list,
        "disclaimer": EDUCATIONAL_DISCLAIMER,
    }
