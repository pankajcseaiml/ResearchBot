"""Research library retrieval tool for ResearchBot.

Provides deterministic, keyword-weighted retrieval over the local curated research corpus
without relying on external paid services or live internet search.
"""

import json
import re
from typing import Any, Dict, List, Optional
from app.config import get_settings
from app.data.sample_documents import SAMPLE_DOCUMENTS

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "let's", "me", "more", "most", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def _tokenize(text: str) -> List[str]:
    """Normalize text into lowercase tokens, handling hyphens and punctuation."""
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    raw_tokens = [t for t in re.split(r"[\s_]+", cleaned) if len(t) > 1]
    tokens: List[str] = []
    for token in raw_tokens:
        tokens.append(token)
        if "-" in token:
            subparts = [p for p in token.split("-") if len(p) > 1]
            tokens.extend(subparts)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def _find_best_excerpt(content: str, query_tokens: List[str]) -> str:
    """Find the most relevant paragraph or sentence window for the query tokens."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if not paragraphs:
        return content[:300] + "..." if len(content) > 300 else content

    best_p = paragraphs[0]
    best_score = -1

    for p in paragraphs:
        p_lower = p.lower()
        score = sum(1 for token in query_tokens if token in p_lower)
        if score > best_score:
            best_score = score
            best_p = p

    return best_p


def search_documents(
    query: str,
    category: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Perform deterministic keyword-weighted retrieval across local sample documents.

    Args:
        query: User search string or research question.
        category: Optional category filter.
        limit: Maximum number of ranked documents to return.

    Returns:
        List of ranked document dictionaries with id, title, category, relevant_excerpt,
        source metadata, and relevance score.
    """
    settings = get_settings()
    max_results = limit if (limit is not None and limit > 0) else settings.MAX_RESEARCH_RESULTS

    normalized_query = query.strip()
    if not normalized_query:
        return []

    tokens = _tokenize(normalized_query)
    meaningful_tokens = [t for t in tokens if t not in STOP_WORDS]
    search_tokens = meaningful_tokens if meaningful_tokens else tokens

    if not search_tokens:
        return []

    query_lower = normalized_query.lower()
    scored_docs: List[Dict[str, Any]] = []

    for doc in SAMPLE_DOCUMENTS:
        doc_category = doc.get("category", "")
        if category and category.lower() not in doc_category.lower():
            continue

        doc_id = doc.get("id", "")
        title = doc.get("title", "")
        content = doc.get("content", "")
        keywords = doc.get("keywords", [])
        keywords_str = " ".join(keywords).lower()
        source = doc.get("source", f"Local Research Library ({doc_id})")

        title_lower = title.lower()
        content_lower = content.lower()

        score = 0.0

        # Exact phrase match boost
        if query_lower in title_lower:
            score += 20.0
        elif query_lower in keywords_str:
            score += 15.0
        elif query_lower in content_lower:
            score += 10.0

        # Token level matching with tiered field weights
        matched_tokens = 0
        for token in search_tokens:
            token_matched = False
            if token in doc_id.lower():
                score += 8.0
                token_matched = True
            if token in title_lower:
                score += 6.0
                token_matched = True
            if token in keywords_str:
                score += 5.0
                token_matched = True
            if token in content_lower:
                count = min(content_lower.count(token), 4)
                score += 1.5 * count
                token_matched = True

            if token_matched:
                matched_tokens += 1

        # Relevance filter: require at least one strong field match or multiple tokens
        # to avoid returning unrelated documents with just a single generic word
        is_relevant = False
        if score >= 6.0:
            is_relevant = True
        elif len(search_tokens) == 1 and matched_tokens == 1 and score >= 4.0:
            is_relevant = True
        elif len(search_tokens) > 1 and matched_tokens >= 2 and score >= 3.0:
            is_relevant = True

        if is_relevant:
            excerpt = _find_best_excerpt(content, search_tokens)
            scored_docs.append({
                "id": doc_id,
                "title": title,
                "category": doc_category,
                "relevant_excerpt": excerpt,
                "source": source,
                "score": round(score, 2),
            })

    # Sort descending by relevance score
    scored_docs.sort(key=lambda d: d["score"], reverse=True)
    return scored_docs[:max_results]


def search_research_library(
    query: str,
    category: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """Tool callable for Agno research agents to search the curated local library.

    Note: This tool searches only the local curated demonstration research library.
    It does NOT connect to the live internet or external commercial search APIs.

    Args:
        query: The research terms, keywords, or sub-questions to look up.
        category: Optional category filter.
        limit: Optional maximum number of matches to return.

    Returns:
        JSON-formatted string containing matched documents and excerpts.
    """
    results = search_documents(query=query, category=category, limit=limit)
    if not results:
        return json.dumps({
            "status": "empty",
            "message": f"No relevant research documents found in the local library for query: '{query}'.",
            "query": query,
            "results": [],
        }, indent=2)

    return json.dumps({
        "status": "success",
        "query": query,
        "count": len(results),
        "results": results,
    }, indent=2)


def get_library_stats() -> Dict[str, Any]:
    """Return summary information about the loaded local research library."""
    categories = sorted(list({d.get("category", "General") for d in SAMPLE_DOCUMENTS}))
    return {
        "available": len(SAMPLE_DOCUMENTS) > 0,
        "total_documents": len(SAMPLE_DOCUMENTS),
        "categories": categories,
    }
