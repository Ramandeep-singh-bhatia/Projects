"""
Knowledge Base management page for document upload and management.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Knowledge Base - AI Customer Support",
    page_icon="📚",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Helper functions
def upload_document(file):
    """Upload document to API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}

        response = requests.post(
            f"{API_URL}/api/documents/upload",
            files=files,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            st.error(f"Upload failed: {error_data.get('detail', 'Unknown error')}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Upload timed out. File may be too large.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def fetch_documents(status_filter=None):
    """Fetch documents from API"""
    try:
        params = {}
        if status_filter and status_filter != "All":
            params["status_filter"] = status_filter.lower()

        response = requests.get(
            f"{API_URL}/api/documents",
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def delete_document(document_id: int, filename: str):
    """Delete document from API"""
    try:
        response = requests.delete(
            f"{API_URL}/api/documents/{document_id}",
            timeout=10
        )

        if response.status_code == 200:
            st.success(f"✅ Deleted: {filename}")
            return True
        else:
            error_data = response.json()
            st.error(f"Delete failed: {error_data.get('detail', 'Unknown error')}")
            return False

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server")
        return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def get_status_badge(status: str) -> str:
    """Get status badge HTML"""
    status_colors = {
        "pending": ("🕐", "#ffc107", "black"),
        "processing": ("⚙️", "#17a2b8", "white"),
        "completed": ("✅", "#28a745", "white"),
        "failed": ("❌", "#dc3545", "white")
    }

    icon, bg_color, text_color = status_colors.get(status.lower(), ("❓", "#6c757d", "white"))

    return f"""
    <span style="
        background-color: {bg_color};
        color: {text_color};
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: bold;
    ">
        {icon} {status.upper()}
    </span>
    """


# Page header
st.title("📚 Knowledge Base Management")

st.markdown("""
Upload and manage documents that power the AI assistant's knowledge base.
Supported formats: **PDF, DOCX, TXT, CSV, HTML**
""")

# ==================== Upload Section ====================
st.markdown("---")
st.subheader("📤 Upload Documents")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "docx", "txt", "csv", "html", "htm"],
        accept_multiple_files=True,
        help="Upload one or more documents (max 50MB each)"
    )

with col2:
    st.markdown("")
    st.markdown("")
    upload_button = st.button("🚀 Upload Files", use_container_width=True, type="primary")

if upload_button and uploaded_files:
    progress_bar = st.progress(0)
    status_text = st.empty()

    successful_uploads = 0
    failed_uploads = 0

    for idx, file in enumerate(uploaded_files):
        progress = (idx / len(uploaded_files))
        progress_bar.progress(progress)
        status_text.text(f"Uploading {file.name}...")

        result = upload_document(file)

        if result and result.get('success'):
            successful_uploads += 1
            st.success(f"✅ Uploaded: {file.name} (ID: {result.get('document_id')})")
        else:
            failed_uploads += 1

    progress_bar.progress(1.0)
    status_text.text("Upload complete!")

    # Summary
    st.info(f"""
    **Upload Summary:**
    - ✅ Successful: {successful_uploads}
    - ❌ Failed: {failed_uploads}
    - 📝 Total: {len(uploaded_files)}

    Note: Documents are processed in the background. Check the table below for status updates.
    """)

elif upload_button and not uploaded_files:
    st.warning("Please select files to upload")

# Upload instructions
with st.expander("ℹ️ Upload Instructions"):
    st.markdown("""
    ### How Document Upload Works

    1. **Select Files**: Choose one or more supported documents
    2. **Upload**: Click the "Upload Files" button
    3. **Processing**: Documents are processed in the background:
       - Text extraction
       - Chunking (500 tokens with 50 token overlap)
       - Embedding generation
       - Vector store indexing
    4. **Ready**: Once status shows "Completed", the AI can answer questions using these documents

    ### Best Practices

    - **File Size**: Keep files under 50MB for optimal processing
    - **Format**: Use structured documents (headings, lists) for better chunking
    - **Content**: Ensure documents contain relevant support information
    - **Updates**: Delete old documents before uploading new versions
    - **Quality**: Well-formatted documents lead to better AI responses

    ### Supported Formats

    | Format | Extension | Notes |
    |--------|-----------|-------|
    | PDF | .pdf | Most common, widely supported |
    | Word | .docx | Good for formatted content |
    | Text | .txt | Simple plain text |
    | CSV | .csv | Tabular data (FAQs, product info) |
    | HTML | .html, .htm | Web pages and documentation |
    """)

# ==================== Document Library ====================
st.markdown("---")
st.subheader("📖 Document Library")

# Filters and actions
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        options=["All", "Pending", "Processing", "Completed", "Failed"],
        index=0
    )

