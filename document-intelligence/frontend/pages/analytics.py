"""
Analytics dashboard page for Streamlit.
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


def show():
    """Display analytics dashboard."""
    st.title("📊 Analytics Dashboard")

    # Tabs for different analytics
    tab1, tab2, tab3 = st.tabs(["📄 Documents", "🔍 Search", "🧠 Content Intelligence"])

    with tab1:
        show_document_analytics()

    with tab2:
        show_search_analytics()

    with tab3:
        show_content_intelligence()


def show_document_analytics():
    """Display document analytics."""
    st.markdown("### Document Overview")

    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/analytics/overview"
        )

        if response.status_code == 200:
            data = response.json()

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Documents", data.get("total_documents", 0))

            with col2:
                st.metric("Total Pages", data.get("total_pages", 0))

            with col3:
                st.metric("Total Words", f"{data.get('total_words', 0):,}")

            with col4:
                avg_time = data.get("avg_processing_time")
                st.metric(
                    "Avg. Processing Time",
                    f"{avg_time:.2f}s" if avg_time else "N/A"
                )

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                # Documents by type
                type_data = data.get("documents_by_type", {})
                if type_data:
                    fig = px.pie(
                        names=list(type_data.keys()),
                        values=list(type_data.values()),
                        title="Documents by Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available")

            with col2:
                # Documents by status
                status_data = data.get("documents_by_status", {})
                if status_data:
                    fig = px.bar(
                        x=list(status_data.keys()),
                        y=list(status_data.values()),
                        title="Documents by Status",
                        labels={"x": "Status", "y": "Count"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available")

        else:
            st.error("Failed to fetch document analytics")

    except Exception as e:
        st.error(f"API error: {str(e)}")
        st.info("Make sure the backend API is running.")


def show_search_analytics():
    """Display search analytics."""
    st.markdown("### Search Statistics")

    # Days selector
    days = st.slider("Days to Analyze", 7, 90, 30)

    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/analytics/search-stats",
            params={"days": days}
        )

        if response.status_code == 200:
            data = response.json()

            # Metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Searches", data.get("total_searches", 0))

            with col2:
                avg_time = data.get("avg_execution_time", 0)
                st.metric("Avg. Execution Time", f"{avg_time:.0f}ms")

            with col3:
                strategies = data.get("searches_by_strategy", {})
                most_used = max(strategies.items(), key=lambda x: x[1])[0] if strategies else "N/A"
                st.metric("Most Used Strategy", most_used)

            st.markdown("---")

            # Top queries
            st.markdown("### 🔥 Top Queries")

            top_queries = data.get("top_queries", [])
            if top_queries:
                df = pd.DataFrame(top_queries)
                st.dataframe(
                    df,
                    column_config={
                        "query": "Query",
                        "count": "Count",
                        "avg_score": st.column_config.NumberColumn(
                            "Avg. Score",
                            format="%.3f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No search data available")

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                # Searches by strategy
                strategy_data = data.get("searches_by_strategy", {})
                if strategy_data:
                    fig = px.pie(
                        names=list(strategy_data.keys()),
                        values=list(strategy_data.values()),
                        title="Searches by Strategy"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Searches over time
                time_data = data.get("searches_over_time", [])
                if time_data:
                    df = pd.DataFrame(time_data)
                    fig = px.line(
                        df,
                        x="date",
                        y="count",
                        title="Search Volume Over Time",
                        labels={"date": "Date", "count": "Number of Searches"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Failed to fetch search analytics")

    except Exception as e:
        st.error(f"API error: {str(e)}")


def show_content_intelligence():
    """Display content intelligence analytics."""
    st.markdown("### Content Intelligence")

    try:
        response = requests.get(
            f"http://{settings.api_host}:{settings.api_port}/api/analytics/content-intelligence"
        )

        if response.status_code == 200:
            data = response.json()

            # Metrics
            col1, col2 = st.columns(2)

            with col1:
                avg_length = data.get("avg_document_length", 0)
                st.metric("Avg. Document Length", f"{avg_length:.0f} words")

            with col2:
                lang_dist = data.get("language_distribution", {})
                most_common_lang = max(lang_dist.items(), key=lambda x: x[1])[0] if lang_dist else "N/A"
                st.metric("Most Common Language", most_common_lang.upper())

            st.markdown("---")

            # Language distribution
            st.markdown("### 🌍 Language Distribution")

            lang_data = data.get("language_distribution", {})
            if lang_data:
                fig = px.bar(
                    x=list(lang_data.keys()),
                    y=list(lang_data.values()),
                    title="Documents by Language",
                    labels={"x": "Language", "y": "Count"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No language data available")

            # Top entities (placeholder)
            st.markdown("### 🏷️ Top Entities")
            entities = data.get("top_entities", [])
            if entities:
                df = pd.DataFrame(entities)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Entity extraction not yet implemented")

            # Top topics (placeholder)
            st.markdown("### 📑 Top Topics")
            topics = data.get("top_topics", [])
            if topics:
                df = pd.DataFrame(topics)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Topic modeling not yet implemented")

        else:
            st.error("Failed to fetch content intelligence")

    except Exception as e:
        st.error(f"API error: {str(e)}")
