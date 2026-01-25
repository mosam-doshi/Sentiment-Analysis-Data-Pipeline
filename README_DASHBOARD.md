# 📊 Dashboard Documentation

This document provides a detailed explanation of the **Sentiment Analysis Dashboard**, including the meaning of each tile and the source of its data.

## 🧠 The Data Journey (Where it comes from)

Before the data hits the dashboard, it flows through these pipeline stages:

1.  **Ingestion (`src/ingest.py`)**: Fetches raw news from Google News RSS.
2.  **Transformation (`src/transform.py`)**: Cleans, deduplicates, and formats the data.
3.  **Sentiment Analysis (`src/send/Sentiment.py`)**: Uses **NLTK VADER AI** to score text from -1 (Negative) to +1 (Positive).
4.  **Aggregation (`analysis/analysis.py`)**: Calculates the math and saves two key files:
    *   `data/analysis/dashboard_insights.csv` (Single numbers for top KPI cards).
    *   `data/analysis/dashboard_metrics.csv` (Detailed tables for the charts).

---

## 🧱 Dashboard Tiles Explained

### 1. Top KPI Cards
These four numbers give you an instant health check of the data.

| Tile Name | Meaning | Calculation Logic | Source Code |
| :--- | :--- | :--- | :--- |
| **Total Analyzed** | Total number of news items/tweets in the current 24h window. | `Count(All Rows)` | `analysis.py` (line 56) |
| **Positivity Index** | The percentage of news considered "Positive" by the AI. <br>*(Small Text: Polarization % - gap between Pos vs Neg)* | `(Positive Count / Total) * 100` | `analysis.py` (lines 104, 110) |
| **Trending Topic** | The topic with the **highest positive sentiment score**. | Topic with max average compound score. | `analysis.py` (line 108) |
| **System Status** | Smart alert system. Shows "Active" normally, effectively a "Spike Alert". | Triggers **RED** if Negative % jumps >15% vs previous run. | `analysis.py` (lines 115-117) |

### 2. The Charts (Visualizations)
These interactive charts visualize the detailed metrics.

#### 🥧 Sentiment Distribution (Pie Chart)
*   **What it is:** The overall mood of the Indian GenZ news cycle.
*   **Data:** Counts of `Positive` vs `Negative` vs `Neutral`.
*   **Insight:** 
    *   Big **Neutral** slice = Factual/Informative news.
    *   Big **Negative** slice = Crisis or bad news day.

#### 📊 Sentiment Intensity by Topic (Bar Chart)
*   **What it is:** Ranks keywords (e.g., "GenZ India", "UPSC Aspirants") by their emotional tone.
*   **Data:** Average compound sentiment score (-1.0 to +1.0).
*   **Visuals:** 
    *   **Green bars (Right)** = Positive topics.
    *   **Red bars (Left)** = Negative topics.

#### 📈 24h Activity Volume (Area Chart)
*   **What it is:** A timeline of when news was published.
*   **Data:** Volume of items grouped by **Hour of Day (0-23)**.
*   **Insight:** Peaks usually indicate morning (8-10 AM) or evening (6-8 PM) news cycles. Flat lines suggest ingestion might have stopped.

#### 🌳 News Source Impact (Treemap)
*   **What it is:** Which publishers are contributing the most content.
*   **Data:** Grouped by `Source Name` (e.g., "Times of India") and colored by sentiment.
*   **Insight:** 
    *   **Size of block** = Volume of news from that source.
    *   **Color** = Whether that source is writing mostly positive (Green) or negative (Red) stories.

