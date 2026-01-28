import subprocess
import sys
import time
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================
BASE_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    {
        "path": BASE_DIR / "src" / "ingest.py",
        "description": "Step 1: Data Ingestion (ingest.py)",
    },
    {
        "path": BASE_DIR / "src" / "transform.py",
        "description": "Step 2: Data Cleaning (transform.py)",
    },
    {
        "path": BASE_DIR / "src" / "send" / "Sentiment.py",
        "description": "Step 3: Sentiment Analysis (Sentiment.py)",
    },
    {
        "path": BASE_DIR / "analysis" / "analysis.py",
        "description": "Step 4: Analytics Aggregation (analysis.py)",
    },
]

# =====================================================
# EXECUTION HELPER
# =====================================================
def run_script(script_path, description):
    print(f"\nStarting: {description}...")
    try:
        # Check if file exists
        if not script_path.exists():
            print(f"Error: File not found: {script_path}")
            sys.exit(1)
            
        start_time = time.time()
        # Execute the script
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        
        duration = time.time() - start_time
        print(f"Completed: {description} ({duration:.2f}s)")
        
    except subprocess.CalledProcessError as e:
        print(f"Execution Failed: {description}")
        print(f"Exit Code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)

# =====================================================
# MAIN PIPELINE
# =====================================================
if __name__ == "__main__":
    print("=======================================================")
    print("   GEN-Z PULSE APPLICATION RUNNER")
    print("=======================================================")
    
    # 1. Run all data processing scripts sequentially
    for script_info in SCRIPTS:
        run_script(script_info["path"], script_info["description"])
        # Add a small delay for stability/file I/O catch-up
        time.sleep(1)

    print("\n=======================================================")
    print("   ALL DATA PROCESSED SUCCESSFULLY. LAUNCHING DASHBOARD")
    print("=======================================================")
    
    # 2. Launch Streamlit Dashboard
    try:
        dashboard_path = BASE_DIR / "dashboard.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)], check=True)
    except KeyboardInterrupt:
        print("\n Stopped by user.")
    except Exception as e:
        print(f"Error launching dashboard: {e}")

