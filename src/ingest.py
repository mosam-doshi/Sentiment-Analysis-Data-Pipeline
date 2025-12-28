import feedparser
import pandas as pd
import time
import random
import html
from pathlib import Path
from urllib.parse import quote
from datetime import date, timedelta

def run_dynamic_bulk_ingest():
    # 1. SETUP DYNAMIC DATES
    # Automatically gets yesterday's date for a rolling 24-hour window
    today_dt = date.today()
    yesterday_dt = today_dt - timedelta(days=1)
    
    target_day = yesterday_dt.isoformat()  # YYYY-MM-DD
    next_day = today_dt.isoformat()        # YYYY-MM-DD

    # 2. SETUP PATHS
    # This keeps everything in your project structure
    project_root = Path(__file__).resolve().parent.parent
    data_folder = project_root / "data" / "raw"
    file_path = data_folder / "raw_data.csv"
    data_folder.mkdir(parents=True, exist_ok=True)

    # 3. HIGH-DENSITY KEYWORDS
    keywords = [
        "GenZ India", "Indian Youth", "Student Life India", "Instagram India", 
        "Twitter India trends", "India Tech Startups", "UPSC Aspirants", 
        "CBSE Exams", "Indian Gamers", "Bollywood GenZ", "India Fashion Trends",
        "Gig Economy India", "Digital India", "India Entrepreneurship", 
        "Mental Health India", "College Festivals India", "India Skill Development"
    ]
    
    all_new_data = []
    print(f"📡 --- India Data Pipeline ---")
    print(f"📅 Window: {target_day} to {next_day}")
    print(f"🚀 Starting fetch for {len(keywords)} shards...")

    for kw in keywords:
        # Construct dynamic query
        query_str = f"{kw} after:{target_day} before:{next_day}"
        encoded_query = quote(query_str)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        print(f"🔍 Fetching {kw}...", end=" ", flush=True)
        
        # User-Agent to prevent bot detection
        feed = feedparser.parse(rss_url, agent="Mozilla/5.0")
        
        batch = []
        for entry in feed.entries:
            clean_text = html.unescape(entry.title).split(' - ')[0]
            batch.append({
                'id': entry.id,
                'topic': kw,
                'text': clean_text,
                'timestamp': entry.published,
                'run_date': target_day, # Tagging when this was fetched
                'source': entry.source.title if hasattr(entry, 'source') else "News"
            })
        
        all_new_data.extend(batch)
        print(f"Added {len(batch)} rows.")
        
        # Short ethical delay
        time.sleep(random.uniform(1.2, 2.5))

    # 4. SAVE & DEDUPLICATE (Append Mode)
    if all_new_data:
        new_df = pd.DataFrame(all_new_data)
        
        # If the file already exists, we combine and remove duplicates across all days
        if file_path.exists():
            existing_df = pd.read_csv(file_path, encoding='utf-8-sig')
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            final_df = combined_df.drop_duplicates(subset=['id'])
        else:
            final_df = new_df.drop_duplicates(subset=['id'])

        try:
            final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"\n✅ SUCCESS!")
            print(f"📊 Total Dataset Size: {len(final_df)} rows")
            print(f"📍 File updated: {file_path}")
        except PermissionError:
            print(f"\n❌ ERROR: Permission Denied. Please close 'raw_data.csv' in Excel.")
    else:
        print(f"❌ No new data found for {target_day}.")

if __name__ == "__main__":
    run_dynamic_bulk_ingest()