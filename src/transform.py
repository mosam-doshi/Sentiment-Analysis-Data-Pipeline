import pandas as pd
from pathlib import Path

def run_clean_transform():
    project_root = Path(__file__).resolve().parent.parent
    raw_path = project_root / "data" / "raw" / "raw_data.csv"
    proc_folder = project_root / "data" / "processed"
    proc_path = proc_folder / "cleaned_data.csv"
    
    if not raw_path.exists():
        print(f"No raw data found at {raw_path}. Run ingest.py first!")
        return

    print(f"Reading raw data...")
    df = pd.read_csv(raw_path, encoding='utf-8-sig')

    # 3. Clean Timestamps
    # Converts "Fri, 26 Dec 2025 07:00:00 GMT" to "2025-12-26 07:00:00"
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    initial_count = len(df)
    df = df.drop_duplicates(subset=['id'])
    df = df.dropna(subset=['text'])
    
    print(f"Removed {initial_count - len(df)} duplicate or empty rows.")

    proc_folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(proc_path, index=False, encoding='utf-8-sig')
    
    print(f"Cleaned data stored in: {proc_path}")
    print(f"Total high-quality records: {len(df)}")

if __name__ == "__main__":
    run_clean_transform()