"""Automated tests for Agno multi-agent coordination, retrieval tools, and workflow.

Verifies:
- Exactly three expected agents are registered.
- Agno Team is configured with TeamMode.coordinate.
- Research & Analysis Agent has access to search_research_library.
- Research tool returns relevant documents for known sample queries.
- Research tool returns empty results for unrelated queries.
- Search results contain source identifiers, titles, and excerpts.
- Final answer structure includes disclaimer and source list for mocked workflow.
- Unsupported source citations are not added by the retrieval layer.
- All tests execute deterministically offline without incurring Groq API charges.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch
import pytest
from agno.agent import Agent
from agno.team import Team, TeamMode

from app.agents.research_team import (
    create_research_agents,
    create_research_team,
    get_agent_names,
    run_research_workflow,
)
from app.agents.tools import (
    get_library_stats,
    search_documents,
    search_research_library,
)
from app.config import AGENT_NAMES, EDUCATIONAL_DISCLAIMER


def test_three_expected_agents_registered():
    """Verify that exactly three agents with the specified names are registered."""
    names = get_agent_names()
    assert len(names) == 3
    assert names == [
        "Research Query Analyzer",
        "Research & Analysis Agent",
        "Research Answer Reviewer",
    ]

    analyzer, researcher, reviewer = create_research_agents()
    assert analyzer.name == "Research Query Analyzer"
    assert researcher.name == "Research & Analysis Agent"
    assert reviewer.name == "Research Answer Reviewer"


def test_agno_team_configured_with_coordinate_mode():
    """Verify that the Agno Team is configured with TeamMode.coordinate."""
    team = create_research_team()
    assert isinstance(team, Team)
    assert team.mode == TeamMode.coordinate
    assert len(team.members) == 3
    member_names = [m.name for m in team.members]
    assert member_names == list(AGENT_NAMES)


def test_research_agent_has_search_research_library_tool():
    """Verify that the Research & Analysis Agent has access to the search_research_library tool."""
    _, researcher, _ = create_research_agents()
    assert researcher.tools is not None
    assert len(researcher.tools) > 0

    tool_names = [
        t.__name__ if hasattr(t, "__name__") else str(t)
        for t in researcher.tools
    ]
    assert "search_research_library" in tool_names


def test_research_tool_returns_relevant_documents_for_known_queries():
    """Verify that the search tool retrieves relevant documents for known sample queries."""
    # Test RAG query
    rag_docs = search_documents("Retrieval-Augmented Generation latency")
    assert len(rag_docs) > 0
    assert any("sample-rag" in d["id"] for d in rag_docs)

    # Test Zero Trust query
    sec_docs = search_documents("Zero Trust cybersecurity micro-segmentation")
    assert len(sec_docs) > 0
    assert any("sample-sec" in d["id"] for d in sec_docs)

    # Test MLOps query
    mlops_docs = search_documents("MLOps data drift concept drift")
    assert len(mlops_docs) > 0
    assert any("sample-mlops" in d["id"] for d in mlops_docs)


def test_research_tool_returns_empty_result_for_unrelated_query():
    """Verify that the search tool returns an empty list for an unrelated query."""
    unrelated_query = "quantum extraterrestrial spacecraft baking recipe xyz987"
    results = search_documents(unrelated_query)
    assert results == []

    # Verify tool string output also indicates empty results
    tool_output = search_research_library(unrelated_query)
    assert '"status": "empty"' in tool_output
    assert '"results": []' in tool_output


def test_search_results_contain_identifiers_and_titles():
    """Verify that search results contain required metadata fields."""
    docs = search_documents("cloud computing microservices")
    assert len(docs) > 0
    first_doc = docs[0]

    assert "id" in first_doc and first_doc["id"]
    assert "title" in first_doc and first_doc["title"]
    assert "category" in first_doc and first_doc["category"]
    assert "relevant_excerpt" in first_doc and first_doc["relevant_excerpt"]
    assert "source" in first_doc and first_doc["source"]
    assert "score" in first_doc and first_doc["score"] > 0


def test_unsupported_source_citations_not_added():
    """Verify that retrieval layer does not invent fake document IDs."""
    stats = get_library_stats()
    assert stats["available"] is True
    total_docs = stats["total_documents"]
    assert total_docs > 0

    results = search_documents("differential privacy")
    for r in results:
        # Every matched id must start with 'sample-' from the known dataset
        assert r["id"].startswith("sample-")


def test_mocked_workflow_returns_report_with_disclaimer_and_sources():
    """Verify that a mocked multi-agent workflow returns the required response structure."""
    import asyncio

    mock_analyzer_output = MagicMock()
    mock_analyzer_output.content = (
        "Domain: Retrieval-Augmented Generation\n"
        "Objective: Explain benefits and trade-offs of RAG.\n"
        "Keywords: rag, retrieval-augmented generation, latency"
    )

    mock_researcher_output = MagicMock()
    mock_researcher_output.content = (
        "Findings:\n"
        "- Reduces hallucinations by 42% (sample-rag-001)\n"
        "- Increases latency by 120ms to 250ms (sample-rag-001)"
    )

    mock_reviewer_output = MagicMock()
    mock_reviewer_output.content = (
        "## 1. Research Classification\nDomain: RAG\n\n"
        "## 2. Executive Summary\nRAG improves factual grounding.\n\n"
        "## 3. Research Findings\nReduces hallucinations.\n\n"
        "## 4. Evidence and Source Analysis\nSupported by sample-rag-001.\n\n"
        "## 5. Analysis and Interpretation\nTrade-offs are manageable.\n\n"
        "## 6. Limitations and Information Gaps\nLocal library demonstration.\n\n"
        "## 7. Conclusion\nRAG provides verified grounding.\n\n"
        "## 8. Sources Consulted\n- sample-rag-001\n\n"
        f"{EDUCATIONAL_DISCLAIMER}"
    )

    # Create mock agents
    mock_analyzer = MagicMock()
    mock_analyzer.run.return_value = mock_analyzer_output

    mock_researcher = MagicMock()
    mock_researcher.run.return_value = mock_researcher_output

    mock_reviewer = MagicMock()
    mock_reviewer.run.return_value = mock_reviewer_output

    mock_team = MagicMock()
    mock_team.members = [mock_analyzer, mock_researcher, mock_reviewer]

    question = "What are the benefits of Retrieval-Augmented Generation?"
    result = asyncio.run(run_research_workflow(question=question, team=mock_team))

    assert result["question"] == question
    assert "answer" in result
    assert "## 1. Research Classification" in result["answer"]
    assert "## 8. Sources Consulted" in result["answer"]
    assert EDUCATIONAL_DISCLAIMER in result["answer"]
    assert result["disclaimer"] == EDUCATIONAL_DISCLAIMER
    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0
    assert any("sample-rag" in s for s in result["sources"])
