import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from pathlib import Path

# ==============================================================================
# 0. CONFIGURATION & PAGE SETUP
# ==============================================================================
st.set_page_config(
    page_title="Sentiment AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Light Theme & Glassmorphism CSS
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background: radial-gradient(circle, #f8f9fa 0%, #e9ecef 100%);
        color: #31333F;
    }
    
    /* Metrics Cards (Neomorphism/Glass) */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(0, 0, 0, 0.05);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
        backdrop-filter: blur(10px);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, #0052D4 0%, #4364F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Removal of default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chart Containers */
    .element-container {
        border-radius: 10px;
        overflow: hidden;
        background-color: rgba(255, 255, 255, 0.5);
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. DATA LOADING
# ==============================================================================
# Use relative paths consistent with project structure
BASE_DIR = Path(__file__).parent
METRICS_PATH = BASE_DIR / "data" / "analysis" / "dashboard_metrics.csv"
INSIGHTS_PATH = BASE_DIR / "data" / "analysis" / "dashboard_insights.csv"
RAW_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"

@st.cache_data(ttl=60)  # Cache requires refresh every 60s
def load_data():
    try:
        metrics_df = pd.read_csv(METRICS_PATH)
        insights_df = pd.read_csv(INSIGHTS_PATH)
        return metrics_df, insights_df
    except FileNotFoundError:
        return None, None

metrics_df, insights_df = load_data()

# ==============================================================================
# 2. HEADER & KPI SECTION
# ==============================================================================
st.title("📡 Sentiment Analysis Dashboard")
st.markdown("Real-time analysis of news & social trends affecting Indian Youth.")

if metrics_df is None or insights_df is None:
    st.error("⚠️ Data files not found. Please run the analysis pipeline first!")
    st.stop()

# Helper to extract KPI value
def get_kpi(label):
    val = insights_df[insights_df['metric'] == label]['value'].values
    return val[0] if len(val) > 0 else "N/A"

# KPI ROW
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Analyzed", get_kpi("Total Tweets"), delta=None)

with kpi2:
    sentiment_label = "Positive %"
    st.metric("Positivity Index", get_kpi("Positive %"), 
              delta=f"{get_kpi('Polarization Index')} Polarization")

with kpi3:
    st.metric("Trending Topic", get_kpi("Trending Topic"))

with kpi4:
    spike = get_kpi("Spike Alert")
    delta_color = "inverse" if "Alert" in str(spike) or "Spike" in str(spike) else "normal"
    st.metric("System Status", "Active", delta=spike, delta_color=delta_color)

st.divider()

# ==============================================================================
# 3. VISUALIZATION ROW 1 (Sentiment)
# ==============================================================================
col1, col2 = st.columns([1, 2])

# A. Sentiment Pie Chart
with col1:
    st.subheader("Sentiment Distribution")
    sent_data = metrics_df[metrics_df['metric_type'] == 'sentiment']
    
    fig_donut = px.pie(
        sent_data, 
        names='dimension', 
        values='count', 
        color='dimension',
        color_discrete_map={
            "positive": "#00CC96",
            "negative": "#EF553B",
            "neutral": "#636EFA"
        },
        hole=0.6
    )
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333333'},
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[dict(text='AI<br>Score', x=0.5, y=0.5, font_size=20, showarrow=False, font_color='#333333')]
    )
    st.plotly_chart(fig_donut, width='stretch')

# B. Sentiment by Topic Bar Chart
with col2:
    st.subheader("Sentiment Intensity by Topic")
    topic_data = metrics_df[metrics_df['metric_type'] == 'topic'].sort_values(by="value", ascending=True)
    
    fig_bar = px.bar(
        topic_data, 
        y='dimension', 
        x='value', 
        orientation='h',
        color='value',
        color_continuous_scale=['#EF553B', '#636EFA', '#00CC96'],
        text='value'
    )
    
    fig_bar.update_layout(
        xaxis_title="Avg Sentiment Score (-1 to +1)", 
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333333'},
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_bar, width='stretch')

# ==============================================================================
# 4. VISUALIZATION ROW 2 (Time & Source)
# ==============================================================================
col3, col4 = st.columns(2)

# C. Hourly Activity Area Chart
with col3:
    st.subheader("24h Activity Volume")
    hour_data = metrics_df[metrics_df['metric_type'] == 'hour'].sort_values(by="dimension")
    
    fig_area = px.area(
        hour_data, 
        x='dimension', 
        y='count',
        markers=True,
        line_shape='spline'
    )
    # CORRECTED fillcolor (prev. fill_color)
    fig_area.update_traces(line_color='#AB63FA', fillcolor='rgba(171, 99, 250, 0.2)')
    fig_area.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Volume",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333333'},
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_area, width='stretch')

# D. Source Treemap
with col4:
    st.subheader("News Source Impact")
    source_data = metrics_df[metrics_df['metric_type'] == 'source']
    # Parse "Source-Sentiment" string back to two columns
    source_data[['Source', 'SentLabel']] = source_data['dimension'].str.split('-', n=1, expand=True)
    
    fig_tree = px.treemap(
        source_data,
        path=[px.Constant("All Sources"), 'Source', 'SentLabel'],
        values='count',
        color='SentLabel',
        color_discrete_map={
            "positive": "#00CC96",
            "negative": "#EF553B",
            "neutral": "#636EFA",
            "(?)": "#333333"
        }
    )
    fig_tree.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, l=0, r=0, b=0)
    )
    st.plotly_chart(fig_tree, width='stretch')

# ==============================================================================
# 5. FOOTER & REFRESH
# ==============================================================================
st.markdown("---")
col_f1, col_f2 = st.columns([8, 2])
with col_f1:
    st.caption(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')} | Data Source: Google News RSS")
with col_f2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
