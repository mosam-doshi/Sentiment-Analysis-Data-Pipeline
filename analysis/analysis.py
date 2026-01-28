import pandas as pd
import os
import numpy as np
from datetime import datetime

# ==================================================
# PATH CONFIGURATION (RELATIVE)
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "..", "src", "send", "tweets_with_sentiment.csv")
METRICS_FILE = os.path.join(BASE_DIR, "..", "data", "analysis", "dashboard_metrics.csv")
INSIGHT_FILE = os.path.join(BASE_DIR, "..", "data", "analysis", "dashboard_insights.csv")
STATE_FILE = os.path.join(BASE_DIR, "..", "data", "analysis", "genz_state.csv")

os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)

print("Running Gen-Z Behavioral Analytics Engine (Safe Mode + Source Metrics)...")

# ==================================================
# STATE HANDLING (SAFE)
# ==================================================

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            df = pd.read_csv(STATE_FILE)
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def append_state(row_dict):
    try:
        old_df = load_state()
        new_row = pd.DataFrame([row_dict])

        # Align columns automatically
        if not old_df.empty:
            combined = pd.concat([old_df, new_row], ignore_index=True, sort=False)
        else:
            combined = new_row

        combined.to_csv(STATE_FILE, index=False)

    except Exception as e:
        print("State file update warning:", e)

# ==================================================
# MAIN ANALYSIS FUNCTION
# ==================================================

def run_analysis():

    if not os.path.exists(DATA_FILE):
        print("Input CSV not found")
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        print("CSV empty")
        return

    # ----------------------------
    # Cleaning
    # ----------------------------
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors="coerce")
    df = df.dropna(subset=['timestamp', 'sentiment_label'])
    df['sentiment_label'] = df['sentiment_label'].str.lower()
    df['hour'] = df['timestamp'].dt.hour
    df['source'] = df['source'].fillna("Unknown")

    total = len(df)

    # ----------------------------
    # Base Metrics
    # ----------------------------
    sentiment_counts = df['sentiment_label'].value_counts()
    topic_counts = df['topic'].value_counts()
    hour_counts = df['hour'].value_counts()
    confidence_avg = df['sent_confidence'].mean()
    volatility = df['sentiment_score'].std()

    positive_pct = (sentiment_counts.get("positive",0)/total)*100
    negative_pct = (sentiment_counts.get("negative",0)/total)*100
    neutral_pct  = (sentiment_counts.get("neutral",0)/total)*100

    # ----------------------------
    # SOURCE SENTIMENT METRICS NEW
    # ----------------------------
    source_sentiment_counts = (
        df.groupby(['source','sentiment_label'])
          .size()
          .sort_values(ascending=False)
    )

    # ----------------------------
    # DASHBOARD METRICS FILE
    # ----------------------------
    metrics_rows = []

    # Sentiment
    for k,v in sentiment_counts.items():
        metrics_rows.append(["sentiment", k, "", v])

    # Topic volume
    for k,v in topic_counts.items():
        metrics_rows.append(["topic_volume", k, "", v])

    # Hourly activity
    for k,v in hour_counts.items():
        metrics_rows.append(["hour_activity", k, "", v])

    # Source sentiment
    for (src, sent), v in source_sentiment_counts.items():
        metrics_rows.append(["source", f"{src}-{sent}", "", v])

    metrics_df = pd.DataFrame(
        metrics_rows,
        columns=["metric_type","dimension","value","count"]
    )

    metrics_df.to_csv(METRICS_FILE, index=False)

    # ----------------------------
    # GEN-Z BEHAVIOR INDICES
    # ----------------------------

    mind_growth = round((neutral_pct + (confidence_avg * 100)) / 2, 2)

    edu_keywords = ["education","college","exam","career","degree","skill"]
    edu_mentions = df['clean_text'].str.contains("|".join(edu_keywords), case=False, na=False)
    education_awareness = round((edu_mentions.sum() / total) * 100, 2)

    political_maturity = round(100 - abs(positive_pct - negative_pct), 2)

    emotional_stability = round(1 / (1 + volatility), 3)

    dominant_group = topic_counts.idxmax()

    night_ratio = round((len(df[df['hour'] >= 22]) / total) * 100, 2)

    responsiveness = round((hour_counts.max() / total) * 100, 2)

    leadership_voice = round((len(df[df['sent_confidence'] > 0.75]) / total) * 100, 2)

    psychological_resilience = round(100 - (volatility * 100), 2)

    # ----------------------------
    # SAFE TREND SENSITIVITY
    # ----------------------------
    prev_state = load_state()
    trend_sensitivity = "Stable"

    if not prev_state.empty and 'dominant_group' in prev_state.columns:
        last_group = prev_state.iloc[-1]['dominant_group']
        if dominant_group != last_group:
            trend_sensitivity = "High"

    # ----------------------------
    # APPEND STATE SAFELY
    # ----------------------------
    state_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mind_growth": mind_growth,
        "education_awareness": education_awareness,
        "political_maturity": political_maturity,
        "emotional_stability": emotional_stability,
        "psychological_resilience": psychological_resilience,
        "trend_sensitivity": trend_sensitivity,
        "leadership_voice": leadership_voice,
        "digital_lifestyle": night_ratio,
        "social_responsiveness": responsiveness,
        "dominant_group": dominant_group
    }

    append_state(state_row)

    # ----------------------------
    # DASHBOARD INSIGHTS
    # ----------------------------
    insights = [
        ["Mind Growth Index", mind_growth],
        ["Education Awareness %", education_awareness],
        ["Political Maturity Score", political_maturity],
        ["Emotional Stability Index", emotional_stability],
        ["Psychological Resilience Score", psychological_resilience],
        ["Trend Sensitivity", trend_sensitivity],
        ["Leadership Voice %", leadership_voice],
        ["Digital Lifestyle %", night_ratio],
        ["Social Responsiveness %", responsiveness],
        ["Dominant Interest Group", dominant_group]
    ]

    insight_df = pd.DataFrame(insights, columns=["metric","value"])
    insight_df.to_csv(INSIGHT_FILE, index=False)

    print("Gen-Z Behavioral Insights Updated Safely")
    print("Files Generated:")
    print(" - dashboard_metrics.csv")
    print(" - dashboard_insights.csv")
    print(" - genz_state.csv")

# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    run_analysis()