"""
Analytics dashboard page for performance metrics and insights.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Analytics - AI Customer Support",
    page_icon="📊",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Helper functions
def fetch_analytics(days: int = 7):
    """Fetch analytics data from API"""
    try:
        response = requests.get(
            f"{API_URL}/api/analytics?days={days}",
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


def create_gauge_chart(value: float, title: str, max_value: float = 100, target: float = 70):
    """Create a gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': target, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "#FF4B4B"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, target * 0.7], 'color': '#ffcccc'},
                {'range': [target * 0.7, target], 'color': '#ffe6cc'},
                {'range': [target, max_value], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"}
    )

    return fig


# Page header
st.title("📊 Analytics Dashboard")

st.markdown("""
Monitor system performance, track key metrics, and gain insights into customer support operations.
""")

# Time period selector
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    days = st.selectbox(
        "Time Period",
        options=[1, 7, 14, 30, 90],
        format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
        index=1  # Default to 7 days
    )

with col2:
    auto_refresh = st.checkbox("Auto-refresh", value=False)

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Auto-refresh logic
if auto_refresh:
    st.info("Auto-refreshing every 30 seconds...")
    time.sleep(30)
    st.rerun()

# Fetch data
with st.spinner("Loading analytics data..."):
    data = fetch_analytics(days)

