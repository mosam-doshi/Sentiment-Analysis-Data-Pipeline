# Project Execution Order

This document outlines the logical execution order of the Python files in the project and the data flow through the pipeline.

## 1. Data Ingestion
*   **File:** `src/ingest.py` (or `main.py`)
*   **Purpose:** Fetches raw news data from RSS feeds.
*   **Output:** Saves to `data/raw/raw_data.csv`.

## 2. Data Cleaning
*   **File:** `src/transform.py`
*   **Purpose:** Cleans timestamps, removes duplicates, and standardizes data.
*   **Input:** `data/raw/raw_data.csv`
*   **Output:** `data/processed/cleaned_data.csv`.

## 3. Sentiment Analysis
*   **File:** `src/send/Sentiment.py`
*   **Purpose:** Applies NLTK VADER sentiment analysis to score text.
*   **Input:** `data/processed/cleaned_data.csv`
*   **Output:** `src/send/tweets_with_sentiment.csv`.

## 4. Aggregation & Metrics
*   **File:** `analysis/analysis.py`
*   **Purpose:** Calculates KPIs, behavioral trends, and source statistics.
*   **Input:** `src/send/tweets_with_sentiment.csv`
*   **Output:** Generates files in `data/analysis/`:
    *   `dashboard_metrics.csv`
    *   `dashboard_insights.csv`
    *   `genz_state.csv`

## 5. Visualization
*   **File:** `dashboard.py`
*   **Purpose:** Displays the interactive Streamlit dashboard.
*   **Input:** The processed CSV files from `data/analysis/`.

---

**Data Flow Summary:**
`ingest.py` → `transform.py` → `Sentiment.py` → `analysis.py` → `dashboard.py`
