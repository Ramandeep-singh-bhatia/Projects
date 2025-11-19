"""
Search and query page for Streamlit dashboard.
"""

import streamlit as st
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


def show():
    """Display search and query page."""
    st.title("🔍 Search & Query")

    # Tabs for different modes
    tab1, tab2 = st.tabs(["🔍 Search", "💬 Ask Questions"])

    with tab1:
        show_search_tab()

    with tab2:
        show_query_tab()


def show_search_tab():
    """Display search interface."""
    st.markdown("### Search Documents")
    st.markdown("Find relevant documents using hybrid search (vector + keyword).")

    # Search input
    query = st.text_input(
        "Search query",
        placeholder="Enter your search query...",
        help="Search across all indexed documents"
    )

    # Advanced options in sidebar
    with st.sidebar:
        st.subheader("Search Options")

        search_strategy = st.selectbox(
            "Search Strategy",
            ["hybrid", "vector", "keyword", "multi_query", "hyde"],
            help="hybrid: Combines vector and keyword search\nvector: Semantic similarity\nkeyword: BM25 exact matching\nmulti_query: Multiple query variations\nhyde: Hypothetical document embeddings"
        )

        top_k = st.slider("Number of Results", 1, 50, 10)

        st.subheader("Filters")

        doc_type = st.selectbox(
            "Document Type",
            ["All", "pdf", "docx", "xlsx", "pptx", "text"],
            index=0
        )

        date_range = st.date_input("Date Range", [])

    # Search button
    if st.button("Search", type="primary") and query:
        with st.spinner("Searching..."):
            results = perform_search(
                query=query,
                strategy=search_strategy,
                top_k=top_k,
                doc_type=None if doc_type == "All" else doc_type
            )

            if results:
                display_search_results(results, query)
            else:
                st.info("No results found.")


def show_query_tab():
    """Display question answering interface."""
    st.markdown("### Ask Questions")
    st.markdown("Get AI-powered answers based on your documents using RAG.")

    # Question input
    question = st.text_area(
        "Your Question",
        placeholder="What is the main topic of the documents?\nSummarize the key findings...",
        height=100
    )

    # Advanced options
    with st.sidebar:
        st.subheader("RAG Options")

        rag_strategy = st.selectbox(
            "Retrieval Strategy",
            ["hybrid", "vector", "multi_query", "hyde"],
            help="Strategy for retrieving relevant documents"
        )

        num_sources = st.slider("Number of Sources", 1, 10, 5)

    # Ask button
    if st.button("Ask", type="primary") and question:
        with st.spinner("Generating answer..."):
            result = perform_rag_query(
                question=question,
                strategy=rag_strategy,
                top_k=num_sources
            )

            if result:
                display_rag_result(result, question)


def perform_search(query: str, strategy: str, top_k: int, doc_type: str = None):
    """Perform search via API."""
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "strategy": strategy
        }

        if doc_type:
            payload["document_type"] = doc_type

        response = requests.post(
            f"http://{settings.api_host}:{settings.api_port}/api/search/",
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Search failed: {response.json().get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        st.error(f"API error: {str(e)}")
        st.info("Make sure the backend API is running.")
        return None


def perform_rag_query(question: str, strategy: str, top_k: int):
    """Perform RAG query via API."""
    try:
        payload = {
            "question": question,
            "top_k": top_k,
            "strategy": strategy
        }

        response = requests.post(
            f"http://{settings.api_host}:{settings.api_port}/api/search/query",
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        st.error(f"API error: {str(e)}")
        st.info("Make sure the backend API is running.")
        return None


def display_search_results(results, query):
    """Display search results."""
    st.markdown(f"### Results for: *{query}*")

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Results", results.get("total_results", 0))
    with col2:
        st.metric("Strategy", results.get("strategy", "Unknown"))
    with col3:
        exec_time = results.get("execution_time", 0)
        st.metric("Execution Time", f"{exec_time * 1000:.0f}ms")

    st.markdown("---")

    # Display each result
    for i, result in enumerate(results.get("results", []), 1):
        with st.expander(f"Result {i} - Score: {result['score']:.4f}"):
            st.markdown(f"**Content:**")
            st.text(result['content'][:500] + ("..." if len(result['content']) > 500 else ""))

            if result.get('metadata'):
                st.markdown("**Metadata:**")
                st.json(result['metadata'])

            if result.get('document_id'):
                st.markdown(f"**Document ID:** {result['document_id']}")


def display_rag_result(result, question):
    """Display RAG query result."""
    st.markdown(f"### Question: *{question}*")

    # Answer
    st.markdown("### 💡 Answer")
    st.markdown(result.get("answer", "No answer generated"))

    # Metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Confidence", f"{result.get('confidence', 0) * 100:.1f}%")
    with col2:
        st.metric("Sources Used", result.get("num_sources", 0))
    with col3:
        st.metric("Strategy", result.get("retrieval_strategy", "Unknown"))
    with col4:
        exec_time = result.get("execution_time", 0)
        st.metric("Time", f"{exec_time:.2f}s")

    # Sources
    st.markdown("---")
    st.markdown("### 📚 Sources")

    for source in result.get("sources", []):
        with st.expander(f"Source {source['number']} - Score: {source['score']:.4f}"):
            st.text(source['content'])

            if source.get('metadata'):
                st.markdown("**Metadata:**")
                st.json(source['metadata'])