with col2:
    search_query = st.text_input("Search documents", placeholder="Enter filename...")

with col3:
    st.markdown("")
    st.markdown("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col4:
    st.markdown("")
    st.markdown("")
    show_details = st.checkbox("Show details", value=False)

# Fetch and display documents
with st.spinner("Loading documents..."):
    data = fetch_documents(status_filter if status_filter != "All" else None)

if data:
    documents = data.get('documents', [])
    total = data.get('total', 0)

    if documents:
        # Filter by search query
        if search_query:
            documents = [doc for doc in documents if search_query.lower() in doc['filename'].lower()]

        st.caption(f"Showing {len(documents)} of {total} documents")

        # Display as table
        for doc in documents:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

                with col1:
                    st.markdown(f"**📄 {doc['filename']}**")
                    if show_details:
                        st.caption(f"ID: {doc['id']} | Type: {doc['file_type'].upper()}")

                with col2:
                    upload_date = datetime.fromisoformat(doc['upload_date'].replace('Z', '+00:00'))
                    st.caption(f"📅 {upload_date.strftime('%Y-%m-%d %H:%M')}")

                with col3:
                    st.markdown(get_status_badge(doc['status']), unsafe_allow_html=True)

                with col4:
                    st.metric("Chunks", doc['num_chunks'])

                with col5:
                    if st.button("🗑️", key=f"delete_{doc['id']}", help="Delete document"):
                        if st.session_state.get(f"confirm_delete_{doc['id']}", False):
                            # Actually delete
                            if delete_document(doc['id'], doc['filename']):
                                # Remove confirmation flag
                                del st.session_state[f"confirm_delete_{doc['id']}"]
                                st.rerun()
                        else:
                            # First click - ask for confirmation
                            st.session_state[f"confirm_delete_{doc['id']}"] = True
                            st.warning(f"Click again to confirm deletion of {doc['filename']}")
                            st.rerun()

                # Show details if enabled
                if show_details:
                    with st.expander(f"Details: {doc['filename']}", expanded=False):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("File Size", f"{doc['file_size'] / 1024:.1f} KB" if doc['file_size'] > 0 else "N/A")

                        with col2:
                            st.metric("Chunks", doc['num_chunks'])

                        with col3:
                            st.metric("Status", doc['status'])

                        if doc.get('metadata'):
                            st.json(doc['metadata'])

                st.markdown("---")

    else:
        st.info("""
        ### 📭 No Documents Found

        Your knowledge base is empty. Upload documents to get started!

        Documents will be processed automatically and made available to the AI assistant.
        """)

else:
    st.warning("""
    ### ⚠️ Cannot Load Documents

    Make sure the API server is running:
    ```
    uvicorn src.api.main:app --reload
    ```
    """)

# ==================== Statistics ====================
if data and documents:
    st.markdown("---")
    st.subheader("📊 Statistics")

    col1, col2, col3, col4 = st.columns(4)

    # Calculate stats
    status_counts = {}
    for doc in documents:
        status = doc['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    total_chunks = sum(doc['num_chunks'] for doc in documents)
    avg_chunks = total_chunks / len(documents) if documents else 0

    with col1:
        st.metric("Total Documents", len(documents))

    with col2:
        st.metric("Total Chunks", total_chunks)

    with col3:
        st.metric("Avg Chunks/Doc", f"{avg_chunks:.1f}")

    with col4:
        completed = status_counts.get('completed', 0)
        completion_rate = (completed / len(documents) * 100) if documents else 0
        st.metric("Completion Rate", f"{completion_rate:.0f}%")

    # Status breakdown
    if status_counts:
        st.markdown("**Status Breakdown:**")
        status_cols = st.columns(len(status_counts))

        for idx, (status, count) in enumerate(status_counts.items()):
            with status_cols[idx]:
                st.metric(status.capitalize(), count)

# ==================== Tips & Best Practices ====================
st.markdown("---")
st.subheader("💡 Tips & Best Practices")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📝 Document Quality
    - Use clear headings and structure
    - Include relevant keywords
    - Keep information up-to-date
    - Break long documents into sections
    """)

with col2:
    st.markdown("""
    ### 🎯 Optimization
    - Regular content audits
    - Remove outdated documents
    - Monitor retrieval performance
    - Update based on user feedback
    """)

# Footer
st.markdown("---")
st.caption(f"Knowledge Base Management | Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
