import pandas as pd
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

INPUT_FILE = "data\processed\cleaned_data.csv"
OUTPUT_FILE ="src/send/tweets_with_sentiment.csv"

df = pd.read_csv(INPUT_FILE)

def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["clean_text"] = df["text"].apply(clean_text)

sia = SentimentIntensityAnalyzer()

def extract_sentiment_features(text):
    scores = sia.polarity_scores(text)
    return pd.Series({
        "sentiment_score": scores["compound"],
        "sent_pos": scores["pos"],
        "sent_neu": scores["neu"],
        "sent_neg": scores["neg"],
        "sent_confidence": abs(scores["compound"])
    })

df[["sentiment_score", "sent_pos", "sent_neu", "sent_neg", "sent_confidence"]] = (
    df["clean_text"].apply(extract_sentiment_features)
)

def get_sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

df["sentiment_label"] = df["sentiment_score"].apply(get_sentiment_label)

df.to_csv(OUTPUT_FILE, index=False)

print("Sentiment analysis completed successfully.")
print("Output saved at:", OUTPUT_FILE)
