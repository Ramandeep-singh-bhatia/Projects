"""
Streamlit Dashboard for Document Intelligence Platform.
Main entry point for the web interface.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

# Page configuration
st.set_page_config(
    page_title=settings.app_name,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .search-result {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "📤 Upload Documents",
        "🔍 Search & Query",
        "📊 Analytics Dashboard",
        "📄 Document Viewer"
    ]
)

# Main content based on selected page
if page == "🏠 Home":
    st.markdown('<div class="main-header">📚 Document Intelligence Platform</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Welcome to the Enterprise Document Intelligence Platform

    This platform provides advanced document processing, hybrid search, and AI-powered question answering capabilities.

    #### Key Features:

    **🔄 Document Processing**
    - Support for PDF, DOCX, XLSX, PPTX, images, and more
    - Intelligent text extraction and preprocessing
    - Automatic metadata extraction

    **🔍 Hybrid Search**
    - Vector search for semantic similarity
    - Keyword search (BM25) for exact matches
    - Intelligent fusion for best results

    **🤖 Advanced RAG**
    - Multi-query retrieval for comprehensive results
    - HyDE (Hypothetical Document Embeddings)
    - Parent-child document relationships
    - Multi-hop reasoning for complex questions

    **📊 Analytics**
    - Document overview and statistics
    - Search pattern analysis
    - Content intelligence insights

    ---

    **Getting Started:**
    1. Upload documents using the **Upload Documents** page
    2. Search or ask questions using the **Search & Query** page
    3. View insights on the **Analytics Dashboard**

    """)

    # Quick stats
    st.markdown("### Quick Stats")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Documents", "0")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Searches", "0")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg. Response Time", "0ms")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Processing Queue", "0")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📤 Upload Documents":
    from frontend.pages import upload
    upload.show()

elif page == "🔍 Search & Query":
    from frontend.pages import search
    search.show()

elif page == "📊 Analytics Dashboard":
    from frontend.pages import analytics
    analytics.show()

elif page == "📄 Document Viewer":
    from frontend.pages import viewer
    viewer.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Version:** {settings.app_version}")
st.sidebar.markdown("**Status:** 🟢 Running")
