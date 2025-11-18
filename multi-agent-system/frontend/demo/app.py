"""
Streamlit Demo Interface for Multi-Agent Business Automation System.
Provides an interactive interface to test workflows and agents.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Business Automation System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API configuration
API_URL = st.secrets.get("API_URL", "http://localhost:8000")


# Helper functions
def execute_workflow(workflow_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a workflow via API."""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/workflows/execute",
            json={"workflow_type": workflow_type, "input_data": input_data},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get workflow status via API."""
    try:
        response = requests.get(f"{API_URL}/api/v1/workflows/{workflow_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def list_workflows() -> Dict[str, Any]:
    """List available workflows."""
    try:
        response = requests.get(f"{API_URL}/api/v1/workflows/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def list_agents() -> Dict[str, Any]:
    """List available agents."""
    try:
        response = requests.get(f"{API_URL}/api/v1/agents/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# Main app
def main():
    """Main Streamlit application."""

    # Title and description
    st.title("🤖 Multi-Agent Business Automation System")
    st.markdown("""
    **Coordinate multiple specialized AI agents to automate complete business workflows end-to-end.**

    This demo interface allows you to:
    - Execute pre-built workflows
    - Monitor workflow progress
    - View agent performance
    - Test individual agents
    """)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Home", "📊 Workflows", "🤖 Agents", "📈 Analytics", "ℹ️ About"],
    )

    if page == "🏠 Home":
        home_page()
    elif page == "📊 Workflows":
        workflows_page()
    elif page == "🤖 Agents":
        agents_page()
    elif page == "📈 Analytics":
        analytics_page()
    elif page == "ℹ️ About":
        about_page()


def home_page():
    """Home page with quick start guide."""
    st.header("Quick Start Guide")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Workflows", "5", "Pre-built templates")

    with col2:
        st.metric("Specialized Agents", "7", "Autonomous AI agents")

    with col3:
        st.metric("API Endpoints", "15+", "Full REST API")

    st.markdown("---")

    st.subheader("🚀 Try a Workflow")

    workflow_type = st.selectbox(
        "Select a workflow to try:",
        [
            "market_research",
            "content_campaign",
            "lead_generation",
            "product_launch",
            "customer_support",
        ],
    )

    if workflow_type == "market_research":
        st.markdown("### Market Research & Competitive Analysis")
        industry = st.text_input("Industry/Market", "SaaS B2B")
        competitors = st.text_area(
            "Competitors (comma-separated)",
            "Salesforce, HubSpot, Microsoft Dynamics",
        )

        if st.button("🚀 Start Market Research"):
            with st.spinner("Executing workflow..."):
                result = execute_workflow(
                    "market_research",
                    {
                        "industry": industry,
                        "competitors": [c.strip() for c in competitors.split(",")],
                        "focus_areas": ["products", "pricing", "market_share"],
                    },
                )

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Workflow started! ID: {result.get('workflow_id')}")
                    st.json(result)

    elif workflow_type == "content_campaign":
        st.markdown("### Content Marketing Campaign")
        topic = st.text_input("Campaign Topic", "AI in Business")
        duration = st.number_input("Duration (weeks)", 1, 12, 4)

        if st.button("🚀 Start Content Campaign"):
            with st.spinner("Executing workflow..."):
                result = execute_workflow(
                    "content_campaign",
                    {
                        "topic": topic,
                        "duration_weeks": duration,
                        "platforms": ["blog", "linkedin", "email"],
                        "target_audience": "Business professionals",
                    },
                )

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Workflow started! ID: {result.get('workflow_id')}")
                    st.json(result)


def workflows_page():
    """Workflows page for executing and monitoring workflows."""
    st.header("📊 Workflows")

    tab1, tab2, tab3 = st.tabs(["Execute Workflow", "Monitor Workflows", "Workflow History"])

    with tab1:
        st.subheader("Execute a New Workflow")

        # Get available workflows
        workflows_data = list_workflows()

        if "error" in workflows_data:
            st.error(f"Error loading workflows: {workflows_data['error']}")
        else:
            workflows = workflows_data.get("workflows", [])

            workflow_options = {w["name"]: w["type"] for w in workflows}
            selected_workflow_name = st.selectbox(
                "Select Workflow",
                list(workflow_options.keys()),
            )

            selected_workflow_type = workflow_options[selected_workflow_name]

            # Display workflow info
            workflow_info = next(
                (w for w in workflows if w["type"] == selected_workflow_type),
                {},
            )
            st.info(f"**Description:** {workflow_info.get('description', 'N/A')}")

            # Input data editor
            st.subheader("Input Data (JSON)")
            input_json = st.text_area(
                "Enter workflow input data as JSON:",
                value='{"industry": "SaaS", "competitors": ["Competitor1", "Competitor2"]}',
                height=200,
            )

            if st.button("▶️ Execute Workflow", type="primary"):
                try:
                    input_data = json.loads(input_json)

                    with st.spinner("Executing workflow..."):
                        result = execute_workflow(selected_workflow_type, input_data)

                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(
                                f"✅ Workflow '{selected_workflow_name}' started successfully!"
                            )
                            st.json(result)

                            # Store workflow ID in session state
                            if "workflow_ids" not in st.session_state:
                                st.session_state.workflow_ids = []
                            st.session_state.workflow_ids.append(result.get("workflow_id"))

                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")

    with tab2:
        st.subheader("Monitor Active Workflows")

        if "workflow_ids" in st.session_state and st.session_state.workflow_ids:
            for workflow_id in st.session_state.workflow_ids:
                with st.expander(f"Workflow: {workflow_id}"):
                    if st.button(f"Refresh Status", key=f"refresh_{workflow_id}"):
                        status = get_workflow_status(workflow_id)

                        if "error" in status:
                            st.error(f"Error: {status['error']}")
                        else:
                            st.json(status)
        else:
            st.info("No active workflows. Execute a workflow to see it here.")

    with tab3:
        st.subheader("Workflow History")
        st.info("Recent workflow executions will appear here.")


def agents_page():
    """Agents page for viewing agent information."""
    st.header("🤖 Agents")

    agents_data = list_agents()

    if "error" in agents_data:
        st.error(f"Error loading agents: {agents_data['error']}")
    else:
        agents = agents_data.get("agents", [])

        st.info(f"**Total Agents:** {len(agents)}")

        for agent in agents:
            with st.expander(f"**{agent['role']}** ({agent['type']})"):
                st.markdown(f"**Goal:** {agent['goal']}")
                st.markdown(f"**Capabilities:** {agent['capabilities']}")


def analytics_page():
    """Analytics page with system metrics."""
    st.header("📈 Analytics & Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Workflows Executed", "0", delta="0 today")

    with col2:
        st.metric("Agent Tasks Completed", "0", delta="0 today")

    with col3:
        st.metric("Success Rate", "N/A", delta="N/A")

    st.markdown("---")

    st.subheader("System Health")
    try:
        response = requests.get(f"{API_URL}/health")
        health = response.json()

        if health.get("status") == "healthy":
            st.success("✅ All systems operational")
        else:
            st.warning(f"⚠️ System status: {health.get('status')}")

        st.json(health)
    except Exception as e:
        st.error(f"Could not fetch health status: {e}")


def about_page():
    """About page with system information."""
    st.header("ℹ️ About")

    st.markdown("""
    ## Multi-Agent Business Automation System

    ### Overview
    This system coordinates multiple specialized AI agents to automate complete business workflows end-to-end.

    ### Key Features
    - **7 Specialized Agents**: Research, Analysis, Planning, Content, Outreach, QA, and Coordinator
    - **5 Pre-Built Workflows**: Market Research, Content Campaign, Lead Generation, Product Launch, Customer Support
    - **Real-Time Monitoring**: Track workflow progress and agent performance
    - **Enterprise Integrations**: CRM, Email, Calendar, Project Management tools
    - **Safety & Governance**: Human-in-the-loop approval, compliance checking, audit trails

    ### Technology Stack
    - **Agent Framework**: CrewAI with LangGraph
    - **LLM**: GPT-4 for reasoning, GPT-3.5 for execution
    - **Memory**: Redis (state), PostgreSQL (persistence)
    - **Backend**: FastAPI
    - **Frontend**: React + Streamlit

    ### Version
    1.0.0

    ### Documentation
    Visit our comprehensive documentation for detailed information on:
    - Getting started
    - API reference
    - Workflow configuration
    - Agent capabilities
    - Deployment guide

    ### Support
    For issues and feature requests, please contact support or create an issue in the repository.
    """)


if __name__ == "__main__":
    main()
