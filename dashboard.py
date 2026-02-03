import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import timedelta
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Gen-Z Pulse Dashboard",
    layout="wide",
    page_icon=""
)

# =====================================================
# LIGHT UI STYLE
# =====================================================
st.markdown("""
<style>
body { background-color: #f5f7fb; }
div[data-testid="stSidebar"] { background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# PATH CONFIG
# =====================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_FILE     = BASE_DIR / "src" / "send" / "tweets_with_sentiment.csv"
METRICS_FILE  = BASE_DIR / "data" / "analysis" / "dashboard_metrics.csv"
INSIGHT_FILE  = BASE_DIR / "data" / "analysis" / "dashboard_insights.csv"
STATE_FILE    = BASE_DIR / "data" / "analysis" / "genz_state.csv"

# =====================================================
# LOAD DATA SAFELY
# =====================================================
def load_csv(path, name):
    if not path.exists():
        st.error(f"❌ Missing file: {name}")
        st.stop()
    return pd.read_csv(path)

tweets_df  = load_csv(DATA_FILE, "tweets_with_sentiment.csv")
metrics_df = load_csv(METRICS_FILE, "dashboard_metrics.csv")
insight_df = load_csv(INSIGHT_FILE, "dashboard_insights.csv")
state_df   = load_csv(STATE_FILE, "genz_state.csv")

# Cleaning
tweets_df["timestamp"] = pd.to_datetime(tweets_df["timestamp"], errors="coerce")
tweets_df = tweets_df.dropna(subset=["timestamp"])

state_df["timestamp"] = pd.to_datetime(state_df["timestamp"], errors="coerce")
state_df = state_df.dropna(subset=["timestamp"]).sort_values("timestamp")

# =====================================================
# HEADER
# =====================================================
st.title("GenZ Sentiment Pipeline and Analytics Dashboard")
st.caption("Integrated real-time analytics of youth sentiment, mindset growth, media influence and engagement.")

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("Dashboard Filters")

time_window = st.sidebar.radio(
    "📅 Time Window",
    ["Last 2 Days"],
    horizontal=True
)

topics = st.sidebar.multiselect("Topic", sorted(tweets_df["topic"].dropna().unique()))
sources = st.sidebar.multiselect("Source", sorted(tweets_df["source"].dropna().unique()))
sentiments = st.sidebar.multiselect("Sentiment", sorted(tweets_df["sentiment_label"].dropna().unique()))

st.sidebar.header("Project Overview")
st.sidebar.caption("Gen-Z Pulse • Data Engineering + Data Analytics Project")
st.sidebar.markdown("""
This project creates an end-to-end data pipeline for analyzing Gen-Z trends.
It ingests social media data, applying sentiment analysis and topic classification.
Key behavioral metrics like mindset growth and emotional stability are tracked.
The system aggregates insights on media influence and engagement patterns.
This dashboard visualizes these metrics, allowing real-time exploration.
Users can filter by time window, topic, and source to gain deep insights.
Designed to monitor the pulse of Gen-Z, it bridges raw data to actionable intelligence.
""")


# =====================================================
# APPLY TIME FILTER ON STATE
# =====================================================
latest_time = state_df["timestamp"].max()
days = 2
cutoff = latest_time - timedelta(days=days)
state_df = state_df[state_df["timestamp"] >= cutoff]

# =====================================================
# APPLY FILTERS ON TWEETS
# =====================================================
df = tweets_df.copy()

if topics:
    df = df[df["topic"].isin(topics)]
if sources:
    df = df[df["source"].isin(sources)]
if sentiments:
    df = df[df["sentiment_label"].isin(sentiments)]

# =====================================================
# KPI CARDS (FROM dashboard_insights.csv)
# =====================================================
st.subheader("Key Behavioral Indicators")

kpi_cols = st.columns(5)
for i, row in insight_df.iterrows():
    kpi_cols[i % 5].metric(row["metric"], row["value"])

st.divider()

# =====================================================
# 🆕 KPI DISTRIBUTION BAR (Insights File)
# =====================================================
st.subheader("KPI Value Distribution")

kpi_numeric = insight_df.copy()
kpi_numeric["value"] = pd.to_numeric(kpi_numeric["value"], errors="coerce")
kpi_numeric = kpi_numeric.dropna()

fig_kpi_dist = px.bar(
    kpi_numeric,
    x="metric",
    y="value",
    color="value",
    title="KPI Strength Comparison",
    template="plotly_white",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_kpi_dist, use_container_width=True)

# =====================================================
# 🆕 KPI CONTRIBUTION DONUT
# =====================================================
fig_kpi_donut = px.pie(
    kpi_numeric,
    names="metric",
    values="value",
    hole=0.55,
    title="KPI Contribution Distribution",
    template="plotly_white"
)

st.plotly_chart(fig_kpi_donut, use_container_width=True)

# =====================================================
# ROW 1 — SENTIMENT ANALYSIS (Raw Data)
# =====================================================
c1, c2 = st.columns(2)

sentiment_dist = df["sentiment_label"].value_counts().reset_index()
sentiment_dist.columns = ["sentiment", "count"]

fig_sent = px.pie(
    sentiment_dist,
    names="sentiment",
    values="count",
    hole=0.45,
    title="Sentiment Distribution",
    template="plotly_white"
)

c1.plotly_chart(fig_sent, use_container_width=True)

topic_score = df.groupby("topic")["sentiment_score"].mean().reset_index()

fig_topic = px.bar(
    topic_score.sort_values("sentiment_score"),
    x="sentiment_score",
    y="topic",
    orientation="h",
    title="Sentiment Intensity by Topic",
    color="sentiment_score",
    template="plotly_white",
    color_continuous_scale="tealgrn"
)

c2.plotly_chart(fig_topic, use_container_width=True)

# =====================================================
# ROW 2 — ENGAGEMENT + SOURCE ANALYSIS
# =====================================================
c3, c4 = st.columns(2)

df["hour"] = df["timestamp"].dt.hour
hourly = df.groupby("hour").size().reset_index(name="count")

fig_hour = px.area(
    hourly,
    x="hour",
    y="count",
    title="24-Hour Engagement Pattern",
    template="plotly_white"
)

c3.plotly_chart(fig_hour, use_container_width=True)

source_sent = df.groupby(["source", "sentiment_label"]).size().reset_index(name="count")

fig_source = px.treemap(
    source_sent,
    path=["source", "sentiment_label"],
    values="count",
    title="Media Source Influence",
    template="plotly_white"
)

c4.plotly_chart(fig_source, use_container_width=True)

# =====================================================
# 🆕 SOURCE SENTIMENT STACKED BAR
# =====================================================
st.subheader("Media Sentiment Distribution")

source_metrics = metrics_df[metrics_df["metric_type"] == "source"].copy()
split_cols = source_metrics["dimension"].str.rsplit("-", n=1, expand=True)

source_metrics["source"] = split_cols[0]
source_metrics["sentiment"] = split_cols[1]


fig_source_stack = px.bar(
    source_metrics,
    x="source",
    y="count",
    color="sentiment",
    title="Source vs Sentiment Comparison",
    template="plotly_white"
)

st.plotly_chart(fig_source_stack, use_container_width=True)

# =====================================================
# NEW: WORD CLOUD SECTION
# =====================================================
from collections import Counter
import pandas as pd

# --- Helper Function: Intra-day Trend Analysis ---
def get_word_trends(current_df, previous_df, stopwords):
    def get_counts_and_sources(df):
        if df is None or df.empty:
            return Counter(), {}
        
        word_counts = Counter()
        word_to_source = {} 
        
        # Keywords from your ingest script
        valid_topics = [
            "GenZ India", "Indian Youth", "Student Life India", "Instagram India", 
            "Twitter India trends", "India Tech Startups", "UPSC Aspirants", 
            "CBSE Exams", "Indian Gamers", "Bollywood GenZ", "India Fashion Trends",
            "Gig Economy India", "Digital India", "India Entrepreneurship", 
            "Mental Health India", "College Festivals India", "India Skill Development"
        ]
        
        for _, row in df.iterrows():
            # Uses 'topic' as defined in your ingest script
            raw_topic = row.get('topic', 'Unknown')
            topic = raw_topic if raw_topic in valid_topics else "Other"
            
            text = str(row["text"]).lower()
            # Filter: Alpha only, not stopword, length > 3
            words = [w for w in text.split() if w.isalpha() and w not in stopwords and len(w) > 3]
            
            for w in words:
                word_counts[w] += 1
                if w not in word_to_source:
                    word_to_source[w] = Counter()
                word_to_source[w][topic] += 1
        
        top_sources = {w: cats.most_common(1)[0][0] for w, cats in word_to_source.items()}
        return word_counts, top_sources

    curr_counts, curr_sources = get_counts_and_sources(current_df)
    prev_counts, _ = get_counts_and_sources(previous_df)
    
    trends = []
    for word, count in curr_counts.items():
        prev_count = prev_counts.get(word, 0)
        diff = count - prev_count
        
        if diff > 0:
            growth_pct = (diff / prev_count * 100) if prev_count > 0 else 100.0
            source = curr_sources.get(word, "General")
            
            if source != "Other":
                trends.append({
                    "Keyword": word.title(), 
                    "Topic Source": source,
                    "Volume": count, 
                    "Growth": diff,
                    "Growth %": round(growth_pct, 1)
                })
    
    # SAFETY: Return structured empty DF if no trends found
    if not trends:
        return pd.DataFrame(columns=["Keyword", "Topic Source", "Volume", "Growth", "Growth %"])
            
    return pd.DataFrame(trends).sort_values(by="Growth", ascending=False)

# --- UI Layout ---
st.divider()
st.subheader("Emerging Themes & Keywords")

# 1. STOPWORDS (Filtering out noise from headlines)
noise_words = {
    "India", "Indian", "GenZ", "Gen", "Pulse", "Headline", "News", "Video", "says", "will",
    "board", "music", "video", "youtube", "social", "media", "link", "post", "today", 
    "latest", "update", "watch", "click", "read", "more", "back", "told", "even", "made", "shared"
}
custom_stopwords = set(STOPWORDS).union(noise_words)

# Assuming 'df' is loaded from your tweets_with_sentiment.csv
if 'df' in locals() and not df.empty:
    
    # 2. WORD CLOUD
    text_data = " ".join(headline for headline in df["text"].dropna().astype(str))
    
    if text_data.strip():
        wc = WordCloud(
            background_color="#f5f7fb", 
            max_words=150,
            width=1600,
            height=800,
            stopwords=custom_stopwords,
            colormap="viridis", 
            collocations=True
        ).generate(text_data)

        fig_wc, ax = plt.subplots(figsize=(20, 10))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        fig_wc.patch.set_facecolor('#f5f7fb')
        st.pyplot(fig_wc)

    # 3. TREND COMPARISON (Splitting the 24hr window)
    st.subheader("📈 Intra-Day Trending Topics")
    st.caption("Comparing the most recent 8 hours against the rest of the 24-hour fetch.")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        latest_time = df["timestamp"].max()
        
        # Split: Recent 8 hours vs Previous 16 hours
        split_time = latest_time - pd.Timedelta(hours=8)
        
        recent_data = df[df["timestamp"] > split_time]
        older_data = df[df["timestamp"] <= split_time]

        trend_df = get_word_trends(recent_data, older_data, custom_stopwords)

        if not trend_df.empty:
            # Display Top 3 Metrics
            cols = st.columns(3)
            for idx in range(min(3, len(trend_df))):
                row = trend_df.iloc[idx]
                cols[idx].metric(
                    label=f"Spiking: {row['Keyword']}", 
                    value=f"{row['Volume']} mentions", 
                    delta=row['Topic Source'],
                    delta_color="normal" 
                )
            
            # --- UPDATED DATAFRAME WITH PROGRESS BAR ---
            with st.expander("📊 Detailed Keyword Analysis (8hr Window)"):
                st.dataframe(
                    trend_df.head(15), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Keyword": st.column_config.TextColumn("Trending Keyword"),
                        "Topic Source": st.column_config.TextColumn("Origin Topic 🏷️"),
                        "Volume": st.column_config.ProgressColumn(
                            "Today's Count",
                            help="Number of mentions in the recent window",
                            format="%d",
                            min_value=0,
                            max_value=int(trend_df["Volume"].max()) # Scales bar to max hits
                        ),
                        "Growth %": st.column_config.NumberColumn("Growth Rate", format="%d%%")
                    }
                )
        else:
            st.info("No significant keyword spikes detected within this 24-hour window.")
# =====================================================
# ROW 3 — BEHAVIORAL TRENDS (genz_state.csv)
# =====================================================
st.subheader("Gen-Z Behavioral Intelligence Trends")

trend_cols = [
    "mind_growth",
    "education_awareness",
    "political_maturity",
    "emotional_stability",
    "leadership_voice"
]

trend_df = state_df[["timestamp"] + trend_cols]

fig_trend = px.line(
    trend_df,
    x="timestamp",
    y=trend_cols,
    markers=True,
    title="Behavior Evolution (Selected Period)",
    template="plotly_white"
)

fig_trend.update_layout(hovermode="x unified")

st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# 🆕 SENTIMENT VOLUME COMPARISON (dashboard_metrics.csv)
# =====================================================
st.subheader("Sentiment Volume Comparison")

sentiment_metrics = metrics_df[metrics_df["metric_type"] == "sentiment"]

fig_sent_vol = px.bar(
    sentiment_metrics,
    x="dimension",
    y="count",
    color="dimension",
    title="Sentiment Distribution Volume",
    template="plotly_white"
)

st.plotly_chart(fig_sent_vol, use_container_width=True)

# =====================================================
# 🆕 TOPIC POPULARITY RANKING
# =====================================================
st.subheader("Topic Engagement Ranking")

topic_metrics = metrics_df[metrics_df["metric_type"] == "topic_volume"]

fig_topic_rank = px.bar(
    topic_metrics.sort_values("count"),
    x="count",
    y="dimension",
    orientation="h",
    color="count",
    title="Most Discussed Topics",
    template="plotly_white",
    color_continuous_scale="tealgrn"
)

st.plotly_chart(fig_topic_rank, use_container_width=True)

# =====================================================
# ROW 4 — METRICS TABLE (dashboard_metrics.csv)
# =====================================================
st.subheader("Aggregated Metrics Explorer")
st.dataframe(metrics_df, width="stretch")

# =====================================================
# RAW DATA VIEW
# =====================================================
with st.expander("View Raw Tweet Data"):
    st.dataframe(df.head(300), width="stretch")

# =====================================================
# FOOTER
# =====================================================
st.caption("Gen-Z Pulse • Data Engineering + Data Analytics Project")