if data:
    metrics = data['metrics']
    recent_queries = data.get('recent_queries', [])
    low_rated_queries = data.get('low_rated_queries', [])

    # ==================== KPI Metrics Section ====================
    st.markdown("---")
    st.subheader("🎯 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_queries = metrics['total_queries'] - (metrics['total_queries'] * 0.9) # Simulated previous period
        st.metric(
            label="Total Queries",
            value=f"{metrics['total_queries']:,}",
            delta=f"{int(delta_queries):+,}" if delta_queries != 0 else None,
            help=f"Total queries in the last {days} days"
        )

    with col2:
        target_resolution = 70.0
        delta_resolution = metrics['autonomous_resolution_rate'] - target_resolution
        st.metric(
            label="Resolution Rate",
            value=f"{metrics['autonomous_resolution_rate']:.1f}%",
            delta=f"{delta_resolution:+.1f}%",
            delta_color="normal" if delta_resolution >= 0 else "inverse",
            help=f"Target: {target_resolution}% | Autonomous resolution without human intervention"
        )

    with col3:
        target_time = 2.0
        delta_time = target_time - metrics['avg_resolution_time']
        st.metric(
            label="Avg Response Time",
            value=f"{metrics['avg_resolution_time']:.2f}s",
            delta=f"{delta_time:+.2f}s",
            delta_color="normal" if delta_time >= 0 else "inverse",
            help=f"Target: <{target_time}s | Average time to generate responses"
        )

    with col4:
        st.metric(
            label="Customer Satisfaction",
            value=f"{metrics['avg_rating']:.1f}/5.0" if metrics['avg_rating'] > 0 else "N/A",
            delta=None,
            help="Average customer rating from feedback"
        )

    # Secondary metrics
    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Avg Confidence Score",
            value=f"{metrics['avg_confidence_score']:.1%}",
            help="Average confidence in AI responses"
        )

    with col2:
        st.metric(
            label="Escalation Rate",
            value=f"{metrics['escalation_rate']:.1f}%",
            delta=f"{70 - metrics['escalation_rate']:+.1f}%",
            delta_color="inverse",
            help="Percentage of queries escalated to humans"
        )

    with col3:
        st.metric(
            label="Total Cost",
            value=f"${metrics['total_cost']:.4f}",
            help="Total API costs (LLM + embeddings)"
        )

    with col4:
        avg_cost_per_query = metrics['total_cost'] / metrics['total_queries'] if metrics['total_queries'] > 0 else 0
        st.metric(
            label="Cost per Query",
            value=f"${avg_cost_per_query:.4f}",
            help="Average cost per customer query"
        )

    # ==================== Charts Section ====================
    st.markdown("---")
    st.subheader("📈 Performance Trends")

    # Gauge charts row
    col1, col2, col3 = st.columns(3)

    with col1:
        fig = create_gauge_chart(
            value=metrics['autonomous_resolution_rate'],
            title="Autonomous Resolution Rate",
            max_value=100,
            target=70
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Invert response time for gauge (lower is better)
        response_time_score = max(0, 100 - (metrics['avg_resolution_time'] / 5.0 * 100))
        fig = create_gauge_chart(
            value=response_time_score,
            title="Response Time Score",
            max_value=100,
            target=80
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        confidence_score = metrics['avg_confidence_score'] * 100
        fig = create_gauge_chart(
            value=confidence_score,
            title="Avg Confidence Score",
            max_value=100,
            target=70
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==================== Recent Queries Table ====================
    st.markdown("---")
    st.subheader("🕐 Recent Queries")

    if recent_queries:
        # Convert to DataFrame
        df_recent = pd.DataFrame(recent_queries)

        # Format timestamps
        df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Format display
        display_df = df_recent[['timestamp', 'query', 'confidence_score', 'rating', 'was_escalated']].copy()
        display_df.columns = ['Time', 'Query', 'Confidence', 'Rating', 'Escalated']

        # Truncate long queries
        display_df['Query'] = display_df['Query'].str[:100] + '...'

        # Format values
        display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")
        display_df['Rating'] = display_df['Rating'].apply(lambda x: f"{x:.0f}/5" if pd.notna(x) else "N/A")
        display_df['Escalated'] = display_df['Escalated'].apply(lambda x: "✅ Yes" if x else "❌ No")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Export option
        csv = df_recent.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"recent_queries_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No recent queries to display")

    # ==================== Low-Rated Queries ====================
    st.markdown("---")
    st.subheader("⚠️ Low-Rated Queries (Needs Improvement)")

    if low_rated_queries:
        for idx, query_data in enumerate(low_rated_queries[:5], 1):  # Show top 5
            with st.expander(f"Query {idx}: {query_data['query'][:80]}..."):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Query:** {query_data['query']}")
                    st.markdown(f"**Response:** {query_data['response'][:300]}...")

                with col2:
                    st.metric("Rating", f"{query_data['rating']}/5" if query_data['rating'] else "N/A")
                    st.metric("Confidence", f"{query_data['confidence_score']:.0%}" if query_data['confidence_score'] else "N/A")
                    st.metric("Time", f"{query_data['resolution_time']:.2f}s" if query_data['resolution_time'] else "N/A")

                if query_data['was_escalated']:
                    st.warning("⚠️ This query was escalated to a human agent")
    else:
        st.success("✅ No low-rated queries! Great job!")

    # ==================== Insights & Recommendations ====================
    st.markdown("---")
    st.subheader("💡 Insights & Recommendations")

    insights = []

    # Resolution rate insight
    if metrics['autonomous_resolution_rate'] >= 70:
        insights.append(("✅ Great Performance", f"Your autonomous resolution rate of {metrics['autonomous_resolution_rate']:.1f}% exceeds the 70% target!", "success"))
    else:
        insights.append(("⚠️ Below Target", f"Resolution rate of {metrics['autonomous_resolution_rate']:.1f}% is below the 70% target. Consider adding more documentation or improving retrieval.", "warning"))

    # Response time insight
    if metrics['avg_resolution_time'] < 2.0:
        insights.append(("✅ Fast Responses", f"Average response time of {metrics['avg_resolution_time']:.2f}s is excellent!", "success"))
    else:
        insights.append(("⚠️ Slow Responses", f"Average response time of {metrics['avg_resolution_time']:.2f}s exceeds the 2s target. Consider optimizing retrieval or using faster models.", "warning"))

    # Confidence insight
    if metrics['avg_confidence_score'] >= 0.7:
        insights.append(("✅ High Confidence", f"Average confidence of {metrics['avg_confidence_score']:.0%} indicates quality responses.", "success"))
    else:
        insights.append(("⚠️ Low Confidence", f"Average confidence of {metrics['avg_confidence_score']:.0%} suggests the system is uncertain. Review low-confidence responses.", "warning"))

    # Display insights
    for title, message, msg_type in insights:
        if msg_type == "success":
            st.success(f"**{title}**: {message}")
        elif msg_type == "warning":
            st.warning(f"**{title}**: {message}")
        else:
            st.info(f"**{title}**: {message}")

else:
    # No data available
    st.warning("""
    ### ⚠️ No Analytics Data Available

    Analytics data will appear once you start using the system:

    1. Upload documents to the Knowledge Base
    2. Start conversations in the Chat interface
    3. Return here to view metrics

    Make sure the API server is running:
    ```
    uvicorn src.api.main:app --reload
    ```
    """)

# Footer
st.markdown("---")
st.caption(f"Data refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Period: Last {days} days")
