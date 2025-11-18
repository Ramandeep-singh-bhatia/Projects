"""
Main Streamlit application for AI Customer Support System.
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="AI Customer Support System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        # AI Customer Support System

        An intelligent customer support chatbot powered by RAG (Retrieval Augmented Generation).

        **Features:**
        - 70% autonomous resolution rate
        - <2 second response times
        - Multi-format document support
        - Real-time analytics
        - Source citations

        **Tech Stack:**
        - LangChain + FAISS
        - Claude Sonnet 4 / GPT-4
        - FastAPI + Streamlit

        Version 1.0.0
        """
    }
)

# Custom CSS
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #FF4B4B;
        --background-color: #0E1117;
        --secondary-background-color: #262730;
        --text-color: #FAFAFA;
    }

    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1rem;
    }

    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }

    .chat-message.user {
        background-color: #2b313e;
        margin-left: 2rem;
    }

    .chat-message.assistant {
        background-color: #1e2530;
        margin-right: 2rem;
    }

    .chat-message .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #FF4B4B;
    }

    .chat-message .message-content {
        color: #FAFAFA;
    }

    /* Source citations */
    .source-citation {
        background-color: #262730;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 3px solid #FF4B4B;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }

    /* Confidence badge */
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }

    .confidence-high {
        background-color: #28a745;
        color: white;
    }

    .confidence-medium {
        background-color: #ffc107;
        color: black;
    }

    .confidence-low {
        background-color: #dc3545;
        color: white;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        border: 2px dashed #FF4B4B;
        border-radius: 0.5rem;
        padding: 1rem;
    }

    /* Tables */
    [data-testid="stTable"] {
        font-size: 0.9rem;
    }

    /* Headers */
    h1 {
        color: #FF4B4B;
        padding-bottom: 1rem;
        border-bottom: 2px solid #262730;
    }

    h2 {
        color: #FAFAFA;
        margin-top: 2rem;
    }

    h3 {
        color: #FAFAFA;
        margin-top: 1.5rem;
    }

    /* Info boxes */
    .info-box {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }

    .warning-box {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }

    .success-box {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: bold;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/FF4B4B/FFFFFF?text=AI+Support", use_container_width=True)
    st.title("AI Customer Support")

    st.markdown("---")

    # Navigation info
    st.markdown("""
    ### 📖 Navigation

    Use the sidebar to navigate between:

    - **💬 Chat**: Customer chat interface
    - **📊 Analytics**: Performance metrics
    - **📚 Knowledge Base**: Document management

    ### ℹ️ System Info
    """)

    # API connection status
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
            health_data = response.json()
            st.caption(f"Database: {health_data.get('database', 'Unknown')}")
            st.caption(f"Docs: {health_data.get('num_documents', 0)}")
        else:
            st.error("⚠️ API Error")
    except:
        st.warning("⚠️ API Offline")
        st.caption("Start with: `uvicorn src.api.main:app`")

    st.markdown("---")

    # Settings
    with st.expander("⚙️ Settings"):
        st.checkbox("Show confidence scores", value=True, key="show_confidence")
        st.checkbox("Show source citations", value=True, key="show_sources")
        st.checkbox("Auto-scroll chat", value=True, key="auto_scroll")

        st.slider("Max history", 1, 20, 5, key="max_history")

    st.markdown("---")
    st.caption("Version 1.0.0")
    st.caption("Powered by Claude & GPT-4")

# Main content
st.title("🤖 AI Customer Support System")

st.markdown("""
Welcome to the AI-Powered Customer Support Dashboard! This system uses RAG (Retrieval Augmented Generation)
to provide intelligent, context-aware responses to customer queries.

### 🎯 Key Features

- **High Accuracy**: 70%+ autonomous resolution rate
- **Fast Responses**: <2 second average response time
- **Smart Retrieval**: Hybrid vector + keyword search
- **Source Citations**: Transparent answer sourcing
- **Multi-Format**: PDF, DOCX, TXT, CSV, HTML support
- **Analytics**: Real-time performance tracking

### 🚀 Quick Start

1. **Upload Documents**: Go to 📚 Knowledge Base to add support documentation
2. **Test Chat**: Use 💬 Chat to interact with the AI assistant
3. **Monitor Performance**: Check 📊 Analytics for metrics and insights

### 📋 System Architecture

This system consists of:
- **RAG Pipeline**: Document processing → Embeddings → Vector search → LLM generation
- **Dual LLM**: Claude Sonnet 4 (primary) with GPT-4 fallback
- **Vector Store**: FAISS for semantic search
- **API Backend**: FastAPI with 8 production endpoints
- **Frontend**: Streamlit multi-page dashboard

Select a page from the sidebar to get started!
""")

# Quick stats on home page
st.markdown("---")
st.subheader("📈 Quick Stats")

try:
    response = requests.get("http://localhost:8000/api/analytics?days=7", timeout=5)
    if response.status_code == 200:
        data = response.json()
        metrics = data['metrics']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Queries (7d)",
                value=metrics['total_queries'],
                delta=None
            )

        with col2:
            st.metric(
                label="Resolution Rate",
                value=f"{metrics['autonomous_resolution_rate']:.1f}%",
                delta=f"{metrics['autonomous_resolution_rate'] - 70:.1f}%" if metrics['autonomous_resolution_rate'] > 0 else None
            )

        with col3:
            st.metric(
                label="Avg Response Time",
                value=f"{metrics['avg_resolution_time']:.2f}s",
                delta=f"{2.0 - metrics['avg_resolution_time']:.2f}s" if metrics['avg_resolution_time'] > 0 else None,
                delta_color="inverse"
            )

        with col4:
            st.metric(
                label="Customer Rating",
                value=f"{metrics['avg_rating']:.1f}/5.0" if metrics['avg_rating'] > 0 else "N/A",
                delta=None
            )
    else:
        st.info("📊 No analytics data available yet. Start chatting to generate metrics!")
except:
    st.info("💡 Start the API server to see real-time statistics.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>AI Customer Support System v1.0.0 | Built with LangChain, Claude, FastAPI & Streamlit</p>
    <p>For support, contact your system administrator</p>
</div>
""", unsafe_allow_html=True)
