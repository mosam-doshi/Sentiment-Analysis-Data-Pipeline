import feedparser
import pandas as pd
import time
import random
import html
from pathlib import Path

def run_realtime_ingest(keyword="GenZ", fetch_limit=20):
    project_root = Path(__file__).resolve().parent.parent
    data_folder = project_root / "data" / "raw"
    file_path = data_folder / "raw_data.csv"
    data_folder.mkdir(parents=True, exist_ok=True)

    # CHANGE: 'when:1h' for the absolute freshest data
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=en-IN&gl=IN&ceid=IN:en"
    
    # CHANGE: Lower wait time for testing (60 seconds)
    base_wait = 60 

    print(f"--- Fast-Track India Pipeline: '{keyword}' ---")

    try:
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Fetching...")
            feed = feedparser.parse(rss_url)

            if feed.entries:
                new_entries = []
                for entry in feed.entries[:fetch_limit]:
                    clean_text = html.unescape(entry.title).split(' - ')[0]
                    source_name = entry.source.title if hasattr(entry, 'source') else "Twitter"
                    new_entries.append({
                        'id': entry.id,
                        'source': source_name,
                        'timestamp': entry.published,
                        'text': clean_text
                    })

                new_df = pd.DataFrame(new_entries)
                
                if file_path.exists():
                    existing_df = pd.read_csv(file_path, encoding='utf-8-sig')
                    new_df = new_df[~new_df['id'].isin(existing_df['id'])]

                if not new_df.empty:
                    new_df.to_csv(file_path, mode='a', index=False, 
                                 header=not file_path.exists(), encoding='utf-8-sig')
                    print(f"Success! Added {len(new_df)} new items.")
                else:
                    print("No new tweets found in the last hour.")
            
            # --- PROGRESS COUNTDOWN ---
            wait_time = base_wait + random.randint(1, 5)
            print(f"Next poll in {wait_time} seconds...", end="", flush=True)
            for _ in range(wait_time):
                time.sleep(1)
                print(".", end="", flush=True)
            print("\n")

    except KeyboardInterrupt:
        print("\n--- Pipeline Stopped. ---")

if __name__ == "__main__":
    run_realtime_ingest()