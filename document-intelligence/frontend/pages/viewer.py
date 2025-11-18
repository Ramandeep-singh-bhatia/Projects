"""
Document viewer page for Streamlit dashboard.
"""

import streamlit as st
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


def show():
    """Display document viewer page."""
    st.title("📄 Document Viewer")

    st.markdown("""
    View and interact with your documents. Select a document to view its details,
    content, and ask questions specifically about that document.
    """)

    # Fetch documents
    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/documents/",
            params={"limit": 100}
        )

        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])

            if not documents:
                st.info("No documents available. Please upload documents first.")
                return

            # Document selector
            doc_options = {
                f"{doc['filename']} ({doc['document_type']})": doc['id']
                for doc in documents
            }

            selected_doc_name = st.selectbox(
                "Select Document",
                options=list(doc_options.keys())
            )

            if selected_doc_name:
                doc_id = doc_options[selected_doc_name]
                display_document(doc_id)

        else:
            st.error("Failed to fetch documents from API")

    except Exception as e:
        st.error(f"API error: {str(e)}")
        st.info("Make sure the backend API is running.")


def display_document(doc_id: int):
    """Display document details."""
    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/documents/{doc_id}"
        )

        if response.status_code == 200:
            doc = response.json()

            # Two columns: details and Q&A
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("### 📋 Document Details")

                st.write(f"**Filename:** {doc['filename']}")
                st.write(f"**Type:** {doc['document_type']}")
                st.write(f"**Status:** {doc['status']}")
                st.write(f"**Size:** {doc['file_size'] / 1024:.2f} KB")

                if doc.get('page_count'):
                    st.write(f"**Pages:** {doc['page_count']}")

                if doc.get('word_count'):
                    st.write(f"**Words:** {doc['word_count']:,}")

                st.write(f"**Uploaded:** {doc['uploaded_at'][:10]}")

                if doc.get('metadata'):
                    st.markdown("**Metadata:**")
                    st.json(doc['metadata'])

            with col2:
                st.markdown("### 💬 Ask About This Document")

                question = st.text_area(
                    "Your Question",
                    placeholder="What is this document about?\nSummarize the main points...",
                    height=100
                )

                if st.button("Ask", type="primary") and question:
                    with st.spinner("Generating answer..."):
                        # Query with document filter
                        answer = query_document(question, doc_id)

                        if answer:
                            st.markdown("**Answer:**")
                            st.markdown(answer.get("answer", "No answer generated"))

                            if answer.get("sources"):
                                with st.expander("View Sources"):
                                    for source in answer["sources"]:
                                        st.text(source["content"][:300] + "...")

        else:
            st.error(f"Failed to fetch document: {response.status_code}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def query_document(question: str, doc_id: int):
    """Query specific document."""
    try:
        payload = {
            "question": question,
            "top_k": 3,
            "strategy": "hybrid"
        }

        response = requests.post(
            f"http://{settings.api_host}:{settings.api_port}/api/search/query",
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error("Query failed")
            return None

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
