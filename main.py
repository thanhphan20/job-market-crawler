import os
import argparse
import csv
from datetime import datetime
from crawlers.itviec import scrap_itviec
from analytics.intelligence_engine import IntelligenceEngine

def main():
    parser = argparse.ArgumentParser(description="Job Market Intelligence Engine v4.0")
    parser.add_argument("--crawl", action="store_true", help="Run the scrapper")
    parser.add_argument("--fetch", action="store_true", help="Fetch SO benchmarks")
    parser.add_argument("--analyze", action="store_true", default=True, help="Run analysis")
    
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Crawl (if requested)
    if args.crawl:
        print("\n--- Scraping Market Data ---")
        results = scrap_itviec(limit=100)
        if results:
            csv_path = f'data/itviec_jobs_{timestamp}.csv'
            os.makedirs('data', exist_ok=True)
            keys = results[0].keys()
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)
            print(f"[+] Saved to {csv_path}")

    # 2. Intelligence Engine Analysis
    if args.analyze:
        print("\n--- Running Intelligence Engine (Bloomberry & LinkedIn Pattern) ---")
        engine = IntelligenceEngine()
        engine.load_all_sources(data_dir="data")
        
        report_path = engine.run_agentic_analysis()
        if report_path:
            print(f"\n[DONE] Strategic Market Intelligence Report: {report_path}")

if __name__ == "__main__":
    main()
