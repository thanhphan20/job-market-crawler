import os
import json
import pandas as pd
from datetime import datetime
from analytics.intelligence_engine import IntelligenceEngine
from analytics.kaggle_analyzer import KaggleMarketAnalyzer
from supabase import create_client, Client
from dotenv import load_dotenv

import numpy as np

load_dotenv()

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    return obj

# Initialize Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[!] ERROR: Supabase credentials missing. Data will be saved to data/sync/ instead.")
    SUPABASE_ENABLED = False
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_ENABLED = True

def sync_itviec_jobs(data_dir="data"):
    """Pushes raw ITviec jobs to Supabase."""
    if not SUPABASE_ENABLED: return
    
    it_files = [f for f in os.listdir(data_dir) if "itviec" in f and f.endswith(".json")]
    if not it_files: return
    
    latest_file = os.path.join(data_dir, sorted(it_files)[-1])
    with open(latest_file, "r") as f:
        jobs = json.load(f)
        
    print(f"[*] Syncing {len(jobs)} jobs to Supabase...")
    for job in jobs:
        # Minimal transformation to match Prisma schema
        payload = {
            "title": job.get("Title"),
            "company": job.get("Company"),
            "source": "ITviec"
        }
        # Note: Parsing logic for salary/exp could be added here or kept in DB triggers
        try:
            supabase.table("Job").upsert(payload, on_conflict="title,company").execute()
        except Exception as e:
            pass # Silent fail for duplicates

def sync_global_intelligence():
    """Syncs processed Global Intelligence data."""
    engine = IntelligenceEngine()
    engine.load_all_sources()
    data = convert_numpy_types(engine.get_processed_data())
    
    if SUPABASE_ENABLED:
        print(f"[*] Syncing {len(data)} intelligence records...")
        try:
            supabase.table("GlobalIntelligence").upsert(data, on_conflict="tech").execute()
        except Exception as e:
            print(f"[!] Supabase error: {e}")
            save_to_local("global_intelligence.json", data)
    else:
        save_to_local("global_intelligence.json", data)

def sync_kaggle_insights():
    """Syncs processed Kaggle insights."""
    analyzer = KaggleMarketAnalyzer()
    insights = convert_numpy_types(analyzer.get_processed_data())
    
    if SUPABASE_ENABLED:
        if insights["ai_impact"]:
            print(f"[*] Syncing AI Impact Matrix ({len(insights['ai_impact'])} records)...")
            try:
                supabase.table("AIImpactMatrix").upsert(insights["ai_impact"], on_conflict="industry,status").execute()
            except Exception as e:
                print(f"[!] Supabase error: {e}")
        if insights["salary_trends"]:
            print(f"[*] Syncing Salary Trends ({len(insights['salary_trends'])} records)...")
            try:
                supabase.table("SalaryTrend").upsert(insights["salary_trends"], on_conflict="year,tech,source").execute()
            except Exception as e:
                print(f"[!] Supabase error: {e}")
        save_to_local("kaggle_insights.json", insights)
    else:
        save_to_local("kaggle_insights.json", insights)

def save_to_local(filename, data):
    sync_dir = "data/sync"
    if not os.path.exists(sync_dir): os.makedirs(sync_dir)
    path = os.path.join(sync_dir, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Data saved to: {path}")

def run():
    print("🚀 Starting Market Intelligence Sync...")
    # sync_itviec_jobs() # Optional: heavy
    sync_global_intelligence()
    sync_kaggle_insights()
    print("✅ Sync complete.")

if __name__ == "__main__":
    run()
