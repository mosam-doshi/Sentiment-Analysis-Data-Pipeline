import pandas as pd
import os

# ==================================
# RELATIVE PATH CONFIGURATION
# ==================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE    = os.path.join("src/send/tweets_with_sentiment.csv")
METRICS_FILE = os.path.join(BASE_DIR, "..", "data/analysis", "dashboard_metrics.csv")
INSIGHT_FILE = os.path.join(BASE_DIR, "..", "data/analysis", "dashboard_insights.csv")
STATE_FILE   = os.path.join(BASE_DIR, "..", "data/analysis", "prev_state.csv")

print("🚀 Running Twitter Analysis...")

# ==================================
# STATE FUNCTIONS
# ==================================

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return pd.read_csv(STATE_FILE)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_state(neg):
    pd.DataFrame([{"negative": neg}]).to_csv(STATE_FILE, index=False)

# ==================================
# MAIN ANALYSIS FUNCTION
# ==================================

def run_analysis():

    if not os.path.exists(DATA_FILE):
        print("❌ Input CSV not found.")
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        print("⚠️ CSV is empty.")
        return

    # -----------------------
    # Data Cleaning
    # -----------------------
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['sentiment_label', 'timestamp'])
    df['sentiment_label'] = df['sentiment_label'].str.lower()
    df['hour'] = df['timestamp'].dt.hour

    total = len(df)

    # -----------------------
    # SENTIMENT METRICS
    # -----------------------
    sentiment_counts = df['sentiment_label'].value_counts()

    # -----------------------
    # TOPIC METRICS
    # -----------------------
    topic_scores = df.groupby('topic')['sentiment_score'].mean()

    # -----------------------
    # TIME METRICS
    # -----------------------
    hour_counts = df.groupby('hour').size()

    # -----------------------
    # SOURCE METRICS
    # -----------------------
    source_counts = df.groupby(['source','sentiment_label']).size()

    # -----------------------
    # BUILD METRICS FILE
    # -----------------------
    rows = []

    for k,v in sentiment_counts.items():
        rows.append(["sentiment", k, "", v])

    for k,v in topic_scores.items():
        rows.append(["topic", k, round(v,2), ""])

    for k,v in hour_counts.items():
        rows.append(["hour", k, "", v])

    for (src, sent), v in source_counts.items():
        rows.append(["source", f"{src}-{sent}", "", v])

    metrics_df = pd.DataFrame(
        rows,
        columns=["metric_type","dimension","value","count"]
    )
    metrics_df.to_csv(METRICS_FILE, index=False)

    # -----------------------
    # KPI INSIGHTS
    # -----------------------
    pos_pct = round((sentiment_counts.get("positive",0)/total)*100,2)
    neg_pct = round((sentiment_counts.get("negative",0)/total)*100,2)
    neu_pct = round((sentiment_counts.get("neutral",0)/total)*100,2)

    trending_topic = topic_scores.sort_values(ascending=False).index[0]
    peak_hour = hour_counts.idxmax()
    polarization = abs(pos_pct - neg_pct)

    # Spike detection (optional history)
    prev = load_state()
    spike = "No Spike"
    if not prev.empty:
        if neg_pct - prev.iloc[0]['negative'] > 15:
            spike = "🚨 Negative Spike"

    save_state(neg_pct)

    insights = [
        ["Total Tweets", total],
        ["Positive %", f"{pos_pct}%"],
        ["Negative %", f"{neg_pct}%"],
        ["Neutral %", f"{neu_pct}%"],
        ["Trending Topic", trending_topic],
        ["Peak Hour", f"{peak_hour}:00"],
        ["Polarization Index", round(polarization,2)],
        ["Spike Alert", spike]
    ]

    insight_df = pd.DataFrame(insights, columns=["metric","value"])
    insight_df.to_csv(INSIGHT_FILE, index=False)

    print("✅ Analysis completed successfully.")
    print("📂 Files generated:")
    print(" - dashboard_metrics.csv")
    print(" - dashboard_insights.csv")

# ==================================
# RUN ONCE
# ==================================

if __name__ == "__main__":
    run_analysis()
