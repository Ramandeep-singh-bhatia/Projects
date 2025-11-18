"""
Chat interface page for customer support.
"""
import streamlit as st
import requests
import uuid
import time
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Chat - AI Customer Support",
    page_icon="💬",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

# Helper functions
def get_confidence_badge(confidence: float) -> str:
    """Generate confidence badge HTML"""
    if confidence >= 0.8:
        badge_class = "confidence-high"
        label = "High Confidence"
    elif confidence >= 0.6:
        badge_class = "confidence-medium"
        label = "Medium Confidence"
    else:
        badge_class = "confidence-low"
        label = "Low Confidence"

    return f'<span class="confidence-badge {badge_class}">{label} ({confidence:.0%})</span>'


def format_source_citation(source: dict) -> str:
    """Format source citation as HTML"""
    return f"""
    <div class="source-citation">
        <strong>📄 {source['filename']}</strong> (Score: {source['similarity_score']:.2f})<br>
        <em>{source['content'][:200]}{'...' if len(source['content']) > 200 else ''}</em>
    </div>
    """


def send_message(message: str) -> dict:
    """Send message to API and get response"""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "include_sources": st.session_state.get("show_sources", True),
            "max_history": st.session_state.get("max_history", 5)
        }

        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please start it with: `uvicorn src.api.main:app`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The AI is taking too long to respond.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def submit_feedback(analytics_id: int, rating: int):
    """Submit feedback for a response"""
    try:
        payload = {
            "analytics_id": analytics_id,
            "session_id": st.session_state.session_id,
            "rating": rating
        }

        response = requests.post(
            f"{API_URL}/api/feedback",
            json=payload,
            timeout=5
        )

        if response.status_code == 200:
            st.success("Thank you for your feedback!")
        else:
            st.error("Failed to submit feedback")

    except Exception as e:
        st.error(f"Error submitting feedback: {str(e)}")


# Page header
st.title("💬 Customer Support Chat")

st.markdown("""
Ask me anything about our products, services, or policies! I'll search our knowledge base
to provide accurate answers with source citations.
""")

# Sidebar with conversation info
with st.sidebar:
    st.subheader("💬 Conversation Info")

    st.text_input("Session ID", value=st.session_state.session_id, disabled=True)
    st.text_input("User ID", value=st.session_state.user_id, disabled=True)

    st.markdown("---")

    # Conversation stats
    if st.session_state.messages:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])

        st.metric("Your Messages", user_msgs)
        st.metric("AI Responses", assistant_msgs)

        if assistant_msgs > 0:
            avg_confidence = sum(
                m.get("confidence", 0) for m in st.session_state.messages
                if m["role"] == "assistant"
            ) / assistant_msgs
            st.metric("Avg Confidence", f"{avg_confidence:.0%}")

    st.markdown("---")

    # Actions
    st.subheader("🔧 Actions")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    if st.button("💾 Export Chat", use_container_width=True):
        # Export conversation as JSON
        import json
        export_data = {
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "messages": st.session_state.messages,
            "exported_at": datetime.utcnow().isoformat()
        }
        st.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"chat_{st.session_state.session_id[:8]}.json",
            mime="application/json",
            use_container_width=True
        )

    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.success("New session started!")

# Main chat interface
chat_container = st.container()

# Display chat messages
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])

        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                # Message content
                st.markdown(message["content"])

                # Confidence score
                if st.session_state.get("show_confidence", True) and "confidence" in message:
                    st.markdown(
                        get_confidence_badge(message["confidence"]),
                        unsafe_allow_html=True
                    )

                # Escalation warning
                if message.get("should_escalate", False):
                    st.warning("⚠️ This query may require human assistance")

                # Source citations
                if st.session_state.get("show_sources", True) and message.get("sources"):
                    with st.expander(f"📚 View Sources ({len(message['sources'])})"):
                        for source in message["sources"]:
                            st.markdown(
                                format_source_citation(source),
                                unsafe_allow_html=True
                            )

                # Suggested questions
                if message.get("suggested_questions"):
                    with st.expander("💡 Suggested Follow-up Questions"):
                        for question in message["suggested_questions"]:
                            if st.button(question, key=f"suggest_{idx}_{question[:20]}"):
                                # Set this as the next user input
                                st.session_state.next_message = question
                                st.rerun()

                # Feedback buttons
                col1, col2, col3 = st.columns([1, 1, 6])
                with col1:
                    if st.button("👍", key=f"thumbs_up_{idx}", help="Helpful"):
                        submit_feedback(message.get("analytics_id"), 5)
                with col2:
                    if st.button("👎", key=f"thumbs_down_{idx}", help="Not helpful"):
                        submit_feedback(message.get("analytics_id"), 1)

                # Processing time
                if "processing_time_ms" in message:
                    st.caption(f"⏱️ Response time: {message['processing_time_ms']:.0f}ms")

# Chat input
if "next_message" in st.session_state:
    # Use suggested question
    user_input = st.session_state.next_message
    del st.session_state.next_message
    # Process immediately
    process_message = True
else:
    user_input = st.chat_input("Type your message here...")
    process_message = bool(user_input)

if process_message and user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Show typing indicator
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            # Send message to API
            start_time = time.time()
            response_data = send_message(user_input)
            elapsed_time = (time.time() - start_time) * 1000

    if response_data:
        # Add assistant response to chat
        assistant_message = {
            "role": "assistant",
            "content": response_data["response"],
            "confidence": response_data.get("confidence_score", 0),
            "should_escalate": response_data.get("should_escalate", False),
            "sources": response_data.get("sources", []),
            "suggested_questions": response_data.get("suggested_questions", []),
            "processing_time_ms": response_data.get("processing_time_ms", elapsed_time),
            "timestamp": datetime.utcnow().isoformat()
        }

        st.session_state.messages.append(assistant_message)

        # Rerun to display the response properly
        st.rerun()

# Show example queries if no messages yet
if not st.session_state.messages:
    st.markdown("---")
    st.subheader("💡 Example Questions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Product Information:**
        - What are your business hours?
        - Do you offer free shipping?
        - What payment methods do you accept?
        """)

    with col2:
        st.markdown("""
        **Support Queries:**
        - How do I track my order?
        - What is your return policy?
        - How do I reset my password?
        """)

    st.markdown("---")
    st.info("👆 Click on a question above or type your own message to start chatting!")

# Footer
st.markdown("---")
st.caption(f"Session: {st.session_state.session_id[:8]}... | Messages: {len(st.session_state.messages)}")
