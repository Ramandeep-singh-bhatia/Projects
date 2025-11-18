"""
Document upload page for Streamlit dashboard.
"""

import streamlit as st
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


def show():
    """Display document upload page."""
    st.title("📤 Upload Documents")

    st.markdown("""
    Upload documents for processing and indexing. Supported formats include:
    PDF, DOCX, XLSX, PPTX, Images (PNG, JPG), HTML, Markdown, and Text files.
    """)

    # File uploader
    st.subheader("Upload Files")

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=settings.allowed_extensions_list,
        help=f"Maximum file size: {settings.max_file_size_mb}MB"
    )

    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")

        # Display files
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.text(file.name)

            with col2:
                size_mb = file.size / (1024 * 1024) if file.size else 0
                st.text(f"{size_mb:.2f} MB")

            with col3:
                st.text(Path(file.name).suffix.upper())

        # Upload button
        if st.button("Upload All", type="primary"):
            upload_files(uploaded_files)

    st.markdown("---")

    # Uploaded documents list
    st.subheader("Recent Uploads")

    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/documents/",
            params={"limit": 10}
        )

        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])

            if documents:
                for doc in documents:
                    with st.expander(f"📄 {doc['filename']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Type:** {doc['document_type']}")
                            st.write(f"**Status:** {doc['status']}")
                            st.write(f"**Size:** {doc['file_size'] / 1024:.2f} KB")

                        with col2:
                            st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                            st.write(f"**Words:** {doc.get('word_count', 'N/A')}")
                            st.write(f"**Uploaded:** {doc['uploaded_at'][:10]}")

                        if st.button(f"Delete", key=f"delete_{doc['id']}"):
                            delete_document(doc['id'])
            else:
                st.info("No documents uploaded yet.")

        else:
            st.error("Failed to fetch documents from API.")

    except Exception as e:
        st.warning(f"API connection error: {str(e)}")
        st.info("Make sure the backend API is running.")


def upload_files(files):
    """Upload files to the API."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_files = len(files)
    successful = 0
    failed = 0

    for i, file in enumerate(files):
        status_text.text(f"Uploading {file.name}...")

        try:
            # Prepare file for upload
            files_data = {"file": (file.name, file.getvalue(), file.type)}

            # Upload to API
            response = requests.post(
                f"http://{settings.api_host}:{settings.api_port}/api/documents/upload",
                files=files_data
            )

            if response.status_code == 200:
                successful += 1
                st.success(f"✅ {file.name} uploaded successfully")
            else:
                failed += 1
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"❌ {file.name} failed: {error_detail}")

        except Exception as e:
            failed += 1
            st.error(f"❌ {file.name} failed: {str(e)}")

        # Update progress
        progress_bar.progress((i + 1) / total_files)

    status_text.text("Upload complete!")

    # Summary
    st.success(f"Upload Summary: {successful} successful, {failed} failed")

    if successful > 0:
        st.balloons()


def delete_document(doc_id: int):
    """Delete a document."""
    try:
        response = requests.delete(
            f"http://{settings.api_host}:{settings.api_port}/api/documents/{doc_id}"
        )

        if response.status_code == 200:
            st.success("Document deleted successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to delete document")

    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
