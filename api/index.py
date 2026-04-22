from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import sys

# Add root to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.intelligence_engine import IntelligenceEngine

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Market Intelligence API is running", "endpoints": ["/api/python-health", "/api/sync", "/api/data"]}

@app.get("/api/python-health")
def health_check():
    return {"status": "ok", "runtime": "python"}

@app.post("/api/sync")
async def run_sync(background_tasks: BackgroundTasks):
    """Triggers the Full Intelligence Flow (Kaggle focused)."""
    def sync_process():
        try:
            engine = IntelligenceEngine()
            engine.load_all_sources(skip_itviec=True)
            report = engine.run_agentic_analysis()
            print(f"[API] Sync completed: {report}")
        except Exception as e:
            print(f"[API_ERR] Sync failed: {str(e)}")

    background_tasks.add_task(sync_process)
    return {"status": "triggered", "message": "Intelligence Sync started."}

@app.post("/api/sync/itviec")
async def run_itviec(background_tasks: BackgroundTasks):
    """Triggers the ITviec Crawler."""
    def itviec_process():
        try:
            from crawlers.itviec import run_itviec_crawler
            run_itviec_crawler(limit=20)
            print("[API] ITviec Sync completed.")
        except Exception as e:
            print(f"[API_ERR] ITviec failed: {str(e)}")

    background_tasks.add_task(itviec_process)
    return {"status": "triggered", "message": "ITviec Crawler started."}

@app.post("/api/sync/extract")
async def run_extract(background_tasks: BackgroundTasks):
    """Triggers the Dataset Extraction."""
    def extract_process():
        try:
            from scripts.extract_datasets import extract_all
            extract_all()
            print("[API] Extraction completed.")
        except Exception as e:
            print(f"[API_ERR] Extraction failed: {str(e)}")

    background_tasks.add_task(extract_process)
    return {"status": "triggered", "message": "Data Extraction started."}

@app.get("/api/market-data")
def get_market_data():
    """Returns the latest intelligence data from /tmp or public."""
    import json
    from pathlib import Path
    from config.settings import SYNC_DIR
    
    # Priority 1: Freshly synced data in /tmp (Vercel) or data/sync (Local)
    sync_path = SYNC_DIR / "intelligence.json"
    # Priority 2: Static build-time data in public folder
    public_path = Path("public/data/intelligence.json")
    
    for data_path in [sync_path, public_path]:
        if data_path.exists():
            try:
                with open(data_path, "r") as f:
                    return json.load(f)
            except: continue
            
    return {"error": "Data not found. Run sync first."}

@app.get("/api/kaggle-data")
def get_kaggle_data():
    """Returns detailed Kaggle benchmarks for verification."""
    try:
        engine = IntelligenceEngine()
        engine.load_all_sources(skip_itviec=True)
        # 1. Try to get correlated data (Local + Global)
        merged = engine._correlate_data()
        
        if merged.empty:
            print("[INFO] Correlation empty. Returning raw global benchmarks.")
            # Return global benchmarks directly if no local data matches
            return engine.global_benchmarks.fillna(0).to_dict(orient="records")
            
        return merged.fillna(0).to_dict(orient="records")
    except Exception as e:
        print(f"[API_ERR] Kaggle data fetch failed: {str(e)}")
        return {"error": "Internal server error"}
