import subprocess
import time
import sys
from pathlib import Path

def run_pipeline():
    print("Starting Data Engineering Pipeline...")
    
    # Define paths to your scripts
    ingest_script = Path("src/ingest.py")
    transform_script = Path("src/transform.py")

    # 1. Start Ingestion as a background process
    print("Step 1: Launching Ingestion (Background)...")
    ingest_proc = subprocess.Popen([sys.executable, str(ingest_script)])

    try:
        while True:
            # 2. Run Transformation every 10 minutes
            print(f"\n[{time.strftime('%H:%M:%S')}] Step 2: Running Transformation/Cleaning...")
            
            # We use .run() for transform because we want it to finish before moving on
            subprocess.run([sys.executable, str(transform_script)])
            
            print("Pipeline cycle complete. Next clean-up in 10 minutes.")
            print("Ingest script is still running in the background...")
            
            # Wait 10 minutes (600 seconds) before the next transformation
            time.sleep(600)

    except KeyboardInterrupt:
        print("\nShutting down pipeline...")
        ingest_proc.terminate() # Safely stop the background ingest script
        print("All processes stopped.")

if __name__ == "__main__":
    run_pipeline()